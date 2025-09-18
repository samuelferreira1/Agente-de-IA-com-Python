# app.py

import os
from flask import Flask, render_template, request, jsonify
from components.workflow import create_workflow

# Instanciar o grafo compilado apenas uma vez ao iniciar a aplicação
grafo_sd = create_workflow()

# Inicializa a aplicação Flask
app = Flask(__name__, template_folder='templates')

def _is_greeting(message: str) -> bool:
    """Verifica se a mensagem é um cumprimento."""
    greetings = ["olá", "oi", "bom dia", "boa tarde", "boa noite"]
    message_lower = message.strip().lower()
    return any(greeting in message_lower for greeting in greetings)

@app.route("/", methods=["GET"])
def index():
    """Rota principal para renderizar a página inicial do chat."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Rota para processar as mensagens do chat."""
    data = request.json
    pergunta = data.get("message")
    
    if not pergunta:
        return jsonify({"answer": "Por favor, digite uma pergunta."})

    # Verifica se a mensagem é um cumprimento
    if _is_greeting(pergunta):
        return jsonify({"answer": "Olá! Como posso ajudar você hoje?"})

    # Se não for um cumprimento, invoca o fluxo do agente
    resultado = grafo_sd.invoke({"pergunta": pergunta})
    
    resposta_final = {
        "answer": resultado.get('resposta'),
        "acao_final": resultado.get('acao_final'),
        "citacoes": resultado.get('citacoes')
    }
    
    return jsonify(resposta_final)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)