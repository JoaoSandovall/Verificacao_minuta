import re
import locale
from datetime import datetime
from core.utils import _roman_to_int

def auditar_epigrafe(texto_completo):
    """Verifica se a epígrafe segue o padrão estrito."""
    erros = []
    
    padrao_epigrafe = re.compile(
        r"(MINUTA )?"
        r"RESOLUÇÃO CONDEL(?:/SUDECO|/SUDENE|/SUDAM)? N° "
        r"(\d+|xx|XX),"
        r"\s+DE\s+(\d{1,2}|xx|XX)\s+DE\s+"
        r"(\w+|xx|XX)\s+DE\s+(\d{4})"
    )
    
    match = padrao_epigrafe.search(texto_completo)
    
    if not match:
        padrao_flexivel = re.compile(r"MINUTA RESOLUÇÃO CONDEL.*? DE \d{4}", re.IGNORECASE)
        match_flexivel = padrao_flexivel.search(texto_completo)
        if match_flexivel:
            contexto = match_flexivel.group(0).strip()
            return {"status": "FALHA", "detalhe": [f"A epígrafe foi encontrada, mas sua formatação está incorreta. Verifique se está tudo em maiúsculas (exceto 'xx', se usado). Encontrado: '{contexto}'"]}
        else:
            return {"status": "FALHA", "detalhe": ["A linha da epígrafe não foi encontrada ou está fora do padrão 'RESOLUÇÃO CONDEL N°..., DE...DE...DE...'."]}

    numero_res, dia_str, mes_str, ano_str = match.groups()[1:]
    
    if mes_str.lower() != 'xx':
        if not mes_str.isupper():
            erros.append(f"O mês na data da epígrafe deve estar em MAIÚSCULO. Foi encontrado: '{mes_str}'.")

        if dia_str.lower() != 'xx':
            try:
                locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
                data_str = f"{dia_str} de {mes_str.lower()} de {ano_str}"
                datetime.strptime(data_str, "%d de %B de %Y")
            except ValueError:
                erros.append(f"A data '{dia_str} de {mes_str} de {ano_str}' parece ser inválida (ex: dia 31 de abril).")
            except locale.Error:
                erros.append("Aviso: Não foi possível validar a data (locale 'pt_BR.UTF-8' não encontrado). Verificação de data pulada.")

    if not erros:
        return {"status": "OK", "detalhe": "O formato da epígrafe e a data estão corretos."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_ementa(texto_completo):
    """Verifica se a ementa começa com um verbo de ação aceitável."""
    VERBOS_ACEITOS = ["Aprova", "Altera", "Dispõe", "Regulamenta", "Define", "Estabelece", "Autoriza", "Prorroga", "Revoga", "Atualização"]

    try:
        padrao_epigrafe = re.compile(r".* DE \d{4}", re.IGNORECASE)
        match_epigrafe = padrao_epigrafe.search(texto_completo)
        if not match_epigrafe:
            return {"status": "FALHA", "detalhe": ["Não foi possível encontrar a ementa pois a linha da data (epígrafe) não foi localizada."]}
        
        texto_apos_epigrafe = texto_completo[match_epigrafe.end():]
        linhas_ementa = texto_apos_epigrafe.strip().split('\n')
        texto_ementa = ""
        for linha in linhas_ementa:
            if linha.strip():
                texto_ementa = linha.strip()
                break
        
        if not texto_ementa:
            return {"status": "FALHA", "detalhe": ["Não foi possível encontrar o texto da ementa após a data."]}
        
        primeira_palavra = texto_ementa.split()[0]
        
        if primeira_palavra in VERBOS_ACEITOS:
            return {"status": "OK", "detalhe": f"A ementa inicia corretamente com o verbo '{primeira_palavra}'."}
        else:
            return {"status": "FALHA", "detalhe": [f"A ementa deve começar com um verbo de ação (ex: Aprova, Altera), mas começou com '{primeira_palavra}'."]}
    except IndexError:
        return {"status": "FALHA", "detalhe": ["A ementa parece estar vazia ou com formatação inválida."]}

def auditar_preambulo(texto_completo):
    """Verifica a formatação do Preâmbulo e Autoridade."""
    erros = []
    try:
        match_epigrafe = re.search(r".* DE \d{4}", texto_completo, re.IGNORECASE)
        texto_apos_epigrafe = texto_completo[match_epigrafe.end():].strip()
        texto_limpo = re.sub(r'\*?\s*MINUTA DE DOCUMENTO\s*', '', texto_apos_epigrafe, flags=re.IGNORECASE).strip()
        linhas_limpas = texto_limpo.split('\n')
        inicio_preambulo_texto = ""
        for i, linha in enumerate(linhas_limpas):
            if linha.strip():
                inicio_preambulo_texto = "\n".join(linhas_limpas[i+1:])
                break
        
        match_artigo1 = re.search(r'Art\.\s*1[ºo°]', inicio_preambulo_texto, re.IGNORECASE)
        texto_preambulo = inicio_preambulo_texto[:match_artigo1.start()].strip()
    except (AttributeError, IndexError):
        return {"status": "FALHA", "detalhe": [{"mensagem": "Não foi possível isolar o texto do preâmbulo para análise. Verifique se a ementa e o Art. 1º existem.", "contexto": ""}]}

    if not texto_preambulo:
        return {"status": "FALHA", "detalhe": [{"mensagem": "O texto do preâmbulo parece estar vazio.", "contexto": ""}]}

    texto_preambulo_normalizado = re.sub(r'\s+', ' ', texto_preambulo).strip()

    autoridades_validas = [
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO CENTRO-OESTE — CONDEL/SUDECO",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DA AMAZÔNIA — CONDEL/SUDAM",
        "O PRESIDENTE DO CONSELHO DELIBERATIVO DA SUPERINTENDÊNCIA DO DESENVOLVIMENTO DO NORDESTE — CONDEL/SUDENE"
    ]
    
    autoridade_encontrada = False
    for autoridade in autoridades_validas:
        autoridade_normalizada = re.sub(r'\s+', ' ', autoridade)
        if texto_preambulo_normalizado.startswith(autoridade_normalizada):
            autoridade_encontrada = True
            break
            
    if not autoridade_encontrada:
        contexto_erro = texto_preambulo.split('\n')[0].strip()
        erros.append(f"O Começo do preâmbulo está incorreto. Esperado uma das autoridades válidas. Encontrado: '{contexto_erro}...'")

    padrao_correto_fim = "o Colegiado resolveu:"
    if not texto_preambulo_normalizado.endswith(padrao_correto_fim):
        contexto_fim = texto_preambulo_normalizado[-50:]
        if texto_preambulo_normalizado.lower().endswith(padrao_correto_fim):
            erros.append(f"A terminação do preâmbulo deve ser '{padrao_correto_fim}' (exatamente, com 'o' minúsculo). Foi encontrado: '...{contexto_fim}'")
        else:
            erros.append(f"O preâmbulo deve terminar com a frase exata '{padrao_correto_fim}'. Foi encontrado: '...{contexto_fim}'")
            
    if not erros:
        return {"status": "OK", "detalhe": "O preâmbulo está estruturado corretamente."}
    else:
        return {"status": "FALHA", "detalhe": erros}

def auditar_pontuacao_incisos(texto_completo):
    """(REGRA - Resolução) Verifica a sequência e pontuação de Incisos (estrito)."""
    erros = []
    incisos = re.findall(r'(^[ \t]*[IVXLCDM]+[\s\-–].*?)(?=\n[ \t]*[IVXLCDM]+[\s\-–]|\Z)', texto_completo, re.MULTILINE | re.DOTALL)
    
    if not incisos:
        return {"status": "OK", "detalhe": "Nenhum inciso (I, II, etc.) foi encontrado para análise."}
    
    num_incisos = len(incisos)
    expected_numeral = 1

    for i, inciso_texto in enumerate(incisos):
        inciso_limpo = inciso_texto.strip()
        numeral_romano = re.match(r'^\s*([IVXLCDM]+)', inciso_limpo).group(1)
        
        current_numeral = _roman_to_int(numeral_romano)
        if current_numeral != expected_numeral:
            erros.append(f"Sequência de incisos incorreta. Esperado inciso de valor {expected_numeral}, mas encontrado '{numeral_romano}'.")
        expected_numeral += 1

        is_last = (i == num_incisos - 1)
        is_penultimate = (i == num_incisos - 2)
        tem_alineas = re.search(r':\s*\n\s*[a-z]\)', inciso_texto)
        
        if tem_alineas:
            if not inciso_limpo.endswith(':'):
                 erros.append(f"O Inciso {numeral_romano} precede alíneas e deve terminar com dois-pontos (:).")
            continue

        if is_last:
            if not inciso_limpo.endswith('.'):
                erros.append(f"O último inciso (Inciso {numeral_romano}) deve terminar com ponto final (.). Encontrado: '{inciso_limpo[-1]}'")
        elif is_penultimate:
            if not inciso_limpo.endswith('; e'):
                erros.append(f"O penúltimo inciso (Inciso {numeral_romano}) deve terminar com '; e'.")
        else:
            if not inciso_limpo.endswith(';'):
                erros.append(f"O inciso intermediário (Inciso {numeral_romano}) deve terminar com ponto e vírgula (;).")

    if not erros:
        return {"status": "OK", "detalhe": "A sequência e pontuação dos incisos estão corretas."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_pontuacao_alineas(texto_completo):
    """(REGRA - Resolução) Verifica a sequência e pontuação das Alíneas (estrito)."""
    erros = []
    blocos_alineas = re.finditer(r'((?:\n\s*[a-z]\).*?)+)', texto_completo)
    
    found_any_block = False
    for bloco in blocos_alineas:
        found_any_block = True
        alineas = re.findall(r'\n\s*([a-z])\)(.*)', bloco.group(1))
        
        if not alineas:
            continue

        num_alineas = len(alineas)
        expected_char_ord = ord('a')

        for i, (letra_alinea, texto_alinea) in enumerate(alineas):
            alinea_limpa = f"{letra_alinea}) {texto_alinea.strip()}"
            current_char_ord = ord(letra_alinea)
            if current_char_ord != expected_char_ord:
                 erros.append(f"Sequência de alíneas incorreta. Esperado '{chr(expected_char_ord)})', mas encontrado '{letra_alinea})'.")
            expected_char_ord += 1

            is_last = (i == num_alineas - 1)
            is_penultimate = (i == num_alineas - 2)
            
            if is_last:
                if not alinea_limpa.endswith('.'):
                    erros.append(f"A última alínea ('{letra_alinea})') deve terminar com ponto final (.).")
            elif is_penultimate:
                if not alinea_limpa.endswith('; e'):
                     erros.append(f"A penúltima alínea ('{letra_alinea})') deve terminar com '; e'.")
            else:
                if not alinea_limpa.endswith(';'):
                    erros.append(f"A alínea intermediária ('{letra_alinea})') deve terminar com ponto e vírgula (;).")

    if not erros:
        if found_any_block:
            return {"status": "OK", "detalhe": "A sequência e pontuação das alíneas estão corretas."}
        else:
            return {"status": "OK", "detalhe": "Nenhuma alínea (a, b, c...) foi encontrada para análise."}
    else:
        return {"status": "FALHA", "detalhe": erros[:5]}

def auditar_fecho_vigencia(texto_completo):
    """Verifica a cláusula de vigência."""
    texto_para_analise = texto_completo
    erros = [] 

    match_anexo = re.search(r'\n\s*ANEXO', texto_para_analise, re.IGNORECASE)
    if match_anexo:
        texto_para_analise = texto_para_analise[:match_anexo.start()]

    padrao_publicacao_texto = "Esta Resolução entra em vigor na data de sua publicação."
    padrao_publicacao_regex = re.compile(r"Esta\s+Resolução\s+entra\s+em\s+vigor\s+na\s+data\s+de\s+sua\s+publicação\.", re.IGNORECASE)
    match_publicacao = padrao_publicacao_regex.search(texto_para_analise)

    if match_publicacao:
        frase_encontrada = re.sub(r'\s+', ' ', match_publicacao.group(0)).strip()
        frase_esperada_normalizada = re.sub(r'\s+', ' ', padrao_publicacao_texto).strip()
        if frase_encontrada.lower() == frase_esperada_normalizada.lower():
             return {"status": "OK", "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"}
        else:
             erros.append(f"Encontrado texto similar, mas não exato '{padrao_publicacao_texto}'. Encontrado: '{frase_encontrada}'")

    padrao_data_especifica_regex = re.compile(
        r"(Esta\s+Resolução\s+entra\s+em\s+vigor\s+em\s+"
        r"(\d{1,2})[º°]\s+de\s+"
        r"([a-záçãõéêíóôú]+)\s+de\s+"
        r"(\d{4})\.)"
    )
    match_data = padrao_data_especifica_regex.search(texto_para_analise)

    if match_data:
        frase_completa, dia_str, mes_str, ano_str = match_data.groups()
        frase_encontrada = re.sub(r'\s+', ' ', frase_completa).strip()

        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            data_str_validacao = f"{dia_str} de {mes_str} de {ano_str}"
            datetime.strptime(data_str_validacao, "%d de %B de %Y")
            return {
                "status": "OK",
                "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'"
            }
        except ValueError:
             return {
                 "status": "FALHA",
                 "detalhe": [f"A data de vigência '{dia_str}º de {mes_str} de {ano_str}' parece ser inválida."]
             }
        except locale.Error:
              return {
                 "status": "OK",
                 "detalhe": f"A cláusula de vigência foi encontrada: '{frase_encontrada}'. Aviso: Não foi possível validar a data (locale pt_BR não encontrado)."
             }

    if not erros:
        msg_falha = ("A cláusula de vigência não foi encontrada ou não segue um dos padrões exatos esperados: "
                     "'Esta Resolução entra em vigor na data de sua publicação.' ou "
                     "'Esta Resolução entra em vigor em [dia]° de [mês minúsculo] de [ano].'")
        erros.append(msg_falha)

    return {"status": "FALHA", "detalhe": erros}

def auditar_assinatura(texto_completo):
    """Verifica se o bloco de assinatura segue o novo padrão."""
    texto_para_analise = texto_completo
    match_anexo = re.search(r'\n\s*ANEXO', texto_completo, re.IGNORECASE)
    if match_anexo:
        texto_para_analise = texto_completo[:match_anexo.start()]

    linhas = [linha.strip() for linha in texto_para_analise.strip().split('\n') if linha.strip()]
    if not linhas:
        return {"status": "FALHA", "detalhe": ["Não foi possível encontrar um bloco de assinatura reconhecível no final da resolução."]}
    
    ultimas_linhas = linhas[-4:] 
    indice_nome = -1
    linha_nome = ""

    for i, linha in enumerate(ultimas_linhas):
        if linha.isupper() and len(linha.split()) > 1 and not linha.startswith('Art.'):
            indice_nome = i
            linha_nome = linha
            break
    
    if indice_nome == -1:
        return {"status": "FALHA", "detalhe": ["O nome do signatário em letras maiúsculas não foi encontrado no bloco de assinatura."]}
    
    if indice_nome < len(ultimas_linhas) - 1:
        linha_seguinte = ultimas_linhas[indice_nome + 1]
        return {"status": "FALHA", "detalhe": [f"O bloco de assinatura deve conter apenas o nome em maiúsculas ('{linha_nome}'). Foi encontrado texto abaixo dele: '{linha_seguinte}'."]}
    
    return {"status": "OK", "detalhe": "O bloco de assinatura (apenas nome) está formatado corretamente."}