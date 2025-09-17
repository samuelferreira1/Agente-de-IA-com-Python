from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Carregar .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# Configurar Flask
app = Flask(__name__)

# Instanciar o modelo
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    api_key=GOOGLE_API_KEY
)

# Rota inicial -> carrega a página
@app.route("/")
def index():
    return render_template("index.html")

# Endpoint para o chat
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    pergunta = data.get("message")

    resposta = llm.invoke(pergunta)

    return jsonify({"answer": resposta.content})

if __name__ == "__main__":
    app.run(debug=True)
