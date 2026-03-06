import streamlit as st
from docx import Document
from docx.text.paragraph import Paragraph
import io
import random
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Anti-Cola Pro", page_icon="🎓")

# --- IMAGEM DE TOPO ---
# Tenta carregar a imagem. Se o arquivo ainda não estiver no GitHub, o site não quebra.
try:
    st.image("logo.png", use_container_width=True)
except:
    pass

st.title("📚 Sistema Anti-Cola Pro - Profa. Milena")
st.write("Faça o upload da prova original em Word (.docx). O sistema irá embaralhar as questões, alternativas e criar um Gabarito Automático no final.")
st.info("⚠️ Regra de ouro: No arquivo original, a resposta CERTA deve ser sempre a PRIMEIRA alternativa (a letra 'a)').")

# --- FUNÇÃO CIRÚRGICA PARA MANTER IMAGENS E NEGRITO ---
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

# --- MOTOR PRINCIPAL COM GABARITO ---
def processar_prova_com_imagens(doc_original):
    padrao_questao = re.compile(r'^\s*(Questão\s*)?\d+[\.\-\:]?\s*', re.IGNORECASE)
    padrao_alternativa = re.compile(r'^\s*[a-e][\)\.\-]\s*', re.IGNORECASE)

    body = doc_original.element.body
    
    questoes = []
    questao_atual = None
    alternativa_atual = None
    cabecalho = []
    
    # 1. ESCANEAMENTO AVANÇADO E MARCAÇÃO DA RESPOSTA CERTA
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

    # 4. IMPRIMINDO O GABARITO NO FINAL
    doc_original.add_page_break() 
    p_titulo = doc_original.add_paragraph()
    run_titulo = p_titulo.add_run("--- GABARITO ---")
    run_titulo.bold = True
    
    for q_num in range(1, contador_questao):
        if q_num in gabarito_final:
            doc_original.add_paragraph(f"Questão {q_num}: {gabarito_final[q_num]}")

    return doc_original

# --- INTERFACE ---
arquivo_prova = st.file_uploader("Selecione o arquivo da prova (.docx)", type=["docx"])
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
                st.success("✨ Sucesso! Provas geradas com formatação original e gabarito no final.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar o arquivo. Erro técnico: {e}")
