import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

# --- CONEXÃO COM GOOGLE SHEETS ---
# Usei o ID da planilha que você me enviou por último
ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"
LINK_CSV = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid=0"

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Certifique-se que o arquivo 'credentials.json' está na mesma pasta no GitHub
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    return gspread.authorize(creds)

# --- ESTILO VISUAL (DARK MODE) ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #121212; color: #E0E0E0; }
    .stButton>button { border-radius: 20px; background-color: #1F1F1F; color: #40E0D0; border: 1px solid #40E0D0; width: 100%; height: 50px; font-weight: bold; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1F1F1F; border-radius: 10px; }
    h1, h2, h3 { color: #40E0D0; }
    .css-1avcm0n { background-color: #1F1F1F; border-radius: 15px; padding: 20px; }
</style>
""", unsafe_allow_html=True)

try:
    # Lendo os dados da planilha
    df = pd.read_csv(LINK_CSV)
    
    st.title("🏋️‍♂️ Meu Treino Pro")
    
    # 1. SELEÇÃO DO TREINO (A, B, C, D, E)
    if 'Treino' in df.columns:
        lista_treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Selecione o Treino do dia:", lista_treinos)
        
        # 2. FILTRAR EXERCÍCIOS
        df_treino = df[df['Treino'] == treino_sel].reset_index(drop=True)
        
        if not df_treino.empty:
            ex_nomes = df_treino['Exercício'].tolist()
            ex_sel = st.selectbox("Escolha o Exercício:", ex_nomes)
            
            # Pega os detalhes do exercício selecionado
            detalhes = df_treino[df_treino['Exercício'] == ex_sel].iloc[0]
            
            # 3. EXIBIÇÃO DOS DETALHES (Baseado nas suas colunas)
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### 📋 Info")
                st.info(f"**Método:** {detalhes.get('Método', 'N/A')}")
                st.write(f"**Séries:** {detalhes.get('Séries', 'N/A')}")
                st.write(f"**Repetições:** {detalhes.get('Repetições', 'N/A')}")
            
            with col2:
                st.markdown(f"### ⏱️ Descanso")
                st.warning(f"**Tempo:** {detalhes.get('Descanso', 'N/A')}")
                st.write(f"**Instruções:** {detalhes.get('Instruções', 'N/A')}")

            # 4. FOTO DO EXERCÍCIO
            if 'Foto' in detalhes and pd.notna(detalhes['Foto']):
                st.image(detalhes['Foto'], caption=f"Execução: {ex_sel}", use_container_width=True)

            # 5. REGISTRO DE CARGA
            st.divider()
            st.subheader("💾 Registrar Progresso")
            carga_input = st.number_input("Carga Utilizada (kg):", min_value=0, step=1, key="carga")
            
            if st.button("SALVAR SÉRIE"):
                try:
                    gc = conectar_google()
                    sh = gc.open_by_key(ID_PLANILHA)
                    
                    # Tenta acessar a aba Historico
                    try:
                        aba_hist = sh.worksheet("Historico")
                    except:
                        st.error("Erro: A aba 'Historico' não foi encontrada na sua planilha!")
                        st.stop()
                    
                    # Monta a linha para salvar
                    nova_linha = [
                        pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                        treino_sel,
                        ex_sel,
                        carga_input,
                        detalhes.get('Método', 'N/A')
                    ]
                    
                    aba_hist.append_row(nova_linha)
                    st.success(f"Sucesso! {carga_input}kg salvos no histórico.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
        else:
            st.warning("Nenhum exercício encontrado para este treino.")
    else:
        st.error("A coluna 'Treino' não foi encontrada na planilha.")

except Exception as e:
    st.error(f"Erro Crítico: {e}")
    st.info("Dica: Verifique se você compartilhou a planilha com o e-mail do robô.")
