import streamlit as st
from docx import Document
from docx.text.paragraph import Paragraph
import io
import random
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Anti-Cola", page_icon="📝")
st.title("📚 Gerador de Provas - Profa. Milena")
st.write("Faça o upload da prova original em Word (.docx). O sistema irá embaralhar as questões, alternativas e manter as imagens e tabelas intactas.")

def processar_prova_com_imagens(doc_original):
    # Radares de texto
    padrao_questao = re.compile(r'^\s*(Questão\s*)?\d+[\.\-\:]?\s*', re.IGNORECASE)
    padrao_alternativa = re.compile(r'^\s*[a-e][\)\.\-]\s*', re.IGNORECASE)

    body = doc_original.element.body
    
    questoes = []
    questao_atual = None
    alternativa_atual = None
    cabecalho = []
    
    # 1. ESCANEAMENTO AVANÇADO (Agrupando caixas de texto e imagem)
    for element in list(body):
        # Ignora metadados de fim de página
        if element.tag.endswith('sectPr'):
            continue
            
        texto = ""
        is_paragraph = element.tag.endswith('p')
        
        if is_paragraph:
            # Lê o texto escondido dentro do código do Word
            for t in element.findall('.//w:t', namespaces=element.nsmap):
                if t.text:
                    texto += t.text

        if is_paragraph and padrao_questao.match(texto):
            questao_atual = {'enunciado': [element], 'alternativas': []}
            questoes.append(questao_atual)
            alternativa_atual = None
            
        elif is_paragraph and padrao_alternativa.match(texto) and questao_atual is not None:
            alternativa_atual = [element]
            questao_atual['alternativas'].append(alternativa_atual)
            
        else:
            if alternativa_atual is not None:
                alternativa_atual.append(element)
            elif questao_atual is not None:
                questao_atual['enunciado'].append(element)
            else:
                cabecalho.append(element)

    # 2. O EMBARALHAMENTO
    random.shuffle(questoes)
    for q in questoes:
        random.shuffle(q['alternativas'])

    # 3. A MONTAGEM (Movendo os blocos sem perder a formatação)
    # Limpa o corpo do documento atual
    for child in list(body):
        if not child.tag.endswith('sectPr'):
            body.remove(child)

    # Devolve o cabeçalho (Nome da escola, aluno, etc)
    for el in cabecalho:
        body.append(el)

    # Devolve as questões na nova ordem
    contador_questao = 1
    for q in questoes:
        # Renumera a primeira linha da questão
        p_xml = q['enunciado'][0]
        body.append(p_xml)
        p_obj = Paragraph(p_xml, doc_original)
        p_obj.text = re.sub(padrao_questao, f"Questão {contador_questao}: ", p_obj.text)
        
        # Cola o resto do enunciado (onde geralmente ficam as IMAGENS)
        for el in q['enunciado'][1:]:
            body.append(el)
            
        # Renumera e cola as alternativas
        letras = ['a) ', 'b) ', 'c) ', 'd) ', 'e) ', 'f) ']
        for idx_alt, alt in enumerate(q['alternativas']):
            p_xml_alt = alt[0]
            body.append(p_xml_alt)
            p_obj_alt = Paragraph(p_xml_alt, doc_original)
            p_obj_alt.text = re.sub(padrao_alternativa, letras[idx_alt], p_obj_alt.text)
            
            # Cola o resto da alternativa (imagens das alternativas, se houver)
            for el in alt[1:]:
                body.append(el)
                
        contador_questao += 1

    return doc_original

# --- INTERFACE DO USUÁRIO ---
arquivo_prova = st.file_uploader("Selecione o arquivo da prova (.docx)", type=["docx"])
qtd_versoes = st.number_input("Quantas versões diferentes você quer gerar?", min_value=1, max_value=10, value=2)

if arquivo_prova is not None:
    if st.button("Embaralhar e Gerar Provas"):
        with st.spinner("Processando textos, imagens e gerando os arquivos..."):
            try:
                doc_original = Document(arquivo_prova)
                st.success("✨ Sucesso! Baixe as versões abaixo:")
                
                for i in range(int(qtd_versoes)):
                    # Lemos o arquivo novamente para cada versão para ter uma base limpa
                    doc_base = Document(arquivo_prova)
                    novo_doc = processar_prova_com_imagens(doc_base)
                    
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
