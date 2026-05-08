import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# Configuração da Página
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

# ID da Planilha
ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"

def conectar_google():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Carrega o JSON do arquivo
    with open("credentials.json", "r") as f:
        info = json.load(f)
    # Conserta a chave privada (converte \n em quebras reais)
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

# Estilo Visual
st.markdown("<style>[data-testid='stAppViewContainer']{background-color:#121212;color:#E0E0E0;} h1,h2,h3{color:#40E0D0;}</style>", unsafe_allow_html=True)

try:
    gc = conectar_google()
    sh = gc.open_by_key(ID_PLANILHA)
    aba_dados = sh.get_worksheet(0)
    dados = aba_dados.get_all_records()
    df = pd.DataFrame(dados)

    st.title("🏋️‍♂️ Dashboard de Treino")

    if not df.empty:
        # 1. Escolha do Treino
        treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Selecione o seu Treino:", treinos)
        
        # 2. Escolha do Exercício
        df_treino = df[df['Treino'] == treino_sel].reset_index(drop=True)
        ex_sel = st.selectbox("Qual o Exercício?", df_treino['Exercício'].tolist())
        
        detalhes = df_treino[df_treino['Exercício'] == ex_sel].iloc[0]
        
        # 3. Exibição
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

        # 4. Salvar Carga
        st.divider()
        carga = st.number_input("Carga usada (kg):", min_value=0, step=1)
        if st.button("💾 SALVAR PROGRESSO"):
            try:
                aba_hist = sh.worksheet("Historico")
                nova_linha = [pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), treino_sel, ex_sel, carga]
                aba_hist.append_row(nova_linha)
                st.success(f"Salvo! Carga de {carga}kg registrada.")
                st.balloons()
            except:
                st.error("Crie uma aba chamada 'Historico' na sua planilha para salvar!")
    else:
        st.warning("Planilha lida, mas parece estar vazia.")

except Exception as e:
    st.error(f"Erro de Conexão: {e}")
