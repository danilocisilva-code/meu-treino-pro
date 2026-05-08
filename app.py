import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

# CONEXÃO DIRETA COM A SUA PLANILHA
ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"
LINK_CSV = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv&gid=0"

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # O arquivo credentials.json DEVE estar na raiz do seu GitHub
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    return gspread.authorize(creds)

# ESTILO DARK
st.markdown("<style>[data-testid='stAppViewContainer']{background-color:#121212;color:#E0E0E0;}.stButton>button{border-radius:20px;background-color:#1F1F1F;color:#40E0D0;border:1px solid #40E0D0;width:100%;font-weight:bold;}h1,h2,h3{color:#40E0D0;}</style>", unsafe_allow_html=True)

try:
    # Lendo os dados
    df = pd.read_csv(LINK_CSV)
    
    st.title("🏋️‍♂️ Meu Treino Pro")
    
    if 'Treino' in df.columns:
        lista_treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Selecione o Treino:", lista_treinos)
        
        df_treino = df[df['Treino'] == treino_sel].reset_index(drop=True)
        
        if not df_treino.empty:
            ex_nomes = df_treino['Exercício'].tolist()
            ex_sel = st.selectbox("Escolha o Exercício:", ex_nomes)
            detalhes = df_treino[df_treino['Exercício'] == ex_sel].iloc[0]
            
            # MOSTRANDO INFORMAÇÕES
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**Método:** {detalhes.get('Método', '---')}")
                st.write(f"**Séries:** {detalhes.get('Séries', '---')}")
            with c2:
                st.warning(f"**Descanso:** {detalhes.get('Descanso', '---')}")
                st.write(f"**Repetições:** {detalhes.get('Repetições', '---')}")

            if 'Foto' in detalhes and pd.notna(detalhes['Foto']):
                st.image(detalhes['Foto'], use_container_width=True)

            # SALVAR CARGA
            st.divider()
            carga = st.number_input("Peso (kg):", min_value=0, step=1)
            
            if st.button("SALVAR SÉRIE"):
                gc = conectar_google()
                sh = gc.open_by_key(ID_PLANILHA)
                aba_hist = sh.worksheet("Historico")
                
                nova_linha = [pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), treino_sel, ex_sel, carga, detalhes.get('Método', '---')]
                aba_hist.append_row(nova_linha)
                st.success(f"Salvo: {carga}kg")
                st.balloons()
    else:
        st.error("Coluna 'Treino' não encontrada. Verifique os títulos na sua planilha!")

except Exception as e:
    st.error(f"Erro: {e}")
    st.info("💡 Certifique-se de que compartilhou a planilha com o e-mail do robô como EDITOR.")
