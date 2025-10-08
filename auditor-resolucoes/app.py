import streamlit as st
import docx
import PyPDF2
from io import BytesIO

# Importa as nossas funções de auditoria já existentes
from core.auditors import (
    auditar_cabecalho_ministerio,
    auditar_epigrafe,
    auditar_ementa,
    auditar_considerando,
    auditar_numeracao_artigos,
    auditar_pontuacao_incisos,
    auditar_uso_siglas,
    auditar_assinatura
)

# Dicionário com todas as auditorias para facilitar a chamada
TODAS_AS_AUDITORIAS = {
    "R001: Cabeçalho do Ministério": auditar_cabecalho_ministerio,
    "R002: Epígrafe (Formato e Data)": auditar_epigrafe,
    "R003: Ementa (Verbo Inicial)": auditar_ementa,
    "R004: Seção CONSIDERANDO": auditar_considerando,
    "R005: Numeração de Artigos": auditar_numeracao_artigos,
    "R008: Pontuação de Incisos": auditar_pontuacao_incisos,
    "R010: Uso de Siglas (Travessão)": auditar_uso_siglas,
    "R012: Bloco de Assinatura": auditar_assinatura,
}

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

st.set_page_config(page_title="Auditor de Minutas", layout="centered")
st.title("🔎 Auditor de Minutas de Resolução")

# 1. Widget de Upload de Arquivo
st.subheader("1. Adicionar arquivo para fazer a verificação")
arquivo_anexado = st.file_uploader(
    "Anexe a minuta aqui:",
    type=['txt', 'docx', 'pdf'],
    label_visibility="collapsed"
)

# 2. Botão de Análise e exibição dos resultados
if arquivo_anexado:
    st.subheader("2. Verificar o documento")
    if st.button("Verificar", type="primary", use_container_width=True):
        with st.spinner("Analisando..."):
            texto_minuta = extrair_texto(arquivo_anexado)

            if texto_minuta:
                # Listas para guardar os resultados
                resultados_ok = []
                resultados_falha = []

                # Executa cada auditoria e separa os resultados
                for nome, funcao_auditoria in TODAS_AS_AUDITORIAS.items():
                    resultado = funcao_auditoria(texto_minuta)
                    if resultado["status"] == "FALHA":
                        resultados_falha.append((nome, resultado["detalhe"]))
                    else:
                        resultados_ok.append(nome)
                
                st.divider()
                st.subheader("Resultado da Auditoria")

                # 3. Cria as duas colunas para os resultados
                col_erros, col_corretos = st.columns(2)

                # Coluna da Esquerda: Erros
                with col_erros:
                    st.markdown("##### 👎 Lista com todos os erros:")
                    if not resultados_falha:
                        st.info("Nenhum erro encontrado.")
                    else:
                        for nome, detalhes in resultados_falha:
                            st.error(f"**{nome}**", icon="❌")
                            for erro in detalhes:
                                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;- {erro}")

                # Coluna da Direita: Itens Corretos
                with col_corretos:
                    st.markdown("##### 👍 Lista com tudo correto:")
                    if not resultados_ok:
                        st.info("Nenhum item verificado passou na auditoria.")
                    else:
                        for nome in resultados_ok:
                            st.success(f"**{nome}**", icon="✅")