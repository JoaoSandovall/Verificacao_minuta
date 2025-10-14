import re

def auditar_fecho_vigencia(texto_completo):
    
    texto_para_analise = texto_completo
    
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    if match_anexo:
        texto_para_analise = texto_completo[:match_anexo.start()]

    padrao = r"Esta Resolução entra em vigor (?:na data de sua publicação|no dia .*?)\."
    
    match = re.search(padrao, texto_para_analise, re.IGNORECASE)
    
    if match:
        return {
            "status": "OK",
            "detalhe": f"A cláusula de vigência foi encontrada: '{match.group(0)}'"
        }
    else:
        return {
            "status": "FALHA",
            "detalhe": [
                "A cláusula de vigência padrão não foi encontrada antes da assinatura. "
                "Esperado: '...entra em vigor na data de sua publicação.' ou '...entra em vigor no dia [data].'"
            ]
        }

def auditar_assinatura(texto_completo):
    """Verifica se o bloco de assinatura segue o padrão (NOME EM MAIÚSCULAS / Cargo)."""
    
    texto_para_analise = texto_completo
    
    # Procura pelo início do anexo para delimitar o fim da resolução
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    if match_anexo:
        # Se encontrou um anexo, analisa apenas o texto ANTES dele
        texto_para_analise = texto_completo[:match_anexo.start()]

    linhas = [linha.strip() for linha in texto_para_analise.strip().split('\n') if linha.strip()]
    
    if len(linhas) < 2:
        return {"status": "FALHA", "detalhe": ["Não foi possível encontrar um bloco de assinatura reconhecível no final da resolução."]}
    
    ultimas_linhas = linhas[-4:]
    try:
        indice_nome = -1
        for i, linha in enumerate(ultimas_linhas):
            if linha.isupper() and len(linha.split()) > 1 and not linha.startswith('Art.'):
                indice_nome = i
                break
        
        if indice_nome == -1:
            return {"status": "FALHA", "detalhe": ["O nome do signatário em letras maiúsculas não foi encontrado no bloco de assinatura."]}
        
        linha_nome = ultimas_linhas[indice_nome]
        linha_cargo = ultimas_linhas[indice_nome + 1]
        
        if not linha_cargo or linha_cargo.isupper():
            return {"status": "FALHA", "detalhe": [f"O cargo abaixo do nome '{linha_nome}' não foi encontrado ou está incorretamente em maiúsculas."]}
        
        return {"status": "OK", "detalhe": "O bloco de assinatura está formatado corretamente."}
    except IndexError:
        return {"status": "FALHA", "detalhe": ["A estrutura do bloco de assinatura parece inválida (ex: nome sem cargo abaixo)."]}