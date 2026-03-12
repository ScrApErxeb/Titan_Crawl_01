import logging
import json
from urllib.parse import urlparse, urlunparse

from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis
from config import Config

logger = logging.getLogger(__name__)

def fingerprint(url: str) -> str:
    """
    Normalise l'URL pour éviter les doublons :
    - supprime le fragment (#)
    - supprime les paramètres de tracking connus
    - standardise le trailing slash
    """
    parsed = urlparse(url)
    
    # Supprimer le fragment
    fragment = ""
    
    # Filtrer certains paramètres inutiles (ex: UTM)
    query_parts = [
        part for part in parsed.query.split("&") 
        if not part.lower().startswith(("utm_", "fbclid", "gclid"))
    ]
    query = "&".join(query_parts)
    
    # Trailing slash standardisé
    path = parsed.path.rstrip("/") or "/"
    
    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        path,
        parsed.params,
        query,
        fragment
    ))
    return normalized

class DatabaseManager:
    def __init__(self):
        self.redis = aioredis.from_url(
            f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}", 
            decode_responses=True
        )
        self.mongo_client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.mongo_client[Config.DB_NAME]
        self.collection = self.db["scraped_data"]

    async def init_db(self):
        """Initialise les index nécessaires pour la performance."""
        try:
            await self.collection.create_index("url", unique=True)
            logger.info("✅ Index MongoDB sur 'url' vérifié/créé.")
        except Exception as e:
            logger.error(f"❌ Erreur init index : {e}")

    # --- Gestion de la file (Queue) ---
    async def is_visited(self, url: str) -> bool:
        fp = fingerprint(url)
        return await self.redis.sismember("crawled_urls", fp)

    async def add_to_queue(self, url: str, depth: int = 0):
        if depth > Config.MAX_DEPTH:
            return

        fp = fingerprint(url)
        added = await self.redis.sadd("seen_urls", fp)
        if added:
            job = json.dumps({"url": url, "depth": depth})
            await self.redis.lpush("url_queue", job)

    async def get_next_url(self, timeout=5):
        job = await self.redis.brpop("url_queue", timeout=timeout)
        return job[1] if job else None

    # --- Sauvegarde ---
    async def save_item(self, item: dict) -> bool:
        try:
            url = item["url"]
            await self.collection.update_one(
                {"url": url},
                {"$set": item},
                upsert=True
            )
            fp = fingerprint(url)
            await self.redis.sadd("crawled_urls", fp)
            return True
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde MongoDB pour {item.get('url')}: {e}")
            return False

    async def close(self):
        self.mongo_client.close()
        await self.redis.aclose()