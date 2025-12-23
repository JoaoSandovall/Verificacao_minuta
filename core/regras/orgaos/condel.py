import re
from core.regras import resolucao

def _limpar_para_comparar(texto):
    """Remove pontuação, traços e espaços extras para comparar apenas o texto."""
    if not texto: return ""
    # Remove tudo que não for letra ou número
    return re.sub(r'[^A-Z0-9]', '', texto.upper())

def auditar_cabecalho_condel(texto_completo):
    linhas = [l.strip() for l in texto_completo.strip().split('\n') if l.strip()]
    if len(linhas) < 3: return {"status": "FALHA", "detalhe": ["Cabeçalho incompleto."]}
    
    # Verifica apenas palavras-chave para evitar erro por detalhe
    erros = []
    if "MINISTÉRIO" not in linhas[0].upper(): erros.append("Linha 1 incorreta.")
    if "CONSELHO DELIBERATIVO" not in linhas[2].upper(): erros.append("Linha 3 incorreta.")
    if erros: return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Cabeçalho OK."}

def auditar_epigrafe_condel(texto_completo):
    padrao = re.compile(
        r"(MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO (?:CONDEL(?:/SUDECO|/SUDENE|/SUDAM)?|COARIDE) N[º°ᵒ] "
        r"(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+(\w+|xx|XX)\s+DE\s+(\d{4})",
        re.IGNORECASE
    )
    match = padrao.search(texto_completo)
    if match:
        conteudo = match.group(0)
        # Verifica maiúsculas ignorando símbolos
        limpo = re.sub(r'[^A-Za-z]', '', conteudo)
        if not limpo.isupper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "A epígrafe deve estar totalmente em MAIÚSCULAS.",
                    "original": conteudo,
                    "sugestao": conteudo.upper(),
                    "span": match.span(),
                    "tipo": "fixable"
                }
            }
        return {"status": "OK", "detalhe": "Epígrafe correta."}
    return {"status": "ALERTA", "detalhe": "Padrão 'RESOLUÇÃO CONDEL... Nᵒ' não encontrado."}

def auditar_preambulo_condel(texto_completo):
    # Mapa de autoridades esperadas
    autoridades_map = {
        "SUDECO": "O PRESIDENTE DO CONSELHO DELIBERATIVO DO DESENVOLVIMENTO DO CENTRO-OESTE — CONDEL/SUDECO",
        "SUDAM": "O PRESIDENTE DO CONSELHO DELIBERATIVO DO DESENVOLVIMENTO DA AMAZÔNIA — CONDEL/SUDAM",
        "SUDENE": "O PRESIDENTE DO CONSELHO DELIBERATIVO DO DESENVOLVIMENTO DO NORDESTE — CONDEL/SUDENE"
    }
    
    # Função auxiliar interna para limpeza (remove pontuação e espaços para comparação)
    def limpar_para_validar(t):
        if not t: return ""
        # Remove tudo que não for letra ou número (ignora traços, pontos, barras)
        return re.sub(r'[^A-Z0-9]', '', t.upper())

    # Regex ajustado:
    # 1. Procura "O PRESIDENTE DO CONSELHO..."
    # 2. Tenta capturar até "CONDEL/SIGLA" (aceitando barra ou traço)
    # 3. OU para antes de ", no uso" (âncora segura)
    # 4. OU para na primeira vírgula (fallback)
    match_linha = re.search(
        r"(O PRESIDENTE DO CONSELHO.*?(?:CONDEL[/\-](?:SUDECO|SUDAM|SUDENE)|(?=\s*,\s*no uso)|(?=\s*,)))", 
        texto_completo, 
        re.IGNORECASE | re.DOTALL
    )

    erros = []

    if match_linha:
        texto_encontrado = match_linha.group(1).strip()
        span_encontrado = match_linha.span(1)
        
        # Identificação da Sigla (busca palavras-chave no texto encontrado)
        texto_upper = texto_encontrado.upper()
        sigla = None
        if "CENTRO-OESTE" in texto_upper or "SUDECO" in texto_upper: sigla = "SUDECO"
        elif "AMAZÔNIA" in texto_upper or "SUDAM" in texto_upper: sigla = "SUDAM"
        elif "NORDESTE" in texto_upper or "SUDENE" in texto_upper: sigla = "SUDENE"
        
        if sigla:
            texto_esperado = autoridades_map[sigla]
            
            # Validação 1: CONTEÚDO (Ignora formatação, traços e espaços)
            if limpar_para_validar(texto_encontrado) != limpar_para_validar(texto_esperado):
                erros.append({
                    "mensagem": f"Autoridade incorreta ou incompleta para {sigla}.<br>Esperado o padrão oficial.",
                    "original": texto_encontrado,
                    "span": span_encontrado,
                    "tipo": "highlight"
                })
            else:
                # Validação 2: FORMATAÇÃO (Verifica Maiúsculas rigorosamente)
                # Removemos números e símbolos para checar apenas letras
                apenas_letras = re.sub(r'[^A-Za-zÀ-Úá-ú]', '', texto_encontrado)
                if not apenas_letras.isupper():
                    erros.append({
                        "mensagem": "O preâmbulo deve estar totalmente em MAIÚSCULAS.",
                        "original": texto_encontrado,
                        "span": span_encontrado,
                        "tipo": "highlight"
                    })
        else:
            # Achou o início, mas não sabe de qual órgão é
            erros.append({
                "mensagem": "Autoridade identificada, mas a sigla (SUDECO/SUDAM/SUDENE) não foi reconhecida no texto.",
                "original": texto_encontrado,
                "span": span_encontrado,
                "tipo": "highlight"
            })
    else:
        erros.append("Início do preâmbulo ('O PRESIDENTE DO CONSELHO...') não encontrado.")
     
    # Verifica o fecho do preâmbulo (resolve/resolveu)
    erros_fecho = resolucao.verificar_fecho_preambulo(texto_completo)
    if erros_fecho: erros.extend(erros_fecho)

    if erros: return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo correto."}