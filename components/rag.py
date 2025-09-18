# components/rag.py

import os
import re
import pathlib
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Importações da LangChain e outros pacotes
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

# --- Configuração Inicial ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("⚠️ A variável de ambiente GOOGLE_API_KEY não foi encontrada.")

# --- Carregamento, Divisão e Embeddings ---
def _load_documents():
    """Carrega todos os arquivos PDF do diretório 'documents'."""
    docs = []
    # Usando o caminho relativo para a pasta documents
    docs_path = Path(__file__).parent.parent / "documents"
    if not docs_path.exists():
        print(f"Diretório de documentos não encontrado: {docs_path}")
        return []
        
    for n in docs_path.glob("*.pdf"):
        try:
            loader = PyMuPDFLoader(str(n))
            docs.extend(loader.load())
            print(f"✔️ Documento {n.name} carregado com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao carregar o documento {n.name}: {e}")
    return docs

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(_load_documents())

print(f"\nDocumentos divididos em {len(chunks)} trechos.")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)

# Cria o Vectorstore a partir dos chunks e embeddings
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.3, "k": 4}
)

# --- Funções Auxiliares de Formatação e Extração ---
def _clean_text(s: str) -> str:
    """Limpa espaços extras de uma string."""
    return re.sub(r"\s+", " ", s or "").strip()

def extrair_trecho(texto: str, query: str, janela: int = 240) -> str:
    """Extrai um trecho relevante do texto baseado na query."""
    txt = _clean_text(texto)
    termos = [t.lower() for t in re.findall(r"\w+", query or "") if len(t) >= 4]
    pos = -1
    for t in termos:
        pos = txt.lower().find(t)
        if pos != -1:
            break
    if pos == -1:
        pos = 0
    ini, fim = max(0, pos - janela // 2), min(len(txt), pos + janela // 2)
    return txt[ini:fim]

def formatar_citacoes(docs_rel: List, query: str) -> List[Dict]:
    """Formata as citações a partir dos documentos recuperados."""
    cites, seen = [], set()
    for d in docs_rel:
        src = pathlib.Path(d.metadata.get("source", "")).name
        page = int(d.metadata.get("page", 0)) + 1
        key = (src, page)
        if key in seen:
            continue
        seen.add(key)
        cites.append({"documento": src, "pagina": page, "trecho": extrair_trecho(d.page_content, query)})
    return cites[:3]

# --- Lógica Principal do RAG ---
llm_rag = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    api_key=GOOGLE_API_KEY
)

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Você é um Assistente de Políticas Internas (RH/IT) da empresa Carraro Desenvolvimento. "
     "Responda SOMENTE com base no contexto fornecido. "
     "Se não houver base suficiente, responda apenas 'Não sei'."),
    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])

document_chain = create_stuff_documents_chain(llm_rag, RAG_PROMPT)

def perguntar_politica_RAG(pergunta: str) -> Dict:
    """Realiza a busca de documentos e gera a resposta com base neles."""
    docs_relacionados = retriever.invoke(pergunta)

    if not docs_relacionados:
        print("🔍 Nenhum documento relacionado encontrado.")
        return {
            "answer": "Não sei.",
            "citacoes": [],
            "contexto_encontrado": False
        }

    answer = document_chain.invoke({
        "input": pergunta,
        "context": docs_relacionados
    })

    txt = (answer or "").strip()

    if txt.rstrip(".!?").lower() == "não sei":
        print("❌ O modelo respondeu 'Não sei'.")
        return {
            "answer": "Não sei.",
            "citacoes": [],
            "contexto_encontrado": False
        }

    print("✔️ Resposta RAG gerada com sucesso.")
    return {
        "answer": txt,
        "citacoes": formatar_citacoes(docs_relacionados, pergunta),
        "contexto_encontrado": True
    }