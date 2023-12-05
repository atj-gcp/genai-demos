import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit.components.v1 import html
from backend.backend import run_llm, run_g_llm, run_palm_directly
import os


def get_text(instruction: str = "You: "):
    input_text = st.text_input(instruction, "", key="user-prompt")
    return input_text

def clear_text(instruction: str = "You: "):
    #st.session_state["temp-user-prompt"] = st.session_state["user-prompt"]
    st.session_state["user-prompt"] = "You are Jarvis, a PaLM2 powered Conversational AI chatbot. You are able to remember all of the previous turns in our conversation and to use that information to inform your future responses."

def add_horizontal_space(num_cols):
    """Add vertical space to your Streamlit app."""
    for _ in range(num_cols):
        st.write(" " * num_cols)

st.set_page_config(page_title="NHL's Gretzky Bot", layout="wide")
with st.sidebar:
    st.markdown(
            """
            ![NHL](https://www-league.nhlstatic.com/images/logos/league-dark/133-flat.svg)
            """
    )
    st.title("🔮 💬 Gretzky Bot: Hockey, Reimagined")
    st.markdown(
        """
    ## About
    Jarvis is an LLM-powered chatbot that serves as hockey expert. Interact with Jarvis to get details on hockey games, merchandise, trivia, and more. 
    
    Use Jarvis to engage with all of the content apart of the NHL archive. Learn more about your favorite games, behind the scenes moments, and more.

    Cine-bot was created using:
    - [PaLM2 LLM Model](https://ai.google/discover/palm2)
    - [LangChain 🦜🔗](https://python.langchain.com/en/latest/index.html)
    - [Pinecone 🌲 Vectorestore](https://www.pinecone.io/)
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
    st.session_state["generated"] = ["I'm Jarvis, How may I help you?"]
if "past" not in st.session_state:
    st.session_state["past"] = ["Hi!"]
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "temp-user-prompt" not in st.session_state:
    st.session_state["temp-user-prompt"] = ""

colored_header(label="", description="", color_name="blue-30")

response_container = st.container()
with response_container::1
    my_html = """<!-- Gen App Builder widget bundle -->
<script src="https://cloud.google.com/ai/gen-app-builder/client"></script>

<!-- Search widget element is not visible by default -->
<gen-search-widget
  configId="4fa295dd-aa39-44b8-ad7c-51d52f053806"
  triggerId="searchWidgetTrigger">
</gen-search-widget>

<!-- Element that opens the widget on click. It does not have to be an input -->
<input placeholder="Search here" id="searchWidgetTrigger" />"""
    
    #st.markdown(my_html, unsafe_allow_html=True)

    html(my_html)


