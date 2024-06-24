#imports
import whisper
import os
import boto3
from openai import OpenAI
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import soundfile as sf
import json
import uuid
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
dynamodb = boto3.resource(
    'dynamodb',
    region_name="ap-southeast-1"
  )
TABLE_CALL_ANALYSIS='call-analysis-table'
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
def callAnalysis(body):
  try:
    print('Call Analysis', body)
    local_file_paths= getFilesToLocal(body)
    # process_with_whisper_api(local_file_paths)
    finalresponse = analysisProcess(local_file_paths)
    print('')
    return finalresponse
  except ClientError as e:
    print('Error in callAnalysis :::', e)
    raise Exception(f"Error in callAnalysis: {e}")

def analysisProcess(local_file_paths):
  try:
    print('*************** Analysis process Started ***************')
    finalAnalysisResponse=[]
    for file_path in local_file_paths:
        transcription = process_with_whisper_hugging_face_model(file_path)
        segments = transcription['chunks']
        updatedSegments=[]
        for index, segment in enumerate(segments):
            updatedSegments.append({'segment_id':index, 'text':segment['text'], 'timestamp':segment['timestamp']})
        analysisResponse = prompting_with_bedrock(updatedSegments)
        print('========================')
        print('transcriptions from whisper ::::::', json.dumps(transcription))
        print('========================')
        print('update segments', updatedSegments)
        print('========================')
        print('analysisResponse completions:::::::', analysisResponse['completion'])
        completion = analysisResponse['completion']
        updatedCompletion = analysisResponse['completion'].replace('Here is the JSON output as per the instructions:', '').replace('Here is the JSON output with the requested information:', '').replace('```json', '').replace('```', '')
        print('updatedCompletion json dumps', json.dumps(updatedCompletion))
        updatedCompletions1= updatedCompletion.replace('\'', '').replace('\n', '')
        print('=======================')
        print('pdatedCompletions1 =====', updatedCompletions1)
        dbRecord = {
         'transcription_whisper': json.dumps(transcription),
          'updated_segments': json.dumps(updatedSegments),
          'analysis_response': json.dumps(updatedCompletions1)
        }
        inserToDB(dbRecord)
        finalAnalysisResponse.append(json.dumps(dbRecord))
        print('analysisResponse', analysisResponse)
    print('*************** Analysis process Ended ***************')
    return finalAnalysisResponse
  except ClientError as e:
    print('Error in analysisProcess :::', e)
    raise Exception(f"Error in analysisProcess: {e}")

#FROM S3 to local
def getFilesToLocal(body):
  try:
    print('*************** Download files from cloud ***************')
    files = body['files']
    print('files ::: ', files)
    local_file_paths=[]
    for file in files:
        temp=download_from_s3(file)
        local_file_paths.append(temp)
    print('local_file_paths', local_file_paths)
    print('*************** Download files completed returning local file paths ***************')
    return local_file_paths  
  except ClientError as e:
    print('Error in getFilesToLocal :::', e)
    raise Exception(f"Error getFilesToLocal: {e}")

def download_from_s3(file_name):
  try:
    local_path = '/tmp/' + file_name
    print('S3_BUCKET', S3_BUCKET)
    s3.download_file(S3_BUCKET, file_name, local_path)
    return local_path
  except ClientError as e:
    print('Error in download_from_s3 :::', e)
    raise Exception(f"Error download_from_s3: {e}")

def process_with_whisper_hugging_face_model(file_path):
  try:
    print('*************** Started process_with_whisper_hugging_face_model')
    # audio_file= open(file_path, "rb")
    # audio_sf_file, sample_rate = sf.read(file_path)
    result = pipe(file_path)
    print('RESPONSE:: process_with_whisper_hugging_face_model')
    print('result', result)
    return result
  except ClientError as e:
    print('Error in process_with_whisper_hugging_face_model :::', e)
    raise Exception(f"Error in process_with_whisper_hugging_face_model: {e}")

def prompting_with_bedrock(transcription):
  try:
    prompt = get_prompt(transcription)
    claude_prompt = f"\n\nHuman:{prompt}\n\nAssistant:"
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
    return response_body
  except ClientError as e:
    print('Error in prompting_with_bedrock :::', e)
    raise Exception(f"Error in prompting_with_bedrock: {e}")

def inserToDB(dbRecord):
  try:
    analysisTable = dynamodb.Table(TABLE_CALL_ANALYSIS)
    item = dbRecord
    item['type'] = 'CALL'
    item['call_id'] = str(uuid.uuid4())
    print('item', item)
    response = analysisTable.put_item(Item=item)
    print('response inserting to DB::: ',response)
  except ClientError as e:
    print('Error inserting analysis to DB:::', e)
    raise Exception(f"Insert failed: {e}")



def get_prompt(data):
    prompt =f'''
       I have a call conversation transcript below is the details of task that needs to be done.
        Below each point describes an key's value in the JSON output
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
                        2. After identifying role,sentiment of each segment give the analysis in an format a string like segment_id, role, sentiment attached with '-' in between. and push these string into an array. I dont want any objects inside the array it should strictly be a string with segment_is, role and sentiment seperated with '-'.
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
                "segregated_conversations": []
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
