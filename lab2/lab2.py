import time
import json
import redis
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def slow_fetch(key):
    time.sleep(1.5)  # імітуємо повільне джерело даних
    return {
        "key": key,
        "value": random.randint(1, 1000),
        "ts": time.time()
    }

def get_with_cache(key, ttl=110):
    v = r.get(key)
    if v is not None:
        logging.info(f"CACHE HIT key={key}")
        return "HIT", json.loads(v)

    logging.info(f"CACHE MISS key={key} -> fetching...")
    data = slow_fetch(key)

    r.setex(key, ttl, json.dumps(data))
    logging.info(f"CACHE SET key={key} ttl={ttl}s")

    return "MISS", data


key = "user:42"

for i in range(5):
    t0 = time.time()
    kind, data = get_with_cache(key, ttl=118)
    dt = time.time() - t0

    print(kind, f"{dt:.3f}s", data)
    print("TTL:", r.ttl(key), "s")

    time.sleep(1)

print("Redis GET:", r.get(key))

