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


if __name__ == "__main__":
    unittest.main()
