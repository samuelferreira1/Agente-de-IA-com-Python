# components/workflow.py

from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, START, END
from .triagem import triagem
from .rag import perguntar_politica_RAG

# --- Definição do Estado ---
class AgentState(TypedDict, total=False):
    pergunta: str
    triagem: dict
    resposta: Optional[str]
    citacoes: List[dict]
    rag_sucesso: bool
    acao_final: str

# --- Nós e Funções de Decisão ---
def node_triagem(state: AgentState) -> AgentState:
    """Nó para triar a pergunta do usuário."""
    print("Executando nó de triagem...")
    return {"triagem": triagem(state["pergunta"])}

def node_auto_resolver(state: AgentState) -> AgentState:
    """Nó para tentar resolver a pergunta usando RAG."""
    print("Executando nó de auto_resolver...")
    pergunta = state["pergunta"]
    resposta_rag = perguntar_politica_RAG(pergunta)

    update: AgentState = {
        "resposta": resposta_rag["answer"],
        "citacoes": resposta_rag.get("citacoes", []),
        "rag_sucesso": resposta_rag["contexto_encontrado"],
    }

    # Define a ação final se o RAG for um sucesso
    if resposta_rag["contexto_encontrado"]:
        update["acao_final"] = "AUTO_RESOLVER"

    return update

def node_pedir_info(state: AgentState) -> AgentState:
    """Nó para solicitar mais informações ao usuário."""
    print("Executando nó de pedir_info...")
    faltantes = state["triagem"].get("campos_faltantes", [])
    detalhe = ",".join(faltantes) if faltantes else "Tema e contexto específico"

    return {
        "resposta": f"Para avançar, preciso que detalhe: {detalhe}",
        "citacoes": [],
        "acao_final": "PEDIR_INFO"
    }

def node_abrir_chamado(state: AgentState) -> AgentState:
    """Nó para abrir um chamado com as informações do usuário."""
    print("Executando nó de abrir_chamado...")
    triagem_data = state["triagem"]

    return {
        "resposta": f"Abrindo chamado com urgência {triagem_data['urgencia']}. Descrição: {state['pergunta'][:140]}",
        "citacoes": [],
        "acao_final": "ABRIR_CHAMADO"
    }

# --- Funções de Transição de Estado ---
KEYWORDS_ABRIR_TICKET = ["aprovação", "exceção", "liberação", "abrir ticket", "abrir chamado", "acesso especial"]

def decidir_pos_triagem(state: AgentState) -> str:
    """Decide o próximo passo após a triagem inicial."""
    print("Decidindo após a triagem...")
    decisao = state["triagem"]["decisao"]

    if decisao == "AUTO_RESOLVER":
        return "auto"
    if decisao == "PEDIR_INFO":
        return "info"
    if decisao == "ABRIR_CHAMADO":
        return "chamado"
    
    # Fallback para garantir que a função sempre retorne um valor válido
    print(f"Valor de triagem inesperado: {decisao}. Retornando para 'info'.")
    return "info"

def decidir_pos_auto_resolver(state: AgentState) -> str:
    """Decide o próximo passo após a tentativa de auto-resolução."""
    print("Decidindo após o auto_resolver...")

    if state.get("rag_sucesso"):
        print("Rag com sucesso, finalizando o fluxo.")
        return "ok"

    pergunta = (state["pergunta"] or "").lower()

    if any(k in pergunta for k in KEYWORDS_ABRIR_TICKET):
        print("Rag falhou, mas keywords de abertura de ticket foram encontradas. Abrindo chamado.")
        return "chamado"

    print("Rag falhou, sem keywords, vou pedir mais informações.")
    return "info"

# --- Criação e Compilação do Grafo ---
def create_workflow():
    """Cria e compila o fluxo de trabalho do agente."""
    workflow = StateGraph(AgentState)

    # Adiciona todos os nós ao grafo
    workflow.add_node("triagem", node_triagem)
    workflow.add_node("auto_resolver", node_auto_resolver)
    workflow.add_node("pedir_info", node_pedir_info)
    workflow.add_node("abrir_chamado", node_abrir_chamado)

    # Adiciona as arestas (edges)
    workflow.add_edge(START, "triagem")
    
    workflow.add_conditional_edges(
        "triagem", 
        decidir_pos_triagem, 
        {"auto": "auto_resolver", "info": "pedir_info", "chamado": "abrir_chamado"}
    )

    workflow.add_conditional_edges(
        "auto_resolver", 
        decidir_pos_auto_resolver, 
        {"info": "pedir_info", "chamado": "abrir_chamado", "ok": END}
    )

    workflow.add_edge("pedir_info", END)
    workflow.add_edge("abrir_chamado", END)

    return workflow.compile()