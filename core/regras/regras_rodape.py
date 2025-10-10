# core/regras/regras_rodape.py
import re

def auditar_assinatura(texto_completo):
    """Verifica se o bloco de assinatura segue o padrão (NOME EM MAIÚSCULAS / Cargo)."""
    linhas = [linha.strip() for linha in texto_completo.strip().split('\n') if linha.strip()]
    if len(linhas) < 2:
        return {"status": "FALHA", "detalhe": ["ERRO R012: Não foi possível encontrar um bloco de assinatura no final do documento."]}
    ultimas_linhas = linhas[-4:]
    try:
        indice_nome = -1
        for i, linha in enumerate(ultimas_linhas):
            if linha.isupper() and len(linha.split()) > 1:
                indice_nome = i
                break
        if indice_nome == -1:
            return {"status": "FALHA", "detalhe": ["ERRO R012: Nome do signatário em letras maiúsculas não encontrado no final do documento."]}
        linha_nome = ultimas_linhas[indice_nome]
        linha_cargo = ultimas_linhas[indice_nome + 1]
        if not linha_cargo or linha_cargo.isupper():
            return {"status": "FALHA", "detalhe": [f"ERRO R012: Cargo abaixo do nome '{linha_nome}' não encontrado ou está incorretamente em maiúsculas."]}
        return {"status": "OK", "detalhe": "Bloco de assinatura parece estar no formato correto (R012)."}
    except IndexError:
        return {"status": "FALHA", "detalhe": ["ERRO R012: Estrutura do bloco de assinatura inválida (nome sem cargo abaixo)."]}

def auditar_fecho_vigencia(texto_completo):
    """Verifica se o documento possui uma cláusula de vigência padrão."""
    padrao = r"Esta Resolução entra em vigor na data de sua publicação\."
    match = re.search(padrao, texto_completo, re.IGNORECASE)
    if match:
        return {"status": "OK", "detalhe": "Cláusula de vigência ('entra em vigor...') encontrada."}
    else:
        return {"status": "FALHA", "detalhe": ["A cláusula padrão 'Esta Resolução entra em vigor na data de sua publicação.' não foi encontrada."]}