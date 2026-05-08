import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def conectar():
    # Puxa os dados dos Secrets
    info = dict(st.secrets["gcp_service_account"])
    
    # --- ESTA LINHA É A CHAVE PARA O SUCESSO ---
    # Ela garante que o texto \n seja lido como uma quebra de linha real
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

st.title("🏋️‍♂️ Dashboard de Treino")

try:
    gc = conectar()
    sh = gc.open_by_key("1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE")
    aba = sh.get_worksheet(0)
    df = pd.DataFrame(aba.get_all_records())
    
    if not df.empty:
        st.success("Conectado com Sucesso!")
        st.dataframe(df)
    else:
        st.warning("Planilha vazia!")
        
except Exception as e:
    st.error(f"Erro Crítico: {e}")
