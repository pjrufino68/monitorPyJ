import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import pydeck as pdk

import os
import psutil
from dotenv import load_dotenv

load_dotenv(override=True)

# Configuração da página
st.set_page_config(page_title="🚍 monitorPyJ", layout="wide")
st.title("📡 monitorPyJ / Monitoramento de Veículos")

# --- 1. Requisição de autenticação ---
AUTH_URL = "https://consultaviagem.m2mfrota.com.br/AutenticarUsuario"
API_URL = "https://zn4.sinopticoplus.com/servico-dados/api/v1/obterPosicaoVeiculo"

CREDENCIAIS = {
    "usuario": os.getenv("userUsuario"),
    "senha": os.getenv("passwordSenha")
}

# Tenta autenticar e obter o token
@st.cache_data(ttl=1800)  # Cache por 30 minutos
def autenticar_e_obter_token():
    response = requests.post(AUTH_URL, json=CREDENCIAIS)
    if response.status_code == 200:
        data = response.json()
        token = data.get("IdentificacaoLogin") or data.get("Authorization") or data.get("authToken")
        if token:
            return token
        else:
            raise Exception("⚠️ Token não encontrado na resposta da autenticação.")
    else:
        raise Exception(f"Erro na autenticação: {response.status_code} - {response.text}")

# Autenticar
try:
    token = autenticar_e_obter_token()
except Exception as e:
    st.error(str(e))
    st.stop()

headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

# Espaços para atualizar
placeholder_tabela = st.empty()
placeholder_mapa = st.empty()

while True:
    try:
        response = requests.get(API_URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            
            if data:
            #if isinstance(data, list) and data:
                # Extrair e filtrar veículos válidos
                veiculos = data.get("veiculos", [])

                # Filtrar apenas os veículos que não são None
                veiculos_validos = [v for v in veiculos if v is not None]

                df = pd.DataFrame(veiculos_validos)
                df = df.drop(['id_migracao_trajeto', 'sentido', 'hodometro', 'direcao'], axis=1)
                
                # Converte timestamp para data legível (opcional)
                if 'dataHora' in df.columns:
                    df['dataHora'] = pd.to_datetime(df['dataHora'], unit='ms')

                #print (data)
                # Exibe o DataFrame no Streamlit
                with placeholder_tabela.container():
                    st.dataframe(df, use_container_width=True)

            else:
                placeholder_tabela.warning("⚠️ Nenhum dado retornado.")
                placeholder_mapa.empty()

        else:
            placeholder_tabela.error(f"Erro {response.status_code}: {response.text}")
            placeholder_mapa.empty()

    except Exception as e:
        placeholder_tabela.error(f"Erro na requisição: {e}")
        placeholder_mapa.empty()

    time.sleep(5)
