import streamlit as st
import requests
import numpy as np
import pandas as pd
import time
from datetime import datetime
#import pydeck as pdk
#from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

import os
import psutil
from dotenv import load_dotenv

load_dotenv(override=True)

# Configuração da página
st.set_page_config(page_title="🚍 monitorPyJ", layout="wide")
st.title("📡 monitorPyJ / Monitoramento de Veículos")

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
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

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

placeholder_tabela = st.empty()
placeholder_mapa = st.empty()

i = 0
while True:
    try:
        response = requests.get(API_URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            
            if data:
                veiculos = data.get("veiculos", [])

                # Filtrar apenas os veículos que não são None
                veiculos_validos = [v for v in veiculos if v is not None]

                df = pd.DataFrame(veiculos_validos)
                df = df.drop(['id_migracao_trajeto', 'hodometro', 'direcao', 'trajeto'], axis=1)
                df = df.sort_values("codigo")
                
                df["local"] = df.apply(
                    lambda row: f"[Mapa](https://www.google.com/maps?q={row['latitude']},{row['longitude']})",
                    axis=1
                )
                
                if 'dataHora' in df.columns:
                    df['dataHora'] = pd.to_datetime(df['dataHora'], unit='ms', utc=True)
                    df['dataHora'] = df['dataHora'].dt.tz_convert('America/Sao_Paulo')
                    df['dataHora'] = df['dataHora'].dt.strftime('%Y-%m-%d %H:%M')
                
                df["sentido"] = np.where((df['latitude'] >= -3.807708) & (df['latitude'] <= -3.805093) & (df['longitude'] >= -38.469888) & (df['longitude'] <= -38.468058), "dentro", "fora")
                
                df['ignicao'] = df['ignicao'].map({1: 'ligada', 0: 'desligada'})

                dentro = (df['sentido'] == 'dentro').sum()
                fora = (df['sentido'] == 'fora').sum()
                df.index = df.index + 1

                df_view = df.drop(columns=["latitude", "longitude"]).rename(columns={"sentido": "garagem"})
                with placeholder_tabela.container():
                    st.write(df_view.to_markdown(index=False), unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label = "Dentro:", value = dentro)
                    with col2:
                        st.metric(label = "Fora:", value = fora)
                    with col3:
                        st.metric(label = "Total:", value = dentro + fora)

            else:
                placeholder_tabela.warning("⚠️ Nenhum dado retornado.")
                placeholder_mapa.empty()

        else:
            placeholder_tabela.error(f"Erro {response.status_code}: {response.text}")
            placeholder_mapa.empty()

    except Exception as e:
        placeholder_tabela.error(f"Erro na requisição: {e}")
        placeholder_mapa.empty()

    time.sleep(20)
    
    
