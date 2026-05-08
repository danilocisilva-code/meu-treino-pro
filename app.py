import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

st.set_page_config(page_title="Meu Treino Pro", layout="wide", page_icon="🏋️‍♂️")

def conectar():
    try:
        # Puxa o JSON blindado que guardamos nos Secrets
        info = json.loads(st.secrets["google_json"])
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {e}")
        return None

# --- CONTROLE DE NAVEGAÇÃO DOS EXERCÍCIOS ---
if 'ex_idx' not in st.session_state:
    st.session_state.ex_idx = 0
if 'treino_atual' not in st.session_state:
    st.session_state.treino_atual = None

# Estilo Dark Mode
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #121212; color: #E0E0E0; }
    h1, h2, h3 { color: #40E0D0; }
    /* Centraliza os botões horizontais (A, B, C) */
    div.row-widget.stRadio > div { flex-direction: row; justify-content: center; flex-wrap: wrap; gap: 15px;}
</style>
""", unsafe_allow_html=True)

st.title("🏋️‍♂️ Meu Treino Pro")

gc = conectar()
if gc:
    try:
        sh = gc.open_by_key("1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE")
        aba = sh.get_worksheet(0)
        df = pd.DataFrame(aba.get_all_records())
        
        if not df.empty:
            
            # 1. OPÇÕES DE TREINO NA HORIZONTAL (A, B, C...)
            treinos = df['Treino'].unique()
            sel_t = st.radio("Selecione o Treino:", treinos, horizontal=True)
            
            # Se mudar o treino (de A para B, por exemplo), zera o contador para o primeiro exercício
            if sel_t != st.session_state.treino_atual:
                st.session_state.treino_atual = sel_t
                st.session_state.ex_idx = 0
                
            df_t = df[df['Treino'] == sel_t].reset_index(drop=True)
            exercicios = df_t['Exercício'].tolist()
            
            # 2. BOTÕES INICIAR, ANTERIOR E PRÓXIMO
            st.divider()
            c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
            with c_btn1:
                if st.button("🔄 Reiniciar", use_container_width=True):
                    st.session_state.ex_idx = 0
            with c_btn2:
                if st.button("⏮️ Anterior", use_container_width=True):
                    if st.session_state.ex_idx > 0:
                        st.session_state.ex_idx -= 1
            with c_btn3:
                if st.button("⏭️ Próximo", use_container_width=True):
                    if st.session_state.ex_idx < len(exercicios) - 1:
                        st.session_state.ex_idx += 1
                    else:
                        st.success("🎉 Treino Finalizado!")
                        st.balloons()

            # Garantir que o índice não saia do limite por erro
            if st.session_state.ex_idx >= len(exercicios):
                st.session_state.ex_idx = 0
                
            # Dados do exercício atual
            idx = st.session_state.ex_idx
            sel_ex = exercicios[idx]
            det = df_t.iloc[idx]
            
            st.subheader(f"💪 {idx + 1}. {sel_ex} ({idx + 1} de {len(exercicios)})")
            
            # Caixas com Séries e Repetições
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**Método:** {det.get('Método', '---')}")
                st.write(f"**Séries:** {det.get('Séries', '---')}")
            with c2:
                st.warning(f"**Descanso:** {det.get('Descanso', '---')}")
                st.write(f"**Repetições:** {det.get('Repetições', '---')}")

            # 3. DETALHES DE COMO FAZER
            # Ele procura na planilha as colunas 'Detalhes', 'Como Fazer' ou 'Observações'
            detalhes = det.get('Detalhes', det.get('Como Fazer', det.get('Observações', 'Nenhum detalhe adicional.')))
            
            if str(detalhes).strip() and str(detalhes).lower() != 'nan':
                with st.expander("📖 Como executar o exercício", expanded=True):
                    st.write(detalhes)

            # Foto do Exercício
            if 'Foto' in det and pd.notna(det['Foto']) and str(det['Foto']).startswith('http'):
                st.image(det['Foto'], use_container_width=True)

            # Salvar Histórico
            st.divider()
            carga = st.number_input("Carga Atual (kg):", min_value=0, step=1)
            if st.button("💾 SALVAR PROGRESSO"):
                try:
                    aba_h = sh.worksheet("Historico")
                    aba_h.append_row([pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), sel_t, sel_ex, carga])
                    st.success("Salvo com sucesso!")
                except:
                    st.error("Crie uma aba chamada 'Historico' na planilha!")
        else:
            st.warning("Planilha vazia!")
            
    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")
