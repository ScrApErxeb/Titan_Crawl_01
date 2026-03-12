import hashlib
from urllib.parse import urlparse, parse_qs, urlencode

TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref"
}

def normalize_url(url: str) -> str:
    parsed = urlparse(url)

    # supprimer fragment (#section)
    fragmentless = parsed._replace(fragment="")

    # nettoyer paramètres tracking
    query = parse_qs(fragmentless.query)
    filtered = {
        k: v for k, v in query.items()
        if k not in TRACKING_PARAMS
    }

    new_query = urlencode(filtered, doseq=True)

    normalized = fragmentless._replace(query=new_query)

    return normalized.geturl().rstrip("/")


def fingerprint(url: str) -> str:
    normalized = normalize_url(url)
    return hashlib.sha1(normalized.encode()).hexdigest()