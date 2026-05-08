import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Meu Treino Pro", layout="wide")

def conectar():
    # Puxa os dados dos Secrets (Formato TOML)
    info = st.secrets["gcp_service_account"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

st.title("🏋️‍♂️ Meu Treino Pro")

try:
    gc = conectar()
    sh = gc.open_by_key("1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE")
    aba = sh.get_worksheet(0)
    df = pd.DataFrame(aba.get_all_records())
    
    if not df.empty:
        st.success("Conectado!")
        st.dataframe(df)
except Exception as e:
    st.error(f"Erro: {e}")
