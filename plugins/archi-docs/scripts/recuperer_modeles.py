#!/usr/bin/env python3
"""Copie des modèles de documents (ADR, DAT...) depuis un repo GitHub ou un dossier local.

Usage : recuperer_modeles.py <source> <cible> [--maj]

<source> : dossier local, ou owner/repo, owner/repo@ref, https://github.com/owner/repo[/tree/<ref>].
Copie les *.md de la racine, sauf README* et exemple*, puis écrit <cible>/SOURCE.md.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com/repos/"
TITRE_USAGE = "## Quand utiliser chaque modèle"
_DEPOT = re.compile(r"^([\w.-]+/[\w.-]+?)(?:\.git)?(?:@(.+))?$")
_URL = re.compile(r"^https://github\.com/([\w.-]+/[\w.-]+?)(?:\.git)?(?:/tree/(.+?))?/?$")


def parser_source(source):
    """Renvoie ("local", chemin, None) ou ("github", "owner/repo", ref ou None)."""
    chemin = Path(source)
    if chemin.exists():
        if not chemin.is_dir():
            raise ValueError(f"la source {source} est un fichier, un dossier est attendu")
        return ("local", str(chemin), None)
    for motif in (_URL, _DEPOT):
        m = motif.match(source)
        if m:
            return ("github", m.group(1), m.group(2))
    raise ValueError(f"source non reconnue : {source} (attendu : dossier, owner/repo[@ref] ou URL GitHub)")


def retenir(nom):
    bas = nom.lower()
    return bas.endswith(".md") and not bas.startswith(("readme", "exemple"))


def lire_local(dossier):
    return {p.name: p.read_bytes() for p in sorted(Path(dossier).iterdir()) if p.is_file() and retenir(p.name)}


def http_get_reseau(url):
    requete = urllib.request.Request(url, headers={"User-Agent": "archi-docs"})
    jeton = os.environ.get("GH_TOKEN")
    if jeton and url.startswith(API):
        requete.add_header("Authorization", "Bearer " + jeton)
    with urllib.request.urlopen(requete, timeout=30) as reponse:
        return reponse.read()


def lire_github(depot, ref, http_get):
    """Renvoie (fichiers retenus, ref résolue, sha du commit)."""
    lire = lambda url: json.loads(http_get(url))  # noqa: E731
    if ref is None:
        ref = lire(API + depot)["default_branch"]
    sha = lire(f"{API}{depot}/commits/{ref}")["sha"]
    entrees = lire(f"{API}{depot}/contents?ref={sha}")
    fichiers = {
        e["name"]: http_get(e["download_url"])
        for e in sorted(entrees, key=lambda e: e["name"])
        if e["type"] == "file" and retenir(e["name"])
    }
    return fichiers, ref, sha


def _table_usage(source_md):
    if not source_md.exists():
        return ""
    texte = source_md.read_text(encoding="utf-8")
    debut = texte.find(TITRE_USAGE)
    return texte[debut + len(TITRE_USAGE):].strip("\n") if debut >= 0 else ""


def ecrire(fichiers, cible, source, ref, commit, maj):
    """Écrit les modèles et SOURCE.md dans cible ; renvoie les noms créés ou modifiés."""
    cible = Path(cible)
    table = _table_usage(cible / "SOURCE.md")
    noms = sorted(fichiers)
    entete = (
        "# Source des modèles\n\n"
        f"- Source : {source}\n- Ref : {ref}\n- Commit : {commit}\n"
        f"- Date : {datetime.date.today().isoformat()}\n- Fichiers : {', '.join(noms)}\n\n"
        f"{TITRE_USAGE}\n\n"
    )
    # Écriture dans un dossier temporaire puis remplacement : rien n'est écrit en cas d'erreur.
    cible.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cible.parent) as tmp:
        tmp = Path(tmp) / cible.name
        if cible.exists():
            shutil.copytree(cible, tmp)
        else:
            tmp.mkdir()
        changes = []
        for nom in noms:
            ancien = tmp / nom
            if not ancien.exists() or ancien.read_bytes() != fichiers[nom]:
                changes.append(nom)
            ancien.write_bytes(fichiers[nom])
        (tmp / "SOURCE.md").write_text(entete + (table + "\n" if table else ""), encoding="utf-8")
        if cible.exists():
            shutil.rmtree(cible)
        shutil.move(str(tmp), str(cible))
    return changes


def _anciens_fichiers(source_md):
    for ligne in source_md.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("- Fichiers : "):
            return [n.strip() for n in ligne[len("- Fichiers : "):].split(",") if n.strip()]
    return []


def main(argv=None, http_get=http_get_reseau):
    p = argparse.ArgumentParser(description="Copie des modèles depuis un repo GitHub ou un dossier local.")
    p.add_argument("source")
    p.add_argument("cible")
    p.add_argument("--maj", action="store_true", help="met à jour des modèles déjà copiés")
    args = p.parse_args(argv)
    cible = Path(args.cible)
    try:
        if cible.exists() and any(cible.iterdir()) and not args.maj:
            raise ValueError(f"{cible} contient déjà des modèles ; relancer avec --maj pour les mettre à jour")
        genre, depot, ref = parser_source(args.source)
        if genre == "local":
            fichiers, ref, commit = lire_local(depot), "local", "non versionné"
        else:
            fichiers, ref, commit = lire_github(depot, ref, http_get)
        if not fichiers:
            raise ValueError(f"aucun modèle trouvé dans {args.source} (*.md hors README et exemple)")
        anciens = _anciens_fichiers(cible / "SOURCE.md") if (cible / "SOURCE.md").exists() else []
        changes = ecrire(fichiers, cible, depot if genre == "github" else args.source, ref, commit, args.maj)
    except urllib.error.HTTPError as e:
        print(f"erreur : GitHub a répondu {e.code} pour {e.url} (repo, ref ou droits d'accès ?)", file=sys.stderr)
        return 1
    except (urllib.error.URLError, OSError, ValueError, KeyError) as e:
        print(f"erreur : {e}", file=sys.stderr)
        return 1
    print(f"Modèles dans {cible} (source {args.source}, ref {ref}).")
    for nom in changes:
        print(f"créé ou modifié : {nom}")
    for nom in sorted(set(anciens) - set(fichiers)):
        print(f"retiré de la source, conservé : {nom}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
