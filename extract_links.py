import os
import json
import redis

# Connexion à Redis (Docker Compose)
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

DATA_DIR = "./data"  # dossier contenant les fichiers JSON
QUEUE_KEY = "url_queue"  # clé Redis pour les URLs
VISITED_KEY = "visited_urls"  # clé Redis pour les URLs déjà visitées

all_links = set()

# Parcours des fichiers JSON
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".json"):
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                links = data.get("links", [])
                all_links.update(links)
            except json.JSONDecodeError:
                print(f"[ERROR] JSON invalide: {filename}")

# Filtrer les liens déjà visités
new_links = [link for link in all_links if not r.sismember(VISITED_KEY, link)]

# Pousser dans Redis
for link in new_links:
    r.rpush(QUEUE_KEY, link)

print(f"[INFO] {len(new_links)} nouveaux liens ajoutés à la queue Redis")