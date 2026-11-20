#!/usr/bin/env python3
"""Traçabilité du kit brain-build : REQ (besoin) → SPEC (specs) → ACT (plan) → tests.

Sous-commandes (sortie sur stdout ; code 0 = rien à signaler, 1 = problèmes, 2 = erreur d'usage) :

  check  <repo> [--tests DIR] [--only k1,k2]   liens et orphelins, JSON {"problems": [...]}
  matrix <repo> [--tests DIR] [--proves F]     matrice Markdown REQ → SPEC → ACT → tests
  guard  <repo> <base> <head> [--tests DIR]    commits « Agent: dev » qui touchent DIR, JSON
  proves <repo> <base> <head> --cmd CMD [--tests DIR]
         chaque test ajouté ou modifié entre base et head échoue sur base et passe sur head.
         CMD est lancé depuis la racine d'un worktree temporaire ; {test} y est remplacé par le
         chemin du test (sinon le chemin est ajouté en fin de commande).
         Avec {case} dans CMD : un verdict par cas de test (--case-regex, défaut « def test… »),
         chaque cas portant les REQ de son bloc (sinon celles du fichier) ; id « chemin::cas ».

Conventions lues :
  docs/besoin.md  une REQ par titre « ### REQ-001 : ... », suivi d'une ligne « Critère : ... »
  docs/specs/*.md  titre « # SPEC-001 : ... » ; les REQ citées dans le fichier sont couvertes
  docs/plan.md     une section « ## ACT-001 : ... » ; les SPEC citées dans la section
  tests            tout fichier de DIR (défaut tests/acceptance) qui cite une REQ

Stdlib uniquement.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

ID = re.compile(r"\b(REQ|SPEC|ACT)-\d{3}\b")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
CRITERE = re.compile(r"^\s*(?:[-*]\s*)?\**crit[eè]res?(?: d'acceptation)?\**\s*:", re.IGNORECASE)
DEFAULT_TESTS = "tests/acceptance"
DEFAULT_CASE = r"^\s*(?:async\s+)?def\s+(test\w*)"


def ids(text, prefix):
    return sorted({m.group(0) for m in ID.finditer(text) if m.group(1) == prefix})


def sections(text, prefix):
    """Découpe un Markdown en sections dont le titre commence par PREFIX-xxx."""
    out, current = {}, None
    for line in text.splitlines():
        h = HEADING.match(line)
        if h:
            m = re.match(rf"({prefix}-\d{{3}})\b", h.group(1))
            current = m.group(1) if m else None
            if current:
                out.setdefault(current, [])
            continue
        if current:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load(repo, tests_dir):
    besoin_path = os.path.join(repo, "docs", "besoin.md")
    if not os.path.isfile(besoin_path):
        sys.exit(f"trace.py : besoin introuvable : {besoin_path}")  # SystemExit(str) ⇒ code 2 dans main()
    reqs = {}
    for req, body in sections(read(besoin_path), "REQ").items():
        reqs[req] = any(CRITERE.match(line) for line in body.splitlines())

    specs = {}  # SPEC -> REQ citées
    specs_dir = os.path.join(repo, "docs", "specs")
    if os.path.isdir(specs_dir):
        for name in sorted(os.listdir(specs_dir)):
            if not name.endswith(".md"):
                continue
            text = read(os.path.join(specs_dir, name))
            own = ids(name, "SPEC") or ids(text.splitlines()[0] if text else "", "SPEC")
            for spec in own[:1]:
                specs[spec] = ids(text, "REQ")

    plan_path = os.path.join(repo, "docs", "plan.md")
    plan = None  # None = pas encore de plan
    if os.path.isfile(plan_path):
        plan = {act: ids(body, "SPEC") for act, body in sections(read(plan_path), "ACT").items()}

    tests = {}  # chemin relatif -> REQ citées
    root = os.path.join(repo, tests_dir)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d != "__pycache__")
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            try:
                found = ids(read(path), "REQ")
            except (UnicodeDecodeError, OSError):
                continue
            if found:
                tests[os.path.relpath(path, repo).replace(os.sep, "/")] = found
    return reqs, specs, plan, tests


def problems(reqs, specs, plan, tests):
    out = []
    for req, has_critere in sorted(reqs.items()):
        if not has_critere:
            out.append({"kind": "req_sans_critere", "id": req})
        if not any(req in r for r in specs.values()):
            out.append({"kind": "req_sans_spec", "id": req})
        if not any(req in r for r in tests.values()):
            out.append({"kind": "req_sans_test", "id": req})
    for spec, cited in sorted(specs.items()):
        if not cited or any(r not in reqs for r in cited):
            out.append({"kind": "spec_orpheline", "id": spec, "cite": cited})
        if plan is not None and not any(spec in s for s in plan.values()):
            out.append({"kind": "spec_sans_act", "id": spec})
    for act, cited in sorted((plan or {}).items()):
        if not cited or any(s not in specs for s in cited):
            out.append({"kind": "act_orpheline", "id": act, "cite": cited})
    for test, cited in sorted(tests.items()):
        if any(r not in reqs for r in cited):
            out.append({"kind": "test_orphelin", "id": test, "cite": cited})
    return out


def cmd_check(a):
    found = problems(*load(a.repo, a.tests))
    if a.only:
        keep = set(a.only.split(","))
        found = [p for p in found if p["kind"] in keep]
    print(json.dumps({"problems": found}, ensure_ascii=False, indent=2))
    return 1 if found else 0


def cmd_matrix(a):
    reqs, specs, plan, tests = load(a.repo, a.tests)
    status, by_case = {}, {}
    if a.proves:
        for t in json.loads(read(a.proves)).get("tests", []):
            if t.get("cas"):
                by_case.setdefault(t["test"], []).append(t)
            else:
                status[t["test"]] = (t.get("depart", "?"), t.get("integration", "?"))
    rows = ["| REQ | SPEC | ACT | test | départ | intégration |", "|---|---|---|---|---|---|"]
    for req in sorted(reqs):
        req_specs = [s for s, r in sorted(specs.items()) if req in r]
        acts = sorted({act for act, s in (plan or {}).items() if set(s) & set(req_specs)})
        spec_cell, act_cell = ", ".join(req_specs) or "∅", ", ".join(acts) or "∅"
        cells = []
        for t in [t for t, r in sorted(tests.items()) if req in r]:
            if t in by_case:
                cells += [(f"{t}::{c['cas']}", c["depart"], c["integration"])
                          for c in by_case[t] if req in c["reqs"]]
            else:
                cells.append((t, *status.get(t, ("?", "?"))))
        for name, dep, integ in cells or [("∅", "-", "-")]:
            rows.append(f"| {req} | {spec_cell} | {act_cell} | {name} | {dep} | {integ} |")
    print("\n".join(rows))
    return 0


def git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.exit(f"trace.py : git {' '.join(args)} : {p.stderr.strip()}")
    return p.stdout


def in_dir(path, tests_dir):
    prefix = tests_dir.strip("/") + "/"
    return path.startswith(prefix)


def cmd_guard(a):
    violations = []
    for sha in git(a.repo, "rev-list", "--reverse", f"{a.base}..{a.head}").split():
        body = git(a.repo, "log", "-1", "--format=%B", sha)
        if not re.search(r"^Agent:\s*dev\b", body, re.MULTILINE):
            continue
        files = git(a.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha).split("\n")
        touched = [f for f in files if f and in_dir(f, a.tests)]
        if touched:
            violations.append({"sha": sha, "files": touched})
    print(json.dumps({"violations": violations}, ensure_ascii=False, indent=2))
    return 1 if violations else 0


def run_test(cwd, cmd, test, case=None):
    line = cmd.replace("{test}", shlex.quote(test)) if "{test}" in cmd else f"{cmd} {shlex.quote(test)}"
    if case is not None:
        line = line.replace("{case}", shlex.quote(case))
    return subprocess.run(line, shell=True, cwd=cwd, capture_output=True).returncode == 0


COMMENT = re.compile(r"^\s*(#|//|--|;|@|/\*|\*)")


def cases(content, case_regex):
    """Cas de test d'un fichier : [(nom, REQ du cas)]. Le bloc d'un cas va des commentaires et
    décorateurs collés au-dessus de sa ligne jusqu'au bloc du cas suivant. Un cas sans REQ dans son
    bloc hérite des REQ du fichier."""
    lines = content.splitlines()
    pattern = re.compile(case_regex)
    found = []
    for i, line in enumerate(lines):
        m = pattern.search(line)
        if m:
            start = i
            while start > 0 and COMMENT.match(lines[start - 1]):
                start -= 1
            found.append((m.group(1), start))
    file_reqs = ids(content, "REQ")
    out = []
    for k, (name, start) in enumerate(found):
        end = found[k + 1][1] if k + 1 < len(found) else len(lines)
        out.append((name, ids("\n".join(lines[start:end]), "REQ") or file_reqs))
    return out


def cmd_proves(a):
    changed = git(a.repo, "diff", "--name-only", "--diff-filter=AM", a.base, a.head, "--", a.tests)
    head_sha = git(a.repo, "rev-parse", a.head).strip()
    delta = []
    for path in changed.split("\n"):
        if not path:
            continue
        content = git(a.repo, "show", f"{head_sha}:{path}")
        reqs = ids(content, "REQ")
        if not reqs:  # les fichiers sans REQ (helpers, conftest) ne sont pas des tests du testeur
            continue
        if "{case}" in a.cmd:
            # ponytail: le filtre de cas du lanceur (-k de unittest/pytest) est une sous-chaîne :
            # test_a lance aussi test_ab. Nommer les cas sans préfixe commun, ou un --cmd à nom exact.
            for name, case_reqs in cases(content, a.case_regex):
                delta.append((path, name, case_reqs))
        else:
            delta.append((path, None, reqs))

    results, found = [], []
    tmp = tempfile.mkdtemp(prefix="trace-proves-")
    wt_base, wt_head = os.path.join(tmp, "base"), os.path.join(tmp, "head")
    try:
        git(a.repo, "worktree", "add", "-q", "--detach", wt_base, a.base)
        git(a.repo, "worktree", "add", "-q", "--detach", wt_head, head_sha)
        if delta:
            # Les tests de head posés sur le code de départ : ils doivent y échouer.
            # Les fichiers d'appui du dossier de tests (conftest, helpers) suivent aussi.
            git(wt_base, "checkout", head_sha, "--", a.tests)
        for path, case, reqs in delta:
            uid = f"{path}::{case}" if case else path
            dep = "passe" if run_test(wt_base, a.cmd, path, case) else "échec"
            integ = "passe" if run_test(wt_head, a.cmd, path, case) else "échec"
            entry = {"id": uid, "test": path, "reqs": reqs, "depart": dep, "integration": integ}
            if case:
                entry["cas"] = case
            results.append(entry)
            if dep == "passe":
                found.append({"kind": "ne_prouve_rien", "id": uid, "reqs": reqs})
            if integ == "échec":
                found.append({"kind": "echoue_integration", "id": uid, "reqs": reqs})
    finally:
        for wt in (wt_base, wt_head):
            git(a.repo, "worktree", "remove", "--force", wt, check=False)
        git(a.repo, "worktree", "prune", check=False)
        subprocess.run(["rm", "-rf", tmp])
    print(json.dumps({"tests": results, "problems": found}, ensure_ascii=False, indent=2))
    return 1 if found else 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="trace.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="sub", required=True)
    for name in ("check", "matrix"):
        s = sub.add_parser(name)
        s.add_argument("repo")
        s.add_argument("--tests", default=DEFAULT_TESTS)
        if name == "check":
            s.add_argument("--only", help="types de problèmes à garder, séparés par des virgules")
        else:
            s.add_argument("--proves", help="sortie JSON de « proves » pour les colonnes de statut")
    for name in ("guard", "proves"):
        s = sub.add_parser(name)
        s.add_argument("repo")
        s.add_argument("base")
        s.add_argument("head")
        s.add_argument("--tests", default=DEFAULT_TESTS)
        if name == "proves":
            s.add_argument("--cmd", required=True)
            s.add_argument("--case-regex", default=DEFAULT_CASE,
                           help="motif d'un cas de test, groupe 1 = son nom (avec {case} dans --cmd)")
    a = p.parse_args(argv)
    a.tests = a.tests.strip("/")
    try:
        return {"check": cmd_check, "matrix": cmd_matrix, "guard": cmd_guard, "proves": cmd_proves}[a.sub](a)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            return 2
        raise


if __name__ == "__main__":
    sys.exit(main())
