import re
import logging
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Set
from config import Config

logger = logging.getLogger(__name__)

# --- Cleaner ---
class Cleaner:
    """Nettoie le texte et les caractères invisibles"""
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Supprime les caractères de contrôle et normalise les espaces
        text = re.sub(r"[\x00-\x1f\x7f]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

# --- Validator ---
class Validator:
    """Valide l'intégrité minimale des données"""
    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return all([parsed.scheme in ('http', 'https'), parsed.netloc])
        except Exception:
            return False

    def validate(self, data: Dict) -> bool:
        # On rejette si l'URL est invalide
        if not data.get("url") or not self.is_valid_url(data["url"]):
            return False
        
        # On rejette si le contenu est vide (pas de titre ET pas de texte)
        if not data.get("title") and not data.get("text"):
            logger.warning(f"Dropping empty item: {data.get('url')}")
            return False
            
        return True

# --- Transformer ---
class Transformer:
    """Normalise les URLs et les formats de données"""
    def transform_links(self, links: List[str], base_url: str) -> List[str]:
        unique_links: Set[str] = set()
        for link in links:
            if not isinstance(link, str) or not link.strip():
                continue
            
            # 1. Normalisation (URL absolue + suppression des ancres #)
            abs_link = urljoin(base_url, link.strip()).split('#')[0]
            
            # 2. Filtrage des protocoles non-web (mailto, tel, etc.)
            parsed = urlparse(abs_link)
            if parsed.scheme in ('http', 'https'):
                unique_links.add(abs_link)
        
        return list(unique_links)

# --- PipelineManager ---
class PipelineManager:
    def __init__(self):
        self.cleaner = Cleaner()
        self.validator = Validator()
        self.transformer = Transformer()

    def process_item(self, raw_item: Dict, url: str) -> Optional[Dict]:
        """Orchestre le nettoyage, la validation et la transformation."""
        if not raw_item:
            return None

        try:
            # 1. Nettoyage initial (on garde la structure brute)
            processed_data = {
                "url": url,
                "title": self.cleaner.clean_text(raw_item.get("title", "")),
                "description": self.cleaner.clean_text(raw_item.get("description", "")),
                "h1": self.cleaner.clean_text(raw_item.get("h1", "")),
                "text": self.cleaner.clean_text(raw_item.get("text", "")),
                "links": raw_item.get("links") or [],
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "spider_version": getattr(Config, "APP_NAME", "unknown_spider")
            }

            # 2. Validation (Est-ce que l'item mérite d'être sauvé ?)
            if not self.validator.validate(processed_data):
                return None

            # 3. Transformation (Normalisation des liens)
            processed_data["links"] = self.transformer.transform_links(
                processed_data["links"], 
                url
                )[:200]

            return processed_data

        except Exception as e:
            logger.error(f"❌ Pipeline error on {url}: {e}", exc_info=True)
            return None