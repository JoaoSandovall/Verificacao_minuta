from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import html

# Importações do Core
from core import obter_regras
from core.regras.anexo import auditar_anexo
from core.regras import comuns

app = FastAPI(title="Auditor de Minutas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MinutaInput(BaseModel):
    texto: str

def executar_auditoria(texto_para_auditar, regras_dict):
    resultados_falha = []
    if not texto_para_auditar: return []

    for nome_regra, funcao_auditoria in regras_dict.items():
        if nome_regra == "Anexo (Identificação)": continue
        try:
            resultado = funcao_auditoria(texto_para_auditar)
            if resultado["status"] == "FALHA":
                # O detalhe pode ser uma lista de strings OU uma lista de dicionários
                detalhes = resultado.get("detalhe", ["Erro genérico."])
                if not isinstance(detalhes, list): detalhes = [detalhes]
                resultados_falha.append((nome_regra, detalhes))
        except Exception as e:
            resultados_falha.append((nome_regra, [f"Erro interno: {e}"])) 
    return resultados_falha

def gerar_html_anotado(texto_original, lista_erros_com_contexto):
    texto_html = html.escape(texto_original)
    erros_estruturados = []
    contador = 0
    
    for nome_regra, detalhes, contexto in lista_erros_com_contexto:
        for item_erro in detalhes:
            
            # --- LÓGICA DE LIMPEZA (AQUI ESTAVA O ERRO VISUAL) ---
            msg_exibicao = ""
            sugestao = None
            original = None
            
            # Verifica se o erro é o novo formato (Dicionário) ou o antigo (String)
            if isinstance(item_erro, dict):
                # É um erro "inteligente" (com correção)
                msg_exibicao = item_erro.get("mensagem", "")
                sugestao = item_erro.get("sugestao")
                original = item_erro.get("original")
            else:
                # É um erro simples (apenas texto)
                msg_exibicao = str(item_erro)

            # Tenta achar o trecho para grifar (Highlight)
            # 1. Pela tag técnica "Trecho:"
            match_trecho = re.search(r"Trecho: ['\"](.*?)['\"]", msg_exibicao, re.DOTALL)
            
            snippet_cru = None
            if match_trecho:
                snippet_cru = match_trecho.group(1)
                # Remove o marcador técnico da mensagem que vai para a tela
                msg_exibicao = msg_exibicao.replace(match_trecho.group(0), "").strip()
            
            # 2. Se não achou, tenta usar o 'original' do dicionário
            if not snippet_cru and original:
                snippet_cru = original

            # Processa o highlight no HTML
            trecho_encontrado = None
            if snippet_cru:
                snippet_busca = snippet_cru[:-3] if snippet_cru.endswith("...") else snippet_cru
                snippet_html = html.escape(snippet_busca)
                
                # Verifica se existe no texto para poder grifar
                if snippet_html in texto_html and len(snippet_html) > 2:
                    trecho_encontrado = snippet_html

            # Monta o objeto final para o Frontend
            obj_erro = {
                "id": None,
                "regra": nome_regra,
                "mensagem": msg_exibicao, # Agora vai o texto limpo, sem { }
                "contexto": contexto,
                "tem_link": False,
                "correcao": None
            }

            if sugestao and original:
                obj_erro["correcao"] = {
                    "original": original,
                    "novo": sugestao
                }

            if trecho_encontrado:
                contador += 1
                id_tag = f"erro_{contador}"
                obj_erro["id"] = id_tag
                obj_erro["tem_link"] = True
                
                # Adiciona a marcação amarela no texto
                tag_mark = f'<mark id="{id_tag}" class="erro-highlight" title="{nome_regra}">{trecho_encontrado}</mark>'
                # Substitui apenas a primeira ocorrência para não quebrar o HTML
                texto_html = texto_html.replace(trecho_encontrado, tag_mark, 1)
            
            erros_estruturados.append(obj_erro)
            
    return texto_html, erros_estruturados

@app.post("/auditar")
async def auditar_minuta(dados: MinutaInput):
    texto_completo = dados.texto
    if not texto_completo.strip(): return {"html": "", "erros": [], "tipo": "N/A"}

    texto_limpo = re.sub(r'\*?\s*MINUTA DE DOCUMENTO', '', texto_completo, flags=re.IGNORECASE)
    regras_detectadas, tipo_doc = obter_regras(texto_limpo)
    
    regras_resolucao = {k: v for k, v in regras_detectadas.items() if not k.startswith("Anexo")}
    regras_anexo = {k: v for k, v in regras_detectadas.items() if k.startswith("Anexo") and k != "Anexo (Identificação)"}
    
    regras_anexo.update({
        "Artigos (Formato)": comuns.auditar_numeracao_artigos,
        "Parágrafos (Espaçamento)": comuns.auditar_espacamento_paragrafo,
        "Siglas": comuns.auditar_uso_siglas,
        "Incisos (Pontuação)": comuns.auditar_pontuacao_incisos,
        "Alíneas (Pontuação)": comuns.auditar_pontuacao_alineas
    })

    texto_res = texto_limpo
    texto_anx = ""
    match_anexo = re.search(r'\n\s*ANEXO\s*$', texto_limpo, re.MULTILINE)
    
    if match_anexo:
        texto_res = texto_limpo[:match_anexo.start()].strip()
        texto_anx = texto_limpo[match_anexo.end():].strip()
        if not texto_anx: texto_anx = texto_limpo[match_anexo.end():].strip()

    lista_final = []

    falhas_res = executar_auditoria(texto_res, regras_resolucao)
    res_anexo_id = auditar_anexo(texto_limpo)
    if res_anexo_id["status"] == "FALHA":
        falhas_res.append(("Estrutura do Anexo", res_anexo_id["detalhe"]))

    for nome, dets in falhas_res:
        lista_final.append((nome, dets, "Resolução"))

    if texto_anx:
        falhas_anx = executar_auditoria(texto_anx, regras_anexo)
        for nome, dets in falhas_anx:
            lista_final.append((nome, dets, "Anexo"))

    html_final, lista_erros = gerar_html_anotado(texto_limpo, lista_final)

    return {
        "tipo_documento": tipo_doc,
        "html": html_final,
        "erros": lista_erros
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")