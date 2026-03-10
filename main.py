import asyncio
import signal
from datetime import datetime, timezone
from urllib.parse import urlparse

# On utilise les versions asynchrones des bibliothèques
from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis

# Tes modules locaux
from fetcher.http_fetcher import HttpFetcher
from parser.generic_parser import GenericParser
from pipeline.cleaner import Cleaner
from pipeline.manager import PipelineManager
from config.settings import Config

class TitanCrawler:
    def __init__(self):
        # 1 & 4. Connexions Asynchrones Unifiées
        self.redis = aioredis.from_url(
            f"redis://{Config.REDIS_HOST}", 
            decode_responses=True
        )
        self.mongo_client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.mongo_client[Config.DB_NAME]
        
        # 3. Fetcher avec Pool de connexions
        self.fetcher = HttpFetcher()
        self.parser = GenericParser()
        self.cleaner = Cleaner()
        self.pipeline = PipelineManager(self.cleaner)

        # 7. Sécurité : Whitelist de domaines
        self.allowed_domains = {
            "news.ycombinator.com", "wikipedia.org", 
            "reuters.com", "bbc.com", "github.com", "dev.to"
        }
        self.max_links_per_page = Config.CONCURRENT_THREADS * 2
        self.is_running = True

# ... (Gardes tes imports et ton __init__ identiques) ...

    async def worker(self, worker_id: int):
        print(f"👷 Worker {worker_id} : Lancé à pleine balle.")
        
        while self.is_running:
            try:
                job = await self.redis.brpop("url_queue", timeout=5)
                if not job: continue
                url = job[1]

                if not await self.redis.sadd("crawled_urls", url):
                    continue

                html = await self.fetcher.fetch(url)
                if not html: continue

                raw_data = self.parser.parse(html, url)
                clean_data = self.pipeline.process_item(raw_data, url)

                if clean_data:
                    await self.db.scraped_data.update_one(
                        {"url": url}, {"$set": clean_data}, upsert=True
                    )

                    # 🔥 EXPLORATION ILLIMITÉE ICI
                    links = raw_data.get("links", [])
                    for link in links[:50]: # On prend les 50 premiers liens par page
                        # On vérifie juste si on l'a déjà vu, c'est tout !
                        if not await self.redis.sismember("crawled_urls", link):
                            await self.redis.lpush("url_queue", link)

            except Exception as e:
                print(f"🔥 Erreur Worker {worker_id} : {e}")
            
            await asyncio.sleep(0.1) # On réduit le délai au minimum
    async def shutdown(self, sig=None):
        """Arrêt propre des connexions"""
        print(f"\n🛑 Signal {sig} reçu. Fermeture des vannes...")
        self.is_running = False
        await self.fetcher.close()
        self.mongo_client.close()
        await self.redis.close()
        print("👋 TitanPro s'est arrêté proprement.")

    async def run(self):
        num_workers = Config.CONCURRENT_THREADS
        print(f"🚀 Démarrage de {Config.APP_NAME}")
        print(f"⚙️  Cibles : {list(self.allowed_domains)}")

        # Lancement des workers en parallèle
        workers = [self.worker(i) for i in range(num_workers)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    crawler = TitanCrawler()
    loop = asyncio.get_event_loop()

    # Gestion propre de l'arrêt (Ctrl+C)
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(crawler.shutdown(sig)))

    try:
        loop.run_until_complete(crawler.run())
    except Exception as e:
        print(f"Dernière erreur avant crash : {e}")