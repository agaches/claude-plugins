# Lancer un agent

## Commande

Une action prête = un lancement, par l'outil Bash avec `run_in_background: true`, depuis la racine
du repo, sur la branche d'intégration. La fin du processus te réveille.

```bash
mkdir -p docs/build/runs
timeout <agent_timeout> <agent_cmd> \
  --agent brain-build:<rôle> \
  --model <modèle> --effort <effort> --max-budget-usd <budget> \
  --permission-mode acceptEdits \
  --allowedTools "Bash(git *)" "Bash(<test_cmd> *)" <agent_tools_extra> \
  -w <nom> \
  --output-format json \
  --json-schema "$(cat "$PLUGIN/schemas/agent-result.schema.json")" \
  "<pointeurs>" \
  > docs/build/runs/<nom>.json 2> docs/build/runs/<nom>.err
echo "exit $?" >> docs/build/runs/<nom>.err
```

- `<rôle>` : `analyst`, `tester` ou `dev` (le diagnostic est le `tester` avec le modèle et
  l'effort de `diagnostic`).
- `<nom>` : `ACT-003`, `tests-1`, `diag-REQ-002-1`… ; l'analyste tourne sans `-w`, seul, dans le
  checkout principal.
- `--allowedTools` prend plusieurs valeurs : ne jamais le placer juste avant le prompt, sinon le
  prompt est pris pour un outil. Le motif est `Bash(git *)` (avec espace).
- L'analyste n'a besoin que de `Bash(git *)` (plus `agent_tools_extra`).
- Un agent qui rend `blocked` / `env` avec « requires approval » sur une commande autorisée :
  regarder `permission_denials` dans son JSON ; si la commande a été réécrite par un hook du poste,
  proposer la règle à ajouter dans `agent_tools_extra`, sans élargir au-delà.
- Si `--agent brain-build:<rôle>` est introuvable alors que le plugin est installé pour un autre
  périmètre, ajouter `--plugin-dir "$PLUGIN"`.

## Pointeurs (le prompt)

Jamais le contenu des fichiers, seulement de quoi les trouver :

| Rôle | Prompt |
|---|---|
| analyst | `Mode specs. Besoin : docs/besoin.md. Config : docs/build/config.md.` |
| analyst | `Mode plan. Specs : docs/specs/. Plan : docs/plan.md.` |
| analyst | `Mode correction SPEC-004. Diagnostic : docs/build/runs/diag-REQ-002-1.json.` |
| tester | `Mode ecrire REQ-001,REQ-002. Config : docs/build/config.md.` |
| tester | `Mode diagnostic tests/acceptance/test_x.py. Sortie : docs/build/runs/proves.json.` |
| dev | `Action ACT-003. Plan : docs/plan.md. Config : docs/build/config.md.` |
| dev | `Mode correction ACT-003. Écart : docs/build/runs/diag-REQ-002-1.json.` |

## Lire le résultat

```bash
python3 - docs/build/runs/<nom>.json <<'EOF'
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
                  "cost": d.get("total_cost_usd"), "result": r}, ensure_ascii=False))
EOF
```

- `structured_output` présent ⇒ son `status` fait foi (`done`, `blocked`, `failed`).
- Pas de JSON, pas de `structured_output`, code ≠ 0 ou `exit 124` (délai) ⇒ `failed`, avec les
  40 dernières lignes de `<nom>.err` et `<nom>.json` dans `etat.md`.
- Noter `total_cost_usd` dans `etat.md` (colonne Coût) : le total va au rapport.

## Intégrer un worktree

`-w <nom>` crée `.claude/worktrees/<nom>` sur la branche `worktree-<nom>`. Après un `done` :

```bash
git merge --no-ff worktree-<nom> -m "build: intègre <nom>"
git worktree unlock .claude/worktrees/<nom>   # -w le verrouille au nom de la session
git worktree remove .claude/worktrees/<nom> && git branch -d worktree-<nom>
```

Si `remove` refuse à cause de fichiers non suivis : `git -C .claude/worktrees/<nom> status --short`.
Seulement des artefacts (`__pycache__`, sorties de build) et la branche intégrée ⇒ `remove --force`.
Autre chose ⇒ ne pas forcer, le noter en incident.

**Conflit** (deux `dev` sur le même fichier) : ne jamais forcer. `git merge --abort`, garder la
première action intégrée, supprimer le worktree de la seconde et la relancer sur la branche
intégrée (`<nom>-r2`). Le conflit va dans les incidents du rapport.

Un agent `blocked` ou `failed` : garder son worktree pour le diagnostic, le supprimer quand la
`REQ` est réglée ou mise de côté.
