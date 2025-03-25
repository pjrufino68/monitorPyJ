import streamlit as st
import speech_recognition as sr
import openai
import keyboard
import os
import psutil
import pyaudio
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

hide_st_style = """
            <style>
            #bui1 > div > div > ul >ul:nth-child(1) {visibility: hidden;}
            #bui1 > div > div > ul >ul:nth-child(2) {visibility: hidden;}
            #bui1 > div > div > ul >ul:nth-child(4) {visibility: hidden;}
            #bui1 > div > div > ul >ul:nth-child(5) {visibility: hidden;}
            #bui1 > div > div > ul >ul:nth-child(7) {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .reportview-container .main footer {visibility: hidden;}
            </style>
            """
st.set_page_config(page_title="hacBot responde!!!")
st.markdown(hide_st_style, unsafe_allow_html=True)

st.write("# Dicas Hospedagem & Turismo")

client = OpenAI(api_key=os.getenv("chaveApi"))

# Instrucoes iniciais para o Bot
assistant_instructions = {
    "role": "system",
    "content": os.getenv("contentBot")
}

lista = []
lista.insert(0, assistant_instructions)

st.session_state["messages"] = lista

@st.cache_data

def enviarIA(textoRecebido, _lista):
    lista.append({"role": "user", "content": texto})
    response = client.chat.completions.create(model="gpt-4o-mini", messages=lista)
    lista.append(response)
    return response.choices[0].message.content

def reconhecer_voz():
    # Inicializa o reconhecedor de voz
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Por favor, fale agora...")
        audio = r.listen(source)
    
    try:
        # Converte áudio em texto
        texto = r.recognize_google(audio, language="pt-BR")
        st.write(f"Você : {texto}")
        return texto
    except sr.UnknownValueError:
        st.write("Não entendi o áudio.")
        return ""
    except sr.RequestError:
        st.write("Erro na solicitação ao serviço de reconhecimento de voz.")
        return ""
    
with st.container():
    i = 0
    texto = ""
    texto_voz = ""

    while True:
        forma = st.radio("", ["Escrever", "Falar :studio_microphone:"], 
            horizontal=True, key=f'{i}'
        )

        if forma == "Escrever":
            texto = st.text_input("", placeholder="Faça sua pergunta", key=f'texto_{i}')
        else:
            texto_voz = reconhecer_voz()
            texto = texto_voz

        if texto == "fim" or len(texto) < 1:
            break
        else:
            msg = enviarIA(texto, lista)
            st.chat_message("assistant").write(msg)
        i = i + 1
        

