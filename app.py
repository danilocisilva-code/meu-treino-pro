import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Meu Treino Pro", layout="wide")

def conectar():
    # Puxa os dados que você salvou nos Secrets do Streamlit
    info = dict(st.secrets["gcp_service_account"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

try:
    gc = conectar()
    sh = gc.open_by_key("1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE")
    aba = sh.get_worksheet(0)
    df = pd.DataFrame(aba.get_all_records())

    st.title("🏋️‍♂️ Dashboard de Treino")
    
    if not df.empty:
        treinos = df['Treino'].unique()
        sel_t = st.selectbox("Selecione o Treino:", treinos)
        df_t = df[df['Treino'] == sel_t].reset_index(drop=True)
        sel_ex = st.selectbox("Exercício:", df_t['Exercício'].tolist())
        det = df_t[df_t['Exercício'] == sel_ex].iloc[0]
        
        st.write(f"**Séries:** {det.get('Séries', '---')} | **Repetições:** {det.get('Repetições', '---')}")
        if 'Foto' in det and pd.notna(det['Foto']):
            st.image(det['Foto'], use_container_width=True)
            
except Exception as e:
    st.error(f"Erro: {e}")
