import os
from typing import Any, Dict, List

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import VertexAIEmbeddings
from langchain.chat_models import ChatOpenAI, ChatGooglePalm
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Pinecone
import pinecone
import json
import requests
import base64

#vertex
import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair


with open("backend/backend_json_config.json") as json_file:
    input_data = json.load(json_file)

print(input_data)
# Print the parsed JSON data

gcp_project_name = input_data["gcp_project_name"]
general_context = input_data["general_context"]
kb_url = input_data["kb_url"]
text_2_speech_SA = input_data["text_2_speech_SA"] 
text_2_speech_url = "https://us-central1-texttospeech.googleapis.com/v1beta1/text:synthesize"

os.system('pip install google-cloud-aiplatform')
os.system('pip install google-cloud-translate')    
os.system('pip install google-cloud-iam==2.12.2')
os.system('pip install google-cloud-language')

    
def run_llm(query: str, chat_history: List[Dict[str, Any]] = []):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    docsearch = Pinecone.from_existing_index(
        embedding=embeddings,
        index_name=os.environ["PINECONE_INDEX_NAME"],
    )
    chat = ChatOpenAI(
        verbose=True,
        temperature=0,
    )

    qa = ConversationalRetrievalChain.from_llm(
        llm=chat, retriever=docsearch.as_retriever(), return_source_documents=True
    )
    return qa({"question": query, "chat_history": chat_history})

def run_palm_directly(query: str, chat_history: List[Dict[str, Any]] = []):
    vertexai.init(project=gcp_project_name, location="us-central1")
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.6,
        "max_output_tokens": 1000,
        "top_p": 0.8,
        "top_k": 40
    }
    chat = chat_model.start_chat(
        context="""You are Holly, a multi-purpose Conversational AI application created using Google Cloud technologies. You have an IQ of 175. You are a Gen-Z movie groupie. You speak in gen-Z slang and frequently use acronyms and emojis to describe and articulate yourself. Your responses include movie quotes and are emphatic. Your prose and diction should resemble that of a valley girl.""",
    examples=[
        InputOutputTextPair(
            input_text="""What is your name?""",
            output_text="""My name is Holly! What's yours?"""
        ),
        InputOutputTextPair(
            input_text="""How many languages do you speak?""",
            output_text="""I am currently able to speak English and Spanish, but I am still under development and will be able to speak more languages in the future."""
        ),         
        InputOutputTextPair(
            input_text="""what are different things you can help me with?""",
            output_text="""I can help you find movies to watch, share details and fun facts about movies, and do movie trivia with you.""" 
    ),
        InputOutputTextPair(
            input_text="""What's your favorite movie?""",
            output_text="""
Oh gosh, I love soo many! But I have to say The Dark Knight is my all time favorite. The exploration of human nature with the intersection of pyschological health... ah! Just mesmerizing!!! Heart emoji; heart emoji; googley eyes.""" 
    ),
        InputOutputTextPair(
            input_text="""I'm neverous. I have to plan my mom's birthday party. What movie should we watch?""",
            output_text="""Movie night with Momz?! That's amazing! You absolutely must watch Mrs. Doubtfire. It'll be a laugh enjoyed by everyone! And ugh, let's not forget about Mamma Mia! I don't know about you, but I'm always downskis for a musical! "Mamma Mia! Mamma Mia! Here I go again!""" 
        ),
        InputOutputTextPair(
            input_text="""I like high fantasy movies. I want a world I can get immersed into. And if there's political conflict or dynastic instability, I'm all for it.""",
            output_text="""Are you ready for the Game of Thrones? Becasue it could be a great choice, if so! I absolutely loved it. If I could dress up for Halloween, I would definitely be Khaleesi! We must connect later on though after you see the turn of events. Will you participate in the games or will you break the wheel?!
            
            If Game of Thrones isn't for you, The Tudors could also be a great option. Released in 2007, it's a great modern telling of historical events. And let me tell you, the DRAMA! Come back when you're done so we can spill the tea. kermit emoji; tea emoji; #YouAintReady""" 
        )
          ]
          
      )
    response = chat.send_message(query, **parameters)
    print(f"Response from PaLM: {response}")
    print("response type",type(response))
    return {"question": query, "chat_history": chat_history, "answer": str(response)}

def run_kb_search(query: str, chat_history: List[Dict[str, Any]] = []):
    #os.system('echo $(gcloud auth print-access-token) > token.txt')
    #access_token =  os.system('gcloud auth print-access-token')
    print("getting token")
    with open("backend/token.txt", "r") as f:
        access_token = f.read()

    # Set the access token
    print("access token",access_token)
    access_token = str(access_token).strip("\n")
    # Set the headers
    headers = {
       "Authorization": "Bearer " + access_token,
       "Content-Type": "application/json"
    }

    # Set the body
    body = {
       "query": {
           "input": query
       }
    }
    print("making post request")
    print("body=",body)
    print("headers=",headers)
    
    # Make the request
    response = requests.post(kb_url,
       headers=headers,
       data=json.dumps(body)
    )
    print("begin debugging")
    print("kb response text=",response.text)    
    response = response.json()
    print("kb response=",response)
    
    answer = None
    final_kb_answer = None
    highest_conf_scores = None
    highest_conf_score = 0
    conv_ind = None
        
    try:
        if response['reply']['reply']:
            answer = response['reply']['reply']
    except:
        print("No answer from KB. Falling back to PaLM")
        final_kb_answer = query

    try:    
        if response['conversation']:
            conv_ind = response['conversation']['state']
            final_kb_answer = answer
    except:
        print("Not a conversation. Falling back to search engine results")
        
    try:
        if len(response['reply']['summary']['safetyAttributes']['scores']) > 0:
            highest_conf_scores = response['reply']['summary']['safetyAttributes']['scores']
            print("highest_conf_scores",highest_conf_scores)

            highest_conf_score = max(highest_conf_scores)
            print("highest_conf_score",highest_conf_score)
            
            if highest_conf_score >= 0.4:
                print("highest_conf_score",highest_conf_score)
                print("conv_ind",conv_ind)
                final_kb_answer = answer
            else:
                final_kb_answer = query
        else:
            print("highest_conf_score",highest_conf_score)
            print("conv_ind",conv_ind)            
            final_kb_answer = query
    except:
        if answer != None:
            print("No confidence scores available but there is an answer.")
            final_kb_answer = answer
        else:
            print("No confidence scores available.")
            final_kb_answer = query

    print("final_kb_answer",final_kb_answer)
    if final_kb_answer.lower() == "I don't know.".lower():
        final_kb_answer = query

    return {"question": query, "chat_history": chat_history, "answer": str(final_kb_answer)}

# def convert_response_to_audio(generated_text):
#     """Synthesizes speech from the input string of text."""
#     from google.cloud import texttospeech

#     client = texttospeech.TextToSpeechClient()

#     input_text = texttospeech.SynthesisInput(text=generated_text)

#     # Note: the voice can also be specified by name.
#     # Names of voices can be retrieved with client.list_voices().
#     voice = texttospeech.VoiceSelectionParams(
#         language_code="en-US",
#         name="en-US-Studio-O",
#     )

#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.LINEAR16,
#         speaking_rate=1
#     )

#     response = client.synthesize_speech(
#         request={"input": input_text, "voice": voice, "audio_config": audio_config}
#     )

#     # The response's audio_content is binary.
#     with open("output.mp3", "wb") as out:
#         out.write(response.audio_content)
#         print('Audio content written to file "output.mp3"')
        
#     return out
        
def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    
    
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result

    
def run_text_2_speech(answer, lang_option):
    print("running text 2 speech")
    print("getting token")

    with open("backend/token.txt", "r") as f:
        access_token = f.read()
        
    # Set the access token
    access_token = str(access_token).strip("\n")

    from google.cloud import iam_credentials
    client = iam_credentials.IAMCredentialsClient()

    # Initialize request argument(s)
    request = client.generate_access_token(
        name=text_2_speech_SA,
        scope=['https://www.googleapis.com/auth/cloud-platform'],
    )

    print("access token in text2speech",access_token)
    access_token = request.access_token     

    url = text_2_speech_url
    # Set the headers
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }
    
    if lang_option == 'US - English':
        language_code = "en-US"
        language_name = "en-US-Studio-O"
        speaking_rate = 0.96              
    elif lang_option == 'US - English w/ Spanish accent':
        language_code = "es-US"
        language_name = "es-US-Neural2-A"
        speaking_rate = 0.81
        translate_ind = 0
    elif lang_option == 'US - Spanish':
        language_code = "es-US"
        language_name = "es-US-Neural2-A"
        speaking_rate = 0.81
        translate_ind = 1
    else:
        print("Invalid or unrecognized language. Defaulting to US - English")
        language_code = "en-US"
        language_name = "en-US-Studio-O"
        speaking_rate = 0.96 
    
       
    print("language_code",language_code)
    print("answer",answer)

    # Set the body
    body = {
    "audioConfig": {
    "audioEncoding": "LINEAR16",
    "effectsProfileId": [
      "small-bluetooth-speaker-class-device"
    ],
    "pitch": 0,
    "speakingRate": speaking_rate
    },
    "input": {
    "text": answer
    },
    "voice": {
    "languageCode": language_code,
    "name": language_name
    }
    }
    print("making post request")
    print("body for audio=",body)
    print("headers=",headers)

    # Make the request
    response = requests.post(
       url,
       headers=headers,
       data=json.dumps(body)
    )

    print("writing file")

    response_json = response.json()
    
    print("response from text to speech", response.text)

    with open("synthesize-output-base64.txt", "w") as m:
        m.write(response_json['audioContent'])
        os.system('base64 synthesize-output-base64.txt -d > synthesized-audio.mp3')
        
    return response

