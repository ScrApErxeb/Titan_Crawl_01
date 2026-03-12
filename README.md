TitanPro Crawler

Un crawler web asynchrone en Python, conçu pour explorer des sites, extraire du contenu structuré, et éviter les doublons grâce à Redis et MongoDB.

⚡ Caractéristiques

Crawling asynchrone avec asyncio et httpx.

Gestion de la file d’attente et des URLs déjà visitées via Redis.

Sauvegarde des données dans MongoDB avec déduplication automatique.

Pipeline de traitement : nettoyage, validation, normalisation des liens.

Gestion du depth pour contrôler la profondeur du crawl.

Retrying automatique sur erreurs réseau (httpx + tenacity).

Extensible : facile à ajouter des fetchers, parsers ou stockages supplémentaires.

🛠️ Prérequis

Python 3.10+

Redis

MongoDB

Dépendances Python :
