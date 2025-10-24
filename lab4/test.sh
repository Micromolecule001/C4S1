#!/usr/bin/env bash
# Тесты для CloudLab-01

URL="http://127.0.0.1:8080"
KEY="lab1key123"

echo "=== ТЕСТ 1: GET /unstable ==="
for i in {1..5}; do
  echo -n "Запрос $i: "
  curl -s -o /dev/null -w "%{http_code}\n" "$URL/unstable"
done
echo

echo "=== ТЕСТ 2: POST /charge с одним ключом ==="
for i in {1..5}; do
  echo "Запрос $i:"
  curl -s -X POST "$URL/charge" \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: $KEY" \
    -d '{"amount":100}' | jq .
done
echo

echo "=== ТЕСТ 3: POST /charge с разными ключами ==="
for i in {1..3}; do
  NEWKEY="key$i-$(date +%s)"
  echo "Запрос с ключом $NEWKEY:"
  curl -s -X POST "$URL/charge" \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: $NEWKEY" \
    -d '{"amount":200}' | jq .
done

