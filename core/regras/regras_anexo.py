import re

def auditar_anexo(texto_completo):
    """
    Verifica se a seção 'ANEXO' existe, se está em maiúsculas
    e se está sozinha na linha.
    """
    
    # Padrão: 
    # \n       - nova linha
    # \s* - espaço em branco opcional no início da linha
    # (ANEXO)  - A palavra-chave (capturada no grupo 1)
    # \s* - espaço em branco opcional no fim da linha
    # (?=\n|$) - Lookahead: garante que a linha termina aqui (sem ler a próxima linha)
    
    # Primeiro, procuramos pela forma exata e correta
    match_correto = re.search(r'\n\s*(ANEXO)\s*(?=\n|$)', texto_completo)
    
    if match_correto:
        # Encontrou "ANEXO" perfeitamente.
         return {"status": "OK", "detalhe": "Seção 'ANEXO' encontrada e formatada corretamente."}

    # Se não achou a correta, procura por versões erradas (case-insensitive)
    # para poder reportar o erro específico.
    match_incorreto = re.search(r'\n\s*(ANEXO\b.*?)\s*(?=\n|$)', texto_completo, re.IGNORECASE)

    if match_incorreto:
        palavra_encontrada = match_incorreto.group(1).strip()
        # Encontrou, mas está no formato errado (ex: "Anexo", "ANEXO I")
        return {"status": "FALHA", "detalhe": [f"Formato de 'Anexo' incorreto. Encontrado: '{palavra_encontrada}'. Esperado: 'ANEXO' (exatamente, em maiúsculas e sozinho na linha)."]}
    
    # Não encontrou nenhuma menção a "ANEXO"
    return {"status": "OK", "detalhe": "Aviso: Nenhuma seção 'ANEXO' foi encontrada (Não obrigatório)."}