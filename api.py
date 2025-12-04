from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import html
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
                detalhes = resultado.get("detalhe", ["Erro genérico."])
                if not isinstance(detalhes, list): detalhes = [str(detalhes)]
                else: detalhes = [str(d) for d in detalhes]
                resultados_falha.append((nome_regra, detalhes))
        except Exception as e:
            resultados_falha.append((nome_regra, [f"Erro interno: {e}"])) 
    return resultados_falha

def gerar_html_anotado(texto_original, lista_erros_com_contexto):
    texto_html = html.escape(texto_original)
    erros_estruturados = []
    contador = 0
    
    for nome_regra, detalhes, contexto in lista_erros_com_contexto:
        for msg in detalhes:
            # CORREÇÃO: re.DOTALL permite pegar trechos com quebra de linha (\n)
            match_trecho = re.search(r"Trecho: ['\"](.*?)['\"]", msg, re.DOTALL)
            
            trecho_encontrado = None
            snippet_cru = None

            if match_trecho:
                snippet_cru = match_trecho.group(1)
                # Remove reticências se houver
                snippet_busca = snippet_cru[:-3] if snippet_cru.endswith("...") else snippet_cru
                snippet_html = html.escape(snippet_busca)
                
                # Busca no texto
                if snippet_html in texto_html and len(snippet_html) > 2:
                    trecho_encontrado = snippet_html

            # Limpa a mensagem para exibição (remove o trecho técnico)
            trecho_remove = f"Trecho: '{snippet_cru}'" if snippet_cru else ""
            msg_limpa = msg.replace(trecho_remove, "").strip()
            
            item_erro = {
                "id": None,
                "regra": nome_regra,
                "mensagem": msg_limpa,
                "contexto": contexto,
                "tem_link": False
            }

            if trecho_encontrado:
                contador += 1
                id_tag = f"erro_{contador}"
                item_erro["id"] = id_tag
                item_erro["tem_link"] = True
                
                # Marca apenas a primeira ocorrência não marcada
                tag_mark = f'<mark id="{id_tag}" class="erro-highlight" title="{nome_regra}">{trecho_encontrado}</mark>'
                texto_html = texto_html.replace(trecho_encontrado, tag_mark, 1)
            
            erros_estruturados.append(item_erro)
            
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