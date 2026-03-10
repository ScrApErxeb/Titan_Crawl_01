# Utilise l'image officielle Playwright qui contient Python 3.12 et toutes les libs système
FROM mcr.microsoft.com/playwright/python:v1.50.0-jammy

# Définir le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Installer uniquement le moteur Chromium (le plus stable pour le scraping)
RUN playwright install chromium

# Commande par défaut
CMD ["python", "main.py"]