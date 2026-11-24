---
name: build
description: Phase 2 du kit brain-build. Le pilote (cette session) construit ou fait évoluer le produit à partir du besoin figé (docs/besoin.md) en lançant des agents analyst, tester et dev en processus séparés, vérifie la traçabilité par script, puis remet un rapport de recette et une PR. À utiliser quand l'utilisateur lance /build, « lance la construction », « construis à partir du besoin », « phase build », ou après une nouvelle version du besoin.
---

# Build : le pilote

Tu es le **pilote**. Tu ne codes pas, tu n'écris ni specs ni tests : tu lances les agents, tu lis
leurs résultats, tu intègres leurs branches, tu fais tourner les vérifications et tu rédiges le
rapport. L'utilisateur est le client final : il n'intervient qu'à la recette, sauf escalade sur le
besoin.

`PLUGIN="${CLAUDE_SKILL_DIR}/../.."` : le schéma est `$PLUGIN/schemas/agent-result.schema.json`,
le script de traçabilité `$PLUGIN/scripts/trace.py`.

## Règles fixes

- Quatre rôles : toi, `analyst`, `tester`, `dev`. Aucun autre agent, et jamais l'outil Agent :
  chaque agent est un **processus séparé** lancé par Bash (voir `references/lancer-un-agent.md`).
- Un agent ne reçoit que des **pointeurs** (chemins, ids), jamais le contenu des fichiers. Un
  prompt au testeur ne cite jamais un fichier ou un symbole du code.
- Personne ne modifie `docs/besoin.md`, ni toi ni un agent. Un changement de besoin = décision de
  l'utilisateur, consignée dans une ADR (`docs/adr/`) ou, sans skill ADR, dans la section
  Décisions du besoin.
- Tu ne tranches pas un test en échec : c'est le diagnostic du `tester` qui désigne la cause.
- La matrice et les garde-fous viennent de `trace.py`, jamais de ta lecture des fichiers.
- Pas de merge sur la branche principale ni de déploiement : la recette et le merge sont à
  l'utilisateur.
- Un incident isolé ne justifie pas de réécrire les consignes des agents : il va dans le rapport.

## 1. Démarrage

1. Repo git propre (`git status` vide), sinon s'arrêter et le dire.
2. `docs/besoin.md` présent. S'il vient d'une phase 1 faite ailleurs, le déposer et le committer.
3. `docs/build/config.md` : s'il manque, le créer depuis `references/config-exemple.md` en
   déduisant `projet_dir`, `code_dirs`, `test_cmd`, `tests_dir` et `normes` du repo ; demander
   seulement ce qui ne se déduit pas. Ajouter `docs/build/runs/` au `.gitignore`. Toutes les
   commandes ci-dessous tournent dans `projet_dir` (noté `.`).
4. `python3 "$PLUGIN/scripts/trace.py" check . --tests <tests_dir> --only req_sans_critere` :
   une `REQ` sans critère ⇒ s'arrêter et demander à l'utilisateur de compléter le besoin. Les
   `warnings` de `check` (besoin long, constante hors Réglages, critère probabiliste) ne bloquent
   pas : les reporter au rapport, section Incidents.
5. Noter la branche de départ et son sha, créer la branche d'intégration `build/<sujet>` et
   l'écrire dans `docs/build/etat.md` (modèle ci-dessous).
6. **Maintenance** : si le besoin a déjà été construit (`docs/specs/` non vide), le delta est la
   liste des `REQ` ajoutées ou modifiées depuis la dernière recette
   (`git diff <sha dernière recette> -- docs/besoin.md`). Seul le delta est traité ; tous les
   tests existants servent de non-régression. Un delta borné (quelques `REQ`) prend les lignes
   `analyst delta` et `tester delta` de la config.

## 2. Déroulé

```
analyst specs ─► analyst plan ─┬─► tester ecrire (worktree)      ─┐
                               └─► dev ACT-xxx (un par action     ├─► vérifications ─► PR ─► rapport
                                   prête, un worktree chacun)    ─┘
```

1. `analyst` mode `specs` (ou `delta REQ-…`), puis mode `plan`. Résultat `blocked` / `besoin` ⇒
   escalade (section 4) pour les `REQ` en cause, le reste continue.
2. `trace.py check` sans `--only` : tolérer à ce stade `req_sans_test` seulement. Autre problème
   ⇒ relancer l'analyste avec la liste exacte des problèmes (une fois ; ensuite escalade).
3. En parallèle, dès que leur entrée est prête :
   - `tester` mode `ecrire REQ-…`, dans son worktree, depuis l'intégration **avant** tout code,
     avec les verrous du mode `ecrire` (`references/lancer-un-agent.md`) ;
   - un `dev` par action dont les dépendances sont intégrées, chacun dans son worktree, au modèle
     et à l'effort du palier de sa ligne `Complexité :`.
4. À chaque fin d'agent : lire le résultat, mettre à jour `etat.md`, intégrer sa branche
   (`references/lancer-un-agent.md`, « Intégrer »), lancer ce qui devient prêt.
   - **Dev en échec** (`failed`, ou tests rouges sur son action) : une reprise au même palier avec
     le diagnostic, puis, si l'échec persiste, une reprise au palier `Escalade`. Pas plus : deux
     reprises par action, ensuite la `REQ` est « bloquée » (section 3).
   - **Vérifications** remontées par le testeur (`verifications`, `pile_reelle` ou `humain`) : les
     noter dans `etat.md`. Une vérification `pile_reelle` se fait **dès** que les actions qu'elle
     touche sont intégrées (construire, lancer, un vrai appel, un essai de 30 s), pas après la
     dernière action ; la commande et le résultat vont dans `etat.md`. Une vérification `humain`
     va au rapport, section 1, avec ce qu'il faut regarder.
   - **Revue visuelle** : pour une action `Rendu : oui`, dès son intégration, une capture du
     produit avec l'outil de navigateur disponible dans la session ; à défaut, la vérification
     passe en `humain`. Un écart visible aux specs est un incident, pas un correctif du pilote.
5. Quand tout est intégré, sur l'intégration :
   - `test_cmd` complet (non-régression comprise) ;
   - `trace.py check . --tests <tests_dir>` ⇒ aucun problème ;
   - `trace.py guard . <sha départ> HEAD --tests <tests_dir>` ⇒ aucune violation ; une violation
     ⇒ annuler le commit fautif (`git revert`) et relancer le `dev` en `correction` ;
   - `trace.py proves . <sha départ> HEAD --tests <tests_dir> --cmd "<test_cmd_un_test>"
     [--case-regex "<case_regex>"] > docs/build/runs/proves.json` (un verdict par cas si la
     commande contient `{case}`) ⇒ `ne_prouve_rien` renvoyé au `tester` (réécrire le test),
     `echoue_integration` ⇒ section 3. `proves` rejoue chaque cas sur un checkout neuf du départ,
     où le produit n'existe pas : lancer sans écran (`env -u DISPLAY -u WAYLAND_DISPLAY`) si la
     commande peut ouvrir une fenêtre (moteur de jeu, navigateur), sinon une alerte s'affiche par
     cas ; un cas `echoue_integration` qui passe dans `test_cmd` signale une étape de préparation
     absente du checkout neuf (import d'assets, dépendances) à mettre dans `test_cmd_un_test` ;
   - `trace.py audit "$RUNS"/tests-*.json --tests <tests_dir> --test-cmd "<test_cmd>"
     --allow <normes, séparées par des virgules>` (les runs du testeur en mode `ecrire` seulement)
     ⇒ chaque lecture du plan ou du code, lecture hors projet ou exécution d'interpréteur qui a
     abouti est une **fuite d'indépendance** : les cas écrits pendant ce run sont relus contre les
     specs (diagnostic `test` si besoin), et la fuite va au rapport. Une tentative bloquée par les
     verrous est marquée `"refuse": true` : elle va au rapport sans relecture ;
   - `trace.py cost "$RUNS"` ⇒ coûts par rôle et par action, lancements et reprises, pour le
     rapport ; noter dans la section « Modèles résolus » de la config les modèles de la colonne
     Modèles et celui de ta session (sinon « non mesuré »).
6. Relire la PR toi-même (diff complet contre la branche de départ) : écarts aux specs, code mort,
   secrets, fichiers hors périmètre. Ton avis va dans le rapport, pas en commit.
7. Pousser la branche d'intégration, ouvrir la PR vers la branche de départ, écrire le rapport
   (`references/rapport-recette.md`), le committer, donner le lien à l'utilisateur.

## 3. Test en échec

Relancer `tester` en mode `diagnostic <test>` (modèle et effort de `diagnostic` dans la config),
avec dans le prompt les ids des specs qui touchent le test (celles qui couvrent ses `REQ`, d'après
la matrice), puis router selon `blocker.kind` :

| Cause | Qui corrige | Suite |
|---|---|---|
| `test` | le testeur l'a déjà corrigé (`done`) | intégrer, relancer le test sur départ et intégration (`proves`) |
| `code` | `dev` mode `correction ACT-xxx` + l'écart | intégrer, relancer le test |
| `spec` | `analyst` mode `correction SPEC-xxx` + le diagnostic | puis `tester` et `dev` sur ce qui dépend de la spec |
| `besoin` | l'utilisateur | escalade (section 4) |
| `env` | personne | s'arrêter si tout est touché, sinon mettre de côté et le dire au rapport |

Chaque cycle diagnostic → correction incrémente le compteur de la `REQ` dans `etat.md`. **Plus de
deux** cycles sur une même `REQ` ⇒ `REQ` « bloquée », ses dépendants mis de côté, le reste continue.
Un second diagnostic sur une même `REQ` part au palier `diagnostic escalade` ; un diagnostic qui
désigne `besoin` y est refait une fois avant l'escalade vers l'utilisateur.

## Tests d'acceptation et tests unitaires

| | Acceptation | Unitaires |
|---|---|---|
| Auteur | `tester`, depuis le besoin et les specs | `dev`, depuis l'action et le code |
| Rattachés à | une `REQ` et un numéro de critère | une `ACT` |
| Dossier | `tests_dir` (interdit aux `dev`, `guard`) | hors `tests_dir` |
| Prouvés par | `proves` (échec au départ, succès à l'intégration) | `test_cmd` |
| Rôle | dire si le besoin est tenu | protéger ce que les tests d'acceptation ne voient pas |

Un `dev` ne reprend pas en unitaire un critère déjà couvert par un test d'acceptation. Une
vérification qu'aucun des deux ne peut faire (pile réelle, rendu, ressenti) est planifiée par toi
(étape 4), pas simulée par des doublures.

## 4. Escalade sans bloquer

Question de besoin (analyste ou diagnostic `besoin`) : mettre de côté la `REQ` et tout ce qui en
dépend (`SPEC`, `ACT`, tests), terminer le reste, et placer la question **en tête du rapport** avec
les options proposées. Quand l'utilisateur répond : si une skill ADR est disponible dans la session (par exemple
`archi-docs:adr` ou une skill de l'utilisateur), l'invoquer pour consigner sa décision ; sinon lui
proposer le texte de la section Décisions du besoin (contexte, choix, raison, date) et signaler
qu'une skill ADR est recommandée. Il met à jour le besoin, et une nouvelle passe `/build` traite le delta.

## 5. Arrêts immédiats

Au **premier** lancement, si la commande est introuvable, l'agent inconnu, l'authentification ou
la facturation refusées : s'arrêter, citer le message exact (stderr), ne pas relancer en boucle.
Un agent sans JSON final, en code ≠ 0 ou hors délai = `failed` (jamais d'attente infinie) : une
relance, puis on le met de côté au rapport.

## État de suivi

`docs/build/etat.md`, tenu par toi seul, committé avec le rapport :

```markdown
# État du build

Départ : main @ <sha> · Intégration : build/<sujet> · Besoin : <sha du besoin>

| Élément | Statut | Agent | Diagnostics | Coût | Note |
|---|---|---|---|---|---|
| REQ-001 | en cours / ok / mise de côté / bloquée | | 0 | | |
| ACT-001 | à faire / en cours / intégrée / failed | dev | | 0,42 $ | standard, 0 reprise |
```

Puis deux rubriques : `## Vérifications` (`REQ`, nature, commande ou ce qu'il faut regarder,
résultat) et `## Fuites d'indépendance` (sortie de `trace.py audit`, « Aucune. » si vide).

## Références

- `references/lancer-un-agent.md` : commande, lecture du résultat, intégration des worktrees.
- `references/config-exemple.md` : `docs/build/config.md` par défaut, lanceur perso.
- `references/rapport-recette.md` : plan du rapport de recette.
- `references/scenarios.md` : scénarios d'acceptation du pilote.
