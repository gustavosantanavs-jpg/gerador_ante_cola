import streamlit as st
from docx import Document
from docx.text.paragraph import Paragraph
import io
import random
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Anti-Cola", page_icon="📝")
st.title("📚 Gerador de Provas - Profa. Milena")
st.write("Faça o upload da prova original em Word (.docx). O sistema irá embaralhar as questões, alternativas e manter as imagens (mesmo na mesma linha) intactas.")

# --- FUNÇÃO CIRÚRGICA PARA MANTER IMAGENS E NEGRITO ---
def atualizar_paragrafo(paragrafo, padrao, novo_texto, aplicar_negrito=False):
    """
    Substitui o número da questão/alternativa preservando imagens in-line
    e outras formatações do resto do parágrafo.
    """
    texto_completo = paragrafo.text
    
    # CORREÇÃO AQUI: Removido o comando duplicado que estava causando o erro vermelho
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

# --- MOTOR PRINCIPAL ---
def processar_prova_com_imagens(doc_original):
    padrao_questao = re.compile(r'^\s*(Questão\s*)?\d+[\.\-\:]?\s*', re.IGNORECASE)
    padrao_alternativa = re.compile(r'^\s*[a-e][\)\.\-]\s*', re.IGNORECASE)

    body = doc_original.element.body
    
    questoes = []
    questao_atual = None
    alternativa_atual = None
    cabecalho = []
    
    # 1. ESCANEAMENTO AVANÇADO
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
            alternativa_atual = [element]
            questao_atual['alternativas'].append(alternativa_atual)
            
        else:
            if alternativa_atual is not None:
                alternativa_atual.append(element)
            elif questao_atual is not None:
                questao_atual['enunciado'].append(element)
            else:
                cabecalho.append(element)

    # 2. EMBARALHAMENTO
    random.shuffle(questoes)
    for q in questoes:
        random.shuffle(q['alternativas'])

    # 3. MONTAGEM CUIDADOSA
    for child in list(body):
        if not child.tag.endswith('sectPr'):
            body.remove(child)

    for el in cabecalho:
        body.append(el)

    contador_questao = 1
    for q in questoes:
        p_xml = q['enunciado'][0]
        body.append(p_xml)
        p_obj = Paragraph(p_xml, doc_original)
        atualizar_paragrafo(p_obj, padrao_questao, f"Questão {contador_questao}: ", aplicar_negrito=True)
        
        for el in q['enunciado'][1:]:
            body.append(el)
            
        letras = ['a) ', 'b) ', 'c) ', 'd) ', 'e) ', 'f) ']
        for idx_alt, alt in enumerate(q['alternativas']):
            p_xml_alt = alt[0]
            body.append(p_xml_alt)
            p_obj_alt = Paragraph(p_xml_alt, doc_original)
            atualizar_paragrafo(p_obj_alt, padrao_alternativa, letras[idx_alt], aplicar_negrito=False)
            
            for el in alt[1:]:
                body.append(el)
                
        contador_questao += 1

    return doc_original

# --- INTERFACE ---
arquivo_prova = st.file_uploader("Selecione o arquivo da prova (.docx)", type=["docx"])
qtd_versoes = st.number_input("Quantas versões diferentes você quer gerar?", min_value=1, max_value=10, value=2)

if arquivo_prova is not None:
    if st.button("Embaralhar e Gerar Provas"):
        with st.spinner("Realizando cirurgia no arquivo para preservar imagens e formatações..."):
            try:
                doc_original = Document(arquivo_prova)
                
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
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                st.success("✨ Sucesso! Provas geradas com formatação e imagens originais:")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar o arquivo. Erro técnico: {e}")
