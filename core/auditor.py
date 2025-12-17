import re
import html
from core import obter_regras, obter_regras_anexo

def executar_auditoria(texto_para_auditar, regras_dict):
    """Executa as regras e retorna lista de falhas formatada."""
    resultados = []
    if not texto_para_auditar: return []

    for nome_regra, funcao_auditoria in regras_dict.items():
        if nome_regra == "Anexo (Identificação)": continue
        try:
            resultado = funcao_auditoria(texto_para_auditar)
            
            # Normaliza o retorno para sempre ser um dicionário com status
            if isinstance(resultado, dict):
                status = resultado.get("status", "OK")
                detalhes = resultado.get("detalhe", [])
            else:
                # Caso alguma regra antiga retorne outra coisa
                status = "OK"
                detalhes = []

            if status in ["FALHA", "ALERTA"]:
                if not isinstance(detalhes, list): detalhes = [detalhes]
                resultados.append((nome_regra, detalhes, status))
                
        except Exception as e:
            resultados.append((nome_regra, [f"Erro interno: {e}"], "FALHA"))
    return resultados

def gerar_html_anotado(texto_original, lista_erros_com_contexto):
    """Gera o HTML com as marcações amarelas (marks)."""
    texto_html = html.escape(texto_original)
    erros_estruturados = []
    contador = 0
    
    # Desempacota: Nome, Detalhes, Contexto (Res/Anexo), Status
    for nome_regra, detalhes, contexto, status in lista_erros_com_contexto:
        for item_erro in detalhes:
            msg_exibicao = ""
            sugestao = None
            original = None
            span = None
            
            # Trata se o detalhe é um objeto rico (dict) ou string simples
            if isinstance(item_erro, dict):
                msg_exibicao = item_erro.get("mensagem", "")
                sugestao = item_erro.get("sugestao")
                original = item_erro.get("original")
                span = item_erro.get("span")
            else:
                msg_exibicao = str(item_erro)

            # Tenta limpar a mensagem se ela tiver "Trecho: '...'" duplicado
            match_trecho = re.search(r"Trecho: ['\"](.*?)['\"]", msg_exibicao, re.DOTALL)
            snippet_cru = None
            if match_trecho:
                snippet_cru = match_trecho.group(1)
                msg_exibicao = msg_exibicao.replace(match_trecho.group(0), "").strip()
            
            # Se não achou trecho na mensagem, usa o 'original' do objeto de erro
            if not snippet_cru and original:
                snippet_cru = original

            # Lógica de marcação no HTML
            trecho_encontrado = None
            if snippet_cru:
                # Remove reticências para busca exata
                snippet_busca = snippet_cru[:-3] if snippet_cru.endswith("...") else snippet_cru
                snippet_html = html.escape(snippet_busca)
                
                # Só marca se achar o trecho e ele não for muito curto (evita marcar letras soltas)
                if snippet_html in texto_html and len(snippet_html) > 2:
                    trecho_encontrado = snippet_html

            obj_erro = {
                "id": None,
                "regra": nome_regra,
                "mensagem": msg_exibicao,
                "contexto": contexto,
                "nivel": status,
                "tem_link": False,
                "correcao": None
            }

            if sugestao and original:
                obj_erro["correcao"] = {"original": original, "novo": sugestao, "span": span}

            if trecho_encontrado:
                contador += 1
                id_tag = f"erro_{contador}"
                obj_erro["id"] = id_tag
                obj_erro["tem_link"] = True
                # Insere a tag <mark> no HTML
                tag_mark = f'<mark id="{id_tag}" class="erro-highlight" title="{nome_regra}">{trecho_encontrado}</mark>'
                texto_html = texto_html.replace(trecho_encontrado, tag_mark, 1)
            
            erros_estruturados.append(obj_erro)
            
    return texto_html, erros_estruturados

def processar_minuta(texto_bruto: str):
    # 1. Normalização
    texto_completo = texto_bruto.replace('\r\n', '\n').replace('\r', '\n')
    if not texto_completo.strip(): return {"html": "", "erros": [], "tipo_documento": "N/A"}

    # 2. Definições e Regras
    texto_limpo = texto_completo 
    # Remove marcações de minuta para identificar o tipo
    texto_para_regras = re.sub(r'\*?\s*MINUTA DE DOCUMENTO', '', texto_completo, flags=re.IGNORECASE)
    
    # Obtém regras da Resolução
    regras_resolucao, tipo_doc = obter_regras(texto_para_regras)
    
    # Filtra para garantir que não pegou regras de anexo por engano (segurança)
    regras_resolucao = {k: v for k, v in regras_resolucao.items() if not k.startswith("Anexo")}

    # 3. Divisão do Texto (Resolução vs Anexo)
    texto_res = texto_limpo
    texto_anx = ""
    offset_anexo = 0
    match_anexo = re.search(r'\n\s*ANEXO', texto_limpo, re.IGNORECASE) # Regex simplificado para achar o corte
    
    if match_anexo:
        texto_res = texto_limpo[:match_anexo.start()] 
        texto_anx = texto_limpo[match_anexo.end():]
        offset_anexo = match_anexo.end()

    lista_final = []

    # 4. Auditoria Resolução (Executa as regras)
    falhas_res = executar_auditoria(texto_res, regras_resolucao)
    
    # Adiciona verificação estrutural básica do Anexo
    from core.regras.anexo import auditar_anexo # Import local ou garantir que está no topo
    res_anexo_id = auditar_anexo(texto_limpo)
    if res_anexo_id["status"] in ["FALHA", "ALERTA"]:
        falhas_res.append(("Estrutura do Anexo", res_anexo_id["detalhe"], res_anexo_id["status"]))

    # Formata falhas da resolução
    for nome, dets, status in falhas_res:
        lista_final.append((nome, dets, "Resolução", status))

    # 5. Auditoria do Anexo (Se existir)
    if texto_anx:
        texto_anexo_completo = "ANEXO" + texto_anx
        
        regras_anexo = obter_regras_anexo()

        falhas_anx = executar_auditoria(texto_anexo_completo, regras_anexo)
        
        # Ajusta os SPANS (índices) porque o anexo está deslocado no texto original
        falhas_anx_ajustadas = []
        for nome_regra, lista_detalhes, status in falhas_anx:
            detalhes_corrigidos = []
            for item in lista_detalhes:
                if isinstance(item, dict) and "span" in item:
                    # Soma o offset para o highlight bater certo no texto completo
                    novo_span = [item["span"][0] + offset_anexo, item["span"][1] + offset_anexo]
                    item_copia = item.copy()
                    item_copia["span"] = novo_span
                    detalhes_corrigidos.append(item_copia)
                else:
                    detalhes_corrigidos.append(item)
            falhas_anx_ajustadas.append((nome_regra, detalhes_corrigidos, status))

        for nome, dets, status in falhas_anx_ajustadas:
            lista_final.append((nome, dets, "Anexo", status))

    # 6. Geração do HTML Final
    html_final, lista_erros = gerar_html_anotado(texto_limpo, lista_final)

    return {"tipo_documento": tipo_doc, "html": html_final, "erros": lista_erros}