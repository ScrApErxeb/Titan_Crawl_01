🕷 TitanPro - Guide rapide

Toutes les commandes essentielles pour piloter et monitorer ton crawler asynchrone 🚀

⚡ Cycle de vie (Docker)
🔹 Action	🔧 Commande
Démarrage complet	docker-compose up -d
Arrêt propre	docker-compose down
Redémarrage crawler uniquement	docker-compose restart crawler
Rebuild (nouvelle dépendance/code)	docker-compose build --no-cache crawler


🔍 Logs & Monitoring
🔹 Action	🔧 Commande
Suivre les logs en direct	docker-compose logs -f crawler
Voir les 50 dernières lignes	docker-compose logs --tail=50 crawler
Vérifier l’état des conteneurs	docker ps


🧠 Redis (Queue)
🔹 Action	🔧 Commande
URLs en attente	docker-compose exec redis redis-cli LLEN url_queue
URLs déjà traitées	docker-compose exec redis redis-cli SCARD crawled_urls
Vider la file (RESET)	docker-compose exec redis redis-cli DEL url_queue
Vider les URLs traitées	docker-compose exec redis redis-cli DEL crawled_urls


💾 MongoDB
🔹 Action	🔧 Commande
Nombre total de pages	docker-compose exec mongodb mongosh titanpro_db --eval "db.scraped_data.countDocuments()"
Visualiser les 5 derniers résultats	docker-compose exec mongodb mongosh titanpro_db --eval "db.scraped_data.find().limit(5).pretty()"
Vider la base	docker-compose exec mongodb mongosh titanpro_db --eval "db.scraped_data.drop()"


🛠 Maintenance & Conseils

Injecter de nouveaux seeds

docker-compose exec crawler python seed.py

Nettoyer le cache (pycache)

Get-ChildItem -Path . -Include __pycache__ -Recurse | Remove-Item -Force -Recurse
Astuces pratiques
💡 Situation	📝 Action
Je change juste une ligne de code	Sauvegarde le fichier → le volume fait le reste
Le code semble ne pas changer	docker-compose restart crawler
Nouvelle dépendance pip ajoutée	docker-compose build --no-cache crawler
Nettoyage complet	docker-compose down → docker-compose up -d
Vider la file avant de nouvelles seeds	await r.delete("url_queue")
Injection d’un fichier seeds.txt	docker-compose exec crawler python seed.py