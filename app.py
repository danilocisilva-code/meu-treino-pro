import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

# SUBSTITUA PELO SEU ID DA PLANILHA (O código entre /d/ e /edit/)
# --- CONEXÃO COM GOOGLE SHEETS ---
# --- CONEXÃO COM GOOGLE SHEETS ---
ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXLE"
LINK_CSV = f"https://docs.google.com/spreadsheets/d/{1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE}/export?format=csv&gid=0"

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    return gspread.authorize(creds)

# Estilo Dark Moderno
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #121212; color: #E0E0E0; }
    .stButton>button { border-radius: 20px; background-color: #1F1F1F; color: #40E0D0; border: 1px solid #40E0D0; width: 100%; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1F1F1F; border-radius: 10px; }
    h1, h2, h3 { color: #40E0D0; }
</style>
""", unsafe_allow_html=True)

try:
    # Lendo a planilha (Aba Principal)
    df = pd.read_csv(LINK_CSV)
    
    st.title("🏋️‍♂️ Dashboard de Treino")
    
    # 1. Filtro de Treino (A, B, C, D, E)
    lista_treinos = df['Treino'].dropna().unique()
    treino_sel = st.selectbox("Selecione o Treino do dia:", lista_treinos)
    
    # 2. Filtrar exercícios desse treino
    df_treino = df[df['Treino'] == treino_sel].reset_index(drop=True)
    
    if not df_treino.empty:
        ex_nomes = df_treino['Exercício'].tolist()
        ex_sel = st.selectbox("Escolha o Exercício:", ex_nomes)
        
        # Pega a linha exata do exercício selecionado
        detalhes = df_treino[df_treino['Exercício'] == ex_sel].iloc[0]
        
        # 3. MOSTRANDO AS INFORMAÇÕES (Na sua sequência)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Detalhes")
            st.info(f"**Método:** {detalhes['Método']}")
            st.write(f"**Séries:** {detalhes['Séries']}")
            st.write(f"**Repetições:** {detalhes['Repetições']}")
        
        with col2:
            st.subheader("⏱️ Descanso")
            st.warning(f"**Tempo:** {detalhes['Descanso']}")
            st.write(f"**Instruções:** {detalhes['Instruções']}")

        # 4. Exibição da Foto (se houver link)
        if 'Foto' in detalhes and pd.notna(detalhes['Foto']):
            st.image(detalhes['Foto'], caption=f"Execução: {ex_sel}", use_container_width=True)

        # 5. Registro de Carga (Salva na aba Historico)
        st.divider()
        st.subheader("💾 Registrar Progresso")
        carga_input = st.number_input("Carga Utilizada (kg):", min_value=0, step=1)
        
        if st.button("Salvar na Planilha"):
            try:
                gc = conectar_google()
                sh = gc.open_by_key(ID_PLANILHA)
                aba_hist = sh.worksheet("Historico")
                
                # Prepara a linha para salvar (Data, Treino, Exercício, Carga, Método)
                nova_linha = [
                    pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    treino_sel,
                    ex_sel,
                    carga_input,
                    detalhes['Método']
                ]
                aba_hist.append_row(nova_linha)
                st.success(f"Feito! {carga_input}kg registrados no histórico.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}. Verifique se a aba 'Historico' existe.")
    else:
        st.error("Nenhum dado encontrado para este treino.")

except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.info("Verifique se os nomes das colunas na planilha estão idênticos ao código.")
