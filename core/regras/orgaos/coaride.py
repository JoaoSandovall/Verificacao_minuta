import re
from core.regras import resolucao

def auditar_epigrafe_coaride(texto_completo):
    """
    Valida a Epígrafe do COARIDE.
    Padrão: RESOLUÇÃO COARIDE/SUDECO Nº X...
    """
    # Regex flexível que captura a linha da resolução
    match = re.search(
        r"(MINUTA\s+(?:DE\s+)?)?RESOLUÇÃO\s+(COARIDE.*?)(?=\n|$)", 
        texto_completo, 
        re.IGNORECASE
    )
    
    if match:
        texto_encontrado = match.group(0).strip()
        span = match.span()

        # 1. Validação de Conteúdo (Sigla)
        if "COARIDE" not in texto_encontrado.upper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "Epígrafe deve conter a sigla 'COARIDE'.",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }
            
        # 2. Validação de Formatação (Caixa Alta)
        apenas_letras = re.sub(r'[^A-Za-zÇçÁ-Úá-ú]', '', texto_encontrado)
        if not apenas_letras.isupper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "A epígrafe deve estar totalmente em MAIÚSCULAS.",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }

        return {"status": "OK", "detalhe": "Epígrafe COARIDE correta."}

    return {"status": "ALERTA", "detalhe": "Epígrafe COARIDE não encontrada."}

def auditar_preambulo_coaride(texto_completo):
    """
    Valida a autoridade do Preâmbulo COARIDE.
    """
    # Autoridade esperada
    autoridade_esperada = "O PRESIDENTE DO CONSELHO ADMINISTRATIVO DA REGIÃO INTEGRADA DE DESENVOLVIMENTO DO DISTRITO FEDERAL E ENTORNO — COARIDE/SUDECO"

    # Regex para capturar a autoridade até a vírgula ou até 'no uso'
    match = re.search(
        r"(O PRESIDENTE DO CONSELHO ADMINISTRATIVO.*?)(?=\s*,|\s+no uso)", 
        texto_completo, 
        re.IGNORECASE | re.DOTALL
    )

    if match:
        texto_encontrado = match.group(1).strip()
        span = match.span(1)

        # Normalização simples (remove espaços extras e põe em maiúsculas)
        texto_norm = re.sub(r'\s+', ' ', texto_encontrado).upper()
        esperado_norm = re.sub(r'\s+', ' ', autoridade_esperada).upper()

        # 1. Validação de Conteúdo
        if texto_norm != esperado_norm:
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "Autoridade incorreta para COARIDE.<br>Verifique a grafia e a sigla (COARIDE/SUDECO).",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }
        
        # 2. Validação de Formatação (Caixa Alta)
        apenas_letras = re.sub(r'[^A-Za-zÇçÁ-Úá-ú]', '', texto_encontrado)
        if not apenas_letras.isupper():
            return {
                "status": "FALHA",
                "detalhe": {
                    "mensagem": "O preâmbulo deve estar totalmente em MAIÚSCULAS.",
                    "original": texto_encontrado,
                    "span": span,
                    "tipo": "highlight"
                }
            }
            
        # Verifica também o fecho (resolve/resolveu)
        erros_fecho = resolucao.verificar_fecho_preambulo(texto_completo)
        if erros_fecho:
            return {"status": "FALHA", "detalhe": erros_fecho}

        return {"status": "OK", "detalhe": "Preâmbulo COARIDE correto."}

    return {"status": "ALERTA", "detalhe": "Autoridade do COARIDE não encontrada no preâmbulo."}