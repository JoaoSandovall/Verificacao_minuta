import re
from core.regras import resolucao
from core.utils import limpar_para_validar

def auditar_cabecalho_cnrh(texto_completo):
    """
    Cabeçalho do CNRH:
    MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL
    CONSELHO NACIONAL DE RECURSOS HÍDRICOS
    """
    linhas = [l.strip() for l in texto_completo.strip().split('\n') if l.strip()]
    
    
    if len(linhas) < 2: 
        return {"status": "FALHA", "detalhe": ["Cabeçalho incompleto. Esperado: Ministério e Conselho."]}
    
    erros = []
    
    # Validação 1
    if "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL" not in linhas[0].upper():
        erros.append(f"Linha 1 incorreta.<br>Esperado: MINISTÉRIO DA INTEGRAÇÃO...<br>Encontrado: {linhas[0]}")
    
    # Validação 2
    if "CONSELHO NACIONAL DE RECURSOS HÍDRICOS" not in linhas[1].upper():
        erros.append(f"Linha 2 incorreta.<br>Esperado: CONSELHO NACIONAL DE RECURSOS HÍDRICOS<br>Encontrado: {linhas[1]}")
        
    if erros: return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Cabeçalho OK."}

def auditar_epigrafe_cnrh(texto_completo):
    
    padrao = re.compile(
        r"(MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO CNRH N[º°ᵒ] "
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
                    "span": match.span(),
                    "tipo": "highlight" 
                }
            }
        return {"status": "OK", "detalhe": "Epígrafe correta."}
    
    return {"status": "ALERTA", "detalhe": "Padrão 'RESOLUÇÃO CNRH ... Nᵒ' não encontrado."}

def auditar_preambulo_cnrh(texto_completo):
    
    autoridade_esperada = "O PRESIDENTE DO CONSELHO NACIONAL DE RECURSOS HÍDRICOS — CNRH"

    # Regex ancora na vírgula ou em "no uso"
    match_linha = re.search(
        r"(O PRESIDENTE DO CONSELHO NACIONAL DE RECURSOS HÍDRICOS.*?(?:CNRH|(?=\s*,\s*no uso)|(?=\s*,)))", 
        texto_completo, 
        re.IGNORECASE | re.DOTALL
    )

    erros = []

    if match_linha:
        texto_encontrado = match_linha.group(1).strip()
        span_encontrado = match_linha.span(1)
        
        # Validação 1: Verifica autoridade
        if limpar_para_validar(texto_encontrado) != limpar_para_validar(autoridade_esperada):
            erros.append({
                "mensagem": f"Autoridade incorreta.<br>Esperado: <em>'{autoridade_esperada}'</em>",
                "original": texto_encontrado,
                "span": span_encontrado,
                "tipo": "highlight"
            })
        else:
            # Validação 2: FORMATAÇ
            apenas_letras = re.sub(r'[^A-Za-zÀ-Úá-ú]', '', texto_encontrado)
            if not apenas_letras.isupper():
                erros.append({
                    "mensagem": "O preâmbulo deve estar totalmente em MAIÚSCULAS.",
                    "original": texto_encontrado,
                    "span": span_encontrado,
                    "tipo": "highlight"
                })
    else:
        erros.append("Início do preâmbulo ('O PRESIDENTE DO CONSELHO NACIONAL...') não encontrado.")
     
    # Verifica o fecho (resolve/resolveu)
    erros_fecho = resolucao.verificar_fecho_preambulo(texto_completo)
    if erros_fecho: erros.extend(erros_fecho)

    if erros: return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Preâmbulo correto."}