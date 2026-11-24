"""Tests de trace.py : python3 -m unittest plugins/brain-build/scripts/test_trace.py"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TRACE = os.path.join(HERE, "trace.py")

BESOIN = """\
# Besoin : compteur de mots

## Exigences

### REQ-001 : compter les mots
Critère : `wc.py a.txt` affiche le nombre de mots du fichier.

### REQ-002 : fichier absent
Critère : `wc.py absent.txt` affiche `introuvable` et sort en code 2.
"""

SPEC1 = "# SPEC-001 : comptage\n\nCouvre : REQ-001, REQ-002\n"
PLAN = "# Plan\n\n## ACT-001 : script\n\nSpecs : SPEC-001\nDépend de : aucune\n"
TEST1 = "# REQ-001\ndef test_compte(): pass\n"
TEST2 = "# REQ-002\ndef test_absent(): pass\n"


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content))


def run(*args):
    p = subprocess.run([sys.executable, TRACE, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def git(root, *args):
    subprocess.run(["git", "-C", root, *args], check=True, capture_output=True, text=True)
    return subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def complete_repo(root):
    write(root, "docs/besoin.md", BESOIN)
    write(root, "docs/specs/SPEC-001.md", SPEC1)
    write(root, "docs/plan.md", PLAN)
    write(root, "tests/acceptance/test_compte.py", TEST1)
    write(root, "tests/acceptance/test_absent.py", TEST2)


def kinds(stdout):
    return {(p["kind"], p["id"]) for p in json.loads(stdout)["problems"]}


class Check(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        complete_repo(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, *extra):
        return run("check", self.root, "--tests", "tests/acceptance", *extra)

    def test_repo_complet(self):
        code, out, _ = self.check()
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["problems"], [])

    def test_req_sans_spec(self):
        write(self.root, "docs/specs/SPEC-001.md", "# SPEC-001 : comptage\n\nCouvre : REQ-001\n")
        code, out, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn(("req_sans_spec", "REQ-002"), kinds(out))

    def test_req_sans_test(self):
        os.remove(os.path.join(self.root, "tests/acceptance/test_absent.py"))
        _, out, _ = self.check()
        self.assertIn(("req_sans_test", "REQ-002"), kinds(out))

    def test_req_sans_critere(self):
        write(self.root, "docs/besoin.md", BESOIN.replace("Critère : `wc.py absent", "`wc.py absent"))
        _, out, _ = self.check()
        self.assertEqual({("req_sans_critere", "REQ-002")}, kinds(out))

    def test_spec_orpheline(self):
        write(self.root, "docs/specs/SPEC-002.md", "# SPEC-002 : autre\n\nCouvre : REQ-999\n")
        _, out, _ = self.check()
        self.assertIn(("spec_orpheline", "SPEC-002"), kinds(out))

    def test_act_orpheline(self):
        write(self.root, "docs/plan.md", PLAN + "\n## ACT-002 : rien\n\nSpecs : SPEC-404\n")
        _, out, _ = self.check()
        self.assertIn(("act_orpheline", "ACT-002"), kinds(out))

    def test_spec_sans_act(self):
        write(self.root, "docs/plan.md", "# Plan\n")
        _, out, _ = self.check()
        self.assertIn(("spec_sans_act", "SPEC-001"), kinds(out))

    def test_only_filtre_avant_analyste(self):
        # Avant l'analyste, seul le besoin existe : on ne regarde que les critères.
        for rel in ("docs/specs/SPEC-001.md", "docs/plan.md",
                    "tests/acceptance/test_compte.py", "tests/acceptance/test_absent.py"):
            os.remove(os.path.join(self.root, rel))
        code, out, _ = self.check("--only", "req_sans_critere")
        self.assertEqual(code, 0, out)

    def test_besoin_absent(self):
        os.remove(os.path.join(self.root, "docs/besoin.md"))
        code, _, err = self.check()
        self.assertEqual(code, 2)
        self.assertIn("besoin.md", err)


class Matrix(unittest.TestCase):
    def test_matrice(self):
        with tempfile.TemporaryDirectory() as root:
            complete_repo(root)
            code, out, _ = run("matrix", root, "--tests", "tests/acceptance")
            self.assertEqual(code, 0)
            self.assertIn("| REQ-001 | SPEC-001 | ACT-001 | tests/acceptance/test_compte.py |", out)
            self.assertIn("| REQ-002 | SPEC-001 | ACT-001 | tests/acceptance/test_absent.py |", out)

    def test_matrice_avec_statuts(self):
        with tempfile.TemporaryDirectory() as root:
            complete_repo(root)
            proves = os.path.join(root, "proves.json")
            with open(proves, "w") as f:
                json.dump({"tests": [{"test": "tests/acceptance/test_compte.py",
                                      "depart": "échec", "integration": "passe"}]}, f)
            _, out, _ = run("matrix", root, "--tests", "tests/acceptance", "--proves", proves)
            self.assertIn("test_compte.py | échec | passe |", out)
            self.assertIn("test_absent.py | ? | ? |", out)


class GitRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "t@example.invalid")
        git(self.root, "config", "user.name", "t")
        write(self.root, "wc.py", "import sys\nsys.exit(1)\n")
        git(self.root, "add", ".")
        self.base = git(self.root, "commit", "-q", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, rel, content, message):
        write(self.root, rel, content)
        git(self.root, "add", ".")
        return git(self.root, "commit", "-q", "-m", message)


class Guard(GitRepo):
    def test_guard_dev_touche_tests(self):
        self.commit("tests/acceptance/x.py", "# REQ-001\n", "test: x\n\nAgent: tester REQ-001")
        sha = self.commit("tests/acceptance/x.py", "# REQ-001 modifié\n", "fix\n\nAgent: dev ACT-001")
        code, out, _ = run("guard", self.root, self.base, "HEAD", "--tests", "tests/acceptance")
        self.assertEqual(code, 1)
        violations = json.loads(out)["violations"]
        self.assertEqual([v["sha"] for v in violations], [sha])
        self.assertEqual(violations[0]["files"], ["tests/acceptance/x.py"])

    def test_guard_propre(self):
        self.commit("tests/acceptance/x.py", "# REQ-001\n", "test: x\n\nAgent: tester REQ-001")
        self.commit("wc.py", "print(1)\n", "feat\n\nAgent: dev ACT-001")
        self.commit("tests/unit/test_wc.py", "pass\n", "test unitaire\n\nAgent: dev ACT-001")
        code, out, _ = run("guard", self.root, self.base, "HEAD", "--tests", "tests/acceptance")
        self.assertEqual(code, 0, out)


class Proves(GitRepo):
    # Un « test » est un script : code 0 si wc.py sort en 0.
    TEST = "# REQ-001\nimport subprocess, sys\nsys.exit(subprocess.call([sys.executable, 'wc.py']))\n"
    CMD = f"{sys.executable} {{test}}"

    def proves(self):
        return run("proves", self.root, self.base, "HEAD", "--tests", "tests/acceptance", "--cmd", self.CMD)

    def test_echoue_puis_passe(self):
        self.commit("tests/acceptance/t1.py", self.TEST, "test")
        self.commit("wc.py", "pass\n", "feat")
        code, out, _ = self.proves()
        self.assertEqual(code, 0, out)
        res = json.loads(out)
        self.assertEqual(res["tests"], [{"id": "tests/acceptance/t1.py", "test": "tests/acceptance/t1.py", "reqs": ["REQ-001"],
                                         "depart": "échec", "integration": "passe"}])

    def test_passe_au_depart(self):
        self.commit("wc.py", "pass\n", "feat")
        base_ok = git(self.root, "rev-parse", "HEAD")
        self.base = base_ok
        self.commit("tests/acceptance/t1.py", self.TEST, "test")
        code, out, _ = self.proves()
        self.assertEqual(code, 1)
        self.assertIn(("ne_prouve_rien", "tests/acceptance/t1.py"), kinds(out))

    def test_echoue_sur_integration(self):
        self.commit("tests/acceptance/t1.py", self.TEST, "test")
        code, out, _ = self.proves()
        self.assertEqual(code, 1)
        self.assertIn(("echoue_integration", "tests/acceptance/t1.py"), kinds(out))

    def test_worktrees_nettoyes(self):
        self.commit("tests/acceptance/t1.py", self.TEST, "test")
        self.commit("wc.py", "pass\n", "feat")
        self.proves()
        out = subprocess.run(["git", "-C", self.root, "worktree", "list"],
                             capture_output=True, text=True).stdout
        self.assertEqual(len(out.strip().splitlines()), 1, out)


class ProvesParCas(GitRepo):
    # Trois cas dans un fichier : l'un prouve REQ-001, l'autre passe déjà au départ,
    # le dernier ne cite aucune REQ et hérite de celles du fichier.
    TEST = """\
import subprocess, sys, unittest

def run():
    return subprocess.call([sys.executable, "wc.py"])


class T(unittest.TestCase):
    # REQ-001
    def test_compte(self):
        self.assertEqual(run(), 0)

    # REQ-002
    def test_toujours(self):
        self.assertTrue(True)

    def test_sans_req(self):
        self.assertEqual(run(), 0)
"""
    CMD = f"{sys.executable} -m unittest {{test}} -k {{case}}"
    P = "tests/acceptance/test_t1.py"

    def setUp(self):
        super().setUp()
        self.commit("tests/__init__.py", "", "init")
        self.commit("tests/acceptance/__init__.py", "", "init")
        self.base = git(self.root, "rev-parse", "HEAD")
        self.commit(self.P, "# REQ-003 (fichier)\n" + self.TEST, "test")
        self.commit("wc.py", "pass\n", "feat")

    def proves(self, *extra):
        return run("proves", self.root, self.base, "HEAD", "--tests", "tests/acceptance",
                   "--cmd", self.CMD, *extra)

    def test_un_verdict_par_cas(self):
        code, out, _ = self.proves()
        self.assertEqual(code, 1, out)
        res = {t["id"]: t for t in json.loads(out)["tests"]}
        p = self.P
        self.assertEqual(set(res), {f"{p}::test_compte", f"{p}::test_toujours", f"{p}::test_sans_req"})
        compte = res[f"{p}::test_compte"]
        self.assertEqual((compte["test"], compte["cas"], compte["depart"], compte["integration"]),
                         (p, "test_compte", "échec", "passe"))
        self.assertEqual({("ne_prouve_rien", f"{p}::test_toujours")}, kinds(out))

    def test_req_du_cas_sinon_du_fichier(self):
        _, out, _ = self.proves()
        res = {t["cas"]: t["reqs"] for t in json.loads(out)["tests"]}
        self.assertEqual(res["test_compte"], ["REQ-001"])
        self.assertEqual(res["test_toujours"], ["REQ-002"])
        self.assertEqual(res["test_sans_req"], ["REQ-001", "REQ-002", "REQ-003"])

    def test_motif_de_cas(self):
        code, out, _ = self.proves("--case-regex", r"def (test_compte)\b")
        self.assertEqual(code, 0, out)
        self.assertEqual([t["cas"] for t in json.loads(out)["tests"]], ["test_compte"])

    def test_matrice_par_cas(self):
        _, out, _ = self.proves()
        proves = os.path.join(self.root, "proves.json")
        with open(proves, "w") as f:
            f.write(out)
        write(self.root, "docs/besoin.md", BESOIN)
        _, mat, _ = run("matrix", self.root, "--tests", "tests/acceptance", "--proves", proves)
        p = self.P
        self.assertIn(f"| REQ-001 | ∅ | ∅ | {p}::test_compte | échec | passe |", mat)
        self.assertIn(f"| REQ-002 | ∅ | ∅ | {p}::test_toujours | passe | passe |", mat)
        self.assertNotIn(f"| REQ-002 | ∅ | ∅ | {p}::test_compte |", mat)


class Avertissements(unittest.TestCase):
    """check signale sans échouer : besoin long, constante hors Réglages, critère probabiliste."""

    def check(self, besoin):
        with tempfile.TemporaryDirectory() as root:
            complete_repo(root)
            write(root, "docs/besoin.md", besoin)
            code, out, _ = run("check", root, "--tests", "tests/acceptance")
            res = json.loads(out)
            return code, {(w["kind"], w["id"]) for w in res["warnings"]}, res["warnings"]

    def test_avertissement_sans_echec(self):
        # « sort en code 2 » : constante hors backticks et hors Réglages, signalée sans faire échouer.
        code, found, _ = self.check(BESOIN)
        self.assertEqual((code, found), (0, {("critere_constante", "REQ-002")}))

    def test_constante_hors_reglages(self):
        b = BESOIN + "\n### REQ-003 : vitesse\nCritère : l'ennemi avance de 120 px par seconde.\n"
        b = b.replace("REQ-001, REQ-002", "REQ-001, REQ-002, REQ-003")
        _, found, warnings = self.check(b)
        self.assertIn(("critere_constante", "REQ-003"), found)
        self.assertEqual(next(w for w in warnings if w["id"] == "REQ-003")["valeurs"], ["120"])

    def test_constante_dans_reglages(self):
        b = BESOIN + ("\n### REQ-003 : vitesse\nCritère : l'ennemi avance de 120 px par seconde.\n"
                      "\n## Réglages\n\n| Nom | Valeur | Unité |\n|---|---|---|\n| vitesse | 120 | px/s |\n")
        _, found, _ = self.check(b)
        self.assertNotIn(("critere_constante", "REQ-003"), found)

    def test_litteral_entre_backticks_ignore(self):
        # « sort en code 2 » est hors backticks dans BESOIN : seul REQ-002 est signalé.
        _, found, _ = self.check(BESOIN)
        self.assertNotIn(("critere_constante", "REQ-001"), found)

    def test_critere_probabiliste(self):
        b = BESOIN + "\n### REQ-003 : départ\nCritère : passe à moins de `40 px` pour au moins 15 graines sur 20.\n"
        _, found, _ = self.check(b)
        self.assertIn(("critere_probabiliste", "REQ-003"), found)

    def test_besoin_long(self):
        b = BESOIN + "".join(f"\n### REQ-{i:03d} : r\nCritère : `ok`.\n" for i in range(3, 18))
        code, found, _ = self.check(b)
        self.assertIn(("besoin_long", "REQ"), found)
        self.assertEqual(code, 1)  # REQ sans spec : ce sont les problèmes qui fixent le code


class SousDossier(GitRepo):
    """Projet dans un sous-dossier du dépôt : chemins et commandes relatifs au projet."""

    def setUp(self):
        super().setUp()
        self.commit("jeu/wc.py", "import sys\nsys.exit(1)\n", "init jeu")
        self.base = git(self.root, "rev-parse", "HEAD")
        self.projet = os.path.join(self.root, "jeu")

    def test_guard(self):
        self.commit("jeu/tests/acceptance/x.py", "# REQ-001\n", "fix\n\nAgent: dev ACT-001")
        code, out, _ = run("guard", self.projet, self.base, "HEAD", "--tests", "tests/acceptance")
        self.assertEqual(code, 1, out)
        self.assertEqual(json.loads(out)["violations"][0]["files"], ["tests/acceptance/x.py"])

    def test_guard_ignore_tests_hors_projet(self):
        self.commit("tests/acceptance/x.py", "# REQ-001\n", "fix\n\nAgent: dev ACT-001")
        code, out, _ = run("guard", self.projet, self.base, "HEAD", "--tests", "tests/acceptance")
        self.assertEqual(code, 0, out)

    def test_proves(self):
        self.commit("jeu/tests/acceptance/t1.py", Proves.TEST, "test")
        self.commit("jeu/wc.py", "pass\n", "feat")
        code, out, _ = run("proves", self.projet, self.base, "HEAD", "--tests", "tests/acceptance",
                           "--cmd", Proves.CMD)
        self.assertEqual(code, 0, out)
        t = json.loads(out)["tests"][0]
        self.assertEqual((t["id"], t["depart"], t["integration"]),
                         ("tests/acceptance/t1.py", "échec", "passe"))


def run_json(path, session, agent=None, ids=(), cost=0.0, model="claude-sonnet-5-5"):
    d = {"type": "result", "session_id": session, "total_cost_usd": cost,
         "modelUsage": {model: {}}}
    if agent:
        d["structured_output"] = {"status": "done", "agent": agent, "ids": list(ids), "summary": "."}
    with open(path, "w", encoding="utf-8") as f:
        f.write("du bruit du lanceur\n" + json.dumps(d) + "\n")


class Audit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runs = os.path.join(self.tmp.name, "runs")
        self.transcripts = os.path.join(self.tmp.name, "projects")
        os.makedirs(os.path.join(self.transcripts, "-wt-tests-1"))
        os.makedirs(self.runs)
        self.cwd = "/wt/tests-1"

    def tearDown(self):
        self.tmp.cleanup()

    def transcript(self, session, uses):
        path = os.path.join(self.transcripts, "-wt-tests-1", f"{session}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "user", "cwd": self.cwd}) + "\n")
            for name, inp in uses:
                content = [{"type": "tool_use", "name": name, "input": inp}]
                f.write(json.dumps({"type": "assistant", "cwd": self.cwd,
                                    "message": {"content": content}}) + "\n")

    def audit(self, *names):
        extra = [n for n in names if not n.endswith(".json")]
        names = [n for n in names if n.endswith(".json")]
        return run("audit", *[os.path.join(self.runs, n) for n in names], *extra, "--tests", "tests/acceptance",
                   "--test-cmd", "node --test", "--transcripts", self.transcripts)

    def test_lectures_autorisees(self):
        run_json(os.path.join(self.runs, "tests-1.json"), "s1", "tester")
        self.transcript("s1", [
            ("Read", {"file_path": "/wt/tests-1/docs/specs/SPEC-001.md"}),
            ("Read", {"file_path": "/wt/tests-1/docs/besoin.md"}),
            ("Bash", {"command": "cat docs/build/config.md; ls docs; grep -n x tests/acceptance/a.test.js 2>/dev/null"}),
            ("Bash", {"command": "node --test tests/acceptance"}),
            ("Bash", {"command": "git add tests/acceptance && git commit -m 'test: couvre js/audio.js'"}),
            ("Write", {"file_path": "/wt/tests-1/tests/acceptance/a.test.js"}),
            ("Bash", {"command": "cd docs/specs && cat SPEC-*.md; find . -path ./.git -prune; node --version"}),
            ("Bash", {"command": "cat docs/normes.md"}),
            ("Read", {"file_path": os.path.join(self.transcripts, "-wt-tests-1", "s1", "tool-results", "x.txt")}),
        ])
        code, out, _ = self.audit("tests-1.json", "--allow", "docs/normes.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["problems"], [])

    def test_fuites(self):
        run_json(os.path.join(self.runs, "tests-1.json"), "s1", "tester")
        self.transcript("s1", [
            ("Read", {"file_path": "/wt/tests-1/docs/plan.md"}),
            ("Bash", {"command": "node -e \"const {delta}=require('./js/delta.js')\""}),
            ("Read", {"file_path": "/wt/tests-1/../ancien/conception.md"}),
            ("Read", {"file_path": "/wt/tests-1/index.html"}),
            ("Grep", {"pattern": "delta"}),
            ("Bash", {"command": "git show HEAD:js/level.js"}),
        ])
        code, out, _ = self.audit("tests-1.json")
        self.assertEqual(code, 1)
        found = [(p["kind"], p["cible"]) for p in json.loads(out)["problems"]]
        self.assertEqual(found, [
            ("lecture_plan", "docs/plan.md"),
            ("execution", "node -e \"const {delta}=require('./js/delta.js')\""),
            ("lecture_code", "js/delta.js"),
            ("lecture_hors_projet", "/wt/ancien/conception.md"),
            ("lecture_code", "index.html"),
            ("lecture_code", "."),
            ("lecture_code", "js/level.js"),
        ])

    def test_agent_lance_hors_du_projet(self):
        # Agent lancé à la racine du dépôt, projet dans jeu/ : --root rend les chemins au projet.
        run_json(os.path.join(self.runs, "tests-1.json"), "s1", "tester")
        self.transcript("s1", [("Bash", {"command": "cat jeu/docs/besoin.md jeu/js/a.js"})])
        _, out, _ = self.audit("tests-1.json", "--root", "jeu")
        self.assertEqual([p["cible"] for p in json.loads(out)["problems"]], ["js/a.js"])

    def test_transcription_introuvable(self):
        run_json(os.path.join(self.runs, "tests-2.json"), "absente", "tester")
        code, out, _ = self.audit("tests-2.json")
        self.assertEqual(code, 1)
        self.assertEqual([p["kind"] for p in json.loads(out)["problems"]], ["transcription_introuvable"])


class Cost(unittest.TestCase):
    def test_couts_par_role_et_action(self):
        with tempfile.TemporaryDirectory() as runs:
            run_json(os.path.join(runs, "specs.json"), "a", "analyst", ["SPEC-001"], 2.0, "claude-opus-5-5")
            run_json(os.path.join(runs, "tests-1.json"), "b", "tester", ["REQ-001"], 1.0)
            run_json(os.path.join(runs, "ACT-001.json"), "c", "dev", ["ACT-001"], 0.5)
            run_json(os.path.join(runs, "ACT-001-r2.json"), "d", "dev", ["ACT-001"], 0.7, "claude-opus-5-5")
            run_json(os.path.join(runs, "ACT-002.json"), "e", None, (), 0.25)  # failed, sans structured_output
            run_json(os.path.join(runs, "diag-REQ-001-1.json"), "f", "tester", ["REQ-001"], 0.3)
            code, out, _ = run("cost", runs)
        self.assertEqual(code, 0, out)
        self.assertIn("| analyst | 1 | 0 | 2,00 | claude-opus-5-5 |", out)
        self.assertIn("| tester | 1 | 0 | 1,00 | claude-sonnet-5-5 |", out)
        self.assertIn("| dev | 3 | 1 | 1,45 | claude-opus-5-5, claude-sonnet-5-5 |", out)
        self.assertIn("| diagnostic | 1 | 0 | 0,30 | claude-sonnet-5-5 |", out)
        self.assertIn("| ACT-001 | 2 | 1 | 1,20 |", out)
        self.assertIn("| ACT-002 | 1 | 0 | 0,25 |", out)
        self.assertIn("Total : 4,75 $", out)


if __name__ == "__main__":
    unittest.main()
