import asyncio
import logging
import json

from config import Config
from database import DatabaseManager
from fetchers import HttpFetcher, Action
from parsers import GenericParser
from pipeline import PipelineManager

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# Réduire le bruit de logs provenant des bibliothèques externes (p.ex. heartbeats
# pymongo, sortie verbose d'urllib3/httpx, ou logs debug d'asyncio). Conserver
# le niveau configuré pour l'application via Config.LOG_LEVEL.
# On met ces loggers dépendances en WARNING pour éviter d'avoir trop de DEBUG/INFO.
for noisy in (
    "pymongo",
    "pymongo.monitoring",
    "motor",
    "urllib3",
    "urllib3.connectionpool",
    "httpx",
    "asyncio",
    "boto3",
    "botocore",
):
    try:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    except Exception:
        # Ne pas échouer si un logger n'existe pas
        pass


class TitanCrawler:

    def __init__(self):
        self.db = DatabaseManager()
        self.fetcher = HttpFetcher(Config.USER_AGENTS)
        self.parser = GenericParser()
        self.pipeline = PipelineManager()

    async def process_url(self, job):

        job_data = json.loads(job)
        url = job_data["url"]
        depth = job_data["depth"]

        if await self.db.is_visited(url):
            return

        logger.info(f"🌐 Crawling {url} (depth={depth})")

        result = await self.fetcher.fetch(url)

        if result["action"] != Action.SUCCESS:
            logger.warning(f"⚠️ Fetch failed {url}")
            return

        html = result["html"]

        raw_item = self.parser.parse(html, url)

        processed = self.pipeline.process_item(raw_item, url)

        if not processed:
            return

        saved = await self.db.save_item(processed)

        if not saved:
            return

        # Ajout des nouveaux liens
        for link in processed.get("links", []):
            await self.db.add_to_queue(link, depth + 1)

    async def worker(self):

        while True:

            job = await self.db.get_next_url()

            if not job:
                await asyncio.sleep(1)
                continue

            try:
                await self.process_url(job)

            except Exception as e:
                logger.error(f"❌ Worker error: {e}", exc_info=True)

            await asyncio.sleep(Config.CRAWL_DELAY)

    async def run(self):

        logger.info("🚀 TitanPro crawler starting...")

        await self.db.init_db()

        workers = [
            asyncio.create_task(self.worker())
            for _ in range(Config.CONCURRENT_THREADS)
        ]

        await asyncio.gather(*workers)


async def main():

    crawler = TitanCrawler()

    try:
        await crawler.run()

    except KeyboardInterrupt:
        logger.info("🛑 Shutdown crawler")

    finally:
        await crawler.fetcher.close()
        await crawler.db.close()


if __name__ == "__main__":
    asyncio.run(main())