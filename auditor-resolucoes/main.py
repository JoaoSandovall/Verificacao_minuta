# main.py

import os
# Importa as funções de auditoria do seu módulo core
from core.auditors import (
    auditar_cabecalho_ministerio,
    auditar_numeracao_artigos,
    auditar_pontuacao_incisos,
    auditar_uso_siglas
)

def carregar_minuta(caminho):
    """Carrega o texto da minuta de um arquivo."""
    caminho_completo = os.path.join(os.path.dirname(__file__), caminho)
    try:
        # Tenta abrir com codificação UTF-8
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("--- ERRO DE INICIALIZAÇÃO ---")
        print(f"Arquivo não encontrado: {caminho_completo}")
        print("Certifique-se de ter criado a pasta 'data' e o arquivo 'minuta_sudeco_texto.txt' dentro dela.")
        return None

def main():
    caminho_minuta = 'data/minuta_sudeco_texto.txt'
    texto_minuta = carregar_minuta(caminho_minuta)
    
    if not texto_minuta:
        return

    print("==================================================")
    print("      INICIANDO AUDITORIA FORMAL DE MINUTA        ")
    print("==================================================")

    # Lista de auditorias a serem executadas
    auditorias = [
        ("R001: Cabeçalho do Ministério", auditar_cabecalho_ministerio),
        ("R005: Numeração de Artigos", auditar_numeracao_artigos),
        ("R008: Pontuação de Incisos", auditar_pontuacao_incisos),
        ("R010: Uso de Siglas (Travessão)", auditar_uso_siglas),
    ]

    total_erros = 0
    
    for nome, funcao_auditoria in auditorias:
        resultado = funcao_auditoria(texto_minuta)
        
        if resultado["status"] == "FALHA":
            num_erros_regra = len(resultado["detalhe"])
            total_erros += num_erros_regra
            print(f"\n[FALHA] - {nome} ({num_erros_regra} erros)")
            for i, erro in enumerate(resultado["detalhe"], 1):
                # Limita a 5 erros por regra para um relatório inicial mais limpo
                if i <= 5: 
                    print(f"  {i}. {erro}")
                elif i == 6:
                    print("  ... (Mais erros encontrados, mostrando apenas os 5 primeiros)")
                    break
        else:
            print(f"\n[OK]    - {nome}")

    print("\n==================================================")
    print(f"AUDITORIA CONCLUÍDA. TOTAL DE ERROS ENCONTRADOS: {total_erros}")
    print("==================================================")
    
    if total_erros > 0:
        print("\n**ATENÇÃO:** Reveja os pontos acima para garantir a conformidade com o checklist.")
    else:
        print("\n🎉 PARABÉNS! Nenhuma falha encontrada nas regras auditadas.")

if __name__ == "__main__":
    main()