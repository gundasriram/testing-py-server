#imports
import whisper
import os
import boto3
from openai import OpenAI
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
#Imports END

############################################ Connections & Config START
S3_BUCKET= os.getenv('S3_BUCKET')
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

###################### Model Setup ##########################
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
print('device', device)
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
dummytranscription =  {
  "text": " Hello, welcome to Astro. Hai, selamat datang ke Astro. Untuk bahasa Melayu, tekan 1. To speak in English, press 2. Untuk pertanyaan akaun, tekan 1. Untuk permohonan akaun baru atau broadband, tekan 2. Sila tunggu sebentar sementara kami mengesahkan maklumat anda. Kami telah mengesan terdapat lebih daripada satu akaun bagi nombor muda alih ini. Untuk memasukkan nombor akaun anda, tekan 1. Atau untuk bercakap dengan ejen kami, tekan 2. Sila tunggu sebentar. Kami akan menyambungkan panggilan anda kepada ejen kami. Harap maklum bahawa semua perbualan adalah dirakam bagi tujuan latihan dan meningkatkan mutu ejen kami agar dapat memberi layanan yang lebih baik kepada anda. Hello, saya Nakibah. Saya nak beritahu sebab sebenarnya saya dah lama dah diaktifkan tutup akaun saya Ujung bulan 1 tu Tapi saya masih lagi dapat saya punya Bil Okay sebelum tu Boleh saya dapatkan akaun nombor istru 089 089 3441 3441 351 351 okay sekejap ya puan ok puan puan boleh tunggu dalam panggilan untuk saya buat saya makan ok ok terima kasih see Thank you. © BF-WATCH TV 2021 Thank you. © B Emily Beynon © BF-WATCH TV 2021 Thank you. © BF-WATCH TV 2021 © transcript Emily Beynon Thank you. Terima kasih kerana menunggu Okey sekarang ni saya tengok Dalam ni memang Puan ada outstanding Semuanya 459 Jadi saya ada tengok dekat Not kat sini Memang Puan ada mohon untuk penutupan Tapi sepatutnya Ada orang yang akan call Puan balik Tapi dia tak call Puan Okey Masa saya call tu dia suruh saya jelaskan ada remaining tu, lepas tu saya dah jelaskan, saya call balik dia kata ok semuanya dah settle tak perlu tunggu apa-apa dah tutup account dia kata mesti ada record kan semua perbualan kan sebab kat sini dia ada ada record tak perbualan,? sebab kat sini dia ada.. tak saya tanya ada record tak perbualan? ada kan? boleh rujuk kan? recorded perbualan kan? itu bukan kuasa saya lah cuma kat sini memang ada yang ada note yang mengatakan cik buat, cik memohon untuk Disconnect Bukan saya memohon, saya telefon untuk saya disconnect terus Nak mohon apa lagi, saya dah Setakan remaining balance dan saya Call untuk putuskan Tutup account Tak ada pun orang kecil tak buatkan call Tapi kat sini Saya dah lama dah saya Kat sini sepatutnya ada Agent yang kena call puan untuk apa dia nak call saya sebab tak itu saya tak tahu sebab memang kat sini dia ada agent yang tak je dia dia tak cakap dia nak call saya dia kata ok ada bahasa sebanyak ini kena tu saya memang saya dah rightly terus bank in remaining balance sebelum saya perlu tutup account lepas tu that's it saya tak nak bayar yang 400 lebih tu sebab saya tak guna dah, saya dah call, saya nak disconnect, nak tutup akaun ok puan ni tak ada cakap, macam mana saya tak nak bayar yang 400 tu sebab saya tak guna dan saya dah call untuk tutup akaun dan ada recorded perbualan sepatutnya, boleh rujuk Ok puan Ok puan boleh tunggu dalam panggilan Untuk saya buat semakan dengan saya punya Team manager lah Ok Saya tunggu Saya nak boleh dicata hari ni Ok © transcript Emily Beynon Thank you. © transcriptF-WATCH TV 2021 © transcriptF-WATCH TV 2021 © transcript Emily Beynon Thank you. Terima kasih dah buat semakan yang saya pun dah bincang dengan TM. Sepatutnya ada satu agent ni dia akan buat penutupan lah tapi kat sini dia memang tak buat penutupan. Jadi kita memang saya akan buat report berkenaan ni dan saya akan suruh agent yang call dengan puan waktu 19.01 tu untuk call puan balik untuk buat penutupan lah. Baru sekarang nak buat penutupan lah baru sekarang nak buat penutupan sebab kat sini memang sepatutnya bil tu macam mana saya tak nak bayar saya dah cakap awal-awal saya nak tutup bil tu memang sepatutnya memang puan dah tak perlu bayar lah sebab sepatutnya puan kena tutup 19 ribu bulan sebab saya ke bill puan pun 22 ribu bulan jadi waktu puan dah bayar pada tarikh puan ada buat bayaran untuk settle kan waktu 18 ribu bulan 1 jadi waktu tu memang dah tak ada apa-apa outstanding jadi kat situ puan dah tak perlu bayar jadi memang kita akan buat report lah berkenaan ni dan dia akan buat penutupan lah sebab dia agent yang sebelum jadi memang kita akan buat report lah berkenaan ni ok dan dia akan buat penutupan lah sebab dia agent yang sebelum ni memang dia tak buat penutupan dia tak ada call pun untuk bagitahu bila untuk buat penutupan semua ok so saya kira dah settle eh saya tak perlu bayar eh yang saya tak guna tu ok betul tapi sebelum tu boleh saya dapatkan nombor telefon pun untuk saya bagi call agent untuk call puan balik? Okey 011. 011. 3707. 3707. 8012. 8012. Okey saya ulang ya. 011. 3707. 8012. Betul. 3707 8012 Betul Ok Puan saya akan buat report ni Sekarang lah untuk dia return call Kepada Puan semula Ok Ada apa-apa lagi boleh saya bantu Puan? Itu sahaja Ok terima kasih Puan Ok",
  "chunks": [
    {
      "timestamp": 3.38,
      "text": " Hello, welcome to Astro."
    },
    {
      "timestamp": 6.5,
      "text": " Hai, selamat datang ke Astro."
    },
    {
      "timestamp": 10.8,
      "text": " Untuk bahasa Melayu, tekan 1."
    },
    {
      "timestamp": 13.5,
      "text": " To speak in English, press 2."
    },
    {
      "timestamp": 20.8,
      "text": " Untuk pertanyaan akaun, tekan 1."
    },
    {
      "timestamp": 25.54,
      "text": " Untuk permohonan akaun baru atau broadband, tekan 2."
    },
    {
      "timestamp": 31.94,
      "text": " Sila tunggu sebentar sementara kami mengesahkan maklumat anda."
    },
    {
      "timestamp": 38.52,
      "text": " Kami telah mengesan terdapat lebih daripada satu akaun bagi nombor muda alih ini."
    },
    {
      "timestamp": 42.1,
      "text": " Untuk memasukkan nombor akaun anda, tekan 1."
    },
    {
      "timestamp": 45.92,
      "text": " Atau untuk bercakap dengan ejen kami, tekan 2."
    },
    {
      "timestamp": 53.48,
      "text": " Sila tunggu sebentar. Kami akan menyambungkan panggilan anda kepada ejen kami."
    },
    {
      "timestamp": 66.04,
      "text": " Harap maklum bahawa semua perbualan adalah dirakam bagi tujuan latihan dan meningkatkan mutu ejen kami agar dapat memberi layanan yang lebih baik kepada anda."
    },
    {
      "timestamp": 75.32,
      "text": " Hello, saya Nakibah."
    },
    {
      "timestamp": 81.7,
      "text": " Saya nak beritahu sebab sebenarnya saya dah lama dah"
    },
    {
      "timestamp": 86,
      "text": " diaktifkan tutup akaun saya Ujung bulan 1 tu"
    },
    {
      "timestamp": 87.94,
      "text": " Tapi saya masih lagi dapat saya punya"
    },
    {
      "timestamp": 88.72,
      "text": " Bil"
    },
    {
      "timestamp": 91.72,
      "text": " Okay sebelum tu"
    },
    {
      "timestamp": 93.62,
      "text": " Boleh saya dapatkan akaun nombor istru"
    },
    {
      "timestamp": 95.68,
      "text": " 089"
    },
    {
      "timestamp": 96.96,
      "text": " 089"
    },
    {
      "timestamp": 98.92,
      "text": " 3441"
    },
    {
      "timestamp": 100.68,
      "text": " 3441"
    },
    {
      "timestamp": 102.56,
      "text": " 351"
    },
    {
      "timestamp": 105.18,
      "text": " 351 okay sekejap ya puan"
    },
    {
      "timestamp": 114.68,
      "text": " ok puan"
    },
    {
      "timestamp": 116.34,
      "text": " puan boleh tunggu dalam panggilan"
    },
    {
      "timestamp": 117.18,
      "text": " untuk saya buat saya makan"
    },
    {
      "timestamp": 118.34,
      "text": " ok"
    },
    {
      "timestamp": 466.98,
      "text": " ok terima kasih see Thank you. © BF-WATCH TV 2021 Thank you. © B Emily Beynon © BF-WATCH TV 2021 Thank you. © BF-WATCH TV 2021 © transcript Emily Beynon Thank you. Terima kasih kerana menunggu Okey sekarang ni saya tengok"
    },
    {
      "timestamp": 468.98,
      "text": " Dalam ni memang Puan ada outstanding"
    },
    {
      "timestamp": 470.72,
      "text": " Semuanya 459"
    },
    {
      "timestamp": 472.96,
      "text": " Jadi saya ada tengok dekat"
    },
    {
      "timestamp": 473.9,
      "text": " Not kat sini"
    },
    {
      "timestamp": 477.28,
      "text": " Memang Puan ada mohon untuk penutupan"
    },
    {
      "timestamp": 479.26,
      "text": " Tapi sepatutnya"
    },
    {
      "timestamp": 481.2,
      "text": " Ada orang yang akan call Puan balik"
    },
    {
      "timestamp": 482.7,
      "text": " Tapi dia tak call Puan"
    },
    {
      "timestamp": 484.04,
      "text": " Okey"
    },
    {
      "timestamp": 486.52,
      "text": " Masa saya call tu"
    },
    {
      "timestamp": 487.94,
      "text": " dia suruh saya jelaskan ada"
    },
    {
      "timestamp": 489.96,
      "text": " remaining tu, lepas tu saya dah"
    },
    {
      "timestamp": 491.72,
      "text": " jelaskan, saya call balik dia kata"
    },
    {
      "timestamp": 493.44,
      "text": " ok semuanya dah settle"
    },
    {
      "timestamp": 495.44,
      "text": " tak perlu tunggu apa-apa"
    },
    {
      "timestamp": 497.46,
      "text": " dah tutup account dia kata"
    },
    {
      "timestamp": 499.66,
      "text": " mesti ada record kan"
    },
    {
      "timestamp": 501.22,
      "text": " semua perbualan kan"
    },
    {
      "timestamp": 502.92,
      "text": " sebab kat sini"
    },
    {
      "timestamp": 504.5,
      "text": " dia ada"
    },
    {
      "timestamp": 506.6,
      "text": " ada record tak perbualan,? sebab kat sini dia ada.. tak saya tanya ada record tak perbualan?"
    },
    {
      "timestamp": 511.5,
      "text": " ada kan? boleh rujuk kan? recorded perbualan kan?"
    },
    {
      "timestamp": 520.04,
      "text": " itu bukan kuasa saya lah cuma kat sini memang ada yang ada note yang mengatakan"
    },
    {
      "timestamp": 525.34,
      "text": " cik buat, cik memohon untuk Disconnect"
    },
    {
      "timestamp": 528.22,
      "text": " Bukan saya memohon, saya telefon untuk saya disconnect terus"
    },
    {
      "timestamp": 529.86,
      "text": " Nak mohon apa lagi, saya dah"
    },
    {
      "timestamp": 532.18,
      "text": " Setakan remaining balance dan saya"
    },
    {
      "timestamp": 533.58,
      "text": " Call untuk putuskan"
    },
    {
      "timestamp": 535.22,
      "text": " Tutup account"
    },
    {
      "timestamp": 538.5,
      "text": " Tak ada pun orang kecil tak buatkan call"
    },
    {
      "timestamp": 540.4,
      "text": " Tapi kat sini"
    },
    {
      "timestamp": 541.06,
      "text": " Saya dah lama dah saya"
    },
    {
      "timestamp": 544.2,
      "text": " Kat sini sepatutnya ada"
    },
    {
      "timestamp": 546.56,
      "text": " Agent yang kena call puan"
    },
    {
      "timestamp": 548.5,
      "text": " untuk apa dia nak call saya"
    },
    {
      "timestamp": 550.56,
      "text": " sebab tak itu saya tak tahu"
    },
    {
      "timestamp": 552.38,
      "text": " sebab memang kat sini dia ada agent yang"
    },
    {
      "timestamp": 554.54,
      "text": " tak je dia dia tak cakap"
    },
    {
      "timestamp": 555.82,
      "text": " dia nak call saya dia kata"
    },
    {
      "timestamp": 557.94,
      "text": " ok ada bahasa sebanyak ini kena tu"
    },
    {
      "timestamp": 560.34,
      "text": " saya memang saya dah rightly terus bank in"
    },
    {
      "timestamp": 561.9,
      "text": " remaining balance"
    },
    {
      "timestamp": 564.4,
      "text": " sebelum saya perlu tutup account"
    },
    {
      "timestamp": 565.64,
      "text": " lepas tu that's it"
    },
    {
      "timestamp": 567.92,
      "text": " saya tak nak bayar yang"
    },
    {
      "timestamp": 569.94,
      "text": " 400 lebih tu sebab saya tak guna dah, saya dah"
    },
    {
      "timestamp": 572.18,
      "text": " call, saya nak disconnect, nak tutup akaun"
    },
    {
      "timestamp": 573.92,
      "text": " ok puan"
    },
    {
      "timestamp": 575.8,
      "text": " ni tak ada cakap, macam mana"
    },
    {
      "timestamp": 577.92,
      "text": " saya tak nak bayar yang 400 tu sebab saya tak"
    },
    {
      "timestamp": 579.98,
      "text": " guna dan saya dah call untuk tutup akaun"
    },
    {
      "timestamp": 581.9,
      "text": " dan ada"
    },
    {
      "timestamp": 585.7,
      "text": " recorded perbualan sepatutnya, boleh rujuk Ok puan"
    },
    {
      "timestamp": 588.36,
      "text": " Ok puan boleh tunggu dalam panggilan"
    },
    {
      "timestamp": 590.04,
      "text": " Untuk saya buat semakan dengan saya punya"
    },
    {
      "timestamp": 592.22,
      "text": " Team manager lah"
    },
    {
      "timestamp": 594.18,
      "text": " Ok"
    },
    {
      "timestamp": 595.14,
      "text": " Saya tunggu"
    },
    {
      "timestamp": 597.16,
      "text": " Saya nak boleh dicata hari ni"
    },
    {
      "timestamp": 943.18,
      "text": " Ok © transcript Emily Beynon Thank you. © transcriptF-WATCH TV 2021 © transcriptF-WATCH TV 2021 © transcript Emily Beynon Thank you. Terima kasih dah buat semakan yang saya pun dah bincang dengan TM. Sepatutnya ada satu agent ni dia akan buat penutupan lah tapi kat sini dia memang tak buat penutupan. Jadi kita memang saya akan buat report berkenaan ni dan saya akan suruh agent yang call dengan puan waktu 19.01 tu untuk call puan balik untuk buat penutupan lah."
    },
    {
      "timestamp": 946.98,
      "text": " Baru sekarang nak buat penutupan lah baru sekarang nak buat penutupan"
    },
    {
      "timestamp": 950.04,
      "text": " sebab kat sini memang"
    },
    {
      "timestamp": 951.26,
      "text": " sepatutnya"
    },
    {
      "timestamp": 954.1,
      "text": " bil tu macam mana saya tak nak bayar"
    },
    {
      "timestamp": 955.92,
      "text": " saya dah cakap awal-awal saya nak tutup"
    },
    {
      "timestamp": 958.12,
      "text": " bil tu memang sepatutnya"
    },
    {
      "timestamp": 960.12,
      "text": " memang puan dah tak perlu bayar lah sebab"
    },
    {
      "timestamp": 961.86,
      "text": " sepatutnya puan kena tutup"
    },
    {
      "timestamp": 966.32,
      "text": " 19 ribu bulan sebab saya ke bill puan pun 22 ribu bulan jadi waktu"
    },
    {
      "timestamp": 968.06,
      "text": " puan dah bayar pada"
    },
    {
      "timestamp": 968.98,
      "text": " tarikh"
    },
    {
      "timestamp": 972.24,
      "text": " puan ada buat bayaran untuk settle kan waktu"
    },
    {
      "timestamp": 974.38,
      "text": " 18 ribu bulan 1 jadi waktu tu memang dah"
    },
    {
      "timestamp": 975.34,
      "text": " tak ada apa-apa"
    },
    {
      "timestamp": 978.54,
      "text": " outstanding jadi kat situ"
    },
    {
      "timestamp": 980.2,
      "text": " puan dah tak perlu bayar"
    },
    {
      "timestamp": 982.44,
      "text": " jadi memang kita akan buat report lah berkenaan ni"
    },
    {
      "timestamp": 984.74,
      "text": " dan dia akan buat penutupan"
    },
    {
      "timestamp": 985.02,
      "text": " lah sebab dia agent yang sebelum jadi memang kita akan buat report lah berkenaan ni ok dan dia akan buat penutupan lah"
    },
    {
      "timestamp": 989.88,
      "text": " sebab dia agent yang sebelum ni memang dia tak buat penutupan"
    },
    {
      "timestamp": 994,
      "text": " dia tak ada call pun untuk bagitahu bila untuk buat penutupan semua"
    },
    {
      "timestamp": 999.6,
      "text": " ok so saya kira dah settle eh saya tak perlu bayar eh yang saya tak guna tu"
    },
    {
      "timestamp": 1003.12,
      "text": " ok betul tapi sebelum tu boleh saya dapatkan nombor telefon pun"
    },
    {
      "timestamp": 1006.04,
      "text": " untuk saya bagi call agent untuk call puan balik?"
    },
    {
      "timestamp": 1024.72,
      "text": " Okey 011. 011. 3707. 3707. 8012. 8012. Okey saya ulang ya. 011. 3707. 8012. Betul."
    },
    {
      "timestamp": 1023.72,
      "text": " 3707 8012"
    },
    {
      "timestamp": 1024.8,
      "text": " Betul"
    },
    {
      "timestamp": 1027.66,
      "text": " Ok Puan saya akan buat report ni"
    },
    {
      "timestamp": 1029.82,
      "text": " Sekarang lah untuk dia return call"
    },
    {
      "timestamp": 1030.7,
      "text": " Kepada Puan semula"
    },
    {
      "timestamp": 1032.02,
      "text": " Ok"
    },
    {
      "timestamp": 1034.52,
      "text": " Ada apa-apa lagi boleh saya bantu Puan?"
    },
    {
      "timestamp": 1036.06,
      "text": " Itu sahaja"
    },
    {
      "timestamp": 1037.64,
      "text": " Ok terima kasih Puan"
    },
    {
      "timestamp": 1038.56,
      "text": " Ok"
    }
  ]
}

############################################ Connections END
# Base Function
def callAnalysis(body):
    print('Call Analysis', body)
    local_file_paths= getFilesToLocal(body)
    # process_with_whisper_api(local_file_paths)
    finalresponse = analysisProcess(local_file_paths)
    return finalresponse

def analysisProcess(local_file_paths):
    print('*************** Analysis process Started ***************')
    finalAnalysisResponse=[]
    for file_path in local_file_paths:
        # transcription = process_with_whisper_api(file_path)
        segments = dummytranscription['chunks']
        updatedSegments=[]
        # print('segments', segments)
        for index, segment in enumerate(segments):
            updatedSegments.append({'segment_id':index, 'text':segment['text'], 'timestamp':segment['timestamp']})
        analysisResponse = prompting_with_openai(updatedSegments)
        finalAnalysisResponse.append(analysisResponse)
        print('analysisResponse', analysisResponse)
    print('*************** Analysis process Ended ***************')
    return finalAnalysisResponse

#FROM S3 to local
def getFilesToLocal(body):
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

def download_from_s3(file_name):
    local_path = '/tmp/' + file_name
    print('S3_BUCKET', S3_BUCKET)
    s3.download_file(S3_BUCKET, file_name, local_path)
    return local_path

def process_with_whisper_api(file_path):
    print('*************** Processing local files with Whisper Transcription API ***************', file_path)
    audio_file= open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    print('Completed Transcription::', transcription.text)
    return transcription

def process_with_whisper_hugging_face_model(file_path):
    audio_file= open(file_path, "rb")
    result = pipe(audio_file)

def prompting_with_openai(transcription):
    prompt = get_prompt(transcription)
    print('************** Prompting with OPEN AI Turbo **************')
    print(prompt)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        model="gpt-3.5-turbo"
    )
    return response.choices[0].message.content


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
