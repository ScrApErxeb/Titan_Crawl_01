# parsers.py

from typing import Dict, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse

# --- BaseParser ---
class BaseParser:
    """Interface de base pour tous les parsers."""
    def parse(self, html: str, url: str) -> Dict:
        """
        Transforme le HTML en données structurées.
        Doit retourner un dictionnaire contenant au minimum:
        - 'url'
        - 'title'
        - 'links'
        """
        raise NotImplementedError("parse doit être implémenté dans le parser concret")

# --- GenericParser ---
class GenericParser(BaseParser):
    def parse(self, html: str, url: str) -> Dict:
        # Utilisation de lxml pour la vitesse, mais gestion d'erreur possible
        soup = BeautifulSoup(html, "lxml")

        # Extraction sécurisée du titre
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Nettoyage sélectif pour le texte
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        # Extraction des liens avec filtrage
        links = self._extract_clean_links(soup, url)

        return {
            "url": url,
            "title": title,
            "links": list(links),
            "text": soup.get_text(separator=" ", strip=True),
            "domain": urlparse(url).netloc # Utile pour le filtrage ultérieur
        }

    def _extract_clean_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extrait uniquement les liens HTTP(S) valides et uniques."""
        found_links = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href").split('#')[0] # Supprime les ancres
            full_url = urljoin(base_url, href)
            
            # On ne garde que le web (pas de mailto, tel, javascript)
            parsed = urlparse(full_url)
            if parsed.scheme in ("http", "https") and len(full_url) < 2000:
                found_links.add(full_url)
        return found_links