import contextlib
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from recuperer_modeles import lire_github, main, parser_source, retenir  # noqa: E402


def faux_get(url):
    base = "https://api.github.com/repos/agaches/adr"
    reponses = {
        base: {"default_branch": "main"},
        base + "/commits/main": {"sha": "abc123"},
        base + "/contents?ref=abc123": [
            {"type": "file", "name": "adr_simple.md", "download_url": "https://raw/adr_simple.md"},
            {"type": "file", "name": "adr_avance.md", "download_url": "https://raw/adr_avance.md"},
            {"type": "file", "name": "README.md", "download_url": "https://raw/README.md"},
            {"type": "dir", "name": "docs", "download_url": None},
        ],
    }
    if url in reponses:
        return json.dumps(reponses[url]).encode()
    if url.startswith("https://raw/"):
        return b"# modele"
    raise AssertionError("URL inattendue : " + url)


def get_404(url):
    raise urllib.error.HTTPError(url, 404, "Not Found", None, None)


class TestRecupererModeles(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        racine = Path(self._tmp.name)
        self.src = racine / "src"
        self.src.mkdir()
        for nom in ["adr_simple.md", "adr_avance.md", "README.md", "exemple_x.md"]:
            (self.src / nom).write_text("# " + nom)
        self.vide = racine / "vide"
        self.vide.mkdir()
        (self.vide / "README.md").write_text("# lisez-moi")
        self.cible = racine / "projet" / "docs" / "adr" / "modeles"

    def tearDown(self):
        self._tmp.cleanup()

    def lancer(self, *args, **kw):
        sortie, erreur = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreur):
            code = main([str(a) for a in args], **kw)
        return code, sortie.getvalue(), erreur.getvalue()

    def test_retenir(self):
        for nom in ["adr_simple.md", "modele.MD"]:
            self.assertTrue(retenir(nom), nom)
        for nom in ["README.md", "Readme.MD", "exemple_adr.md", "Exemple_x.md", "notes.txt"]:
            self.assertFalse(retenir(nom), nom)

    def test_parser_source(self):
        self.assertEqual(parser_source("agaches/adr"), ("github", "agaches/adr", None))
        self.assertEqual(parser_source("agaches/adr@v1"), ("github", "agaches/adr", "v1"))
        self.assertEqual(parser_source("https://github.com/agaches/adr"), ("github", "agaches/adr", None))
        self.assertEqual(
            parser_source("https://github.com/agaches/adr/tree/main"), ("github", "agaches/adr", "main")
        )
        self.assertEqual(parser_source(str(self.src))[0], "local")

    def test_source_invalide(self):
        code, _, err = self.lancer(self.src / "adr_simple.md", self.cible)
        self.assertEqual(code, 1)
        self.assertTrue(err)
        code, _, _ = self.lancer("pas-un-repo", self.cible)
        self.assertEqual(code, 1)
        self.assertFalse(self.cible.exists())

    def test_copie_locale(self):
        code, _, _ = self.lancer(self.src, self.cible)
        self.assertEqual(code, 0)
        self.assertEqual(
            sorted(p.name for p in self.cible.iterdir()), ["SOURCE.md", "adr_avance.md", "adr_simple.md"]
        )
        source = (self.cible / "SOURCE.md").read_text()
        self.assertIn("- Ref : local", source)
        self.assertIn("- Commit : non versionné", source)
        self.assertIn("- Fichiers : adr_avance.md, adr_simple.md", source)
        self.assertIn("## Quand utiliser chaque modèle", source)

    def test_refus_ecrasement(self):
        self.lancer(self.src, self.cible)
        code, _, err = self.lancer(self.src, self.cible)
        self.assertEqual(code, 1)
        self.assertIn("--maj", err)

    def test_aucun_modele(self):
        code, _, _ = self.lancer(self.vide, self.cible)
        self.assertEqual(code, 1)
        self.assertFalse(self.cible.exists())

    def test_maj_conserve_table_usage(self):
        self.lancer(self.src, self.cible)
        s = self.cible / "SOURCE.md"
        s.write_text(s.read_text() + "| simple | par défaut |\n")
        (self.src / "adr_simple.md").write_text("v2")
        code, sortie, _ = self.lancer(self.src, self.cible, "--maj")
        self.assertEqual(code, 0)
        self.assertIn("| simple | par défaut |", s.read_text())
        self.assertEqual((self.cible / "adr_simple.md").read_text(), "v2")
        self.assertIn("adr_simple.md", sortie)

    def test_maj_signale_supprime_en_amont(self):
        self.lancer(self.src, self.cible)
        (self.src / "adr_avance.md").unlink()
        code, sortie, _ = self.lancer(self.src, self.cible, "--maj")
        self.assertEqual(code, 0)
        self.assertTrue((self.cible / "adr_avance.md").exists())
        self.assertIn("retiré de la source, conservé : adr_avance.md", sortie)

    def test_github_simule(self):
        fichiers, ref, sha = lire_github("agaches/adr", None, faux_get)
        self.assertEqual((ref, sha), ("main", "abc123"))
        self.assertEqual(sorted(fichiers), ["adr_avance.md", "adr_simple.md"])

    def test_github_copie_ecrit_commit(self):
        code, _, _ = self.lancer("agaches/adr", self.cible, http_get=faux_get)
        self.assertEqual(code, 0)
        source = (self.cible / "SOURCE.md").read_text()
        self.assertIn("- Source : agaches/adr", source)
        self.assertIn("- Ref : main", source)
        self.assertIn("- Commit : abc123", source)

    def test_chemin_local_absent_sans_appel_reseau(self):
        for chemin in ["./absent", "../absent"]:
            code, _, err = self.lancer(chemin, self.cible, http_get=get_404)
            self.assertEqual(code, 1)
            self.assertIn("dossier introuvable", err)
        self.assertFalse(self.cible.exists())

    def test_maj_refuse_modeles_non_copies_par_l_outil(self):
        self.cible.mkdir(parents=True)
        (self.cible / "adr_simple.md").write_text("mon modele")
        code, _, err = self.lancer(self.src, self.cible, "--maj")
        self.assertEqual(code, 1)
        self.assertIn("SOURCE.md", err)
        self.assertEqual((self.cible / "adr_simple.md").read_text(), "mon modele")

    def test_refus_ecrasement_sans_source_md_ne_conseille_pas_maj(self):
        self.cible.mkdir(parents=True)
        (self.cible / "adr_simple.md").write_text("mon modele")
        code, _, err = self.lancer(self.src, self.cible)
        self.assertEqual(code, 1)
        self.assertNotIn("--maj", err)

    def test_source_garde_la_ref_donnee(self):
        code, _, _ = self.lancer("agaches/adr@main", self.cible, http_get=faux_get)
        self.assertEqual(code, 0)
        self.assertIn("- Source : agaches/adr@main", (self.cible / "SOURCE.md").read_text())

    def test_source_md_de_la_source_n_est_pas_un_modele(self):
        self.assertFalse(retenir("SOURCE.md"))
        (self.src / "SOURCE.md").write_text("# Source des modèles\n")
        self.lancer(self.src, self.cible)
        self.assertIn("- Fichiers : adr_avance.md, adr_simple.md\n", (self.cible / "SOURCE.md").read_text())

    def test_github_404(self):
        code, _, err = self.lancer("agaches/inexistant", self.cible, http_get=get_404)
        self.assertEqual(code, 1)
        self.assertIn("404", err)
        self.assertFalse(self.cible.exists())


if __name__ == "__main__":
    unittest.main()
