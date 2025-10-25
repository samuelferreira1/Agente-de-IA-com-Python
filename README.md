# Agente de IA com Python

Um agente de IA em Python para atendimento de RH com interface web simples, triagem inteligente de solicitações, recuperação de conteúdo a partir de documentos (RAG) e fluxo de decisão orquestrado com LangGraph. O projeto expõe uma API HTTP via Flask e uma página única em HTML/CSS/JS para conversação.

- Back-end: Flask + LangGraph
- Front-end: HTML/CSS/JS (página única)
- Conteúdo: Recuperação de respostas com citações a partir de PDFs no diretório `documents/`

---

## Badges

![GitHub stars](https://img.shields.io/github/stars/samuelferreira1/Agente-de-IA-com-Python?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/samuelferreira1/Agente-de-IA-com-Python?style=for-the-badge)
![Issues abertas](https://img.shields.io/github/issues/samuelferreira1/Agente-de-IA-com-Python?style=for-the-badge)
![Último commit](https://img.shields.io/github/last-commit/samuelferreira1/Agente-de-IA-com-Python?style=for-the-badge)
![Licença](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)

---

## Sumário/Índice

- [Instalação](#instalação)
- [Uso / Exemplos](#uso--exemplos)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato / Autor](#contato--autor)

---

## Instalação

Pré-requisitos:
- Python 3.10 ou superior
- Git
- (Opcional) Ambiente virtual com venv

Passo a passo:

```bash
# 1) Clonar o repositório
git clone https://github.com/samuelferreira1/Agente-de-IA-com-Python.git
cd Agente-de-IA-com-Python

# 2) Criar e ativar um ambiente virtual (recomendado)
python -m venv .venv
# Windows (PowerShell):
.\\.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3) Instalar dependências mínimas observadas no código
pip install Flask langgraph

# Observação:
# O componente de RAG pode requerer bibliotecas adicionais (por exemplo, para leitura/consulta de PDFs
# e embeddings). Caso necessário, instale-as conforme indicado nos módulos em components/.
# Ex.: pip install pypdf chromadb sentence-transformers (AJUSTE conforme sua implementação)
```

---

## Uso / Exemplos

Executar o servidor Flask:

```bash
# Porta padrão 5000; você pode sobrescrever via variável de ambiente PORT
export PORT=5000  # macOS/Linux
set PORT=5000     # Windows (cmd)
$env:PORT=5000    # Windows (PowerShell)

python app.py
```

Acesse no navegador:
- http://localhost:5000

A interface “Fale com o RH” (single page) permite enviar mensagens e exibe:
- Resposta do agente
- Ação final tomada pelo fluxo (quando aplicável)
- Citações das fontes (documento e página) quando a resposta vier do RAG

Exemplo de chamada HTTP direta (via curl) ao endpoint de chat:

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Como funcionam as férias?"}'
```

Resposta típica (JSON):
```json
{
  "answer": "Texto da resposta...",
  "acao_final": "AUTO_RESOLVER",
  "citacoes": [
    {"documento": "Ferreira_Developer_Politicas.pdf", "pagina": 3}
  ]
}
```

---

## Funcionalidades

- Triagem inteligente de solicitações:
  - Classifica a intenção inicial do usuário e os campos faltantes
  - Decide se deve responder com RAG, pedir mais informações ou abrir chamado

- Recuperação aumentada por conteúdo (RAG):
  - Consulta documentos PDF do diretório `documents/`
  - Devolve citações de fonte (documento/página) junto à resposta

- Fluxo de decisão com LangGraph:
  - Nós: triagem, auto_resolver (RAG), pedir_info, abrir_chamado
  - Transições condicionais com finais possíveis: resposta direta, pedido de detalhes ou registro/abertura de chamado

- Interface web moderna e responsiva:
  - Página única em `templates/index.html`
  - Envio de mensagens com indicador de digitação e exibição de citações

- API simples:
  - GET `/` — carrega a interface
  - POST `/chat` — recebe `{ "message": "..." }` e retorna a resposta do agente

---

## Tecnologias

- Linguagens:
  - Python (back-end, 69.4%)
  - HTML/CSS/JS (front-end, 30.6%)

- Principais bibliotecas:
  - Flask (servidor web e endpoints)
  - LangGraph (orquestração do fluxo de decisão)

- Estrutura de diretórios (principais):
  - [app.py](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/d50384955972a4cf69386efbf781e8ead2874ad2/app.py) — App Flask e rotas
  - components/
    - [workflow.py](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/d50384955972a4cf69386efbf781e8ead2874ad2/components/workflow.py) — Definição do grafo (LangGraph)
    - [triagem.py](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/main/components/triagem.py) — Lógica de triagem
    - [rag.py](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/main/components/rag.py) — Lógica de RAG (consulta e citações)
  - templates/
    - [index.html](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/d50384955972a4cf69386efbf781e8ead2874ad2/templates/index.html) — Interface do chat
  - documents/
    - [Ferreira_Developer_Politicas.pdf](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/main/documents/Ferreira_Developer_Politicas.pdf)
    - [Ferreira_Developer_Seções_Úteis.pdf](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/main/documents/Ferreira_Developer_Se%C3%A7%C3%B5es_%C3%9Ateis.pdf)

Outros arquivos:
- [.gitignore](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/d50384955972a4cf69386efbf781e8ead2874ad2/.gitignore)
- [.gitattributes](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/d50384955972a4cf69386efbf781e8ead2874ad2/.gitattributes)
- [LICENSE](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/d50384955972a4cf69386efbf781e8ead2874ad2/LICENSE)

---

## Contribuição

Contribuições são bem-vindas! Siga os passos:

1) Crie um fork e um branch de feature/correção:
```bash
git checkout -b feat/minha-feature
# ou
git checkout -b fix/ajuste-bug
```

2) Implemente sua mudança com clareza (inclua docstrings/comentários quando necessário)

3) Valide o funcionamento localmente:
```bash
python app.py
# Navegue até http://localhost:5000 e teste os fluxos
```

4) Abra um Pull Request descrevendo:
- Motivação e problema resolvido
- Mudanças no fluxo (se houver)
- Instruções de teste
- Impactos conhecidos

Boas práticas sugeridas:
- Mantenha o escopo do PR focado e pequeno
- Siga convenções de nome de branch e mensagens de commit
- Se adicionar dependências, documente-as nesta seção “Instalação”

---

## Licença

Este projeto está licenciado sob a licença MIT.

Consulte o arquivo [LICENSE](https://github.com/samuelferreira1/Agente-de-IA-com-Python/blob/d50384955972a4cf69386efbf781e8ead2874ad2/LICENSE) para mais detalhes.

---

## Contato / Autor

- Autor: Samuel Ferreira
- GitHub: [samuelferreira1](https://github.com/samuelferreira1)
- Repositório: [Agente-de-IA-com-Python](https://github.com/samuelferreira1/Agente-de-IA-com-Python)

Dúvidas ou sugestões? Abra uma issue no repositório ou entre em contato.
