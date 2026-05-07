import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
import os

# --- CONFIGURAÇÕES DE ESTILO (VISUAL DARK MODERNO) ---
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #121212; color: #E0E0E0; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .stButton>button { border-radius: 20px; background-color: #1F1F1F; color: #40E0D0; border: 1px solid #40E0D0; width: 100%; }
    .stButton>button:hover { background-color: #40E0D0; color: #121212; }
    .stSelectbox div[data-baseweb="select"] { border-radius: 10px; background-color: #1F1F1F; }
    .stTab { color: #888; font-weight: bold; }
    .stTab[aria-selected="true"] { color: #40E0D0; border-bottom: 2px solid #40E0D0; }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS ---
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTGu49CBNiHFDBIMgt3Y-o_Nl5pGN2MRKImGAycSyJDuH0MUtxMxihpA9VJ2t-JdDnx2KGcGxUdK9Pk/pub?gid=0&single=true&output=csv"
# ID da sua planilha (aquela parte grande entre /d/ e /edit no link do navegador)
ID_PLANILHA = "1Gu49CBNiHFDBIMgt3Y-o_Nl5pGN2MRKImGAycSyJDuH0" 

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Aqui ele lê o arquivo credentials.json que você criou no GitHub
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    return gspread.authorize(creds)

# Inicializar memória do treino
if 'indice_ex' not in st.session_state: st.session_state.indice_ex = 0
if 'watch_connected' not in st.session_state: st.session_state.watch_connected = False

try:
    # Lendo dados para exibição (via CSV para ser rápido)
    df = pd.read_csv(LINK_CSV)
    
    st.title("🏋️‍♂️ Meu Treino Pro")
    aba1, aba2, aba3 = st.tabs(["✍️ Treinar", "📊 Histórico", "⏱️ Cronômetro"])

    with aba1:
        # Filtros
        l_treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Selecione o Treino:", l_treinos)
        d_filtrados = df[df['Treino'] == treino_sel].reset_index(drop=True)
        l_exercicios = d_filtrados['Exercício'].tolist()

        # Navegação
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶️ Iniciar / Resetar"):
                st.session_state.indice_ex = 0
                st.rerun()
        with c2:
            if st.button("⏭️ Próximo"):
                if st.session_state.indice_ex < len(l_exercicios) - 1:
                    st.session_state.indice_ex += 1
                    st.rerun()

        ex_sel = st.selectbox("Exercício Atual:", l_exercicios, index=st.session_state.indice_ex)
        
        # Exibição de Foto/GIF
        linha_ex = d_filtrados[d_filtrados['Exercício'] == ex_sel]
        if 'Foto' in df.columns:
            url_foto = linha_ex['Foto'].values[0]
            if pd.notna(url_foto): st.image(url_foto, width=400)

        # Registro de Carga e Relógio
        col_dados, col_watch = st.columns([2, 1])
        with col_dados:
            carga = st.number_input("Carga (kg):", min_value=0, key=f"c_{ex_sel}")
            if st.button("💾 Salvar Série"):
                try:
                    gc = conectar_google()
                    # Abre a aba 'Historico' da sua planilha
                    planilha = gc.open_by_key("1Gu49CBNiHFDBIMgt3Y-o_Nl5pGN2MRKImGAycSyJDuH0MUtxMxihpA9VJ2t-JdDnx2KGcGxUdK9Pk".split('/')[-2]) # Tenta extrair ID do link
                    aba_hist = planilha.worksheet("Historico")
                    
                    data_hora = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    calorias = 420 if st.session_state.watch_connected else 0
                    
                    aba_hist.append_row([data_hora, treino_sel, ex_sel, carga, calorias])
                    st.toast("✅ Registrado no Google Drive!", icon="💪")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

        with col_watch:
            st.write("⌚ Amazfit GTS 2e")
            if st.button("Conectar" if not st.session_state.watch_connected else "Desconectar"):
                st.session_state.watch_connected = not st.session_state.watch_connected
                st.rerun()
            if st.session_state.watch_connected:
                st.info("🔥 420 kcal")

    with aba2:
        st.subheader("Histórico de Evolução")
        st.info("Os dados aqui são lidos diretamente da aba 'Historico' da sua planilha.")
        # Adicionar visualização do histórico aqui depois

except Exception as e:
    st.error(f"Erro ao carregar app: {e}")
