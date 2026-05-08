import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# Configuração da Página
st.set_page_config(page_title="Meu Treino Pro", layout="centered", page_icon="🏋️‍♂️")

def conectar():
    try:
        info = json.loads(st.secrets["google_json"])
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro ao carregar credenciais: {e}")
        return None

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    /* Fundo Escuro do App */
    [data-testid="stAppViewContainer"] {
        background-color: #0B0F19;
        color: #FFFFFF;
    }
    
    /* Título Principal */
    h1 {
        color: #C6F022 !important;
        text-align: center;
        font-weight: 800 !important;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
    
    /* Subtítulo (Nome do Exercício) */
    h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        margin-top: 10px;
    }

    /* Botão Principal (Salvar Carga) */
    button[kind="primary"] {
        background-color: #C6F022 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 15px !important;
    }

    /* Botões Secundários (Navegação) */
    button[kind="secondary"] {
        background-color: #1E232F !important;
        color: #FFFFFF !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }

    /* --- TRANSFORMA OS RADIO BUTTONS EM CAIXAS --- */
    div.row-widget.stRadio > div {
        flex-direction: row;
        justify-content: center;
        gap: 10px;
    }
    div.row-widget.stRadio > div > label {
        background-color: #1E232F;
        padding: 10px 25px;
        border-radius: 8px;
        border: 1px solid #333;
        cursor: pointer;
    }
    /* Esconde a bolinha do radio */
    div.row-widget.stRadio > div > label > div:first-child {
        display: none;
    }
    /* Cor do texto do botão do treino */
    div.row-widget.stRadio > div > label [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF;
        font-weight: bold;
        margin: 0;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Controle de Sessão para Navegação
if 'ex_idx' not in st.session_state:
    st.session_state.ex_idx = 0
if 'treino_atual' not in st.session_state:
    st.session_state.treino_atual = None

st.title("MEU TREINO")

gc = conectar()
if gc:
    try:
        sh = gc.open_by_key("1Q5dc9QcIRjhPn_SOHjX9LZTJtFJS2D7mjs2KjaMZXlE")
        aba = sh.get_worksheet(0)
        
        # Pega os dados e remove linhas totalmente vazias
        df = pd.DataFrame(aba.get_all_records())
        # Remove linhas onde a coluna 'Treino' está vazia
        df = df[df['Treino'].astype(str).str.strip() != ''] 
        
        if not df.empty:
            # Ordena e cria os botões de Treino (A, B, C...)
            treinos = sorted(df['Treino'].unique().tolist())
            sel_t = st.radio("Escolha o Treino:", treinos, horizontal=True, label_visibility="collapsed")
            
            # Zera o contador se mudar de treino
            if sel_t != st.session_state.treino_atual:
                st.session_state.treino_atual = sel_t
                st.session_state.ex_idx = 0
                
            df_t = df[df['Treino'] == sel_t].reset_index(drop=True)
            exercicios = df_t['Exercício'].tolist()
            
            # Trava o índice para não dar erro
            if st.session_state.ex_idx >= len(exercicios):
                st.session_state.ex_idx = 0
                
            # Coleta os dados exatos da linha atual
            idx = st.session_state.ex_idx
            det = df_t.iloc[idx]
            
            # Variáveis puxando exatamente as colunas que você pediu
            sel_ex = det.get('Exercício', 'Sem Nome')
            foto_url = det.get('Foto', '')
            metodo = det.get('Método', '-')
            series = det.get('Séries', '-')
            reps = det.get('Repetições', '-')
            descanso = det.get('Descanso', '-')
            instrucoes = det.get('Instruções', '')

            st.write("") # Espaço em branco

            # 1. FOTO DO EXERCÍCIO
            if pd.notna(foto_url) and str(foto_url).startswith('http'):
                st.image(foto_url, use_container_width=True)

            # 2. NOME DO EXERCÍCIO
            st.subheader(f"{idx + 1}. {sel_ex}")

            # 3. BADGES DE INFORMAÇÃO (M, S, R, D)
            html_badges = f"""
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                <div style="background-color: #1E232F; padding: 5px 12px; border-radius: 6px; font-size: 14px;">
                    <span style="color: #C6F022; font-weight: bold;">M:</span> <span style="color: white;">{metodo}</span>
                </div>
                <div style="background-color: #1E232F; padding: 5px 12px; border-radius: 6px; font-size: 14px;">
                    <span style="color: #C6F022; font-weight: bold;">S:</span> <span style="color: white;">{series}</span>
                </div>
                <div style="background-color: #1E232F; padding: 5px 12px; border-radius: 6px; font-size: 14px; width: 100%;">
                    <span style="color: #C6F022; font-weight: bold;">R:</span> <span style="color: white;">{reps}</span>
                </div>
                <div style="background-color: #1E232F; padding: 5px 12px; border-radius: 6px; font-size: 14px;">
                    <span style="color: #C6F022; font-weight: bold;">D:</span> <span style="color: white;">{descanso}</span>
                </div>
            </div>
            """
            st.markdown(html_badges, unsafe_allow_html=True)

            # 4. INSTRUÇÕES (Com borda verde neon)
            if pd.notna(instrucoes) and str(instrucoes).strip() != '':
                html_instrucoes = f"""
                <div style="background-color: #1E232F; border-left: 4px solid #C6F022; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                    <strong style="color: white; font-size: 14px;">Instruções:</strong><br>
                    <span style="color: #A0AAB5; font-size: 14px;">{instrucoes}</span>
                </div>
                """
                st.markdown(html_instrucoes, unsafe_allow_html=True)

            # 5. BOTÕES DE NAVEGAÇÃO
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("⏮️ Anterior", use_container_width=True):
                    if st.session_state.ex_idx > 0:
                        st.session_state.ex_idx -= 1
                        st.rerun()
            with col2:
                if st.button("🔄 Início", use_container_width=True):
                    st.session_state.ex_idx = 0
                    st.rerun()
            with col3:
                if st.button("Próximo ⏭️", use_container_width=True):
                    if st.session_state.ex_idx < len(exercicios) - 1:
                        st.session_state.ex_idx += 1
                        st.rerun()
                    else:
                        st.success("🎉 Treino Finalizado!")
                        st.balloons()

            st.write("---")

            # 6. INPUT DE CARGA E SALVAR
            carga = st.number_input("Carga Atual (kg):", min_value=0.0, step=1.0, format="%.1f")
            
            if st.button("SALVAR CARGA", type="primary", use_container_width=True):
                try:
                    aba_h = sh.worksheet("Historico")
                    # Salva Data, Treino, Exercício e Carga
                    data_hora = pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
                    aba_h.append_row([data_hora, sel_t, sel_ex, carga])
                    st.toast("✅ Carga salva no histórico!")
                except:
                    st.error("Erro! Crie uma aba chamada 'Historico' na sua planilha para salvar as cargas.")
        else:
            st.warning("Sua planilha não possui treinos cadastrados ou as colunas estão vazias.")
            
    except Exception as e:
        st.error(f"Erro de conexão com a planilha: {e}")
