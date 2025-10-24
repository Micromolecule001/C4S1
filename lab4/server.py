#!/usr/bin/env python3
import os, random
from flask import Flask, request, jsonify

app = Flask(__name__)

# В памяти: сопоставление Idempotency-Key -> результат транзакции.
# Пояснение: при перезапуске сервера это исчезнет — это важно понимать.
processed = {}  # Idempotency-Key -> результат

@app.route("/unstable")
def unstable():
    # 50% - возвращаем ошибку 500 (симуляция временной проблемы)
    if random.random() < 0.5:
        return "temporary error", 500
    return "ok", 200

@app.route("/charge", methods=["POST"])
def charge():
    key = request.headers.get("Idempotency-Key")
    data = request.get_json(silent=True) or {}
    amount = data.get("amount", 0)

    # 30% - временная ошибка
    if random.random() < 0.3:
        return "temporary error", 500

    if not key:
        return "missing Idempotency-Key", 400

    if key in processed:
        # Если ключ уже виделся — возвращаем тот же результат (идемпотентность)
        return jsonify(processed[key])

    # "Обрабатываем" платеж — генерируем tx_id
    txn = {"status": "success", "amount": amount, "tx_id": os.urandom(4).hex()}
    processed[key] = txn
    return jsonify(txn), 200

if __name__ == "__main__":
    # Для разработки: запускаем встроенным сервером Flask
    app.run(host="0.0.0.0", port=8080)

