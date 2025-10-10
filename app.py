import streamlit as st
import docx
import PyPDF2
from io import BytesIO

# Importa o dicionário central de auditorias da nossa estrutura organizada
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

# --- BARRA LATERAL COM O FILTRO DE REGRAS ---
with st.sidebar:
    st.header("⚙️ Filtro de Regras")
    st.write("Selecione as regras que você deseja avaliar:")
    
    # Pega a lista de nomes de todas as regras disponíveis
    lista_de_regras = list(TODAS_AS_AUDITORIAS.keys())
    
    # Cria o widget de multiseleção. Por padrão, todas as regras vêm selecionadas.
    regras_selecionadas = st.multiselect(
        "Regras de Auditoria:",
        options=lista_de_regras,
        default=lista_de_regras,
        label_visibility="collapsed"
    )

# --- CONTEÚDO PRINCIPAL DA PÁGINA ---
st.title("🔎 Revisão de Minutas de Resolução")
st.write("Envie um arquivo (.txt, .docx ou .pdf) para análise conforme com o checklist.")

arquivo_anexado = st.file_uploader(
    "Anexe a minuta aqui:",
    type=['txt', 'docx', 'pdf']
)

if arquivo_anexado:
    if st.button("Analisar Arquivo", type="primary", use_container_width=True):
        if not regras_selecionadas:
            st.warning("Por favor, selecione pelo menos uma regra na barra lateral para fazer a análise.")
        else:
            with st.spinner("Realizando auditoria..."):
                texto_minuta = extrair_texto(arquivo_anexado)
                if texto_minuta:
                    resultados_ok = []
                    resultados_falha = []

                    # Itera sobre todas as auditorias disponíveis
                    for nome_regra, funcao_auditoria in TODAS_AS_AUDITORIAS.items():
                        # >>> A MÁGICA ACONTECE AQUI <<<
                        # Só executa a auditoria se o nome da regra estiver na lista de selecionadas
                        if nome_regra in regras_selecionadas:
                            resultado = funcao_auditoria(texto_minuta)
                            if resultado["status"] == "FALHA":
                                resultados_falha.append((nome_regra, resultado["detalhe"]))
                            else:
                                resultados_ok.append(nome_regra)
                    
                    st.divider()
                    st.subheader("Resultado da Auditoria")
                    col_erros, col_corretos = st.columns(2)

                    with col_erros:
                        st.markdown("##### 👎 Itens com Erros:")
                        if not resultados_falha:
                            st.info("Nenhum erro encontrado nas regras selecionadas.")
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