# Lancer un agent

## Variables

```bash
ROOT="$(git rev-parse --show-toplevel)"         # racine du dépôt (checkout principal)
PROJ="<projet_dir>"                             # . ou sous-dossier qui contient docs/besoin.md
RUNS="$ROOT/$PROJ/docs/build/runs"              # chemin ABSOLU : runs/ n'est pas suivi par git
mkdir -p "$RUNS"
```

`docs/build/runs/` est dans `.gitignore` : il n'existe que dans le checkout principal, jamais dans
un worktree. Tout pointeur vers un fichier de run passe donc par son chemin absolu (`$RUNS/…`).

## Worktree

Le pilote crée lui-même le worktree, **depuis la branche d'intégration** (`HEAD` du checkout
principal), puis lance l'agent dedans. Ne pas utiliser `-w` de `claude -p` : il ne part pas
toujours de la branche courante (constaté : 8 worktrees sur 11 créés sur `main`).

```bash
git -C "$ROOT" worktree add -q "$ROOT/.claude/worktrees/<nom>" -b "worktree-<nom>" HEAD
cd "$ROOT/.claude/worktrees/<nom>/$PROJ"
```

L'analyste tourne sans worktree, seul, dans `$ROOT/$PROJ`.

## Commande

Une action prête = un lancement, par l'outil Bash avec `run_in_background: true`. La fin du
processus te réveille.

```bash
cd "<dossier de l'agent>"
timeout <agent_timeout> <agent_cmd> \
  --agent brain-build:<rôle> \
  --model <modèle> --effort <effort> --max-budget-usd <budget> \
  --permission-mode acceptEdits \
  --allowedTools "Bash(git *)" "Bash(<test_cmd> *)" <agent_tools_extra> \
  [--disallowedTools <règles de refus du testeur>] \
  --output-format json \
  --json-schema "$(cat "$PLUGIN/schemas/agent-result.schema.json")" \
  "<pointeurs>" \
  < /dev/null > "$RUNS/<nom>.json" 2> "$RUNS/<nom>.err"
echo "exit $?" >> "$RUNS/<nom>.err"
```

- `<rôle>` : `analyst`, `tester` ou `dev` (le diagnostic est le `tester` avec le modèle et
  l'effort de `diagnostic`).
- `< /dev/null` : sans lui, `claude -p` en arrière-plan attend 3 s une entrée et l'annonce.
- `--allowedTools` et `--disallowedTools` prennent plusieurs valeurs : ne jamais placer l'un d'eux
  juste avant le prompt, sinon le prompt est pris pour un outil. Le motif est `Bash(git *)` (avec
  espace).
- L'analyste n'a besoin que de `Bash(git *)` (plus `agent_tools_extra`).
- Un agent qui rend `blocked` / `env` avec « requires approval » sur une commande autorisée :
  regarder `permission_denials` dans son JSON ; si la commande a été réécrite par un hook du poste,
  proposer la règle à ajouter dans `agent_tools_extra`, sans élargir au-delà.
- Si `--agent brain-build:<rôle>` est introuvable alors que le plugin est installé pour un autre
  périmètre, ajouter `--plugin-dir "$PLUGIN"`.

### Modèle, effort, budget

| Lancement | Ligne de la config |
|---|---|
| analyst, tester `ecrire` | `analyst` / `tester` ; `analyst delta` / `tester delta` si le build ne traite qu'un delta borné |
| dev `ACT-xxx` | palier de la ligne `Complexité :` de l'action (`standard` si absente) |
| dev reprise après échec | une fois au même palier avec le diagnostic, puis une fois au palier `Escalade` |
| diagnostic | `diagnostic` ; `diagnostic escalade` si le premier verdict est contesté (le test ou le correctif qui en découle échoue encore) ou si la cause désignée est `besoin` |

### Testeur en mode `ecrire` : verrous

Le testeur ne doit ni lire ni exécuter le code. Au lancement :

- `--allowedTools` : `Bash(git *)` et `Bash(<test_cmd> *)` seulement, plus les formes réécrites
  par un hook ; jamais un interpréteur générique ;
- `--disallowedTools` : une règle `Read(./<chemin>)` (dossier : `Read(./<dossier>/**)`) par entrée
  de `code_dirs`, plus `Read(./docs/plan.md)`. Les chemins sont relatifs au dossier de lancement.

Ces règles couvrent l'outil Read (vérifié) et, d'après la documentation de Claude Code, les
commandes de fichier reconnues (`cat`, `head`, `sed`…) ; pas un `grep -r` sur un dossier parent ni
un script qui ouvre les fichiers lui-même :
`trace.py audit` contrôle après coup (étape 5 de la skill).

Le diagnostic n'a pas ces verrous : il lit le code par définition.

## Noms des runs

| Lancement | `<nom>` |
|---|---|
| analyst | `specs`, `plan`, `delta-1`, `corr-SPEC-004-1` |
| tester | `tests-1`, `tests-2`… |
| dev | `ACT-003` |
| reprise d'un dev (relance, correction, escalade) | `ACT-003-r2`, `ACT-003-r3` |
| diagnostic | `diag-REQ-002-1` |

`trace.py cost` compte comme reprise tout nom en `-r<n>` ou `-c<n>`.

## Pointeurs (le prompt)

Jamais le contenu des fichiers, seulement de quoi les trouver : des ids (`REQ`, `SPEC`, `ACT`) et
des chemins de **documents**. Un prompt au testeur ne cite **jamais** un fichier ou un symbole du
code : une reprise de test se formule avec l'id du cas et le critère de la spec en cause.

| Rôle | Prompt |
|---|---|
| analyst | `Mode specs. Besoin : docs/besoin.md. Config : docs/build/config.md.` |
| analyst | `Mode plan. Specs : docs/specs/. Plan : docs/plan.md.` |
| analyst | `Mode correction SPEC-004. Diagnostic : <RUNS>/diag-REQ-002-1.json.` |
| tester | `Mode ecrire REQ-001,REQ-002. Config : docs/build/config.md.` |
| tester | `Mode ecrire REQ-003. Réécrire le cas tests/acceptance/test_x.py::test_req003_c1, qui passe déjà au départ : il doit prouver le critère 1 de REQ-003 (SPEC-002).` |
| tester | `Mode diagnostic tests/acceptance/test_x.py::test_req002_c1. Specs : SPEC-001, SPEC-004. Sortie : <RUNS>/proves.json.` |
| dev | `Action ACT-003. Plan : docs/plan.md. Config : docs/build/config.md.` |
| dev | `Mode correction ACT-003. Écart : <RUNS>/diag-REQ-002-1.json.` |

`<RUNS>` est remplacé par le chemin absolu.

## Lire le résultat

```bash
python3 - "$RUNS/<nom>.json" <<'EOF'
import json, sys
d = None
try:
    # Un lanceur peut écrire autre chose sur stdout : garder la ligne JSON de type « result ».
    for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
        if line.startswith("{"):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("type") == "result":
                d = o
except OSError:
    pass
if d is None:
    print("failed: pas de JSON"); sys.exit()
r = d.get("structured_output")
print(json.dumps({"is_error": d.get("is_error"), "subtype": d.get("subtype"),
                  "cost": d.get("total_cost_usd"), "models": list(d.get("modelUsage") or {}),
                  "result": r}, ensure_ascii=False))
EOF
```

- `structured_output` présent ⇒ son `status` fait foi (`done`, `blocked`, `failed`).
- Pas de JSON, pas de `structured_output`, code ≠ 0 ou `exit 124` (délai) ⇒ `failed`, avec les
  40 dernières lignes de `<nom>.err` et `<nom>.json` dans `etat.md`.
- Noter `total_cost_usd` dans `etat.md` (colonne Coût). Le rapport prend ses totaux dans
  `trace.py cost`.
- `verifications` du testeur ⇒ à reporter dans `etat.md` et à planifier (étape 5 de la skill).

## Intégrer un worktree

Après un `done`, depuis le checkout principal :

```bash
cd "$ROOT"
git merge --no-ff worktree-<nom> -m "build: intègre <nom>"
git worktree remove ".claude/worktrees/<nom>" && git branch -d worktree-<nom>
```

Si `remove` refuse à cause de fichiers non suivis : `git -C .claude/worktrees/<nom> status --short`.
Seulement des artefacts (`__pycache__`, sorties de build) et la branche intégrée ⇒ `remove --force`.
Autre chose ⇒ ne pas forcer, le noter en incident.

**Conflit** (deux `dev` sur le même fichier) : ne jamais forcer. `git merge --abort`, garder la
première action intégrée, supprimer le worktree de la seconde et la relancer sur la branche
intégrée (`<nom>-r2`). Le conflit va dans les incidents du rapport.

Un agent `blocked` ou `failed` : garder son worktree pour le diagnostic, le supprimer quand la
`REQ` est réglée ou mise de côté.
