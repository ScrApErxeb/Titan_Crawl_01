# config.py

import os
import random

class Config:
    # --- Identification ---
    APP_NAME = "TitanPro"
    
    # --- Réseau & Infra ---
    REDIS_HOST = "redis"
    REDIS_PORT = 6379
    MONGO_URI = "mongodb://mongodb:27017/"
    DB_NAME = "titanpro_db"

    # --- Crawl Logic ---
    MAX_DEPTH = 2
    CRAWL_DELAY = 1
    DOWNLOAD_DELAY = 1
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3

    # --- Concurrence & Browser ---
    CONCURRENT_THREADS = 10
    USE_BROWSER = False
    USE_PLAYWRIGHT = False

    # --- Storage ---
    STORAGE_TYPE = "file"

    # --- Logging ---
    LOG_LEVEL = "INFO"

    # --- Proxies & User Agents ---
    PROXIES = [
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8002",
        # Ajouter vos proxies ici
    ]
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36",
    ]

# --- Gestion de l'environnement (dev/prod) ---
ENV = os.getenv("APP_ENV", "development").lower()
if ENV == "production":
    Config.CONCURRENT_THREADS = 50
    Config.USE_PLAYWRIGHT = True
    Config.LOG_LEVEL = "INFO"
else:
    Config.CONCURRENT_THREADS = 2
    # En développement, éviter d'avoir trop de DEBUG bruyant par défaut.
    # Utilisez une variable d'environnement si vous avez besoin de DEBUG.
    Config.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")