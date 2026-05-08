import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import re

st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Lendo o arquivo bruto do GitHub
    with open("credentials.json", "r") as f:
        conteudo = f.read()
    
    # Limpeza de emergência para JSON malformado
    conteudo_limpo = conteudo.strip()
    # Remove vírgulas extras no final antes do fechamento }
    conteudo_limpo = re.sub(r',\s*}', '}', conteudo_limpo)
    
    try:
        info = json.loads(conteudo_limpo)
    except Exception as e:
        st.error(f"Erro na estrutura do credentials.json: {e}")
        st.stop()
    
    # Corrige a chave privada (\n virando quebra de linha real)
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

# Estilo
st.markdown("<style>[data-testid='stAppViewContainer']{background-color:#121212;color:#E0E0E0;} h1,h2,h3{color:#40E0D0;}</style>", unsafe_allow_html=True)

try:
    gc = conectar_google()
    sh = gc.open_by_key(ID_PLANILHA)
    
    # Tenta ler a aba de exercícios
    aba_dados = sh.get_worksheet(0)
    df = pd.DataFrame(aba_dados.get_all_records())

    st.title("🏋️‍♂️ Dashboard de Treino")

    if not df.empty:
        treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Escolha o Treino:", treinos)
        
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

        st.divider()
        carga = st.number_input("Peso (kg):", min_value=0, step=1)
        if st.button("💾 SALVAR"):
            try:
                aba_hist = sh.worksheet("Historico")
                nova_linha = [pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), treino_sel, ex_sel, carga]
                aba_hist.append_row(nova_linha)
                st.success("Salvo!")
                st.balloons()
            except:
                st.error("Crie a aba 'Historico' na planilha!")
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
