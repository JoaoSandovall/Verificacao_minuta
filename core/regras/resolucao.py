# import re
# import locale
# from datetime import datetime
# from core.utils import _roman_to_int

# def auditar_pontuacao_incisos(texto_completo):
#     """(REGRA - Resolução) Verifica a sequência e pontuação de Incisos (estrito)."""
#     erros = []
#     incisos = re.findall(r'(^[ \t]*[IVXLCDM]+[\s\-–].*?)(?=\n[ \t]*[IVXLCDM]+[\s\-–]|\Z)', texto_completo, re.MULTILINE | re.DOTALL)
    
#     if not incisos:
#         return {"status": "OK", "detalhe": "Nenhum inciso (I, II, etc.) foi encontrado para análise."}
    
#     num_incisos = len(incisos)
#     expected_numeral = 1

#     for i, inciso_texto in enumerate(incisos):
#         inciso_limpo = inciso_texto.strip()
#         numeral_romano = re.match(r'^\s*([IVXLCDM]+)', inciso_limpo).group(1)
        
#         current_numeral = _roman_to_int(numeral_romano)
#         if current_numeral != expected_numeral:
#             erros.append(f"Sequência de incisos incorreta. Esperado inciso de valor {expected_numeral}, mas encontrado '{numeral_romano}'.")
#         expected_numeral += 1

#         is_last = (i == num_incisos - 1)
#         is_penultimate = (i == num_incisos - 2)
#         tem_alineas = re.search(r':\s*\n\s*[a-z]\)', inciso_texto)
        
#         if tem_alineas:
#             if not inciso_limpo.endswith(':'):
#                  erros.append(f"O Inciso {numeral_romano} precede alíneas e deve terminar com dois-pontos (:).")
#             continue

#         if is_last:
#             if not inciso_limpo.endswith('.'):
#                 erros.append(f"O último inciso (Inciso {numeral_romano}) deve terminar com ponto final (.). Encontrado: '{inciso_limpo[-1]}'")
#         elif is_penultimate:
#             if not inciso_limpo.endswith('; e'):
#                 erros.append(f"O penúltimo inciso (Inciso {numeral_romano}) deve terminar com '; e'.")
#         else:
#             if not inciso_limpo.endswith(';'):
#                 erros.append(f"O inciso intermediário (Inciso {numeral_romano}) deve terminar com ponto e vírgula (;).")

#     if not erros:
#         return {"status": "OK", "detalhe": "A sequência e pontuação dos incisos estão corretas."}
#     else:
#         return {"status": "FALHA", "detalhe": erros[:5]}

# def auditar_pontuacao_alineas(texto_completo):
#     """(REGRA - Resolução) Verifica a sequência e pontuação das Alíneas (estrito)."""
#     erros = []
#     blocos_alineas = re.finditer(r'((?:\n\s*[a-z]\).*?)+)', texto_completo)
    
#     found_any_block = False
#     for bloco in blocos_alineas:
#         found_any_block = True
#         alineas = re.findall(r'\n\s*([a-z])\)(.*)', bloco.group(1))
        
#         if not alineas:
#             continue

#         num_alineas = len(alineas)
#         expected_char_ord = ord('a')

#         for i, (letra_alinea, texto_alinea) in enumerate(alineas):
#             alinea_limpa = f"{letra_alinea}) {texto_alinea.strip()}"
#             current_char_ord = ord(letra_alinea)
#             if current_char_ord != expected_char_ord:
#                  erros.append(f"Sequência de alíneas incorreta. Esperado '{chr(expected_char_ord)})', mas encontrado '{letra_alinea})'.")
#             expected_char_ord += 1

#             is_last = (i == num_alineas - 1)
#             is_penultimate = (i == num_alineas - 2)
            
#             if is_last:
#                 if not alinea_limpa.endswith('.'):
#                     erros.append(f"A última alínea ('{letra_alinea})') deve terminar com ponto final (.).")
#             elif is_penultimate:
#                 if not alinea_limpa.endswith('; e'):
#                      erros.append(f"A penúltima alínea ('{letra_alinea})') deve terminar com '; e'.")
#             else:
#                 if not alinea_limpa.endswith(';'):
#                     erros.append(f"A alínea intermediária ('{letra_alinea})') deve terminar com ponto e vírgula (;).")

#     if not erros:
#         if found_any_block:
#             return {"status": "OK", "detalhe": "A sequência e pontuação das alíneas estão corretas."}
#         else:
#             return {"status": "OK", "detalhe": "Nenhuma alínea (a, b, c...) foi encontrada para análise."}
#     else:
#         return {"status": "FALHA", "detalhe": erros[:5]}

# def auditar_fecho_vigencia(texto_completo):
#     """Verifica a cláusula de vigência."""
#     texto_para_analise = texto_completo
#     erros = [] 

#     match_anexo = re.search(r'\n\s*ANEXO', texto_para_analise, re.IGNORECASE)
#     if match_anexo:
#         texto_para_analise = texto_para_analise[:match_anexo.start()]

#     padrao_publicacao_texto = "Esta Resolução entra em vigor na data de sua publicação."
#     padrao_publicacao_regex = re.compile(r"Esta\s+Resolução\s+entra\s+em\s+vigor\s+na\s+data\s+de\s+sua\s+publicação\.", re.IGNORECASE)
#     match_publicacao = padrao_publicacao_regex.search(texto_para_analise)

#     if match_publicacao:
#         frase_encontrada = re.sub(r'\s+', ' ', match_publicacao.group(0)).strip()
#         frase_esperada_normalizada = re.sub(r'\s+', ' ', padrao_publicacao_texto).strip()
#         if frase_encontrada.lower() == frase_esperada_normalizada.lower():
#              return {"status": "OK", "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"}
#         else:
#              erros.append(f"Encontrado texto similar, mas não exato '{padrao_publicacao_texto}'. Encontrado: '{frase_encontrada}'")

#     padrao_data_especifica_regex = re.compile(
#         r"(Esta\s+Resolução\s+entra\s+em\s+vigor\s+em\s+"
#         r"(\d{1,2})[º°]\s+de\s+"
#         r"([a-záçãõéêíóôú]+)\s+de\s+"
#         r"(\d{4})\.)"
#     )
#     match_data = padrao_data_especifica_regex.search(texto_para_analise)

#     if match_data:
#         frase_completa, dia_str, mes_str, ano_str = match_data.groups()
#         frase_encontrada = re.sub(r'\s+', ' ', frase_completa).strip()

#         try:
#             locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
#             data_str_validacao = f"{dia_str} de {mes_str} de {ano_str}"
#             datetime.strptime(data_str_validacao, "%d de %B de %Y")
#             return {
#                 "status": "OK",
#                 "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"
#             }
#         except ValueError:
#              return {
#                  "status": "FALHA",
#                  "detalhe": [f"A data de vigência '{dia_str}º de {mes_str} de {ano_str}' parece ser inválida."]
#              }
#         except locale.Error:
#               return {
#                  "status": "OK",
#                  "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'. Aviso: Não foi possível validar a data (locale pt_BR não encontrado)."
#              }

#     if not erros:
#         msg_falha = ("A cláusula de vigência não foi encontrada ou não segue um dos padrões exatos esperados: "
#                      "'Esta Resolução entra em vigor na data de sua publicação.' ou "
#                      "'Esta Resolução entra em vigor em [dia]° de [mês minúsculo] de [ano].'")
#         erros.append(msg_falha)

#     return {"status": "FALHA", "detalhe": erros}

# def auditar_assinatura(texto_completo):
#     """Verifica se o bloco de assinatura segue o novo padrão."""
#     texto_para_analise = texto_completo
#     match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
#     if match_anexo:
#         texto_para_analise = texto_completo[:match_anexo.start()]

#     linhas = [linha.strip() for linha in texto_para_analise.strip().split('\n') if linha.strip()]
#     if not linhas:
#         return {"status": "FALHA", "detalhe": ["Não foi possível encontrar um bloco de assinatura reconhecível no final da resolução."]}
    
#     ultimas_linhas = linhas[-4:] 
#     indice_nome = -1
#     linha_nome = ""

#     for i, linha in enumerate(ultimas_linhas):
#         if linha.isupper() and len(linha.split()) > 1 and not linha.startswith('Art.'):
#             indice_nome = i
#             linha_nome = linha
#             break
    
#     if indice_nome == -1:
#         return {"status": "FALHA", "detalhe": ["O nome do signatário em letras maiúsculas não foi encontrado no bloco de assinatura."]}
    
#     if indice_nome < len(ultimas_linhas) - 1:
#         linha_seguinte = ultimas_linhas[indice_nome + 1]
#         return {"status": "FALHA", "detalhe": [f"O bloco de assinatura deve conter apenas o nome em maiúsculas ('{linha_nome}'). Foi encontrado texto abaixo dele: '{linha_seguinte}'."]}
    
#     return {"status": "OK", "detalhe": "O bloco de assinatura (apenas nome) está formatado corretamente."}