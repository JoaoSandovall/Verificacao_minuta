# import streamlit as st
# import docx
# import PyPDF2
# from io import BytesIO
# import re
# import html

# # Importações do Core
# from core import obter_regras
# from core.regras.anexo import auditar_anexo
# from core.regras import comuns

# # --- CONFIGURAÇÃO DA PÁGINA ---
# st.set_page_config(page_title="Auditor de Minutas", layout="wide")

# # --- ESTILOS CSS (Visual Profissional) ---
# st.markdown("""
#     <style>
#     /* Visual de Folha de Papel */
#     .documento-visual {
#         background-color: #ffffff;
#         padding: 50px;
#         border: 1px solid #ddd;
#         box-shadow: 0 4px 8px rgba(0,0,0,0.1);
#         font-family: 'Times New Roman', serif;
#         font-size: 18px;
#         line-height: 1.6;
#         color: #2c3e50;
#         white-space: pre-wrap; /* Mantém quebras de linha */
#         border-radius: 5px;
#     }
    
#     /* Destaque de Erro (Highlight) */
#     mark.erro-highlight {
#         background-color: #ffcccc;
#         color: #990000;
#         border-bottom: 2px solid #ff0000;
#         padding: 2px 0;
#         font-weight: bold;
#     }

#     /* Card de Erro na Lateral */
#     .erro-card {
#         background-color: #fff0f0;
#         border-left: 5px solid #ff4444;
#         padding: 15px;
#         margin-bottom: 15px;
#         border-radius: 5px;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.1);
#     }
    
#     .erro-titulo {
#         font-weight: bold;
#         color: #cc0000;
#         font-size: 14px;
#         margin-bottom: 5px;
#     }
    
#     .erro-desc {
#         font-size: 13px;
#         color: #333;
#     }

#     /* Botão "Ver no Texto" (Link Âncora) */
#     a.btn-ir {
#         display: inline-block;
#         margin-top: 8px;
#         padding: 4px 10px;
#         background-color: #ff4444;
#         color: white !important;
#         text-decoration: none;
#         border-radius: 4px;
#         font-size: 12px;
#     }
#     a.btn-ir:hover { background-color: #cc0000; }
    
#     /* Botão Voltar Flutuante (Opcional) */
#     .stButton button {
#         width: 100%;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # --- FUNÇÕES AUXILIARES ---

# def extrair_texto(arquivo_enviado):
#     try:
#         if arquivo_enviado.type == "text/plain":
#             return arquivo_enviado.read().decode("utf-8")
#         elif arquivo_enviado.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#             doc = docx.Document(BytesIO(arquivo_enviado.read()))
#             return "\n".join([para.text for para in doc.paragraphs])
#         elif arquivo_enviado.type == "application/pdf":
#             texto = ""
#             leitor_pdf = PyPDF2.PdfReader(BytesIO(arquivo_enviado.read()))
#             for pagina in leitor_pdf.pages:
#                  page_text = pagina.extract_text()
#                  if page_text: texto += page_text + "\n"
#             return texto
#     except Exception as e:
#         st.error(f"Erro ao ler arquivo: {e}")
#         return None

# def executar_auditoria(texto_para_auditar, regras_dict):
#     """Roda as regras e retorna listas limpas."""
#     resultados_ok = []
#     resultados_falha = []
    
#     if not texto_para_auditar: return [], []

#     for nome_regra, funcao_auditoria in regras_dict.items():
#         if nome_regra == "Anexo (Identificação)": continue # Tratado à parte

#         try:
#             resultado = funcao_auditoria(texto_para_auditar)
#             if resultado["status"] == "FALHA":
#                 detalhes = resultado.get("detalhe", ["Erro genérico."])
#                 if not isinstance(detalhes, list): detalhes = [str(detalhes)]
#                 else: detalhes = [str(d) for d in detalhes]
#                 resultados_falha.append((nome_regra, detalhes))
#             else:
#                 resultados_ok.append((nome_regra, resultado.get("detalhe", "")))
#         except Exception as e:
#             resultados_falha.append((nome_regra, [f"Erro interno: {e}"])) 

#     return resultados_ok, resultados_falha

# def gerar_html_anotado(texto_original, lista_erros):
#     """
#     Transforma o texto puro em HTML com marcações <mark> onde houver erros.
#     Usa o padrão "Trecho: '...'" das mensagens de erro para localizar o texto.
#     """
#     # 1. Escapar HTML do texto original para evitar injeção ou quebra de layout
#     texto_html = html.escape(texto_original)
    
#     mapa_erros_visual = [] # Lista de dicionários para montar o painel lateral
#     contador = 0
    
#     # Vamos processar erro por erro
#     for nome_regra, detalhes in lista_erros:
#         for msg in detalhes:
#             # Tenta extrair o trecho citado na mensagem
#             match_trecho = re.search(r"Trecho: ['\"](.*?)['\"]", msg)
            
#             trecho_encontrado = None
#             if match_trecho:
#                 snippet_cru = match_trecho.group(1)
#                 # Remove reticências se houver, para busca exata
#                 if snippet_cru.endswith("..."): snippet_cru = snippet_cru[:-3]
                
#                 # Escapa o snippet também para bater com o texto_html
#                 snippet_html = html.escape(snippet_cru)
                
#                 # Verifica se existe no texto
#                 if snippet_html in texto_html and len(snippet_html) > 3:
#                     trecho_encontrado = snippet_html

#             item_erro = {
#                 "regra": nome_regra,
#                 "msg": msg.replace(f"Trecho: '{match_trecho.group(1) if match_trecho else ''}'", "").strip(), # Limpa msg
#                 "id": None
#             }

#             if trecho_encontrado:
#                 contador += 1
#                 id_tag = f"erro_{contador}"
#                 item_erro["id"] = id_tag
                
#                 # Cria a marcação HTML
#                 # Nota: replace(..., 1) substitui apenas a primeira ocorrência encontrada para este erro específico
#                 tag_mark = f'<mark id="{id_tag}" class="erro-highlight" title="{nome_regra}">{trecho_encontrado}</mark>'
#                 texto_html = texto_html.replace(trecho_encontrado, tag_mark, 1)
            
#             mapa_erros_visual.append(item_erro)
            
#     return texto_html, mapa_erros_visual

# # --- GERENCIAMENTO DE ESTADO (SESSION STATE) ---
# if 'tela_atual' not in st.session_state:
#     st.session_state.tela_atual = 'editor' # 'editor' ou 'revisao'
# if 'texto_cache' not in st.session_state:
#     st.session_state.texto_cache = ""

# def ir_para_revisao():
#     st.session_state.tela_atual = 'revisao'

# def ir_para_editor():
#     st.session_state.tela_atual = 'editor'

# # --- TELA 1: EDITOR (Entrada de Dados) ---
# if st.session_state.tela_atual == 'editor':
#     st.title("📝 Auditor de Minutas")
#     st.markdown("Cole sua minuta abaixo para validar a formatação (CONDEL/CEG).")
    
#     col_txt, col_upload = st.tabs(["✍️ Colar Texto", "📂 Carregar Arquivo"])
    
#     texto_input = ""
    
#     with col_txt:
#         # Se já tiver texto no cache, preenche a area
#         val_area = st.text_area("Minuta:", value=st.session_state.texto_cache, height=400, label_visibility="collapsed")
#         if st.button("Analisar Texto", type="primary"):
#             if val_area.strip():
#                 st.session_state.texto_cache = val_area
#                 ir_para_revisao()
#                 st.rerun()
#             else:
#                 st.warning("O texto está vazio.")

#     with col_upload:
#         arq = st.file_uploader("Formatos: .txt, .docx, .pdf", type=['txt', 'docx', 'pdf'])
#         if arq and st.button("Analisar Arquivo"):
#             txt_ext = extrair_texto(arq)
#             if txt_ext:
#                 st.session_state.texto_cache = txt_ext
#                 ir_para_revisao()
#                 st.rerun()

# # --- TELA 2: REVISÃO (Visualização Rica) ---
# else:
#     # Header de Navegação
#     c_voltar, c_titulo = st.columns([1, 6])
#     with c_voltar:
#         st.button("⬅️ Editar", on_click=ir_para_editor)
#     with c_titulo:
#         st.subheader("Resultado da Análise")

#     texto_completo = st.session_state.texto_cache
    
#     # --- PROCESSAMENTO DO BACKEND ---
#     # 1. Limpeza e Identificação
#     texto_limpo = re.sub(r'\*?\s*MINUTA DE DOCUMENTO', '', texto_completo, flags=re.IGNORECASE)
#     regras_detectadas, tipo_doc = obter_regras(texto_limpo)
    
#     # 2. Separação de Escopos
#     regras_resolucao = {k: v for k, v in regras_detectadas.items() if not k.startswith("Anexo")}
#     regras_anexo = {k: v for k, v in regras_detectadas.items() if k.startswith("Anexo") and k != "Anexo (Identificação)"}
    
#     # Injeção manual de regras comuns no Anexo (sua regra de negócio)
#     regras_anexo.update({
#         "Artigos": comuns.auditar_numeracao_artigos,
#         "Parágrafos": comuns.auditar_espacamento_paragrafo,
#         "Siglas": comuns.auditar_uso_siglas,
#         "Incisos": comuns.auditar_pontuacao_incisos,
#         "Alíneas": comuns.auditar_pontuacao_alineas
#     })

#     # 3. Execução das Auditorias
#     # Resolução Principal
#     texto_res = texto_limpo
#     texto_anx = ""
#     match_anexo = re.search(r'^\s*ANEXO\s*$', texto_limpo, re.MULTILINE)
    
#     if match_anexo:
#         texto_res = texto_limpo[:match_anexo.start()].strip()
#         texto_anx = texto_limpo[match_anexo.end():].strip()

#     _, falhas_res = executar_auditoria(texto_res, regras_resolucao)
    
#     # Validação da Seção Anexo
#     res_anexo_id = auditar_anexo(texto_limpo)
#     if res_anexo_id["status"] == "FALHA":
#         falhas_res.append(("Estrutura", res_anexo_id["detalhe"]))

#     # Validação do Conteúdo do Anexo
#     falhas_anx = []
#     if texto_anx:
#         _, falhas_anx = executar_auditoria(texto_anx, regras_anexo)

#     # Combina todas as falhas para gerar o visual
#     todas_falhas = falhas_res + falhas_anx

#     # --- RENDERIZAÇÃO VISUAL ---
    
#     # Gera o HTML com <mark> e o mapa de erros
#     html_doc, lista_erros_visual = gerar_html_anotado(texto_limpo, todas_falhas)

#     col_doc, col_painel = st.columns([2, 1], gap="medium")

#     with col_doc:
#         st.markdown(f"**Documento Visualizado:** Resolução {tipo_doc}")
#         # Injeta o HTML estilizado
#         st.markdown(f'<div class="documento-visual">{html_doc}</div>', unsafe_allow_html=True)

#     with col_painel:
#         st.markdown("### 🛠️ Painel de Correção")
        
#         if not lista_erros_visual:
#             st.success("Tudo certo! Nenhum erro encontrado. ✅")
#         else:
#             qtd = len(lista_erros_visual)
#             st.warning(f"Encontrados **{qtd}** problemas.")
            
#             # Renderiza os cards
#             for item in lista_erros_visual:
#                 botao_html = ""
#                 if item['id']:
#                     # O href com #id faz o navegador rolar até o <mark id="...">
#                     botao_html = f'<a href="#{item["id"]}" class="btn-ir" target="_self">🎯 Ver no Texto</a>'
                
#                 card_html = f"""
#                 <div class="erro-card">
#                     <div class="erro-titulo">{item['regra']}</div>
#                     <div class="erro-desc">{item['msg']}</div>
#                     {botao_html}
#                 </div>
#                 """
#                 st.markdown(card_html, unsafe_allow_html=True)