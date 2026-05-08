import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

# ID da sua planilha (conforme seu link enviado)
ID_PLANILHA = "1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE"

def conectar_google():
    """Conecta ao Google Sheets tratando a chave privada para evitar erro de assinatura."""
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Abre o arquivo credentials.json que está no seu GitHub
    with open("credentials.json", "r") as f:
        info = json.load(f)
    
    # CURA DO ERRO 'Invalid JWT Signature':
    # Converte os caracteres de texto '\n' em quebras de linha reais que o Google exige
    if "private_key" in info:
        info["private_key"] = info["private_key"].replace("\\n", "\n")
    
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

# --- ESTILO VISUAL (DARK MODE) ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #121212; color: #E0E0E0; }
    .stButton>button { border-radius: 20px; background-color: #1F1F1F; color: #40E0D0; border: 1px solid #40E0D0; width: 100%; font-weight: bold; }
    h1, h2, h3 { color: #40E0D0; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1F1F1F; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

try:
    # 1. CONECTAR E BUSCAR DADOS
    gc = conectar_google()
    sh = gc.open_by_key(ID_PLANILHA)
    
    # Pega a primeira aba (onde estão os exercícios)
    aba_dados = sh.get_worksheet(0)
    dados = aba_dados.get_all_records()
    df = pd.DataFrame(dados)

    st.title("🏋️‍♂️ Dashboard de Treino")

    if not df.empty:
        # 2. FILTRO DE TREINO (A, B, C, D, E)
        lista_treinos = df['Treino'].dropna().unique()
        treino_sel = st.selectbox("Escolha o Treino:", lista_treinos)
        
        # 3. FILTRAR EXERCÍCIOS
        df_treino = df[df['Treino'] == treino_sel].reset_index(drop=True)
        
        ex_nomes = df_treino['Exercício'].tolist()
        ex_sel = st.selectbox("Exercício:", ex_nomes)
        
        # Pega a linha do exercício selecionado
        detalhes = df_treino[df_treino['Exercício'] == ex_sel].iloc[0]
        
        # 4. EXIBIR DETALHES (Colunas da sua planilha)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Método:** {detalhes.get('Método', 'N/A')}")
            st.write(f"**Séries:** {detalhes.get('Séries', 'N/A')}")
            st.write(f"**Repetições:** {detalhes.get('Repetições', 'N/A')}")
        
        with col2:
            st.warning(f"**Descanso:** {detalhes.get('Descanso', 'N/A')}")
            st.write(f"**Instruções:** {detalhes.get('Instruções', 'N/A')}")

        # Foto (Link da Planilha)
        if 'Foto' in detalhes and pd.notna(detalhes['Foto']) and str(detalhes['Foto']).startswith('http'):
            st.image(detalhes['Foto'], use_container_width=True)

        # 5. REGISTRO DE CARGA
        st.divider()
        carga_input = st.number_input("Carga usada (kg):", min_value=0, step=1)
        
        if st.button("💾 SALVAR PROGRESSO"):
            try:
                # Tenta abrir a aba Historico para salvar
                aba_hist = sh.worksheet("Historico")
                nova_linha = [
                    pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                    treino_sel,
                    ex_sel,
                    carga_input,
                    detalhes.get('Método', 'N/A')
                ]
                aba_hist.append_row(nova_linha)
                st.success(f"Registrado: {carga_input}kg em {ex_sel}!")
                st.balloons()
            except Exception as e_hist:
                st.error("Erro: Verifique se você criou a aba chamada 'Historico' na sua planilha.")
    else:
        st.warning("Nenhum dado encontrado na planilha principal.")

except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.info("💡 Verifique se o conteúdo do 'credentials.json' está correto e se a planilha foi compartilhada com o e-mail do robô.")
