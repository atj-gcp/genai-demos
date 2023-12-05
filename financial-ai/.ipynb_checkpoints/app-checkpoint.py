import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit.components.v1 import html
from backend.backend import run_palm_directly
from backend.backend import run_kb_search
from backend.backend import run_text_2_speech
from backend.backend import translate_text


import os
import json
import base64

with open("app_json_config.json") as json_file:
    input_data = json.load(json_file)

print(input_data)

task_specific_context = input_data["task_specific_context"]
customer_name = input_data["customer_name"]
bot_name = input_data["bot_name"]
task_to_perform = input_data["task_to_perform"]
logo_url = input_data["logo_url"]
about_blurb = str(input_data["about_blurb"])
how_to_use = str(input_data["how_to_use"])
enable_search = input_data["enable_search"]
enable_t2s = input_data["enable_t2s"]

def get_text(instruction: str = "You: "):
    input_text = st.text_input(instruction, "", key="user-prompt")
    return input_text

def clear_text(instruction: str = "You: "):
    #st.session_state["temp-user-prompt"] = st.session_state["user-prompt"]
    st.session_state["user-prompt"] = task_specific_context

def add_horizontal_space(num_cols):
    """Add vertical space to your Streamlit app."""
    for _ in range(num_cols):
        st.write(" " * num_cols)

st.set_page_config(page_title=f"{customer_name}'s {bot_name}", layout="wide")
with st.sidebar:
    st.markdown(
            f"""
            ![Sphere]({logo_url})
            """
    )
    st.title(f"🔮 💬 {bot_name}: Financial Analysis, Reimagined")
    
    lang_option = st.selectbox(
        'Preferred Language:',
        ('US - English', 'US - English w/ Spanish accent', 'US - Spanish'))
    st.write('You selected:', lang_option)
    
    st.markdown(
        f"""
    ## About
    This **{bot_name}** module is an LLM-powered conversational AI, which serves as a {task_to_perform}. {about_blurb}
    
    *Instructions:* {how_to_use}

    This **{bot_name}** module was created using:
    - [Google's PaLM2 LLM Model](https://ai.google/discover/palm2)
    - [Google's Vertex Search & Conversation](https://cloud.google.com/blog/products/ai-machine-learning/vertex-ai-search-and-conversation-is-now-generally-available)
    - [Vertex Matching Engine](https://cloud.google.com/vertex-ai/docs/matching-engine/overview)
    - [Streamlit](https://streamlit.io/)


    """
    )
    add_vertical_space(5)
    # api_key_container = st.container()
    # with api_key_container:
    #     palm_api_key = get_text(instruction="PALM2_API_KEY")
    #     if palm_api_key:
    #         os.environ["PALM_2_API_KEY"]

    st.write("Made by [Adrian Jones](https://www.linkedin.com/in/adrian-t-jones/)")

if "generated" not in st.session_state:
    st.session_state["generated"] = [f"Greetings! How may I help you?"]
if "past" not in st.session_state:
    st.session_state["past"] = ["Hi!"]
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "temp-user-prompt" not in st.session_state:
    st.session_state["temp-user-prompt"] = ""

input_container = st.container()
colored_header(label="", description="", color_name="blue-30")
response_container = st.container()
speech_container = st.container()


with input_container:
    user_input = get_text(instruction="You: ")
    #submit_button = st.button("Clear Prompt", on_click=clear_text)
## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input:
        with st.spinner("Generating response..."):
            if enable_t2s == True:
                kb_response = run_kb_search(
                    query=user_input, chat_history=st.session_state["chat_history"]
                )
            
                kb_answer = kb_response['answer']
                print("kb_answer",kb_answer)
                if (kb_answer.lower() == "I'm sorry, I don't have access to that information") or (kb_answer.lower() == user_input.lower())\
                 or (kb_answer.lower() == "I'm sorry, I don't have access to that information at the moment. Would you like me to help you find something else?".lower()) \
                 or (kb_answer.lower() == "There is not enough information to answer the query.".lower()) \
                 or (kb_answer.lower() == "I don't know.".lower()):
                    #prompted_user_input=f"""Make a high level assumption and try to answer the following question: {query}.""" 
                    prompted_user_input=user_input 
                    print("prompted_user_input",prompted_user_input)

                else:
                    prompted_user_input = f"""You are a conversational summarizer and elaborater. You take messages from a knowledge base and summarize them. 

                    Do not change the core meaning or accuracy of the message.

                    Rewrite the following text to make it more conversational: {kb_answer}. 
            """
                    print("prompted_user_input",prompted_user_input)

                print("prompted_user_input before palm directly",prompted_user_input)
            else:
                prompted_user_input=user_input 

            response = run_palm_directly(
                query=prompted_user_input, chat_history=st.session_state["chat_history"]
            )
            
            print("response from palm", response)
            print("response from kb", kb_answer)
            answer = response["answer"]
            
            print("lang_option",lang_option)
            # translate spanish
            if lang_option == "US - Spanish":
                translated_text = translate_text("es", answer)
                answer = translated_text['translatedText']
                print("translated answer=",answer)
            else:
                answer = answer 
            
            st.session_state.past.append(user_input)
            st.session_state.generated.append(answer)
            print("response answer from app.py",answer)
            st.session_state["chat_history"].append((user_input, answer))
            if enable_t2s == True:
                print("Generating audio file")           
                audio_stream = run_text_2_speech(answer, lang_option)

                audio_file = open('synthesized-audio.mp3', 'rb')
                audio_bytes = audio_file.read()
                #st.audio(audio_bytes, format=‘audio/ogg’)

                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
                st.markdown(audio_tag, unsafe_allow_html=True)
    if st.session_state["generated"]:
        print(4)
        for i in reversed(range(len(st.session_state["generated"]))):
            print("past=", type(st.session_state["past"][i]))
            print("generated=", type(st.session_state["generated"][i]))
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
            #message(st.session_state["generated"][i], key=str(i))


# with response_container:
#     my_html = """<!-- Gen App Builder widget bundle -->
#     <script src="https://cloud.google.com/ai/gen-app-builder/client"></script>

#     <!-- Search widget element is not visible by default -->
#     <gen-search-widget
#     configId="4fa295dd-aa39-44b8-ad7c-51d52f053806"
#     triggerId="searchWidgetTrigger">
#     </gen-search-widget>

#     <!-- Element that opens the widget on click. It does not have to be an input -->
#     <input placeholder="Search here" id="searchWidgetTrigger" />"""

#     #st.markdown(my_html, unsafe_allow_html=True)

#     html(my_html)


