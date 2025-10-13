from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    prompt = data.get("prompt", "")
    payload = {"model": "phi3", "prompt": prompt}
    response = requests.post(OLLAMA_URL, json=payload, stream=True)

    answer = ""
    for line in response.iter_lines():
        if line:
            part = line.decode("utf-8")
            if '"response":"' in part:
                # вытаскиваем текст
                text = part.split('"response":"')[-1].split('"')[0]
                answer += text
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

