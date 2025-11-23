from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "")
    
    # Явно отключаем стриминг
    payload = {
        "model": "phi3", 
        "prompt": prompt, 
        "stream": False 
    }

    logging.info(f"Sending request to Ollama: {payload}")

    response = requests.post(OLLAMA_URL, json=payload) # stream=True не нужен
    
    if response.status_code == 200:
        # Ollama вернет один JSON объект с полным ответом
        answer = response.json().get("response", "")
        return jsonify({"answer": answer})
    else:
        return jsonify({"error": "Ollama error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

