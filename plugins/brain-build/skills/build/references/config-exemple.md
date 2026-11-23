# Exemple de `docs/build/config.md`

À copier dans le repo construit et à adapter. Le pilote lit ce fichier à chaque lancement.

```markdown
# Configuration du build

## Lanceur

agent_cmd: claude -p
agent_timeout: 60m
agent_tools_extra:

## Projet

projet_dir: .
code_dirs: src, index.html

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
| analyst delta | opus | medium | 3 |
| tester | sonnet | high | 3 |
| tester delta | sonnet | medium | 2 |
| diagnostic | sonnet | high | 2 |
| diagnostic escalade | opus | high | 2 |

## Dev par complexité

| Complexité | Modèle | Effort | Budget max ($) | Escalade |
|---|---|---|---|---|
| simple | sonnet | low | 1 | standard |
| standard | sonnet | medium | 3 | difficile |
| difficile | opus | high | 5 | aucune |

## Modèles résolus

<rempli par le pilote à la fin du build, depuis modelUsage des runs :
opus → claude-opus-x-y, sonnet → claude-sonnet-x-y ; pilote : <modèle de la session>>
```

## Champs

| Champ | Rôle |
|---|---|
| `agent_cmd` | commande qui lance un agent ; reçoit ensuite les options de Claude Code |
| `agent_timeout` | délai maximal d'un agent (`timeout` POSIX) ; au-delà, résultat `failed` |
| `agent_tools_extra` | règles `--allowedTools` en plus de `Bash(git *)` et de la commande de test ; vide par défaut. Utile si un hook du poste réécrit les commandes (ex. `git status` devient `outil git status`) : ajouter la forme réécrite, `"Bash(outil git *)"`. Jamais d'interpréteur générique (`Bash(node *)`, `Bash(python3 *)`) : il permet au testeur d'exécuter le code |
| `projet_dir` | dossier du projet (celui qui contient `docs/besoin.md`) par rapport à la racine du dépôt ; `.` par défaut. Les agents sont lancés dedans, `trace.py` le reçoit comme `<repo>` |
| `code_dirs` | fichiers et dossiers du code du produit, par rapport à `projet_dir` : le testeur en mode `ecrire` ne peut pas les lire (`--disallowedTools`) |
| `test_cmd` | lance toute la suite de tests (non-régression), depuis `projet_dir` |
| `test_cmd_un_test` | lance un seul test (sert à `trace.py proves`) : `{test}` = chemin du fichier, `{case}` = nom du cas. Avec `{case}`, un verdict par cas ; sans, un verdict par fichier. unittest : `python3 -m unittest {test} -k {case}` ; `node --test` : `node --test --test-name-pattern {case} {test}` |
| `case_regex` | facultatif : motif d'un cas de test, groupe 1 = son nom (défaut : `def test…`, Python). JS, ancré en début de ligne pour ne pas prendre `split('\n')` pour un cas : `^\s*(?:it\|test)\(\s*['"]([^'"]+)` |
| `tests_dir` | dossier des tests du testeur, interdit aux `dev` |
| `normes` | fichiers de normes et conventions que lisent tous les agents |
| Agents | modèle, effort (`--effort`) et budget (`--max-budget-usd`) par rôle ; les lignes `delta` servent quand le build ne traite qu'un delta borné du besoin (quelques `REQ`) ; `diagnostic` = testeur en mode diagnostic |
| Dev par complexité | modèle, effort et budget du `dev` selon la ligne `Complexité :` de l'action dans `docs/plan.md` (sans cette ligne : `standard`) ; `Escalade` = palier de la reprise si l'action échoue |
| Modèles résolus | identifiants réels derrière les alias à la date du build, et modèle du pilote : deux builds se comparent |

## Pourquoi ces valeurs

Mesures sur trois produits construits avec le kit (voir `docs/retours_sur_brain_build.md` du
plugin) :

- les `dev` sont le premier poste de coût (40 à 44 %), parce qu'ils sont les plus nombreux, et
  leurs échecs venaient des specs ou des tests, pas du modèle : `sonnet` par défaut, `opus`
  seulement pour une action `difficile` ou en escalade ;
- l'analyste en `opus` high a attrapé des critères intenables et des contradictions entre `REQ` :
  pas de passage sous `opus` sans mesure qui l'autorise ;
- 3 diagnostics sur 4 ont désigné un test faux faute d'avoir relu une règle des specs : le facteur
  limitant était l'information, pas le modèle. Le diagnostic part donc en `sonnet` avec les specs
  en cause, et passe en `opus` seulement en escalade ;
- sur un petit delta, l'effort `medium` de l'analyste et du testeur a raccourci la chaîne sans perte
  observée ;
- sur un abonnement, le modèle compte aussi en **quota** : `opus` en consomme plus.

`haiku` n'a pas été mesuré sur un build. Il a seulement été vérifié que
`claude -p --agent brain-build:tester --model haiku --json-schema …` rend une sortie structurée
valide. Pour le palier `simple`, le mettre à l'essai (`Modèle : haiku`) en comparant les reprises :
un modèle moins cher qui échoue coûte deux fois.

## Lanceur et facturation

Le plugin ne sait pas qui paie. Pilote et agents peuvent tourner sur un abonnement (compte
connecté) ou sur une clé API, ensemble ou séparément : seul `agent_cmd` change.

- `claude -p` : compte connecté de la machine.
- Lanceur personnel (script qui pose une clé API, un autre compte, une passerelle…) : il doit
  accepter les options de Claude Code (`--agent`, `--model`, `--effort`, `--max-budget-usd`,
  `--output-format`, `--json-schema`, `--permission-mode`, `--allowedTools`, `--disallowedTools`) et
  les transmettre à `claude -p`. Exemple : `agent_cmd: mon-lanceur-api`.

Aucune consigne du plugin ne dépend du type d'authentification.
