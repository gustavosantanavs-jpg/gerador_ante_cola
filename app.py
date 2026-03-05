import streamlit as st
from docx import Document
import io

# Configuração da página
st.set_page_config(page_title="Gerador Anti-Cola", page_icon="📝")

st.title("📚 Gerador de Provas - Profa. Milena")
st.write("Faça o upload da prova original em Word (.docx). O sistema irá embaralhar as questões e alternativas.")

# Área de Upload
arquivo_prova = st.file_uploader("Selecione o arquivo da prova (.docx)", type=["docx"])

# Escolha da quantidade
qtd_versoes = st.number_input("Quantas versões diferentes você quer gerar?", min_value=1, max_value=10, value=2)

if arquivo_prova is not None:
    if st.button("Embaralhar e Gerar Provas"):
        with st.spinner("Processando o documento..."):
            
            # --- AQUI ENTRARÁ O MOTOR DE EMBARALHAMENTO NO PRÓXIMO PASSO ---
            # Por enquanto, estamos lendo o arquivo com sucesso e preparando o download
            doc = Document(arquivo_prova)
            
            st.success("Tudo pronto! Baixe as versões abaixo:")
            
            # Gerando os botões de download
            for i in range(int(qtd_versoes)):
                # Salva o arquivo na memória para o usuário poder baixar
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.download_button(
                    label=f"⬇️ Baixar Prova - Versão {i+1}",
                    data=buffer,
                    file_name=f"Prova_Milena_Versao_{i+1}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
