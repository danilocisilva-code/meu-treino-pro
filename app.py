import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# Configuração da Página para ficar com cara de App de Celular (Centered)
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

# --- ESTILOS CSS PERSONALIZADOS (O Segredo do Visual) ---
st.markdown("""
<style>
    /* Fundo Escuro do App */
    [data-testid="stAppViewContainer"] {
        background-color: #0B0F19;
        color: #FFFFFF;
    }
    
    /* Cor do Título Principal */
    h1 {
        color: #C6F022 !important;
        text-align: center;
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    
    /* Subtítulo (Nome do Exercício) */
    h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Botão Principal (Salvar Carga - Verde Neon) */
    button[kind="primary"] {
        background-color: #C6F022 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px !important;
    }

    /* Botões Secundários (Navegação) */
    button[kind="secondary"] {
        background-color: #1E232F !important;
        color: #FFFFFF !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }

    /* Esconder o fundo branco padrão do rádio (seleção de treino) */
    div.row-widget.stRadio > div {
        justify-content: center;
        gap: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Controle de Sessão
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
        df = pd.DataFrame(aba.get_all_records())
        
        if not df.empty:
            # Seleção de Treino
            treinos = df['Treino'].unique()
            sel_t = st.radio("Escolha o Treino:", treinos, horizontal=True, label_visibility="collapsed")
            
            # Zera o contador se mudar de treino
            if sel_t != st.session_state.treino_atual:
                st.session_state.treino_atual = sel_t
                st.session_state.ex_idx = 0
                
            df_t = df[df['Treino'] == sel_t].reset_index(drop=True)
            exercicios = df_t['Exercício'].tolist()
            
            # Limite do índice
            if st.session_state.ex_idx >= len(exercicios):
                st.session_state.ex_idx = 0
                
            # Dados do exercício atual
            idx = st.session_state.ex_idx
            sel_ex = exercicios[idx]
            det = df_t.iloc[idx]

            st.write("") # Espaço

            # Foto do Exercício
            if 'Foto' in det and pd.notna(det['Foto']) and str(det['Foto']).startswith('http'):
                st.image(det['Foto'], use_container_width=True)

            # Nome do Exercício
            st.subheader(f"{idx + 1}. {sel_ex}")

            # --- "BADGES" HTML COM AS INFORMAÇÕES (M, S, R, D) ---
            metodo = det.get('Método', '-')
            series = det.get('Séries', '-')
            reps = det.get('Repetições', '-')
            descanso = det.get('Descanso', '-')
            
            html_badges = f"""
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                <div style="background-color: #1E232F; padding: 5px 10px; border-radius: 6px; font-size: 14px;">
                    <span style="color: #C6F022; font-weight: bold;">M:</span> {metodo}
                </div>
                <div style="background-color: #1E232F; padding: 5px 10px; border-radius: 6px; font-size: 14px;">
                    <span style="color: #C6F022; font-weight: bold;">S:</span> {series}
                </div>
                <div style="background-color: #1E232F; padding: 5px 10px; border-radius: 6px; font-size: 14px; width: 100%;">
                    <span style="color: #C6F022; font-weight: bold;">R:</span> {reps}
                </div>
                <div style="background-color: #1E232F; padding: 5px 10px; border-radius: 6px; font-size: 14px;">
                    <span style="color: #C6F022; font-weight: bold;">D:</span> {descanso}
                </div>
            </div>
            """
            st.markdown(html_badges, unsafe_allow_html=True)

            # --- CAIXA DE INSTRUÇÕES (Com borda verde neon) ---
            detalhes = det.get('Detalhes', det.get('Como Fazer', det.get('Observações', ''))).strip()
            if detalhes and str(detalhes).lower() != 'nan':
                html_instrucoes = f"""
                <div style="background-color: #1E232F; border-left: 4px solid #C6F022; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                    <strong style="color: white; font-size: 14px;">Instruções:</strong><br>
                    <span style="color: #A0AAB5; font-size: 14px;">{detalhes}</span>
                </div>
                """
                st.markdown(html_instrucoes, unsafe_allow_html=True)

            # --- BOTÕES DE NAVEGAÇÃO ---
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

            # --- INPUT DE CARGA E SALVAR ---
            carga = st.number_input("Carga Atual (kg):", min_value=0.0, step=1.0, format="%.1f")
            
            # O type="primary" faz o botão pegar a cor verde neon que configuramos no CSS
            if st.button("SALVAR CARGA", type="primary", use_container_width=True):
                try:
                    aba_h = sh.worksheet("Historico")
                    aba_h.append_row([pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"), sel_t, sel_ex, carga])
                    st.toast("✅ Carga salva com sucesso no histórico!")
                except:
                    st.error("Erro! Crie uma aba chamada 'Historico' na sua planilha.")
        else:
            st.warning("Sua planilha parece estar vazia!")
            
    except Exception as e:
        st.error(f"Erro de conexão com a planilha: {e}")
