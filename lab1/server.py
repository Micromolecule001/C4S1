#!/usr/bin/env python3
import os, random, threading, time, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Память для idempotent-ключей
processed = {}  # Idempotency-Key -> результат

# ---------------------------
#        ENDPOINT 1
# ---------------------------
@app.route("/unstable")
def unstable():
    if random.random() < 0.5:
        return "temporary error", 500
    return "ok", 200


# ---------------------------
#        ENDPOINT 2
# ---------------------------
@app.route("/charge", methods=["POST"])
def charge():
    key = request.headers.get("Idempotency-Key")
    print(f'Key: {key}\n')
    data = request.get_json(silent=True) or {}
    amount = data.get("amount", 0)

    # 30% шанс ошибки
    if random.random() < 0.3:
        return "temporary error", 500

    if not key:
        return "missing Idempotency-Key", 400

    if key in processed:
        return jsonify(processed[key])

    # создаём транзакцию
    txn = {"status": "success", "amount": amount, "tx_id": os.urandom(4).hex()}
    processed[key] = txn
    return jsonify(txn), 200


# ----------------------------------------------------
# requsts spam
# ----------------------------------------------------
def auto_requests():
    URL = "http://127.0.0.1:8080"
    IDEMP_KEY_1 = "01234abcdef"
    IDEMP_KEY_2 = "newKey12345"

    time.sleep(1)

    counter = 1

    while True:
        while counter < 10:
            print(f"\n--- ЦИКЛ {counter} ---")
            # ----------- GET /unstable -----------
            try:
                r = requests.get(f"{URL}/unstable")
                print("[GET /unstable]", r.status_code, r.text)
            except Exception as e:
                print("[GET ERROR]", e)

            # ----------- POST /charge -----------
            try:
                key = IDEMP_KEY_1
                if (counter > 5):
                    key = IDEMP_KEY_2

                r = requests.post(
                    f"{URL}/charge",
                    headers={
                        "Content-Type": "application/json",
                        "Idempotency-Key": key 
                    },
                    json={"amount": 100}
                )
                print("[POST /charge]", r.status_code, r.text)
            except Exception as e:
                print("[POST ERROR]", e)

            counter += 1
            time.sleep(1)


if __name__ == "__main__":
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False),
        daemon=True
    ).start()

    auto_requests()

