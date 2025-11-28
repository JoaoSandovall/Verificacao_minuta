import streamlit as st
import docx
import PyPDF2
from io import BytesIO
import re

# Importa a nova função "inteligente"
from core import obter_regras
# Importa a regra de anexo separada para verificação inicial
from core.regras.anexo import auditar_anexo
# Importa as regras comuns para forçar o uso no Anexo
from core.regras import comuns

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
                 page_text = pagina.extract_text()
                 if page_text:
                    texto += page_text + "\n"
            return texto
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

def executar_auditoria(texto_para_auditar, regras_dict):
    """Executa um dicionário de regras em um bloco de texto."""
    resultados_ok = []
    resultados_falha = []
    
    if not texto_para_auditar:
        return [], []

    for nome_regra, funcao_auditoria in regras_dict.items():
        # Pula a regra de identificação do anexo (já feita separadamente)
        if nome_regra == "Anexo (Identificação)":
            continue

        try:
            resultado = funcao_auditoria(texto_para_auditar)
            if resultado["status"] == "FALHA":
                detalhes = resultado.get("detalhe", ["Erro desconhecido na regra."])
                if not isinstance(detalhes, list):
                    detalhes = [str(detalhes)]
                else:
                    detalhes = [str(d) for d in detalhes]
                resultados_falha.append((nome_regra, detalhes))
            else:
                resultados_ok.append((nome_regra, resultado.get("detalhe", "")))
        except Exception as e:
            resultados_falha.append((nome_regra, [f"Erro interno ao executar a regra: {e}"])) 

    return resultados_ok, resultados_falha

def exibir_resultados(titulo, resultados_ok, resultados_falha):
    """Exibe os resultados na interface."""
    st.subheader(titulo)
    col_erros, col_corretos = st.columns(2)
    with col_erros:
        st.markdown("##### 👎 Itens com Erros:")
        if not resultados_falha:
            st.info("Nenhum erro encontrado.")
        else:
            for nome, detalhes in resultados_falha:
                st.error(f"**{nome}**", icon="❌")
                if isinstance(detalhes, list):
                    for erro in detalhes:
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;- {erro}")
                else:
                     st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;- {detalhes}")
    with col_corretos:
        st.markdown("##### 👍 Itens Corretos:")
        if not resultados_ok:
            st.info("Nenhum item verificado passou na auditoria.")
        else:
            for nome, detalhe in resultados_ok:
                st.success(f"**{nome}**", icon="✅")
                detalhe_str = str(detalhe) if detalhe is not None else ""
                if detalhe_str.startswith("Aviso:"):
                    st.warning(f"&nbsp;&nbsp;&nbsp;&nbsp;{detalhe_str}")
                elif detalhe_str:
                    st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;{detalhe_str}")

def limpar_caixa_texto():
    if "texto_colado_input" in st.session_state:
        st.session_state.texto_colado_input = ""

# --- Interface Gráfica ---
st.set_page_config(page_title="Auditor de Minutas", layout="wide")
st.title("🔎 Auditor de Minutas de Resolução")

tab_texto, tab_arquivo = st.tabs(["Colar Texto", "Anexar Arquivo"])

def analisar_e_exibir(texto_completo):
    if not texto_completo or not texto_completo.strip():
        st.warning("Texto fornecido está vazio ou contém apenas espaços.")
        return

    texto_limpo = re.sub(r'\*?\s*MINUTA DE DOCUMENTO', '', texto_completo, flags=re.IGNORECASE)
    if not texto_limpo or not texto_limpo.strip():
        st.warning("Texto após remover 'MINUTA DE DOCUMENTO' está vazio.")
        return

    regras_detectadas, tipo_doc = obter_regras(texto_limpo)
    st.info(f"🔍 Tipo de Documento Detectado: **Resolução {tipo_doc}**")

    regras_resolucao = {k: v for k, v in regras_detectadas.items() if not k.startswith("Anexo")}
    
    regras_anexo = {k: v for k, v in regras_detectadas.items() if k.startswith("Anexo") and k != "Anexo (Identificação)"}

    regras_anexo["Artigos (Formato Numeração)"] = comuns.auditar_numeracao_artigos
    regras_anexo["Parágrafos (§ Espaçamento)"] = comuns.auditar_espacamento_paragrafo
    regras_anexo["Siglas (Uso do travessão)"] = comuns.auditar_uso_siglas
    regras_anexo["Incisos (Pontuação Estrita)"] = comuns.auditar_pontuacao_incisos

    # Identificação do Anexo
    resultado_identificacao_anexo = auditar_anexo(texto_limpo)

    # Divisão do Texto
    texto_resolucao = texto_limpo
    texto_anexo = None
    match_anexo = re.search(r'^\s*ANEXO\s*$', texto_limpo, re.MULTILINE)

    if match_anexo:
        split_point = match_anexo.start()
        texto_resolucao = texto_limpo[:split_point].strip()
        texto_anexo = texto_limpo[match_anexo.end():].strip()

    ok_res, falha_res = executar_auditoria(texto_resolucao, regras_resolucao)

    # Adiciona resultado da identificação do Anexo
    detalhes_anexo_id = resultado_identificacao_anexo.get("detalhe", [])
    if not isinstance(detalhes_anexo_id, list): detalhes_anexo_id = [str(detalhes_anexo_id)]
    else: detalhes_anexo_id = [str(d) for d in detalhes_anexo_id]

    if resultado_identificacao_anexo["status"] == "FALHA":
        falha_res.append(("Anexo (Identificação)", detalhes_anexo_id))
    else:
        ok_res.append(("Anexo (Identificação)", str(resultado_identificacao_anexo.get("detalhe", ""))))

    st.divider()
    exibir_resultados(f"Resultado da Resolução Principal ({tipo_doc})", ok_res, falha_res)

    # Auditoria do Anexo
    if texto_anexo and texto_anexo.strip():
        st.divider()
        ok_anexo, falha_anexo = executar_auditoria(texto_anexo, regras_anexo)
        exibir_resultados("Resultado do Anexo", ok_anexo, falha_anexo)
    elif match_anexo and (not texto_anexo or not texto_anexo.strip()):
        st.divider()
        st.info("Seção 'ANEXO' encontrada, mas está vazia.")

# --- Interface ---
with tab_texto:
    st.write("Copie e cole o texto completo da minuta na caixa abaixo para análise.")
    texto_colado = st.text_area("Texto da Minuta:", height=350, label_visibility="collapsed", key="texto_colado_input")
    col1, col2 = st.columns([4, 1])
    if col1.button("Analisar Texto", type="primary", use_container_width=True):
        if texto_colado: 
            with st.spinner("Analisando..."): analisar_e_exibir(texto_colado)
        else: st.warning("Cole um texto primeiro.")
    if col2.button("Limpar", use_container_width=True, on_click=limpar_caixa_texto): pass

with tab_arquivo:
    st.write("Envie um arquivo (.txt, .docx ou .pdf).")
    arq = st.file_uploader("Anexe aqui:", type=['txt', 'docx', 'pdf'], label_visibility="collapsed")
    if arq and st.button("Analisar Arquivo", type="primary", use_container_width=True):
        with st.spinner("Analisando..."):
            txt = extrair_texto(arq)
            if txt: analisar_e_exibir(txt)