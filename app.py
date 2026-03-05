import streamlit as st
from docx import Document
import io
import random
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Anti-Cola", page_icon="📝")
st.title("📚 Gerador de Provas - Profa. Milena")
st.write("Faça o upload da prova original em Word (.docx). O sistema irá embaralhar as questões e as alternativas.")

def processar_prova(doc_original):
    doc = Document()
    questoes = []
    questao_atual = None
    alternativa_atual = None
    
    # RADAR ATUALIZADO: Agora aceita "Questão 1:", "1.", "1 -", etc.
    padrao_questao = re.compile(r'^\s*(Questão\s*)?\d+[\.\-\:]?\s*', re.IGNORECASE)
    # RADAR DE ALTERNATIVAS: Aceita "a)", "A)", "a.", "a -", etc.
    padrao_alternativa = re.compile(r'^\s*[a-e][\)\.\-]\s*', re.IGNORECASE)

    # 1. ESCANEAMENTO DO DOCUMENTO
    for paragrafo in doc_original.paragraphs:
        texto = paragrafo.text
        
        if padrao_questao.match(texto):
            questao_atual = {'enunciado': [paragrafo.text], 'alternativas': []}
            questoes.append(questao_atual)
            alternativa_atual = None
            
        elif padrao_alternativa.match(texto) and questao_atual is not None:
            alternativa_atual = [paragrafo.text]
            questao_atual['alternativas'].append(alternativa_atual)
            
        else:
            if alternativa_atual is not None:
                alternativa_atual.append(paragrafo.text)
            elif questao_atual is not None:
                questao_atual['enunciado'].append(paragrafo.text)
            else:
                doc.add_paragraph(paragrafo.text)

    # 2. O EMBARALHAMENTO
    random.shuffle(questoes)
    for q in questoes:
        random.shuffle(q['alternativas'])

    # 3. A MONTAGEM DO NOVO DOCUMENTO
    contador_questao = 1
    for q in questoes:
        for i, texto_enunciado in enumerate(q['enunciado']):
            if i == 0:
                # Troca pelo novo número no formato que a Milena usa
                texto_limpo = re.sub(padrao_questao, f"Questão {contador_questao}: ", texto_enunciado)
                doc.add_paragraph(texto_limpo)
            else:
                if texto_enunciado.strip() != "":
                    doc.add_paragraph(texto_enunciado)
        
        letras = ['a) ', 'b) ', 'c) ', 'd) ', 'e) ']
        for idx_alt, alt in enumerate(q['alternativas']):
            for i, texto_alt in enumerate(alt):
                if i == 0:
                    texto_limpo = re.sub(padrao_alternativa, letras[idx_alt], texto_alt)
                    doc.add_paragraph(texto_limpo)
                else:
                    if texto_alt.strip() != "":
                        doc.add_paragraph(texto_alt)
        
        doc.add_paragraph("") 
        contador_questao += 1

    return doc

# --- INTERFACE DO USUÁRIO ---
arquivo_prova = st.file_uploader("Selecione o arquivo da prova (.docx)", type=["docx"])
qtd_versoes = st.number_input("Quantas versões diferentes você quer gerar?", min_value=1, max_value=10, value=2)

if arquivo_prova is not None:
    if st.button("Embaralhar e Gerar Provas"):
        with st.spinner("Lendo padrões, embaralhando e gerando os arquivos..."):
            try:
                doc_original = Document(arquivo_prova)
                st.success("✨ Sucesso! Baixe as versões abaixo:")
                
                for i in range(int(qtd_versoes)):
                    novo_doc = processar_prova(doc_original)
                    
                    buffer = io.BytesIO()
                    novo_doc.save(buffer)
                    buffer.seek(0)
                    
                    st.download_button(
                        label=f"⬇️ Baixar Prova - Versão {i+1}",
                        data=buffer,
                        file_name=f"Prova_AntiCola_Versao_{i+1}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar o arquivo. Erro técnico: {e}")
