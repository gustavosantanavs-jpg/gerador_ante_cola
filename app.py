import streamlit as st
from docx import Document
from docx.text.paragraph import Paragraph
import io
import random
import re
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA (Para ficar em tela cheia e moderna) ---
st.set_page_config(
    page_title="Sistema Anti-Cola Pro - Login",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================================
# 🔐 SEÇÃO DE SEGURANÇA - LISTA VIP DE ACESSO
# =========================================================================
USUARIOS_AUTORIZADOS = {
    "milena": "m1l3n@",
    "gustavo": "g@p",
    "unimam_admin": "uni123",
}

# =========================================================================
# 🎨 ESTILIZAÇÃO AVANÇADA CORRIGIDA
# =========================================================================
CSS_STYLE = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    /* Esconde barra superior e rodapé padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Puxa a tela para cima, tirando o espaço em branco gigante */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }

    /* Fundo suave com grafismos abstratos e geométricos sutis */
    .stApp {
        background-color: #F8F9FB;
        background-image: linear-gradient(135deg, #F8F9FB 0%, #E3E9F2 100%);
        background-attachment: fixed;
    }

    /* O Card Central de Login */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        width: 100%;
    }
    .login-card {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        width: 100%;
        max-width: 420px;
        text-align: center;
    }

    /* Estilização da Logo e Títulos Comerciais */
    .logo-container {
        margin-bottom: 25px;
    }
    .logo-shield {
        font-size: 5rem;
        color: #1A3C6B;
        text-shadow: 0 0 10px rgba(26, 60, 107, 0.2);
    }
    .mortarboard-glow {
        font-size: 2.2rem;
        color: #FFFFFF;
        position: absolute;
        top: 2.5rem;
        left: 2rem;
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
    }
    .product-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 1.8rem;
        color: #1A3C6B;
        margin-top: 10px;
        margin-bottom: 5px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .product-tagline {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 0.95rem;
        color: #6D84A4;
        margin-bottom: 25px;
    }

    /* Estilização dos Campos de Entrada (com ícones embutidos) */
    .input-wrapper {
        position: relative;
        margin-bottom: 20px;
        text-align: left;
    }
    .input-label {
        color: #6D84A4;
        font-size: 0.85rem;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .icon-field {
        position: absolute;
        top: 2.1rem;
        left: 15px;
        color: #A3B3C7;
        font-size: 1rem;
    }
    
    /* Targetando o input real do Streamlit através do CSS */
    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #E1E8F1 !important;
        background-color: #F8F9FB !important;
        padding-left: 45px !important; 
        height: 45px !important;
        font-size: 0.95rem !important;
    }
    .stTextInput input::placeholder {
        color: #A3B3C7;
    }

    /* Estilização do Botão Azul "ENTRAR" */
    div.stButton > button:first-child {
        background-color: #1A73E8;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
        height: 48px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #0E59C7;
        color: white;
    }

    /* Rodapé Profissional Fixado */
    .app-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #F8F9FB;
        padding: 15px 0;
        border-top: 1px solid #E1E8F1;
        text-align: center;
        font-size: 0.85rem;
        color: #A3B3C7;
        z-index: 99;
    }
</style>
"""

# =========================================================================
# ⚙️ MOTOR DE EMBARALHAMENTO (Inalterado)
# =========================================================================
def atualizar_paragrafo(paragrafo, padrao, novo_texto, aplicar_negrito=False):
    texto_completo = paragrafo.text
    match = padrao.match(texto_completo) 
    if not match: return
    
    tamanho_padrao = match.end()
    texto_acumulado = ""
    runs_modificadas = False
    ultima_run_alterada = None
    
    for run in paragrafo.runs:
        texto_original = run.text
        if not texto_original: 
            continue
            
        if not runs_modificadas:
            texto_acumulado += texto_original
            ultima_run_alterada = run
            
            if len(texto_acumulado) <= tamanho_padrao:
                run.text = "" 
            else:
                sobra = texto_acumulado[tamanho_padrao:]
                run.text = novo_texto + sobra
                if aplicar_negrito:
                    run.bold = True
                runs_modificadas = True
                
    if not runs_modificadas and ultima_run_alterada is not None:
        ultima_run_alterada.text = novo_texto
        if aplicar_negrito:
            ultima_run_alterada.bold = True

def processar_prova_com_imagens(doc_original):
    padrao_questao = re.compile(r'^\s*(Questão\s*)?\d+[\.\-\:]?\s*', re.IGNORECASE)
    padrao_alternativa = re.compile(r'^\s*[a-e][\)\.\-]\s*', re.IGNORECASE)

    body = doc_original.element.body
    
    questoes = []
    questao_atual = None
    alternativa_atual = None
    cabecalho = []
    
    for element in list(body):
        if element.tag.endswith('sectPr'):
            continue
            
        texto = ""
        is_paragraph = element.tag.endswith('p')
        
        if is_paragraph:
            for t in element.findall('.//w:t', namespaces=element.nsmap):
                if t.text:
                    texto += t.text

        if is_paragraph and padrao_questao.match(texto):
            questao_atual = {'enunciado': [element], 'alternativas': []}
            questoes.append(questao_atual)
            alternativa_atual = None
            
        elif is_paragraph and padrao_alternativa.match(texto) and questao_atual is not None:
            is_correct = (len(questao_atual['alternativas']) == 0)
            alternativa_atual = {'blocos': [element], 'correta': is_correct}
            questao_atual['alternativas'].append(alternativa_atual)
            
        else:
            if alternativa_atual is not None:
                alternativa_atual['blocos'].append(element)
            elif questao_atual is not None:
                questao_atual['enunciado'].append(element)
            else:
                cabecalho.append(element)

    random.shuffle(questoes)
    for q in questoes:
        random.shuffle(q['alternativas'])

    for child in list(body):
        if not child.tag.endswith('sectPr'):
            body.remove(child)

    for el in cabecalho:
        body.append(el)

    gabarito_final = {}
    letras_maiusculas = ['A', 'B', 'C', 'D', 'E', 'F']
    letras_formatadas = ['a) ', 'b) ', 'c) ', 'd) ', 'e) ', 'f) ']

    contador_questao = 1
    for q in questoes:
        p_xml = q['enunciado'][0]
        body.append(p_xml)
        p_obj = Paragraph(p_xml, doc_original)
        atualizar_paragrafo(p_obj, padrao_questao, f"Questão {contador_questao}: ", aplicar_negrito=True)
        
        for el in q['enunciado'][1:]:
            body.append(el)
            
        for idx_alt, alt in enumerate(q['alternativas']):
            if alt['correta']:
                gabarito_final[contador_questao] = letras_maiusculas[idx_alt]
                
            p_xml_alt = alt['blocos'][0]
            body.append(p_xml_alt)
            p_obj_alt = Paragraph(p_xml_alt, doc_original)
            atualizar_paragrafo(p_obj_alt, padrao_alternativa, letras_formatadas[idx_alt], aplicar_negrito=False)
            
            for el in alt['blocos'][1:]:
                body.append(el)
                
        contador_questao += 1

    doc_original.add_page_break()
    p_titulo = doc_original.add_paragraph()
    run_titulo = p_titulo.add_run("--- GABARITO ---")
    run_titulo.bold = True
    
    for q_num in range(1, contador_questao):
        if q_num in gabarito_final:
            doc_original.add_paragraph(f"Questão {q_num}: {gabarito_final[q_num]}")

    return doc_original

# =========================================================================
# 🚧 APLICAÇÃO PRINCIPAL COM TRAVA DE SEGURANÇA
# =========================================================================

st.markdown(CSS_STYLE, unsafe_allow_html=True)

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="login-container"><div class="login-card">', unsafe_allow_html=True)
        
        # O HTML corrigido do logo e título
        st.markdown("""
        <div class="logo-container">
            <div style="position: relative; display: inline-block;">
                <i class="fa-solid fa-shield-halved logo-shield"></i>
                <i class="fa-solid fa-graduation-cap mortarboard-glow"></i>
                <div style="position: absolute; top: 1rem; left: 1rem; font-size: 2rem; color: #6D84A4;">
                    <i class="fa-solid fa-rotate-right" style="position: absolute; top: 0.8rem; left: 1rem;"></i>
                </div>
            </div>
            <div class="product-title">Sistema Anti-Cola Pro</div>
            <div class="product-tagline">Plataforma de Geração de Provas Inteligentes</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="input-wrapper"><div class="input-label">USUÁRIO</div><i class="fa-solid fa-user icon-field"></i>', unsafe_allow_html=True)
        usuario_digitado = st.text_input("", key="login_user", placeholder="ex: milena").strip()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="input-wrapper"><div class="input-label">SENHA</div><i class="fa-solid fa-lock icon-field"></i>', unsafe_allow_html=True)
        senha_digitada = st.text_input("", key="login_pass", type="password", placeholder="").strip()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("ENTRAR"):
            if usuario_digitado in USUARIOS_AUTORIZADOS and senha_digitada == USUARIOS_AUTORIZADOS[usuario_digitado]:
                st.session_state['logado'] = True
                # Comando de recarregar a página atualizado
                st.rerun()
            else:
                st.error("🛑 Usuário ou senha incorretos. Tente novamente.")
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
    st.markdown(f'<div class="app-footer">© {datetime.now().year} - Todos os direitos reservados | Sistema Anti-Cola Pro Versão 1.0</div>', unsafe_allow_html=True)

else:
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title(f"🚀 Bem-vindo, {st.session_state['login_user']}!")
    with col2:
        if st.button("Sair do Sistema"):
            st.session_state['logado'] = False
            # Comando de recarregar a página atualizado
            st.rerun()
            
    st.write("---")
    st.info("⚠️ No arquivo original (.docx), a resposta CERTA deve ser sempre a PRIMEIRA alternativa (a letra 'a)').")

    arquivo_prova = st.file_uploader("Selecione o arquivo da prova original (.docx)", type=["docx"])
    qtd_versoes = st.number_input("Quantas versões diferentes você quer gerar?", min_value=1, max_value=10, value=2)

    if arquivo_prova is not None:
        if st.button("Embaralhar e Gerar Provas"):
            with st.spinner("Embaralhando tudo e calculando os gabaritos..."):
                try:
                    for i in range(int(qtd_versoes)):
                        doc_base = Document(arquivo_prova)
                        novo_doc = processar_prova_com_imagens(doc_base)
                        
                        buffer = io.BytesIO()
                        novo_doc.save(buffer)
                        buffer.seek(0)
                        
                        st.download_button(
                            label=f"⬇️ Baixar Prova - Versão {i+1}",
                            data=buffer,
                            file_name=f"Prova_AntiCola_Versao_{i+1}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"download_{i}"
                        )
                    st.success("✨ Sucesso! Provas geradas com formatação original e gabarito na última página.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao processar o arquivo. Erro técnico: {e}")
