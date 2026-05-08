import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Lendo o arquivo que você colou no GitHub
    with open("credentials.json", "r") as f:
        info = json.load(f)
    
    # --- O CONSERTO MÁGICO ---
    # Isto transforma o texto "\n" em quebras de linha reais que o Google exige
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

# Estilo visual Dark
st.markdown("<style>[data-testid='stAppViewContainer']{background-color:#121212;color:#E0E0E0;}.stButton>button{border-radius:20px;background-color:#1F1F1F;color:#40E0D0;border:1px solid #40E0D0;width:100%;font-weight:bold;}h1,h2,h3{color:#40E0D0;}</style>", unsafe_allow_html=True)

try:
    gc = conectar_google()
    sh = gc.open_by_key(ID_PLANILHA)
    
    # Lendo a primeira aba
    aba_dados = sh.get_worksheet(0)
    df = pd.DataFrame(aba_dados.get_all_records())

    st.title("🏋️‍♂️ Dashboard de Treino")

    if not df.empty:
        # Seleção de Treino
        treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Escolha o Treino:", treinos)
        
        # Filtro de Exercícios
        df_treino = df[df['Treino'] == treino_sel].reset_index(drop=True)
        ex_sel = st.selectbox("Exercício:", df_treino['Exercício'].tolist())
        
        detalhes = df_treino[df_treino['Exercício'] == ex_sel].iloc[0]
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Método:** {detalhes.get('Método', 'N/A')}")
            st.write(f"**Séries:** {detalhes.get('Séries', 'N/A')}")
        with col2:
            st.warning(f"**Descanso:** {detalhes.get('Descanso', 'N/A')}")
            st.write(f"**Repetições:** {detalhes.get('Repetições', 'N/A')}")

        if 'Foto' in detalhes and pd.notna(detalhes['Foto']):
            st.image(detalhes['Foto'], use_container_width=True)

        # Registro de Peso
        st.divider()
        carga = st.number_input("Peso usado (kg):", min_value=0, step=1)
        if st.button("💾 SALVAR SÉRIE"):
            try:
                aba_hist = sh.worksheet("Historico")
                nova_linha = [pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), treino_sel, ex_sel, carga]
                aba_hist.append_row(nova_linha)
                st.success("Progresso salvo com sucesso!")
                st.balloons()
            except:
                st.error("Erro: Crie uma aba chamada 'Historico' na sua planilha.")

except Exception as e:
    st.error(f"Erro de Conexão: {e}")
