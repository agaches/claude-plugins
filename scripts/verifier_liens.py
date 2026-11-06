"""Vérifie les liens http(s) de fichiers Markdown.

Usage : python3 scripts/verifier_liens.py FICHIER.md [FICHIER.md ...]
Imprime une ligne par URL non ok ; code de sortie 1 si au moins une URL est ko.
Un 403, 429 ou 503 (site qui bloque ou limite les robots) est signalé « a-verifier » sans échouer.
"""

import re
import sys
import urllib.error
import urllib.request

_URL = re.compile(r"https?://[^\s<>()\[\]\"'`]+")
_UA = "premiers-pas-link-check"
_A_VERIFIER = (403, 429, 503)  # robots bloqués, quota, défi anti-robot : pas une preuve de lien mort


def extraire_urls(texte: str) -> list[str]:
    urls = []
    for brut in _URL.findall(texte):
        url = brut.rstrip(".,;:!?*")
        if url not in urls:
            urls.append(url)
    return urls


def _statut(url: str, methode: str, timeout: float) -> int:
    req = urllib.request.Request(url, method=methode, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def verifier(url: str, timeout: float = 10.0) -> tuple[str, str]:
    try:
        code = _statut(url, "HEAD", timeout)
        if code in (403, 405):
            code = _statut(url, "GET", timeout)
    except (urllib.error.URLError, OSError, ValueError) as e:
        return "ko", f"injoignable : {e}"
    if code in _A_VERIFIER:
        return "a-verifier", f"HTTP {code}, site qui bloque ou limite peut-être les robots : ouvrir à la main"
    if code >= 400:
        return "ko", f"HTTP {code}"
    return "ok", f"HTTP {code}"


def main(argv: list[str]) -> int:
    echec = False
    for chemin in argv:
        with open(chemin, encoding="utf-8") as f:
            urls = extraire_urls(f.read())
        for url in urls:
            statut, detail = verifier(url)
            if statut != "ok":
                print(f"{statut}\t{chemin}\t{url}\t{detail}")
            echec |= statut == "ko"
    return 1 if echec else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
