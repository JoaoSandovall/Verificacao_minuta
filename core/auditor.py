import re
import html
from core import obter_regras, obter_regras_anexo 
from core.regras.anexo import auditar_anexo 

def substituir_por_espacos(match):
    return " " * len(match.group(0))

def substituir_prefixo_minuta(match):
    texto_todo = match.group(0)
    palavra_chave = match.group(2) 
    inicio_palavra = match.start(2) - match.start(0)
    return (" " * inicio_palavra) + palavra_chave

def executar_auditoria(texto_para_auditar, regras_dict):
    
    resultados = []
    
    if not texto_para_auditar: 
        return []
    
    for nome_regra, funcao_auditoria in regras_dict.items():
    
        if nome_regra == "Anexo (Identificação)": continue
        try:
            resultado = funcao_auditoria(texto_para_auditar)
            if isinstance(resultado, dict):
                status = resultado.get("status", "OK")
                detalhes = resultado.get("detalhe", [])
            else:
                status = "OK"; detalhes = []
            if status in ["FALHA", "ALERTA"]:
                if not isinstance(detalhes, list): detalhes = [detalhes]
                resultados.append((nome_regra, detalhes, status))
        except Exception as e:
            resultados.append((nome_regra, [f"Erro: {e}"], "FALHA"))
    return resultados

def gerar_html_anotado(texto_original, lista_erros_com_contexto):
    
    erros_para_processar = []
    
    erros_estruturados_retorno = [] 
    
    contador = 0
    
    for nome_regra, detalhes, contexto, status in lista_erros_com_contexto:
        for item_erro in detalhes:
            
            contador += 1
            
            obj_erro_frontend = { "id": None,
                                 "regra": nome_regra, 
                                 "mensagem": "", 
                                 "contexto": contexto,
                                 "nivel": status, 
                                 "tem_link": False,
                                 "correcao": None 
                                 }
            
            msg = ""; span = None; sugestao = None; original = None
            
            if isinstance(item_erro, dict):
                msg = item_erro.get("mensagem", "")
                span = item_erro.get("span")
                sugestao = item_erro.get("sugestao")
                original = item_erro.get("original")
                
                if sugestao and original:
                    obj_erro_frontend["correcao"] = {"original": original, "novo": sugestao, "span": span}
            else:
                msg = str(item_erro)
            
            match_trecho = re.search(r"Trecho: ['\"](.*?)['\"]", msg, re.DOTALL)
            
            if match_trecho: 
                msg = msg.replace(match_trecho.group(0), "").strip()
            obj_erro_frontend["mensagem"] = msg

            if span and isinstance(span, (list, tuple)) and len(span) == 2:
                id_tag = f"erro_{contador}"
                obj_erro_frontend["id"] = id_tag
                obj_erro_frontend["tem_link"] = True
                erros_para_processar.append({ "start": span[0], "end": span[1], "id": id_tag, "title": f"{nome_regra}: {msg}" })
            erros_estruturados_retorno.append(obj_erro_frontend)

    erros_para_processar.sort(key=lambda x: x["start"])
    html_parts = []; cursor = 0
    for erro in erros_para_processar:
        start, end = erro["start"], erro["end"]

        if start < cursor:
            continue
        
        html_parts.append(html.escape(texto_original[cursor:start]))
        trecho_erro = html.escape(texto_original[start:end])
        mark_tag = f'<mark id="{erro["id"]}" class="erro-highlight" title="{html.escape(erro["title"])}">{trecho_erro}</mark>'
        html_parts.append(mark_tag)
        cursor = end
        
    html_parts.append(html.escape(texto_original[cursor:]))
    return "".join(html_parts), erros_estruturados_retorno

def processar_minuta(texto_bruto: str):
    texto_completo = texto_bruto.replace('\r\n', '\n').replace('\r', '\n')
    if not texto_completo.strip(): return {"html": "", "erros": [], "tipo_documento": "N/A"}

    texto_analise = texto_completo
    # Limpeza segura (não apaga \n)
    texto_analise = re.sub(r'^[\s\*]*MINUTA DE DOCUMENTO[^\n]*', substituir_por_espacos, texto_analise, flags=re.IGNORECASE | re.MULTILINE)
    texto_analise = re.sub(r'(MINUTA\s+(?:DE\s+)?)(RESOLUÇÃO|PORTARIA)', substituir_prefixo_minuta, texto_analise, flags=re.IGNORECASE)
    texto_analise = re.sub(r'Minuta\s+assinada\s+para\s+fins\s+de\s+visualização', substituir_por_espacos, texto_analise, flags=re.IGNORECASE)

    regras_resolucao, tipo_doc = obter_regras(texto_analise)
    regras_resolucao = {k: v for k, v in regras_resolucao.items() if not k.startswith("Anexo")}

    texto_res = texto_analise; texto_anx = ""; offset_anexo = 0
    match_anexo = re.search(r'\n\s*ANEXO', texto_analise, re.IGNORECASE) 
   
    if match_anexo:
        texto_res = texto_analise[:match_anexo.start()] 
        texto_anx = texto_analise[match_anexo.end():]
        offset_anexo = match_anexo.end()

    lista_final = []
    falhas_res = executar_auditoria(texto_res, regras_resolucao)
  
    try:
        res_anexo_id = auditar_anexo(texto_analise)
        
        if res_anexo_id["status"] in ["FALHA", "ALERTA"]:
            falhas_res.append(("Estrutura do Anexo", res_anexo_id["detalhe"], res_anexo_id["status"]))
    except ImportError: pass 

    for nome, dets, status in falhas_res:
        lista_final.append((nome, dets, "Resolução", status))

    if texto_anx:
        try:
            texto_anexo_completo = "ANEXO" + texto_anx
            regras_anexo = obter_regras_anexo()
            falhas_anx = executar_auditoria(texto_anexo_completo, regras_anexo)
            falhas_anx_ajustadas = []
            len_prefixo_anexo = len("ANEXO") 
            
            for nome_regra, lista_detalhes, status in falhas_anx:
                detalhes_corrigidos = []
                
                for item in lista_detalhes:
                    if isinstance(item, dict) and "span" in item:
                        ajuste = offset_anexo - len_prefixo_anexo
                        novo_span = [item["span"][0] + ajuste, item["span"][1] + ajuste]
                        item_copia = item.copy(); item_copia["span"] = novo_span
                        detalhes_corrigidos.append(item_copia)
                        
                    else: 
                        detalhes_corrigidos.append(item)
                falhas_anx_ajustadas.append((nome_regra, detalhes_corrigidos, status))
                
            for nome, dets, status in falhas_anx_ajustadas:
                lista_final.append((nome, dets, "Anexo", status))
        except Exception: pass

    html_final, lista_erros = gerar_html_anotado(texto_completo, lista_final)
    return {"tipo_documento": tipo_doc, "html": html_final, "erros": lista_erros}