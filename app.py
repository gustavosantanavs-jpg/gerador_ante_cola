import streamlit as st
from docx import Document
import io
import random
import re
import copy

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador Anti-Cola", page_icon="📝")
st.title("📚 Gerador de Provas - Profa. Milena")
st.write("Faça o upload da prova original em Word (.docx). O sistema irá embaralhar as questões e as alternativas.")

# --- FUNÇÃO PRINCIPAL DE EMBARALHAMENTO ---
def processar_prova(doc_original):
    """
    Lê o documento Word, identifica questões e alternativas,
    e retorna um novo documento embaralhado.
    """
    doc = Document()
    
    # Variáveis para armazenar a estrutura
    questoes = []
    questao_atual = None
    alternativa_atual = None
    
    # Padrões que o programa vai procurar (1. , 2. , a) , b) )
    padrao_questao = re.compile(r'^\s*\d+[\.\-]\s+')
    padrao_alternativa = re.compile(r'^\s*[a-e][\)\.\-]\s+')

    # 1. ESCANEAMENTO DO DOCUMENTO
    for paragrafo in doc_original.paragraphs:
        texto = paragrafo.text
        
        # Se achou uma nova questão (Ex: "1. ")
        if padrao_questao.match(texto):
            questao_atual = {
                'enunciado': [paragrafo.text],
                'alternativas': []
            }
            questoes.append(questao_atual)
            alternativa_atual = None
            
        # Se achou uma alternativa (Ex: "a) ")
        elif padrao_alternativa.match(texto) and questao_atual is not None:
            alternativa_atual = [paragrafo.text]
            questao_atual['alternativas'].append(alternativa_atual)
            
        # Se for um texto de continuação (imagem, resto do enunciado ou resto da alternativa)
        else:
            if alternativa_atual is not None:
                alternativa_atual.append(paragrafo.text)
            elif questao_atual is not None:
                questao_atual['enunciado'].append(paragrafo.text)
            else:
                # Textos antes da primeira questão (cabeçalho, nome do aluno, etc)
                doc.add_paragraph(paragrafo.text)

    # 2. O EMBARALHAMENTO
    random.shuffle(questoes) # Mistura as questões 1, 2, 3...
    
    for q in questoes:
        random.shuffle(q['alternativas']) # Mistura as letras a, b, c... dentro da questão

    # 3. A MONTAGEM DO NOVO DOCUMENTO
    contador_questao = 1
    for q in questoes:
        # Escreve o enunciado renumerado
        for i, texto_enunciado in enumerate(q['enunciado']):
            if i == 0:
                # Troca o número antigo pelo novo número sorteado
                texto_limpo = re.sub(padrao_questao, f"{contador_questao}. ", texto_enunciado)
                doc.add_paragraph(texto_limpo)
            else:
                if texto_enunciado.strip() != "":
                    doc.add_paragraph(texto_enunciado)
        
        # Escreve as alternativas com as letras corrigidas (a, b, c, d, e)
        letras = ['a) ', 'b) ', 'c) ', 'd) ', 'e) ', 'f) ']
        for idx_alt, alt in enumerate(q['alternativas']):
            for i, texto_alt in enumerate(alt):
                if i == 0:
                    # Troca a letra antiga pela nova letra na ordem certa
                    texto_limpo = re.sub(padrao_alternativa, letras[idx_alt], texto_alt)
                    doc.add_paragraph(texto_limpo)
                else:
                    if texto_alt.strip() != "":
                        doc.add_paragraph(texto_alt)
        
        doc.add_paragraph("") # Espaço em branco entre as questões
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
                
                # Gera os botões de download dinamicamente
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
                st.error(f"Ocorreu um erro ao processar o arquivo. Verifique se o padrão de numeração está correto. Erro técnico: {e}")
