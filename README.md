# Auditor de Minutas de Resolução

Ferramenta para validação de conformidade estrutural e redacional de atos normativos, com suporte às regras específicas do CONDEL/SUDECO e CEG/MIDR, baseada nas diretrizes do Decreto nº 12.002/2024.

## Funcionalidades

* **Identificação de Tipo:** Detecção automática do tipo de resolução (CONDEL ou CEG) e aplicação do conjunto de regras correspondente.
* **Validação de Formatação:** Verificação de espaçamentos, numeração de artigos, grafia de datas e uso de siglas.
* **Análise Sintática e Hierárquica:** Validação da pontuação e sequência lógica de incisos e alíneas (regras de abertura, itens intermediários e fecho).
* **Suporte a Arquivos:** Processamento de textos colados e arquivos nos formatos `.txt`, `.docx` e `.pdf`.
* **Interface de Revisão:** Visualização do texto processado com destaque (highlight) nos erros encontrados e navegação via âncoras.

## Regras de Auditoria

O sistema aplica validações divididas em escopos:

### 1. Regras Comuns (Aplicáveis a todos os documentos)
* **Artigos:** Numeração (ordinal até 9º, cardinal a partir de 10) e espaçamento.
* **Parágrafos:** Formatação do símbolo `§` e espaçamento.
* **Datas:** Validação de grafia (ex: vedação de zero à esquerda em dias).
* **Siglas:** Exigência de travessão para separação de siglas.
* **Ementa:** Verificação de verbos de ação iniciais.
* **Assinatura:** Validação do bloco de assinatura (apenas nome em maiúsculo).
* **Pontuação de Listas:** Validação estrita de incisos e alíneas conforme Decreto nº 12.002/2024 (uso de `;`, `.` e `:` conforme a hierarquia e continuidade do bloco).

### 2. Regras Específicas
* **CONDEL:** Validação de cabeçalho, epígrafe e preâmbulo conforme padrões do Conselho Deliberativo.
* **CEG:** Validação de cabeçalho, epígrafe (uso de barra `/`) e preâmbulo (uso de travessão `—`) conforme padrões do Comitê Estratégico de Governança.

### 3. Regras de Anexo
* Identificação da seção `ANEXO`.
* Validação da sequência numérica de Capítulos, Seções e Artigos dentro do anexo.

## Estrutura do Projeto

```text
/
├── app.py                  # Interface frontend (Streamlit) e lógica de visualização
├── core/
│   ├── __init__.py         # Controlador de seleção de regras (Factory)
│   ├── utils.py            # Funções utilitárias (ex: conversão de romanos)
│   └── regras/
│       ├── comuns.py       # Regras compartilhadas (formatação, incisos, alíneas)
│       ├── condel.py       # Regras específicas CONDEL
│       ├── ceg.py          # Regras específicas CEG
│       └── anexo.py        # Regras estruturais do Anexo
├── requirements.txt        # Dependências do projeto
└── packages.txt            # Dependências do sistema (locales)
Execução
Pré-requisitos
Python 3.9 ou superior

Git

Instalação
Clone o repositório:

Bash

git clone [URL_DO_REPOSITORIO]
cd Verificacao_minuta
Crie e ative o ambiente virtual:

Bash

# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
Instale as dependências:

Bash

pip install -r requirements.txt
Execute a aplicação:

Bash

streamlit run app.py
Acesse a aplicação no navegador através do endereço exibido no terminal (geralmente http://localhost:8501).
