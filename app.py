# app.py

import streamlit as st
import docx
import PyPDF2
import pandas as pd
from io import BytesIO
import re

# Importa o dicionário central de auditorias
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
                texto += pagina.extract_text() + "\n"
            return texto
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

def executar_auditoria(texto_para_auditar, regras_selecionadas):
    """Executa um conjunto de regras de auditoria em um bloco de texto."""
    # ... (esta função continua a mesma)
    resultados_ok = []
    resultados_falha = []
    if not texto_para_auditar:
        return [], []
    for nome_regra, funcao_auditoria in TODAS_AS_AUDITORIAS.items():
        if nome_regra in regras_selecionadas:
            resultado = funcao_auditoria(texto_para_auditar)
            if resultado["status"] == "FALHA":
                resultados_falha.append((nome_regra, resultado["detalhe"]))
            else:
                resultados_ok.append((nome_regra, resultado.get("detalhe", "")))
    return resultados_ok, resultados_falha

def exibir_resultados(titulo, resultados_ok, resultados_falha):
    """Cria as duas colunas e exibe os resultados de uma auditoria."""
    # ... (esta função continua a mesma)
    st.subheader(titulo)
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
            for nome, detalhe in resultados_ok:
                st.success(f"**{nome}**", icon="✅")
                if detalhe:
                    st.caption(f"&nbsp;&nbsp;&nbsp;&nbsp;{detalhe}")

# --- Interface Gráfica (Front-end) ---
st.set_page_config(page_title="Auditor de Minutas", layout="wide")

with st.sidebar:
    st.header("⚙️ Filtro de Regras")
    st.write("Selecione as regras para avaliar:")
    lista_de_regras = list(TODAS_AS_AUDITORIAS.keys())
    regras_selecionadas = st.multiselect(
        "Regras de Auditoria:",
        options=lista_de_regras,
        default=lista_de_regras,
        label_visibility="collapsed"
    )

st.title("🔎 Auditor de Minutas de Resolução")

tab1, tab2 = st.tabs(["Anexar Arquivo", "Colar Texto"])

# --- ABA 1: UPLOAD DE ARQUIVO ---
with tab1:
    st.write("Envie um arquivo (.txt, .docx ou .pdf) para análise de conformidade.")
    arquivo_anexado = st.file_uploader("Anexe a minuta aqui:", type=['txt', 'docx', 'pdf'], label_visibility="collapsed")
    if arquivo_anexado:
        if st.button("Analisar Arquivo", type="primary", use_container_width=True, key="btn_analisar_arquivo"):
            if not regras_selecionadas:
                st.warning("Por favor, selecione pelo menos uma regra na barra lateral para fazer a análise.")
            else:
                with st.spinner("Realizando auditoria do arquivo..."):
                    texto_completo = extrair_texto(arquivo_anexado)
                    if texto_completo:
                        # >>> NOVO PASSO: Limpa o texto antes da análise <<<
                        texto_completo = re.sub('minuta de documento', '', texto_completo, flags=re.IGNORECASE)
                        
                        texto_resolucao = texto_completo
                        texto_anexo = None
                        match_anexo = re.search(r'\n\s*ANEXO\s*\n', texto_completo, re.IGNORECASE)
                        if match_anexo:
                            texto_resolucao = texto_completo[:match_anexo.start()]
                            texto_anexo = texto_completo[match_anexo.end():]
                        
                        st.divider()
                        ok_res, falha_res = executar_auditoria(texto_resolucao, regras_selecionadas)
                        exibir_resultados("Resultado da Resolução Principal", ok_res, falha_res)
                        
                        st.divider()
                        if texto_anexo:
                            regras_para_anexo = ["Artigos (Numeração)", "Incisos (Pontuação)", "Siglas (Uso do travessão)"]
                            regras_a_rodar_no_anexo = [regra for regra in regras_para_anexo if regra in regras_selecionadas]
                            ok_anexo, falha_anexo = executar_auditoria(texto_anexo, regras_a_rodar_no_anexo)
                            exibir_resultados("Resultado do Anexo", ok_anexo, falha_anexo)
                        else:
                            st.info("Nenhuma seção 'ANEXO' foi encontrada para auditoria separada.")

# --- ABA 2: COLAR TEXTO ---
with tab2:
    st.write("Copie e cole o texto completo da minuta na caixa abaixo para análise.")
    texto_colado = st.text_area("Texto da Minuta:", height=300, label_visibility="collapsed")
    if st.button("Analisar Texto", type="primary", use_container_width=True, key="btn_analisar_texto"):
        if not regras_selecionadas:
            st.warning("Por favor, selecione pelo menos uma regra na barra lateral para fazer a análise.")
        elif not texto_colado:
            st.warning("Por favor, cole um texto na caixa acima para fazer a análise.")
        else:
            with st.spinner("Realizando auditoria do texto..."):
                texto_completo = texto_colado
                
                # >>> NOVO PASSO: Limpa o texto antes da análise <<<
                texto_completo = re.sub(r'\*?\s*MINUTA DE DOCUMENTO', '', texto_completo, flags=re.IGNORECASE)
                
                texto_resolucao = texto_completo
                texto_anexo = None
                match_anexo = re.search(r'\n\s*ANEXO\s*\n', texto_completo, re.IGNORECASE)
                if match_anexo:
                    texto_resolucao = texto_completo[:match_anexo.start()]
                    texto_anexo = texto_completo[match_anexo.end():]
                
                st.divider()
                ok_res, falha_res = executar_auditoria(texto_resolucao, regras_selecionadas)
                exibir_resultados("Resultado da Resolução Principal", ok_res, falha_res)
                
                st.divider()
                if texto_anexo:
                    regras_para_anexo = ["Artigos (Numeração)", "Incisos (Pontuação)", "Siglas (Uso do travessão)"]
                    regras_a_rodar_no_anexo = [regra for regra in regras_para_anexo if regra in regras_selecionadas]
                    ok_anexo, falha_anexo = executar_auditoria(texto_anexo, regras_a_rodar_no_anexo)
                    exibir_resultados("Resultado do Anexo", ok_anexo, falha_anexo)
                else:
                    st.info("Nenhuma seção 'ANEXO' foi encontrada para auditoria separada.")