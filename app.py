import streamlit as st
import docx
import PyPDF2
import pandas as pd
from io import BytesIO
import re
from core import TODAS_AS_AUDITORIAS
from core.regras.regras_anexo import auditar_anexo

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
                 # Adiciona verificação para evitar erro se extract_text retornar None
                 page_text = pagina.extract_text()
                 if page_text:
                    texto += page_text + "\n"
            return texto
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

def executar_auditoria(texto_para_auditar, regras_selecionadas):
    """Executa um conjunto de regras de auditoria em um bloco de texto."""
    resultados_ok = []
    resultados_falha = []
    if not texto_para_auditar:
        return [], []
    for nome_regra, funcao_auditoria in TODAS_AS_AUDITORIAS.items():
        if nome_regra in regras_selecionadas:
            # A regra 'Anexo (Identificação)' é tratada separadamente no app.py
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
    """Cria as duas colunas e exibe os resultados de uma auditoria."""
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
                else: # Se não for lista (caso inesperado), exibe diretamente
                     st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;- {detalhes}")
    with col_corretos:
        st.markdown("##### 👍 Itens Corretos:")
        if not resultados_ok:
            st.info("Nenhum item verificado passou na auditoria.")
        else:
            for nome, detalhe in resultados_ok:
                st.success(f"**{nome}**", icon="✅")
                # Garante que detalhe seja string antes de checar startswith
                detalhe_str = str(detalhe) if detalhe is not None else ""
                if detalhe_str.startswith("Aviso:"):
                    st.warning(f"&nbsp;&nbsp;&nbsp;&nbsp;{detalhe_str}")
                elif detalhe_str:
                    st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;{detalhe_str}")


def limpar_caixa_texto():
    if "texto_colado_input" in st.session_state:
        st.session_state.texto_colado_input = ""

# --- Interface Gráfica (Front-end) ---
st.set_page_config(page_title="Auditor de Minutas", layout="wide")

# Nomes das regras conforme __init__.py
TODAS_REGRAS_NOMES = list(TODAS_AS_AUDITORIAS.keys())

# --- MUDANÇA DE LÓGICA ---
# Define quais regras rodam em qual parte
REGRAS_RESOLUCAO = [
    "Brasão / Nome do Ministério",
    "Epígrafe (Formato e Data)",
    "Ementa (Verbo Inicial)",
    "Preâmbulo (Estrutura)",
    "Bloco de Assinatura",
    "Fecho de Vigência",
    "Artigos (Formato Numeração)",
    "Parágrafos (§ Espaçamento)",
    "Datas (Zero à Esquerda no Dia)",
    "Siglas (Uso do travessão)",
    "Incisos (Pontuação - Resolução)",
    "Alíneas (Pontuação - Resolução)",
]

REGRAS_ANEXO = [
    # Regras de formatação que continuam valendo
    "Artigos (Formato Numeração)",
    "Parágrafos (§ Espaçamento)",
    "Datas (Zero à Esquerda no Dia)",
    "Siglas (Uso do travessão)",
    
    # Novas regras de sequência e pontuação específicas do Anexo
    "Anexo: Sequência de Capítulos",
    "Anexo: Sequência de Seções",
    "Anexo: Sequência de Artigos",
    "Anexo: Pontuação Hierárquica",
]
# --- FIM DA MUDANÇA ---


st.title("🔎 Auditor de Minutas de Resolução")

tab_texto, tab_arquivo = st.tabs(["Colar Texto", "Anexar Arquivo"])

# --- Função Auxiliar para Análise ---
def analisar_e_exibir(texto_completo):
    """Função centralizada para analisar e exibir os resultados."""
    if not texto_completo or not texto_completo.strip():
        st.warning("Texto fornecido está vazio ou contém apenas espaços.")
        return

    # Limpa marca d'água ANTES de qualquer análise
    texto_limpo = re.sub(r'\*?\s*MINUTA DE DOCUMENTO', '', texto_completo, flags=re.IGNORECASE)
    if not texto_limpo or not texto_limpo.strip():
        st.warning("Texto após remover 'MINUTA DE DOCUMENTO' está vazio.")
        return

    # 1. Executa a regra do Anexo no texto COMPLETO (já limpo)
    resultado_anexo = auditar_anexo(texto_limpo)

    # 2. Divide o texto (baseado na versão limpa)
    texto_resolucao = texto_limpo
    texto_anexo = None
    # Regex para encontrar linha exata "ANEXO"
    match_anexo = re.search(r'^\s*ANEXO\s*$', texto_limpo, re.MULTILINE)

    if match_anexo:
        split_point = match_anexo.start()
        texto_resolucao = texto_limpo[:split_point].strip()
        texto_anexo = texto_limpo[match_anexo.end():].strip()

    # 3. Executa o resto das regras na Resolução
    ok_res, falha_res = executar_auditoria(texto_resolucao, REGRAS_RESOLUCAO)

    # 4. Adiciona o resultado da regra do Anexo (Identificação)
    detalhes_anexo = resultado_anexo.get("detalhe", [])
    if not isinstance(detalhes_anexo, list):
        detalhes_anexo = [str(detalhes_anexo)]
    else:
        detalhes_anexo = [str(d) for d in detalhes_anexo]

    if resultado_anexo["status"] == "FALHA":
        falha_res.append(("Anexo (Identificação)", detalhes_anexo))
    else:
        detalhe_ok = resultado_anexo.get("detalhe", "")
        ok_res.append(("Anexo (Identificação)", str(detalhe_ok)))

    # 5. Exibe resultados da Resolução
    st.divider()
    exibir_resultados("Resultado da Resolução Principal", ok_res, falha_res)

    # 6. Exibe resultados do Anexo (se existir E contiver texto)
    if texto_anexo and texto_anexo.strip():
        st.divider()
        # Usa a lista REGRAS_ANEXO definida globalmente
        ok_anexo, falha_anexo = executar_auditoria(texto_anexo, REGRAS_ANEXO)
        exibir_resultados("Resultado do Anexo", ok_anexo, falha_anexo)
    elif match_anexo and (not texto_anexo or not texto_anexo.strip()):
        # Se encontrou "ANEXO" mas não há conteúdo depois
        st.divider()
        st.info("Seção 'ANEXO' encontrada, mas está vazia.")


# --- ABA 1: COLAR TEXTO ---
with tab_texto:
    st.write("Copie e cole o texto completo da minuta na caixa abaixo para análise.")
    texto_colado = st.text_area("Texto da Minuta:", height=350, label_visibility="collapsed", key="texto_colado_input")

    col_analisar, col_limpar = st.columns([4, 1])
    with col_analisar:
        botao_analisar_clicado = st.button("Analisar Texto", type="primary", use_container_width=True, key="btn_analisar_texto")
    with col_limpar:
        st.button("Limpar", use_container_width=True, key="btn_limpar_texto", on_click=limpar_caixa_texto)

    if botao_analisar_clicado:
        if not texto_colado:
            st.warning("Por favor, cole um texto na caixa acima para fazer a análise.")
        else:
            with st.spinner("Realizando auditoria do texto..."):
                analisar_e_exibir(texto_colado) # Chama a função centralizada

# --- ABA 2: UPLOAD DE ARQUIVO ---
with tab_arquivo:
    st.write("Envie um arquivo (.txt, .docx ou .pdf) para análise de conformidade.")
    # Define arquivo_anexado aqui
    arquivo_anexado = st.file_uploader("Anexe a minuta aqui:", type=['txt', 'docx', 'pdf'], label_visibility="collapsed")

    # --- CORREÇÃO DE ESCOPO/ORDEM ---
    # Verifica PRIMEIRO se um arquivo foi anexado
    if arquivo_anexado:
        # SÓ ENTÃO verifica se o botão foi clicado
        if st.button("Analisar Arquivo", type="primary", use_container_width=True, key="btn_analisar_arquivo"):
            with st.spinner("Realizando auditoria do arquivo..."):
                # Agora, arquivo_anexado está garantido de existir aqui
                texto_completo = extrair_texto(arquivo_anexado)
                if texto_completo:
                    analisar_e_exibir(texto_completo) # Chama a função centralizada