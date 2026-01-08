import re
from core.regras import resolucao
from core.utils import limpar_para_validar

def auditar_cabecalho_ceg(texto_completo):
    linhas = [l.strip() for l in texto_completo.strip().split('\n') if l.strip()]
    
    # O CEG exige Ministério e o nome do Comitê
    if len(linhas) < 2:
        return {"status": "FALHA", "detalhe": ["Cabeçalho incompleto. Esperado: Ministério e Comitê."]}
    
    erros = []
    
    # Validação da Linha 1
    if "MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL" not in linhas[0].upper():
        erros.append(f"Linha 1 incorreta.<br>Esperado: MINISTÉRIO DA INTEGRAÇÃO...<br>Encontrado: {linhas[0]}")
    
    # Validação da Linha 2 "COMITÊ ESTRATÉGICO DE GOVERNANÇA"
    if "COMITÊ ESTRATÉGICO DE GOVERNANÇA" not in linhas[1].upper():
        erros.append(f"Linha 2 incorreta.<br>Esperado: COMITÊ ESTRATÉGICO DE GOVERNANÇA<br>Encontrado: {linhas[1]}")
        
    if erros: return {"status": "FALHA", "detalhe": erros}
    return {"status": "OK", "detalhe": "Cabeçalho OK."}

def auditar_epigrafe_ceg(texto_completo):

    padrao = re.compile(
        r"(MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO CEG/MIDR N[º°ᵒ] "
        r"(\d+|xx|XX),\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+(\w+|xx|XX)\s+DE\s+(\d{4})",
        re.IGNORECASE
    )
    
    match = padrao.search(texto_completo)
    
    if match:
        conteudo = match.group(0)
        # Verifica se está em maiúsculas (ignorando números e símbolos)
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
            
        return {"status": "OK", "detalhe": "Epígrafe CEG correta."}
    
    return {"status": "ALERTA", "detalhe": "Padrão 'RESOLUÇÃO CEG/MIDR ...' não encontrado."}

def auditar_preambulo_ceg(texto_completo):
    """
    O começo do preambulo, verifica a autoridade (O COORDENADOR DO COMITÊ ESTRATÉGICO DE GOVERNANÇA DO MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL — CEG-MIDR)
    """
    
    autoridade_esperada = "O COORDENADOR DO COMITÊ ESTRATÉGICO DE GOVERNANÇA DO MINISTÉRIO DA INTEGRAÇÃO E DO DESENVOLVIMENTO REGIONAL — CEG-MIDR"
    
    match_linha = re.search(
        r"(O COORDENADOR DO COMITÊ ESTRATÉGICO.*?(?:CEG.?MIDR|(?=\s*,\s*no uso)|(?=\s*,)))", 
        texto_completo, 
        re.IGNORECASE | re.DOTALL
    )

    if match_linha:
        texto_encontrado = match_linha.group(1).strip()
        span_encontrado = match_linha.span(1)

        # 1. Validação de Conteúdo (Ignora traços vs hífen)
        # O _limpar_para_validar remove o traço, então CEG-MIDR e CEG—MIDR ficam iguais para validação
        if limpar_para_validar(texto_encontrado) != limpar_para_validar(autoridade_esperada):
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "Autoridade incorreta.<br>Esperado: <em>O COORDENADOR ... CEG-MIDR</em>",
                    "original": texto_encontrado,
                    "span": span_encontrado,
                    "tipo": "highlight"
                }
            }
        
        # 2. Validação de Formatação (Caixa Alta)
        apenas_letras = re.sub(r'[^A-Za-zÀ-Úá-ú]', '', texto_encontrado)
        if not apenas_letras.isupper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "O preâmbulo deve estar totalmente em MAIÚSCULAS.",
                    "original": texto_encontrado,
                    "span": span_encontrado,
                    "tipo": "highlight"
                }
            }
            
        # Verifica o fecho (resolve/resolveu)
        erros_fecho = resolucao.verificar_fecho_preambulo(texto_completo)
        if erros_fecho: return {"status": "FALHA", "detalhe": erros_fecho}

        return {"status": "OK", "detalhe": "Preâmbulo CEG correto."}

    return {"status": "ALERTA", "detalhe": "Autoridade 'O COORDENADOR DO COMITÊ...' não encontrada."}