# Exemple de `docs/build/config.md`

À copier dans le repo construit et à adapter. Le pilote lit ce fichier à chaque lancement.

```markdown
# Configuration du build

## Lanceur

agent_cmd: claude -p
agent_timeout: 60m
agent_tools_extra:

## Tests

test_cmd: python3 -m pytest -q
test_cmd_un_test: python3 -m pytest -q {test} -k {case}
tests_dir: tests/acceptance

## Normes

normes: docs/normes.md, CONTRIBUTING.md

## Agents

| Rôle | Modèle | Effort | Budget max ($) |
|---|---|---|---|
| analyst | opus | high | 5 |
| tester | sonnet | high | 3 |
| dev | sonnet | medium | 3 |
| diagnostic | opus | high | 2 |
```

## Champs

| Champ | Rôle |
|---|---|
| `agent_cmd` | commande qui lance un agent ; reçoit ensuite les options de Claude Code |
| `agent_timeout` | délai maximal d'un agent (`timeout` POSIX) ; au-delà, résultat `failed` |
| `agent_tools_extra` | règles `--allowedTools` en plus de `Bash(git *)` et de la commande de test ; vide par défaut. Utile si un hook du poste réécrit les commandes (ex. `git status` devient `outil git status`) : ajouter la forme réécrite, `"Bash(outil git *)"` |
| `test_cmd` | lance toute la suite de tests (non-régression) |
| `test_cmd_un_test` | lance un seul test (sert à `trace.py proves`) : `{test}` = chemin du fichier, `{case}` = nom du cas. Avec `{case}`, un verdict par cas ; sans, un verdict par fichier. unittest : `python3 -m unittest {test} -k {case}` |
| `case_regex` | facultatif : motif d'un cas de test, groupe 1 = son nom (défaut : `def test…`, Python). Ex. JS : `(?:it\|test)\(\s*['"]([^'"]+)` |
| `tests_dir` | dossier des tests du testeur, interdit aux `dev` |
| `normes` | fichiers de normes et conventions que lisent tous les agents |
| Agents | modèle, effort (`--effort`) et budget (`--max-budget-usd`) par rôle ; `diagnostic` = testeur en mode diagnostic |

## Lanceur et facturation

Le plugin ne sait pas qui paie. Pilote et agents peuvent tourner sur un abonnement (compte
connecté) ou sur une clé API, ensemble ou séparément : seul `agent_cmd` change.

- `claude -p` : compte connecté de la machine.
- Lanceur personnel (script qui pose une clé API, un autre compte, une passerelle…) : il doit
  accepter les options de Claude Code (`--agent`, `--model`, `--effort`, `--max-budget-usd`,
  `--output-format`, `--json-schema`, `-w`, `--permission-mode`, `--allowedTools`) et les
  transmettre à `claude -p`. Exemple : `agent_cmd: mon-lanceur-api`.

Aucune consigne du plugin ne dépend du type d'authentification.
