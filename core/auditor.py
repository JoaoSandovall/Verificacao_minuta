import re
import html
from core import obter_regras
from core.regras.anexo import auditar_anexo
from core.regras import comuns

def executar_auditoria(texto_para_auditar, regras_dict):
    resultados_falha = []
    if not texto_para_auditar: return []

    for nome_regra, funcao_auditoria in regras_dict.items():
        if nome_regra == "Anexo (Identificação)": continue
        try:
            resultado = funcao_auditoria(texto_para_auditar)
            if resultado["status"] == "FALHA":
                detalhes = resultado.get("detalhe", ["Erro genérico."])
                if not isinstance(detalhes, list): detalhes = [detalhes]
                resultados_falha.append((nome_regra, detalhes))
        except Exception as e:
            resultados_falha.append((nome_regra, [f"Erro interno: {e}"])) 
    return resultados_falha

def gerar_html_anotado(texto_original, lista_erros_com_contexto):
    """Gera o HTML com as marcações (<mark>) e a lista estruturada de erros."""
    texto_html = html.escape(texto_original)
    erros_estruturados = []
    contador = 0
    
    for nome_regra, detalhes, contexto in lista_erros_com_contexto:
        for item_erro in detalhes:
            
            msg_exibicao = ""
            sugestao = None
            original = None
            span = None
            
            if isinstance(item_erro, dict):
                msg_exibicao = item_erro.get("mensagem", "")
                sugestao = item_erro.get("sugestao")
                original = item_erro.get("original")
                span = item_erro.get("span")
            else:
                msg_exibicao = str(item_erro)

            match_trecho = re.search(r"Trecho: ['\"](.*?)['\"]", msg_exibicao, re.DOTALL)
            
            snippet_cru = None
            if match_trecho:
                snippet_cru = match_trecho.group(1)
                msg_exibicao = msg_exibicao.replace(match_trecho.group(0), "").strip()
            
            if not snippet_cru and original:
                snippet_cru = original

            trecho_encontrado = None
            if snippet_cru:
                snippet_busca = snippet_cru[:-3] if snippet_cru.endswith("...") else snippet_cru
                snippet_html = html.escape(snippet_busca)
                if snippet_html in texto_html and len(snippet_html) > 2:
                    trecho_encontrado = snippet_html

            obj_erro = {
                "id": None,
                "regra": nome_regra,
                "mensagem": msg_exibicao,
                "contexto": contexto,
                "tem_link": False,
                "correcao": None
            }

            if sugestao and original:
                obj_erro["correcao"] = {
                    "original": original,
                    "novo": sugestao,
                    "span": span
                }

            if trecho_encontrado:
                contador += 1
                id_tag = f"erro_{contador}"
                obj_erro["id"] = id_tag
                obj_erro["tem_link"] = True
                tag_mark = f'<mark id="{id_tag}" class="erro-highlight" title="{nome_regra}">{trecho_encontrado}</mark>'
                texto_html = texto_html.replace(trecho_encontrado, tag_mark, 1)
            
            erros_estruturados.append(obj_erro)
            
    return texto_html, erros_estruturados

def processar_minuta(texto_bruto: str):
    
    # 1. Normalização de quebras de linha (CRUCIAL para manter sincronia com JS)
    texto_completo = texto_bruto.replace('\r\n', '\n').replace('\r', '\n')
    
    if not texto_completo.strip():
        return {"html": "", "erros": [], "tipo_documento": "N/A"}

    # 2. Texto base para auditoria
    texto_limpo = texto_completo 
    
    # 3. Detecção de regras (versão sem cabeçalho para não confundir regex de identificação)
    texto_para_regras = re.sub(r'\*?\s*MINUTA DE DOCUMENTO', '', texto_completo, flags=re.IGNORECASE)
    regras_detectadas, tipo_doc = obter_regras(texto_para_regras)
    
    # Separação das Regras
    regras_resolucao = {k: v for k, v in regras_detectadas.items() if not k.startswith("Anexo")}
    regras_anexo = {k: v for k, v in regras_detectadas.items() if k.startswith("Anexo") and k != "Anexo (Identificação)"}
    
    # Injeta regras comuns no contexto do anexo
    regras_anexo.update({
        "Artigos (Formato)": comuns.auditar_numeracao_artigos,
        "Parágrafos (Espaçamento)": comuns.auditar_espacamento_paragrafo,
        "Siglas": comuns.auditar_uso_siglas,
        "Incisos (Pontuação)": comuns.auditar_pontuacao_incisos,
        "Alíneas (Pontuação)": comuns.auditar_pontuacao_alineas
    })

    # 4. Divisão do Texto (SEM STRIP para não perder a contagem de índices)
    texto_res = texto_limpo
    texto_anx = ""
    offset_anexo = 0
    
    match_anexo = re.search(r'\n\s*ANEXO\s*$', texto_limpo, re.MULTILINE)
    
    if match_anexo:
        texto_res = texto_limpo[:match_anexo.start()] 
        texto_anx = texto_limpo[match_anexo.end():]
        offset_anexo = match_anexo.end()

    lista_final = []

    # Audita a Resolução
    falhas_res = executar_auditoria(texto_res, regras_resolucao)
    
    # Valida estrutura macro do Anexo
    res_anexo_id = auditar_anexo(texto_limpo)
    if res_anexo_id["status"] == "FALHA":
        falhas_res.append(("Estrutura do Anexo", res_anexo_id["detalhe"]))

    for nome, dets in falhas_res:
        lista_final.append((nome, dets, "Resolução"))

    # Audita o conteúdo do Anexo (com correção de offset)
    if texto_anx:
        falhas_anx = executar_auditoria(texto_anx, regras_anexo)
        
        # Ajusta os índices somando o offset
        falhas_anx_ajustadas = []
        for nome_regra, lista_detalhes in falhas_anx:
            detalhes_corrigidos = []
            for item in lista_detalhes:
                # Se o erro tem coordenadas (span), somamos o offset do anexo
                if isinstance(item, dict) and "span" in item:
                    novo_span = [item["span"][0] + offset_anexo, item["span"][1] + offset_anexo]
                    item_copia = item.copy()
                    item_copia["span"] = novo_span
                    detalhes_corrigidos.append(item_copia)
                else:
                    detalhes_corrigidos.append(item)
            falhas_anx_ajustadas.append((nome_regra, detalhes_corrigidos))

        for nome, dets in falhas_anx_ajustadas:
            lista_final.append((nome, dets, "Anexo"))

    # Gera HTML final
    html_final, lista_erros = gerar_html_anotado(texto_limpo, lista_final)

    return {
        "tipo_documento": tipo_doc,
        "html": html_final,
        "erros": lista_erros
    }