# app.py

import streamlit as st
import docx
import PyPDF2
from io import BytesIO

# Importa o dicionário central de auditorias da nossa nova estrutura
from core.regras import TODAS_AS_AUDITORIAS

def extrair_texto(arquivo_enviado):
    """Extrai texto de diferentes tipos de arquivo."""
    try:
        if arquivo_enviado.type == "text/plain":
            return arquivo_enviado.read().decode("utf-8")
        elif arquivo_enviado.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(BytesIO(arquivo_enviado.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        elif arquivo_enviado.type == "application/pdf":
            texto = ""
            leitor_pdf = PyPDF2.PdfReader(BytesIO(arquivo_enviado.read()))
            for pagina in leitor_pdf.pages:
                texto += pagina.extract_text()
            return texto
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

# --- Interface Gráfica (Front-end) ---
st.set_page_config(page_title="Auditor de Minutas", layout="wide")
st.title("🔎 Auditor de Minutas de Resolução")
st.write("Envie um arquivo (.txt, .docx ou .pdf) para análise de conformidade com o checklist.")

arquivo_anexado = st.file_uploader(
    "Anexe a minuta aqui:",
    type=['txt', 'docx', 'pdf']
)

if arquivo_anexado:
    if st.button("Analisar Arquivo", type="primary", use_container_width=True):
        with st.spinner("Realizando auditoria..."):
            texto_minuta = extrair_texto(arquivo_anexado)
            if texto_minuta:
                resultados_ok = []
                resultados_falha = []

                # O loop continua o mesmo, mas agora usa o dicionário importado
                for nome, funcao_auditoria in TODAS_AS_AUDITORIAS.items():
                    resultado = funcao_auditoria(texto_minuta)
                    if resultado["status"] == "FALHA":
                        resultados_falha.append((nome, resultado["detalhe"]))
                    else:
                        resultados_ok.append(nome)
                
                st.divider()
                st.subheader("Resultado da Auditoria")
                col_erros, col_corretos = st.columns(2)

                with col_erros:
                    st.markdown("##### 👎 Itens com Erros:")
                    if not resultados_falha:
                        st.info("Nenhum erro encontrado.")
                    else:
                        for nome, detalhes in resultados_falha:
                            st.error(f"**{nome}**", icon="❌")
                            for erro in detalhes:
                                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;- {erro}")

                with col_corretos:
                    st.markdown("##### 👍 Itens Corretos:")
                    if not resultados_ok:
                        st.info("Nenhum item verificado passou na auditoria.")
                    else:
                        for nome in resultados_ok:
                            st.success(f"**{nome}**", icon="✅")