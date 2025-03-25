import streamlit as st
import speech_recognition as sr

# Função para capturar áudio e transcrever
def transcrever_audio():
    # Cria um reconhecedor de fala
    recognizer = sr.Recognizer()

    # Usa o microfone como fonte de áudio
    with sr.Microphone() as source:
        st.info("Aguardando você falar...")
        # Ajusta para o ruído ambiente
        recognizer.adjust_for_ambient_noise(source)
        
        # Captura o áudio
        audio = recognizer.listen(source)
        
        try:
            # Transcreve o áudio usando a API do Google
            texto = recognizer.recognize_google(audio, language='pt-BR')
            return texto
        except sr.UnknownValueError:
            return "Não consegui entender o áudio."
        except sr.RequestError:
            return "Erro ao tentar conectar ao serviço de reconhecimento de fala."

# Título da aplicação Streamlit
st.title("Conversão de Áudio em Texto")

# Botão para iniciar a captura de áudio
if st.button("Clique para falar"):
    texto_transcrito = transcrever_audio()
    st.write(f"Texto transcrito: {texto_transcrito}")
