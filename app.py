import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Meu Treino Pro", layout="wide")

# ID da sua planilha (final MZXlE)
ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"

def conectar():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Garanta que o nome do arquivo no GitHub é exatamente credentials.json
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    return gspread.authorize(creds)

try:
    client = conectar()
    sh = client.open_by_key(ID_PLANILHA)
    aba = sh.get_worksheet(0)
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)

    st.title("🏋️‍♂️ Meu Treino Pro")

    if not df.empty:
        treinos = df['Treino'].unique()
        sel_treino = st.selectbox("Treino:", treinos)
        
        exercicios = df[df['Treino'] == sel_treino]
        sel_ex = st.selectbox("Exercício:", exercicios['Exercício'].tolist())
        
        detalhe = exercicios[exercicios['Exercício'] == sel_ex].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Método", detalhe.get('Método', 'N/A'))
            st.write(f"Séries: {detalhe.get('Séries', 'N/A')}")
        with col2:
            st.write(f"Repetições: {detalhe.get('Repetições', 'N/A')}")
            st.write(f"Descanso: {detalhe.get('Descanso', 'N/A')}")

        if 'Foto' in detalhe and detalhe['Foto']:
            st.image(detalhe['Foto'])
            
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
