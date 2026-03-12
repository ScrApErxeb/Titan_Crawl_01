
import asyncio
import json

import redis.asyncio as redis



async def seed_massive():

    r = redis.from_url("redis://redis:6379", decode_responses=True)

    

    seeds = [

        "https://burkina24.com/"]

    

    print(f"🚀 Injection de {len(seeds)} nouveaux hubs de données...")

    for url in seeds:

        await r.lpush("url_queue", json.dumps({
            "url": url,
            "depth": 0
        }))

        print(f"📡 Ajouté : {url}")

        

    print("---")

    count = await r.llen("url_queue")

    print(f"📈 Total dans la file d'attente : {count}")

    await r.aclose()



if __name__ == "__main__":

    asyncio.run(seed_massive())
    