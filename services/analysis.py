# import datetime
import os
import boto3
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import json
import uuid
import re
# from decimal import decimal
from services.db.db_connection import updateTaskStatusforCallId, updateFinalAnalysis, updateWhisperTimeTaken, promptResponseTimeTaken
from datetime import datetime
#Imports END

############################################ Connections & Config START
brt = boto3.client(
    service_name='bedrock-runtime', 
    region_name='us-east-1'
    )
S3_BUCKET= 'genesys-audio-file-dev'
print('S3_BUCKET', S3_BUCKET)
s3 = boto3.client(
    's3',
    region_name='ap-southeast-1'
  )
############################################ Connections & Config END

###################### Model Setup ##########################
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print('device', device)
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
print('torch_dtype', torch_dtype)
model_id = "openai/whisper-large-v3"
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

###################### Model Setup END ##########################


# Base Function
def callAnalysis(file, call, db):
  try:
    print('*************** callAnalysis Function Started ***************')
    print('*************** Call Analysis file :::', file)
    print('*************** Call Analysis call :::', call)
    local_file_path= getFilesToLocal(file)
    finalresponse = analysisProcess(local_file_path, call, db)
    print('finalresponse in call analysis', finalresponse)
    print('*************** callAnalysis Function END ***************')
    return finalresponse
  except Exception as e:
    print('Error in callAnalysis :::', e)
    raise Exception(f"Error in callAnalysis: {e}")

def analysisProcess(file_path, call, db):
  try:
    print('*************** Analysis process Started ***************')
    finalAnalysisResponse=[]
    transcription = process_with_whisper_hugging_face_model(file_path, call['call_id'], db)
    segments = transcription['chunks']
    updatedSegments=[]
    for index, segment in enumerate(segments):
        updatedSegments.append({'segment_id':index, 'text':segment['text'], 'timestamp':segment['timestamp']})
    analysisResponse = prompting_with_bedrock(updatedSegments, call['call_id'], db)
    completion =  analysisResponse['completion']
    completion_json =  re.search(r'```json(.*?)```', completion, re.DOTALL)
    updatedCompletion = completion_json.group(1).strip()
    escape_pattern = r'\\[abfnrtv\\]'
    updatedCompletionNoEscape = re.sub(escape_pattern, '', updatedCompletion)
    whisper_dumps = json.dumps(transcription)
    updated_segments_dumps = json.dumps(updatedSegments)
    dbRecord = {
      'transcription_whisper': json.dumps(transcription),
      'updated_segments': json.dumps(updatedSegments),
      'analysis_response': json.loads(updatedCompletionNoEscape)
    }
    inserToDB(dbRecord, call, db)
    finalAnalysisResponse.append(dbRecord)
    print('analysisResponse', analysisResponse)
    print('*************** Analysis process Ended ***************')
    return finalAnalysisResponse
  except Exception as e:
    print('Error in analysisProcess :::', e)
    raise Exception(f"Error in analysisProcess: {e}")

#FROM S3 to local
def getFilesToLocal(file):
  try:
    print('*************** Download files from cloud ***************')
    # files = body['files']
    print('file ::: ', file)
    # local_file_paths=[]
    # for file in files:
    temp=download_from_s3(file)
    print('file', file)
    print('*************** Download files completed returning local file paths ***************')
    return temp  
  except Exception as e:
    print('Error in getFilesToLocal :::', e)
    raise Exception(f"Error getFilesToLocal: {e}")

def download_from_s3(file_name):
  try:
    local_path = '/tmp/' + file_name
    print('S3_BUCKET', S3_BUCKET)
    s3.download_file(S3_BUCKET, file_name, local_path)
    return local_path
  except Exception as e:
    print('Error in download_from_s3 :::', e)
    raise Exception(f"Error download_from_s3: {e}")

def process_with_whisper_hugging_face_model(file_path, call_id, db):
  try:
    startTime = datetime.now()
    print('*************** Started process_with_whisper_hugging_face_model')
    result = pipe(file_path)
    endTime = datetime.now()
    time_difference = endTime - startTime
    # Get the difference in seconds
    difference_in_seconds = time_difference.total_seconds()
    updateWhisperTimeTaken(db, difference_in_seconds, call_id)
    print('RESPONSE:: process_with_whisper_hugging_face_model')
    print('result', result)
    return result
  except Exception as e:
    print('Error in process_with_whisper_hugging_face_model :::', e)
    raise Exception(f"Error in process_with_whisper_hugging_face_model: {e}")

def prompting_with_bedrock(transcription, call_id, db):
  try:
    startTime = datetime.now()
    prompt = get_prompt(transcription)
    claude_prompt = f"Human:{prompt}  Answer in JSON format Assistant:"
    print('Prompt:::', prompt)
    body = json.dumps({
        "prompt": claude_prompt,
        "temperature": 0.1,
        "max_tokens_to_sample": 4096
    })
    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'
    response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    print('response from AWS Bedrock', response_body)
    endTime = datetime.now()
    time_difference = endTime - startTime
    # Get the difference in seconds
    difference_in_seconds = time_difference.total_seconds()
    promptResponseTimeTaken(db, difference_in_seconds, call_id)
    return response_body
  except Exception as e:
    print('Error in prompting_with_bedrock :::', e)
    raise Exception(f"Error in prompting_with_bedrock: {e}")

def inserToDB(dbRecord, call, db):
  try:
    print('*************** inserToDB process Started ***************')
    updateTaskStatusforCallId(db, 'DONE', call['call_id'])
    analysis_response = dbRecord['analysis_response']
    analysis_response['processed_timestamp'] = datetime.now()
    updateFinalAnalysis(
      db,
      {'call_id': call['call_id']},
      analysis_response,
      dbRecord['transcription_whisper']
    )
    print('*************** inserToDB process Completed ***************')
  except Exception as e:
    print('Error inserting analysis to DB:::', e)
    raise Exception(f"Insert failed: {e}")

def get_prompt(data):
    prompt =f'''
       My Company name is Astro. I have a call conversation transcript below is the details of task that needs to be done.
        Below each point describes an key's value in the JSON output in markdown format. 
        Note: DO NOT PASS THE INSTRUCTIONS IN RESPONSE ONLY RETURN THE JSON OBJECT
            1. Identifying Role and Sentiment:
                How to identify roles 
                    IVR Identification: Segments that involve automatic responses, instructions for pressing buttons, and general introductory messages are typically IVR.
                    Customer Identification: Segments where personal information is provided, complaints are made, or specific issues are raised are usually from the customer.
                    Agent Identification: Segments where the speaker verifies information, provides assistance, or takes actions to resolve an issue are typically from the agent.
                Identify the possible role of the speaker like agent, IVR or customer from the given possible roles for each segment based on text in the segment object. Follow the below give How to identify roles text.
                These are the possible roles: IVR, customer , agent.
                These are the possible sentiments: positive, negative, neutral.
                Determine the sentiment of each segment (positive, negative, neutral).
                Return the results in a JSON array where each object includes the segment id, role, and sentiment.
                    Note:
                        1. Ensure all segments from the conversation are included in the JSON output. (for example if there are 154 segments then the output should have the same number of segments)
                        2. After identifying role,sentiment of each segment give the analysis in an format a string like segment_id, role, sentiment attached with '-' in between. and push these string into an array. I dont want any objects inside the array it should strictly be a string with segment_id, role and sentiment seperated with '-'. (Here these three parameter segment_id, role and sentiment are required and should not be missed for any segment)
            2. Collect Meta Data: Extract any customer meta data such as name, account number, email, or if any other meta data provided during the call and include it in the JSON under "customer_meta_data".
            3. Call Summary: Provide a concise summary of the call within the same JSON structure in 'call_summary'.
            4. Call Objective: Identify and include the main objective of the call. Add it in the JSON under 'call_objective'
            5. Product Discussion: Identify and include the product being discussed in the call. Use the corresponding term from the list below if it matches, otherwise identify the product/service dicussed in the conversation and give it in product discuccion:
            Ensure that the product is not marked as N/A if a product is clearly mentioned in the conversation which is related to the below products.
                Note:
                if there is not Product discussed but they discussed about any service please provide the service requested for in the product.
                a. Ultra Setup Box issue
                b. Ulti Setup Box issue
                c. Fiber issue
                d. Fiber Plan
                e. DTH Issuez
                f. DTH Plan
                g. OTT issue
                h. Mobile Service
            Add it in the JSON under 'product_discussed'
            6. Agent Actions: List the actions taken by the agents to address the customer's issue or request. Add it in the JSON under 'agent_actions'
            7. Overall Conversation Rating for Agents: Provide an overall conversation rating out of 10 for the agent(s) based on their performance. Add it in the JSON under 'overall_conversation_rating_for_agents'
            8. Overall Sentiment of the Call: Provide the overall sentiment of the customer in the call. Add it in the JSON under 'overall_sentiment_of_the_call'
            9. Issue resolved: I need the information if the customer got the necessary help from the agent and resolved the issue or not. Add it in the JSON key 'issue_resolved'
            10. Analyze the customer conversation to determine if the customer has called more than once for the same issue. Add it in the JSON under 'called_more_than_once'
            11. Overall customer satisfaction: Assess the overall satisfaction level of the customer during the call and rate it on 10. Add it in the JSON under  overall_customer_satisfaction_level
            12. Give me the over all call time in seconds. Add it in the JSON under 'overall_call_time'. Over all call time would be the sum of all endTime - startTime for each segment.
            13. Give me individual call time for different roles in the call in an array of object where key is role and value will call time in seconds. Here call time would be the sum of the endTime-startTime for each segment of respective role. Add it in the JSON under 'individual_call_time'.

            Here is the call transcription from Open AI Whispher in stringify JSON format:

            {data}

            Example of expected JSON output:
                "segregated_conversations": ["0-IVR-neutral", "1-IVR-positive"]
                "customer_meta_data":
                "name": "John Doe",
                "account_number": "1234567890",
                "email": "mailto:john.doe@example.com"
                "call_summary": "The customer called to report an issue with their product. They were transferred through the IVR system and spoke with an agent.",
                "call_objective": "Report and resolve an issue with a product.",
                "product_discussed": "XYZ Product",
                "agent_actions": [
                "Verified the customer's account",
                "Troubleshot the issue",
                "Processed a replacement order"
                ],
                "overall_call_summary": "The call began with an IVR interaction, followed by the customer reporting an issue with XYZ Product to agent_1. After initial troubleshooting, the call was escalated to agent_2, who processed a replacement order for the customer.",
                "overall_conversation_rating_for_agents": 8.5,
                "overall_sentiment_of_the_call": "Neutral"
                "overall_call_time": 30,
                "individual_call_time": 'agent_1': 30, customer: 40, ivr: 60
    '''
    return prompt
