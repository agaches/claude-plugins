# brain-build

Kit léger pour construire et maintenir un produit avec des agents, en gardant les bonnes pratiques
de gestion de projet : besoin figé, specs, traçabilité, tests qui prouvent quelque chose, recette.

- **Phase 1, Brain** (`/brain`, interactive) : réflexion, passage sur le grill, puis relecture
  critique par personas (`/roast-me`) jusqu'à un besoin figé, `docs/besoin.md`, avec des
  exigences `REQ-xxx` et leurs critères d'acceptation. Les décisions qui engagent sont consignées
  en ADR si une skill ADR est installée (par exemple le plugin `archi-docs`), sinon dans le besoin.
- **Phase 2, Build** (`/build`) : la session devient le **pilote**. Elle lance des agents
  `analyst`, `tester` et `dev` en **processus séparés** (`claude -p`), chacun avec son modèle et son
  effort, et les fait travailler jusqu'à la recette sans vous, sauf question sur le besoin.

Vous êtes le client final : vous fixez le besoin, tranchez les questions de besoin, faites la
recette sur un rapport court et mergez la PR.

## Pourquoi un cycle en V

Le kit applique un cycle en V : chaque niveau de description (besoin, specs, plan) a en face le
niveau de test qui le vérifie, et le tout est tracé (`REQ → SPEC → ACT → tests`). Le but est de
rendre le TDD **déterministe** et **fondé sur les specs, pas sur le code** :

- les tests sont écrits par un agent distinct du développeur, depuis le besoin et les specs
  seulement : un test ne peut pas se contenter de valider ce que le code fait ;
- `proves` vérifie que chaque test échoue avant le code et passe après : un test déjà vert ne
  prouve rien ;
- un test en échec est jugé contre les specs, qui désignent la cause (test, code, spec ou besoin),
  au lieu de plier le test au code ;
- la traçabilité est vérifiée par script (`trace.py`), pas à l'œil.

Ce que ça ne couvre pas : ce qui n'est pas écrit dans le besoin (ressenti, rendu, fonctionnement
sur la pile réelle). Le kit convient donc surtout aux produits dont les règles comptent plus que le
ressenti. Retours chiffrés sur trois produits réels : [docs/retours_sur_brain_build.md](docs/retours_sur_brain_build.md).
Pourquoi tant de tests pour un petit code : [docs/volume_des_tests.md](docs/volume_des_tests.md).
Comparaison avec Spec Kit, BMAD, OpenSpec et Kiro : [docs/comparaison_cadres_sdd.md](docs/comparaison_cadres_sdd.md).

## Prérequis

- Claude Code, `git`, Python 3 (le script de traçabilité n'utilise que la bibliothèque standard).
- `gh` connecté, pour ouvrir la PR à la fin du build.
- Pour la phase 1, le plugin `superpowers` (skill `brainstorming` ; `brain` sait s'en passer) :

  ```
  claude plugin install superpowers@claude-plugins-official
  ```
- Complément conseillé : le plugin `archi-docs` (skill `adr`) pour consigner les décisions en ADR.
  Toute autre skill ADR installée convient ; sans skill ADR, les décisions vont dans la section
  Décisions du besoin.

  > 0.3.0 : la skill `adr` quitte `brain-build` et passe dans le plugin `archi-docs`.

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install brain-build@agaches
```

## Usage

1. Dans le repo du produit : `/brain`. La session se termine par `docs/besoin.md` committé.
2. `/build`. Au premier lancement, le pilote crée `docs/build/config.md` (lanceur, commande de test,
   dossier des tests, normes, modèle et effort par rôle) et vous demande ce qu'il ne peut pas
   déduire du repo.
3. Le pilote enchaîne : specs et plan (`analyst`), tests écrits depuis le besoin et les specs
   seulement (`tester`), code action par action dans des worktrees séparés (`dev`), puis
   vérifications, PR et rapport `docs/recette/<date>-<sujet>.md`.
4. Vous lisez le rapport : questions en attente d'abord, puis matrice
   `REQ → SPEC → ACT → tests`, specs modifiées, incidents, avis de relecture. Recette, merge.

Nouvelle version du besoin : `/brain` pour la rédiger, puis `/build` ne traite que les `REQ`
ajoutées ou modifiées ; tous les tests existants servent de non-régression.

## Skills d'appui

Utilisables aussi seules, sur n'importe quel document ou décision :

| Skill | Rôle |
|---|---|
| `/roast-me` | relecture critique par personas (métier, architecte, chef de projet, test « 12 ans », détecteur de bullshit…), chacun en sous-agent à contexte vierge ; seules les critiques soulevées par au moins deux personas sont retenues. Catalogue : [agaches/ia_field](https://github.com/agaches/ia_field/blob/main/doc_negative_review/catalogue_prompt.md) |

## Rôles

| Rôle | Lit | Produit | Ne touche jamais |
|---|---|---|---|
| pilote (`/build`) | besoin, config, résultats des agents | lancements, intégration, vérifications, PR, rapport | besoin, specs, tests, code |
| `analyst` | besoin, normes | `docs/specs/SPEC-xxx.md`, `docs/plan.md` | besoin |
| `tester` | besoin, specs | tests dans `tests_dir`, chacun rattaché à une `REQ` | plan, code (sauf en diagnostic, en lecture) |
| `dev` | une action du plan, ses specs, normes | code et tests unitaires | `tests_dir`, besoin, specs |

Un test en échec est diagnostiqué par le `tester`, qui désigne la cause : test, code, spec ou
besoin. Plus de deux cycles sur une même `REQ` : elle est déclarée bloquée au rapport, le reste se
termine.

## Traçabilité

`scripts/trace.py` (stdlib, testé) vérifie ce que le pilote ne doit pas juger à l'œil :

| Commande | Vérifie |
|---|---|
| `check` | chaque `REQ` a un critère, une spec et un test ; aucune spec, action ou test orphelin |
| `matrix` | matrice `REQ → SPEC → ACT → tests → statut départ / intégration` |
| `guard` | aucun commit `Agent: dev …` n'a touché aux tests du testeur |
| `proves` | chaque test ajouté échoue sur la branche de départ et passe sur l'intégration, cas par cas si la commande de test le permet |

Tests du script : `python3 -m unittest plugins/brain-build/scripts/test_trace.py`.

## Lanceur et facturation

Le plugin ne sait pas qui paie. `agent_cmd` dans `docs/build/config.md` vaut `claude -p` par défaut
(compte connecté). Un lanceur personnel (clé API, autre compte, passerelle) convient s'il accepte
les options de Claude Code et les transmet à `claude -p` ; rien d'autre ne change.

Exemple de configuration : [skills/build/references/config-exemple.md](skills/build/references/config-exemple.md).

## Permissions des agents

Les agents tournent en `acceptEdits`, avec une liste blanche Bash limitée à `git` et à la commande
de test. `bypassPermissions` n'est à envisager que dans un conteneur.

## Fichiers produits dans le repo

`docs/besoin.md`, `docs/specs/`, `docs/plan.md`, `docs/adr/`, `GLOSSARY.md`, `docs/recette/`,
`docs/build/config.md`, `docs/build/etat.md` (et `docs/build/runs/`, non commité).
