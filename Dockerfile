# Dockerfile corrigé pour TitanPro

# 1️⃣ Base image Playwright + Python
FROM mcr.microsoft.com/playwright/python:v1.50.0-jammy

# 2️⃣ Définir le répertoire de travail
WORKDIR /app

# 3️⃣ Installer les dépendances système nécessaires pour lxml et autres libs Python
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt1-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ Copier requirements et installer les packages Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copier tout le projet
COPY . .

# 6️⃣ Installer Chromium (Playwright)
RUN playwright install chromium

# 7️⃣ Commande par défaut pour lancer le crawler
CMD ["python", "main.py"]