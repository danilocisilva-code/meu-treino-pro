import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def conectar():
    try:
        # Puxa os dados e limpa a private_key para evitar erros de formatação
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

st.title("🏋️‍♂️ Meu Treino Pro")

gc = conectar()
if gc:
    try:
        sh = gc.open_by_key("1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE")
        aba = sh.get_worksheet(0)
        df = pd.DataFrame(aba.get_all_records())
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erro ao abrir planilha: {e}")
