#!/usr/bin/env python3
"""Traçabilité du kit brain-build : REQ (besoin) → SPEC (specs) → ACT (plan) → tests.

Sous-commandes (sortie sur stdout ; code 0 = rien à signaler, 1 = problèmes, 2 = erreur d'usage) :

  check  <repo> [--tests DIR] [--only k1,k2]   liens et orphelins, JSON {"problems": [...],
         "warnings": [...]} ; les avertissements (besoin long, constante hors Réglages, critère
         probabiliste) ne changent pas le code de sortie
  matrix <repo> [--tests DIR] [--proves F]     matrice Markdown REQ → SPEC → ACT → tests
  guard  <repo> <base> <head> [--tests DIR]    commits « Agent: dev » qui touchent DIR, JSON
  proves <repo> <base> <head> --cmd CMD [--tests DIR]
         chaque test ajouté ou modifié entre base et head échoue sur base et passe sur head.
         CMD est lancé depuis la racine d'un worktree temporaire ; {test} y est remplacé par le
         chemin du test (sinon le chemin est ajouté en fin de commande).
         Avec {case} dans CMD : un verdict par cas de test (--case-regex, défaut « def test… »),
         chaque cas portant les REQ de son bloc (sinon celles du fichier) ; id « chemin::cas ».
  audit  <run.json>... [--tests DIR] [--test-cmd CMD] [--allow P1,P2] [--root SOUS_DOSSIER]
         [--transcripts DIR]
         relit la transcription de chaque run du testeur (session_id du JSON) et liste les
         lectures et exécutions hors du besoin, des specs, des ADR, de la config et des tests
  cost   <runs_dir>   coût, lancements et reprises (nom en -r<n> ou -c<n>) par rôle et par action

<repo> est le dossier qui contient docs/besoin.md, éventuellement un sous-dossier du dépôt git :
les chemins produits lui sont relatifs et proves lance CMD depuis ce sous-dossier.

Conventions lues :
  docs/besoin.md  une REQ par titre « ### REQ-001 : ... », suivi d'une ligne « Critère : ... »
  docs/specs/*.md  titre « # SPEC-001 : ... » ; les REQ citées dans le fichier sont couvertes
  docs/plan.md     une section « ## ACT-001 : ... » ; les SPEC citées dans la section
  tests            tout fichier de DIR (défaut tests/acceptance) qui cite une REQ

Stdlib uniquement.
"""

import argparse
import glob
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
REQ_MAX = 15  # au-delà, le besoin ne se relit plus en quelques minutes
NOMBRE = re.compile(r"(?<![\w.,-])\d+(?:[.,]\d+)?")
PROBA = re.compile(r"\b\d+\s+(?:\w+\s+){0,3}sur\s+\d+\b|probabilit", re.IGNORECASE)
BACKTICKS = re.compile(r"`[^`]*`")


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


def nombres(line):
    """Constantes d'une ligne de critère, hors littéraux entre backticks (messages, commandes)."""
    return {n.replace(",", ".") for n in NOMBRE.findall(BACKTICKS.sub(" ", line))}


def reglages(text):
    """Valeurs de la rubrique « ## Réglages » du besoin."""
    vals, inside = set(), False
    for line in text.splitlines():
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            if inside and len(h.group(1)) <= 2:
                inside = False
            if re.match(r"r[ée]glages\b", h.group(2), re.IGNORECASE):
                inside = True
            continue
        if inside:
            vals |= {n.replace(",", ".") for n in NOMBRE.findall(line)}
    return vals


def avertissements(text):
    out, reqs = [], sections(text, "REQ")
    if len(reqs) > REQ_MAX:
        out.append({"kind": "besoin_long", "id": "REQ", "nombre": len(reqs), "seuil": REQ_MAX})
    known = reglages(text)
    for req, body in sorted(reqs.items()):
        crit = [line for line in body.splitlines() if CRITERE.match(line)]
        vals = sorted({n for line in crit for n in nombres(line)} - known, key=float)
        if vals:
            out.append({"kind": "critere_constante", "id": req, "valeurs": vals})
        if any(PROBA.search(BACKTICKS.sub(" ", line)) for line in crit):
            out.append({"kind": "critere_probabiliste", "id": req})
    return out


def cmd_check(a):
    found = problems(*load(a.repo, a.tests))
    warned = avertissements(read(os.path.join(a.repo, "docs", "besoin.md")))
    if a.only:
        keep = set(a.only.split(","))
        found = [p for p in found if p["kind"] in keep]
        warned = [w for w in warned if w["kind"] in keep]
    print(json.dumps({"problems": found, "warnings": warned}, ensure_ascii=False, indent=2))
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


def prefix(repo):
    """Chemin du projet dans le dépôt git (« » à la racine, « jeu/ » en sous-dossier)."""
    return git(repo, "rev-parse", "--show-prefix").strip()


def cmd_guard(a):
    violations, pre = [], prefix(a.repo)
    for sha in git(a.repo, "rev-list", "--reverse", f"{a.base}..{a.head}").split():
        body = git(a.repo, "log", "-1", "--format=%B", sha)
        if not re.search(r"^Agent:\s*dev\b", body, re.MULTILINE):
            continue
        files = git(a.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha).split("\n")
        touched = [f[len(pre):] for f in files if f.startswith(pre) and in_dir(f[len(pre):], a.tests)]
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
    pre = prefix(a.repo)
    changed = git(a.repo, "diff", "--relative", "--name-only", "--diff-filter=AM", a.base, a.head,
                  "--", a.tests)
    head_sha = git(a.repo, "rev-parse", a.head).strip()
    delta = []
    for path in changed.split("\n"):
        if not path:
            continue
        content = git(a.repo, "show", f"{head_sha}:{pre}{path}")
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
        proj_base, proj_head = os.path.join(wt_base, pre), os.path.join(wt_head, pre)
        if delta:
            # Les tests de head posés sur le code de départ : ils doivent y échouer.
            # Les fichiers d'appui du dossier de tests (conftest, helpers) suivent aussi.
            git(proj_base, "checkout", head_sha, "--", a.tests)
        for path, case, reqs in delta:
            uid = f"{path}::{case}" if case else path
            dep = "passe" if run_test(proj_base, a.cmd, path, case) else "échec"
            integ = "passe" if run_test(proj_head, a.cmd, path, case) else "échec"
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


def result_of(path):
    """Ligne JSON de type « result » d'un run (un lanceur peut écrire autre chose sur stdout)."""
    found = None
    try:
        for line in open(path, encoding="utf-8", errors="replace"):
            if line.startswith("{"):
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                if o.get("type") == "result":
                    found = o
    except OSError:
        pass
    return found


ALLOWED = ("docs/besoin.md", "docs/specs", "GLOSSARY.md", "docs/adr", "docs/build/config.md", ".git")
INTERPRETERS = {"node", "python", "python3", "deno", "bun", "ruby", "php", "perl", "npx", "sh",
                "bash", "tsx", "ts-node"}
GIT_READ = {"show", "cat-file", "grep", "blame", "diff", "log"}
LISTING = {"ls", "find", "tree", "mkdir", "cd", "test", "[", "pwd", "echo", "wc", "stat", "touch"}
TOKEN = re.compile(r"[^\s'\"`;|&<>()=,{}\[\]]+")
EXT = re.compile(r"\.[A-Za-z]\w{0,5}$")
PATHLIKE = re.compile(r"[\w.~*$/+-]+")
BARE_OK = re.compile(r"(?:SPEC|ADR)-[\w*-]*\.md|besoin\.md|config\.md|GLOSSARY\.md")
INLINE_PATH = re.compile(r"(?<![\w/.])(?:\.{1,2}/|/)?[\w-]+(?:/[\w.-]+)+\.[A-Za-z]{1,5}\b")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1([^\n]*)\n.*?\n\s*\2\s*(?=\n|$)", re.DOTALL)


def classify(path, cwd, allowed, own=(), root=None):
    """None si l'accès est permis au testeur, sinon (kind, cible). CWD : dossier courant de la
    commande ; ROOT : racine du projet (défaut CWD). OWN : dossiers propres à la session
    (transcriptions, sorties d'outil mises de côté, /tmp), toujours permis."""
    root = root or cwd
    if "/" not in path and ("$" in path or BARE_OK.fullmatch(path)):
        return None  # nom nu lu après un cd ou dans une boucle : on ne sait pas où, présumé permis
    full = os.path.normpath(os.path.expanduser(path) if path.startswith("~")
                            else path if os.path.isabs(path) or not cwd else os.path.join(cwd, path))
    if full.startswith("/dev/") or any(full == o or full.startswith(o + "/") for o in own):
        return None
    rel = os.path.relpath(full, root).replace(os.sep, "/") if root and os.path.isabs(full) else full
    if rel == ".." or rel.startswith("../"):
        return ("lecture_hors_projet", full)
    if rel == "docs/plan.md":
        return ("lecture_plan", rel)
    for ok in allowed:
        if rel == ok or rel.startswith(ok + "/") or ok.startswith(rel + "/"):
            return None  # dans un dossier permis, ou un de ses parents (simple liste)
    return ("lecture_code", rel)


def segments(command):
    """Découpe sur ; & | et fin de ligne, hors guillemets."""
    out, cur, quote, i = [], [], None, 0
    while i < len(command):
        ch = command[i]
        if quote:
            if ch == "\\" and quote == '"' and i + 1 < len(command):
                cur.append(command[i:i + 2]); i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch in ";&|\n":
            out.append("".join(cur)); cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    out.append("".join(cur))
    return out


def bash_access(command, cwd, allowed, test_cmd, own=(), root=None):
    """Accès d'une commande Bash : exécutions d'interpréteur, puis chemins cités. Les commandes
    de listage (ls, find…) ne montrent que des noms et ne comptent pas comme lectures."""
    # ponytail: lecture heuristique (variables, boucles et sous-shells non suivis) : assez pour un
    # audit qui se relit, pas pour un garde-fou. Le vrai verrou est --disallowedTools au lancement.
    out, root = [], root or cwd
    inline = "<<" in command
    for seg in segments(HEREDOC.sub(r"\3", command)):
        seg = seg.strip().lstrip("(").strip()
        words = seg.split()
        if not words or (test_cmd and seg.startswith(test_cmd)):
            continue
        first = os.path.basename(words[0])
        tokens = TOKEN.findall(seg)[1:]
        if first == "cd" and len(words) > 1 and cwd:
            cwd = os.path.normpath(os.path.join(cwd, os.path.expanduser(words[1])))
            continue
        if first in LISTING or re.fullmatch(r"\S+\s+(?:--version|-v|-V)", seg):
            continue
        if first == "git":
            sub = next((w for w in words[1:] if not w.startswith("-")), "")
            if sub not in GIT_READ:
                continue
            tokens = [t.rsplit(":", 1)[-1] for t in tokens[tokens.index(sub) + 1:]] if sub in tokens else []
        elif first in INTERPRETERS:
            # Code en ligne (-e, -c, stdin) : seuls les chemins à extension y sont lus.
            code = inline or any(w in ("-e", "-c", "-p", "-", "--eval", "--print") for w in words[1:])
            scripts = [w for w in words[1:] if not w.startswith("-") and EXT.search(w)]
            if code or any(classify(w, cwd, allowed, own, root) for w in scripts):
                out.append(("execution", seg))
            tokens = INLINE_PATH.findall(seg) if code else scripts
        if first == "sed":
            tokens = [t for t in tokens if not re.match(r"[sy]/", t)]  # l'expression, pas un fichier
        for t in tokens:
            if (t.startswith("-") or "://" in t or not PATHLIKE.fullmatch(t)
                    or not ("/" in t or EXT.search(t)) or re.fullmatch(r"/[^/]*", t)):
                continue
            hit = classify(t, cwd, allowed, own, root)
            if hit:
                out.append(hit)
    return out


def cmd_audit(a):
    allowed = ALLOWED + (a.tests,) + tuple(x.strip().strip("/") for x in a.allow.split(",") if x.strip())
    own = (os.path.normpath(a.transcripts), "/tmp", os.path.realpath(tempfile.gettempdir()))
    runs, found = [], []
    for run_path in a.runs:
        name = os.path.splitext(os.path.basename(run_path))[0]
        d = result_of(run_path) or {}
        sid = d.get("session_id")
        refused = {x.get("tool_use_id") for x in d.get("permission_denials") or []}
        hits = glob.glob(os.path.join(a.transcripts, "*", f"{sid}.jsonl")) if sid else []
        if not hits:
            found.append({"kind": "transcription_introuvable", "run": name, "session": sid})
            continue
        seen, uses, root = set(), 0, None
        for line in open(hits[0], encoding="utf-8", errors="replace"):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            content = (o.get("message") or {}).get("content") if o.get("type") == "assistant" else None
            for c in content if isinstance(content, list) else []:
                if c.get("type") != "tool_use":
                    continue
                uses += 1
                tool, inp, cwd = c.get("name"), c.get("input") or {}, o.get("cwd")
                if root is None and cwd:  # racine du projet : dossier de lancement de l'agent (+ --root)
                    root = os.path.normpath(os.path.join(cwd, a.root))
                if tool == "Bash":
                    access = bash_access(inp.get("command", ""), cwd, allowed, a.test_cmd, own, root)
                elif tool == "Grep":
                    access = [classify(inp.get("path") or ".", cwd, allowed, own, root)]
                elif inp.get("file_path") or inp.get("notebook_path"):
                    access = [classify(inp.get("file_path") or inp["notebook_path"], cwd, allowed, own, root)]
                else:
                    access = []
                denied = c.get("id") in refused  # tentative bloquée par --disallowedTools : le verrou a tenu
                for hit in access:
                    if hit and (hit, denied) not in seen:
                        seen.add((hit, denied))
                        found.append({"kind": hit[0], "run": name, "outil": tool, "cible": hit[1], "refuse": denied})
        runs.append({"run": name, "session": sid, "outils": uses})
    print(json.dumps({"runs": runs, "problems": found}, ensure_ascii=False, indent=2))
    return 1 if any(not f.get("refuse") for f in found) else 0


def euros(x):
    return f"{x:.2f}".replace(".", ",")


def cmd_cost(a):
    roles, acts, total, sans = {}, {}, 0.0, []
    for fname in sorted(os.listdir(a.runs)):
        if not fname.endswith(".json"):
            continue
        stem, d = fname[:-5], result_of(os.path.join(a.runs, fname))
        if d is None:
            if stem != "proves":
                sans.append(stem)
            continue
        so = d.get("structured_output") or {}
        act = re.match(r"ACT-\d{3}", stem)
        if stem.startswith("diag-"):
            role = "diagnostic"
        else:
            role = so.get("agent") or ("dev" if act else "tester" if stem.startswith("tests-") else "?")
        reprise = 1 if re.search(r"-[rc]\d+$", stem) else 0
        cost = float(d.get("total_cost_usd") or 0)
        total += cost
        r = roles.setdefault(role, [0, 0, 0.0, set()])
        r[0] += 1; r[1] += reprise; r[2] += cost; r[3] |= set(d.get("modelUsage") or {})
        act_id = next((i for i in so.get("ids", []) if i.startswith("ACT-")), act.group(0) if act else None)
        if role == "dev" and act_id:
            x = acts.setdefault(act_id, [0, 0, 0.0])
            x[0] += 1; x[1] += reprise; x[2] += cost
    order = ["analyst", "tester", "dev", "diagnostic"]
    rows = ["| Rôle | Lancements | Reprises | Coût ($) | Modèles |", "|---|---|---|---|---|"]
    for role in order + sorted(set(roles) - set(order)):
        if role in roles:
            n, rep, cost, models = roles[role]
            rows.append(f"| {role} | {n} | {rep} | {euros(cost)} | {', '.join(sorted(models))} |")
    rows += ["", "| Action | Lancements | Reprises | Coût ($) |", "|---|---|---|---|"]
    rows += [f"| {k} | {n} | {rep} | {euros(c)} |" for k, (n, rep, c) in sorted(acts.items())]
    rows += ["", f"Total : {euros(total)} $ (agents seuls, pilote non compté)"]
    if sans:
        rows.append(f"Sans résultat JSON (coût inconnu) : {', '.join(sans)}")
    print("\n".join(rows))
    return 0


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
    s = sub.add_parser("audit")
    s.add_argument("runs", nargs="+", help="JSON de résultat des runs du testeur en mode ecrire")
    s.add_argument("--tests", default=DEFAULT_TESTS)
    s.add_argument("--test-cmd", default="", help="commande de test, permise au testeur")
    s.add_argument("--root", default="", help="projet dans ce sous-dossier du dossier de lancement de l'agent")
    s.add_argument("--allow", default="", help="autres chemins permis, séparés par des virgules (normes)")
    s.add_argument("--transcripts", help="dossier des transcriptions (défaut ~/.claude/projects)",
                   default=os.path.join(os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"),
                                        "projects"))
    s = sub.add_parser("cost")
    s.add_argument("runs", help="dossier des runs (docs/build/runs)")
    a = p.parse_args(argv)
    if hasattr(a, "tests"):
        a.tests = a.tests.strip("/")
    try:
        return {"check": cmd_check, "matrix": cmd_matrix, "guard": cmd_guard, "proves": cmd_proves,
                "audit": cmd_audit, "cost": cmd_cost}[a.sub](a)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            return 2
        raise


if __name__ == "__main__":
    sys.exit(main())
