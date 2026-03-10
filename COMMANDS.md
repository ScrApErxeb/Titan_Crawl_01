# TitanPro - Aide-mémoire opérationnel

Voici les commandes essentielles pour piloter, monitorer et maintenir ton crawler asynchrone.

## 🚀 Cycle de vie (Docker)
| Action | Commande |
| :--- | :--- |
| **Démarrage complet** | `docker-compose up -d` |
| **Arrêt propre** | `docker-compose down` |
| **Redémarrage (crawler uniquement)** | `docker-compose restart crawler` |
| **Rebuild (si modif dépendances/code)** | `docker-compose build --no-cache crawler` |

## 🔍 Monitoring & Logs
| Action | Commande |
| :--- | :--- |
| **Suivre les logs en direct** | `docker-compose logs -f crawler` |
| **Voir les 50 dernières lignes** | `docker-compose logs --tail=50 crawler` |
| **Vérifier l'état des conteneurs** | `docker ps` |

## 🧠 Redis (File d'attente)
| Action | Commande |
| :--- | :--- |
| **URLs en attente (queue)** | `docker-compose exec redis redis-cli LLEN url_queue` |
| **URLs déjà traitées (set)** | `docker-compose exec redis redis-cli SCARD crawled_urls` |
| **Vider la file (RESET complet)** | `docker-compose exec redis redis-cli DEL url_queue` |

## 💾 MongoDB (Stockage)
| Action | Commande |
| :--- | :--- |
| **Nombre total de pages récoltées** | `docker-compose exec mongodb mongosh titanpro_db --eval "db.scraped_data.countDocuments()"` |
| **Visualiser les 5 derniers résultats** | `docker-compose exec mongodb mongosh titanpro_db --eval "db.scraped_data.find().limit(5).pretty()"` |
| **Vider la base de données** | `docker-compose exec mongodb mongosh titanpro_db --eval "db.scraped_data.drop()"` |

## 🌐 Maintenance
* **Injecter de nouveaux seeds** : 
  `docker-compose exec crawler python seed.py`
* **Nettoyage des fichiers cache (PowerShell)** : 
  `Get-ChildItem -Path . -Include __pycache__ -Recurse | Remove-Item -Force -Recurse`



  SituationAction à faire
  Je change une ligne de code  
  Sauvegarde simplement ton fichier, 
  le volume fait le travail
  
  .Le code semble ne pas changer
  docker-compose restart crawler



  J'ai ajouté une dépendance (pip)
  docker-compose build --no-cache crawler
  Je veux tout nettoyer proprement
  docker-compose down puis docker-compose up -d


  vider la file avant d'injecter de nouveaux seeds
  await r.delete("url_queue")

  Une fois ton fichier seeds.txt créé, lance simplement :
  docker-compose exec crawler python seed.py