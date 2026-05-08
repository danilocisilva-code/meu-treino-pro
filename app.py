import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

# ID da sua planilha
ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"

def conectar():
    # Puxa os dados direto dos Secrets do Streamlit (Muito mais seguro e sem erro de assinatura!)
    info = st.secrets["gcp_service_account"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

# Estilo Dark
st.markdown("<style>[data-testid='stAppViewContainer']{background-color:#121212;color:#E0E0E0;} h1,h2,h3{color:#40E0D0;}</style>", unsafe_allow_html=True)

try:
    gc = conectar()
    sh = gc.open_by_key(ID_PLANILHA)
    aba = sh.get_worksheet(0)
    df = pd.DataFrame(aba.get_all_records())

    st.title("🏋️‍♂️ Dashboard de Treino")

    if not df.empty:
        treinos = df['Treino'].unique()
        sel_t = st.selectbox("Selecione o Treino:", treinos)
        
        df_t = df[df['Treino'] == sel_t].reset_index(drop=True)
        sel_ex = st.selectbox("Exercício:", df_t['Exercício'].tolist())
        
        det = df_t[df_t['Exercício'] == sel_ex].iloc[0]
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Método:** {det.get('Método', '---')}")
            st.write(f"**Séries:** {det.get('Séries', '---')}")
        with col2:
            st.warning(f"**Descanso:** {det.get('Descanso', '---')}")
            st.write(f"**Repetições:** {det.get('Repetições', '---')}")

        if 'Foto' in det and pd.notna(det['Foto']):
            st.image(det['Foto'], use_container_width=True)

        st.divider()
        carga = st.number_input("Peso (kg):", min_value=0, step=1)
        if st.button("💾 SALVAR SÉRIE"):
            try:
                aba_h = sh.worksheet("Historico")
                aba_h.append_row([pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), sel_t, sel_ex, carga])
                st.success("Salvo com sucesso!")
                st.balloons()
            except:
                st.error("Crie a aba 'Historico' na planilha!")
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
