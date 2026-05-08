import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

# 1. DADOS DO ROBÔ (Configure aqui)
DADOS_ROBO = {
    "type": "service_account",
    "project_id": "modified-return-471321-k6",
    "private_key_id": "03d62135b9a55e0f0bfe6dbd5dfdef88c718e075",
    "private_key": "COLE_AQUI_O_TEXTO_GIGANTE_QUE_COMECA_COM_BEGIN_PRIVATE_KEY", # <--- COLE AQUI!
    "client_email": "treino-bot@modified-return-471321-k6.iam.gserviceaccount.com",
    "client_id": "112000857757706046520",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/web/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/treino-bot%40modified-return-471321-k6.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Fazemos uma cópia para não mexer nos dados originais
    info = DADOS_ROBO.copy()
    # Conserta as quebras de linha da chave privada
    info["private_key"] = info["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

# Estilo Visual Dark
st.markdown("<style>[data-testid='stAppViewContainer']{background-color:#121212;color:#E0E0E0;} h1,h2,h3{color:#40E0D0;}</style>", unsafe_allow_html=True)

try:
    gc = conectar_google()
    sh = gc.open_by_key(ID_PLANILHA)
    aba = sh.get_worksheet(0)
    df = pd.DataFrame(aba.get_all_records())

    st.title("🏋️‍♂️ Dashboard de Treino")

    if not df.empty:
        # Filtro de Treino (A, B, C...)
        lista_treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Selecione o Treino:", lista_treinos)
        
        # Filtro de Exercícios
        df_treino = df[df['Treino'] == treino_sel].reset_index(drop=True)
        ex_sel = st.selectbox("Exercício:", df_treino['Exercício'].tolist())
        
        det = df_treino[df_treino['Exercício'] == ex_sel].iloc[0]
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**Método:** {det.get('Método', 'N/A')}")
            st.write(f"**Séries:** {det.get('Séries', 'N/A')}")
        with c2:
            st.warning(f"**Descanso:** {det.get('Descanso', 'N/A')}")
            st.write(f"**Repetições:** {det.get('Repetições', 'N/A')}")

        if 'Foto' in det and pd.notna(det['Foto']) and str(det['Foto']).startswith('http'):
            st.image(det['Foto'], use_container_width=True)

        # Registro de Carga
        st.divider()
        carga = st.number_input("Carga (kg):", min_value=0, step=1)
        if st.button("💾 SALVAR SÉRIE"):
            try:
                aba_h = sh.worksheet("Historico")
                aba_h.append_row([pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), treino_sel, ex_sel, carga])
                st.success("Salvo com sucesso!")
                st.balloons()
            except:
                st.error("Crie a aba 'Historico' na planilha para salvar!")
except Exception as e:
    st.error(f"Erro Crítico de Conexão: {e}")
