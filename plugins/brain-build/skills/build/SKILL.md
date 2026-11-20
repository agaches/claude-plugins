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
- Un agent ne reçoit que des **pointeurs** (chemins, ids), jamais le contenu des fichiers.
- Personne ne modifie `docs/besoin.md`, ni toi ni un agent. Un changement de besoin = décision de
  l'utilisateur, consignée dans une ADR (`docs/adr/`).
- Tu ne tranches pas un test en échec : c'est le diagnostic du `tester` qui désigne la cause.
- La matrice et les garde-fous viennent de `trace.py`, jamais de ta lecture des fichiers.
- Pas de merge sur la branche principale ni de déploiement : la recette et le merge sont à
  l'utilisateur.
- Un incident isolé ne justifie pas de réécrire les consignes des agents : il va dans le rapport.

## 1. Démarrage

1. Repo git propre (`git status` vide), sinon s'arrêter et le dire.
2. `docs/besoin.md` présent. S'il vient d'une phase 1 faite ailleurs, le déposer et le committer.
3. `docs/build/config.md` : s'il manque, le créer depuis `references/config-exemple.md` en
   déduisant `test_cmd`, `tests_dir` et `normes` du repo ; demander seulement ce qui ne se déduit
   pas. Ajouter `docs/build/runs/` au `.gitignore`.
4. `python3 "$PLUGIN/scripts/trace.py" check . --tests <tests_dir> --only req_sans_critere` :
   une `REQ` sans critère ⇒ s'arrêter et demander à l'utilisateur de compléter le besoin.
5. Noter la branche de départ et son sha, créer la branche d'intégration `build/<sujet>` et
   l'écrire dans `docs/build/etat.md` (modèle ci-dessous).
6. **Maintenance** : si le besoin a déjà été construit (`docs/specs/` non vide), le delta est la
   liste des `REQ` ajoutées ou modifiées depuis la dernière recette
   (`git diff <sha dernière recette> -- docs/besoin.md`). Seul le delta est traité ; tous les
   tests existants servent de non-régression.

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
   - `tester` mode `ecrire REQ-…`, dans son worktree, depuis l'intégration **avant** tout code ;
   - un `dev` par action dont les dépendances sont intégrées, chacun dans son worktree.
4. À chaque fin d'agent : lire le résultat, mettre à jour `etat.md`, intégrer sa branche
   (`references/lancer-un-agent.md`, « Intégrer »), lancer ce qui devient prêt.
5. Quand tout est intégré, sur l'intégration :
   - `test_cmd` complet (non-régression comprise) ;
   - `trace.py check . --tests <tests_dir>` ⇒ aucun problème ;
   - `trace.py guard . <sha départ> HEAD --tests <tests_dir>` ⇒ aucune violation ; une violation
     ⇒ annuler le commit fautif (`git revert`) et relancer le `dev` en `correction` ;
   - `trace.py proves . <sha départ> HEAD --tests <tests_dir> --cmd "<test_cmd_un_test>"
     [--case-regex "<case_regex>"] > docs/build/runs/proves.json` (un verdict par cas si la
     commande contient `{case}`) ⇒ `ne_prouve_rien` renvoyé au `tester` (réécrire le test),
     `echoue_integration` ⇒ section 3.
6. Relire la PR toi-même (diff complet contre la branche de départ) : écarts aux specs, code mort,
   secrets, fichiers hors périmètre. Ton avis va dans le rapport, pas en commit.
7. Pousser la branche d'intégration, ouvrir la PR vers la branche de départ, écrire le rapport
   (`references/rapport-recette.md`), le committer, donner le lien à l'utilisateur.

## 3. Test en échec

Relancer `tester` en mode `diagnostic <test>` (modèle et effort de `diagnostic` dans la config),
puis router selon `blocker.kind` :

| Cause | Qui corrige | Suite |
|---|---|---|
| `test` | le testeur l'a déjà corrigé (`done`) | intégrer, relancer le test sur départ et intégration (`proves`) |
| `code` | `dev` mode `correction ACT-xxx` + l'écart | intégrer, relancer le test |
| `spec` | `analyst` mode `correction SPEC-xxx` + le diagnostic | puis `tester` et `dev` sur ce qui dépend de la spec |
| `besoin` | l'utilisateur | escalade (section 4) |
| `env` | personne | s'arrêter si tout est touché, sinon mettre de côté et le dire au rapport |

Chaque cycle diagnostic → correction incrémente le compteur de la `REQ` dans `etat.md`. **Plus de
deux** cycles sur une même `REQ` ⇒ `REQ` « bloquée », ses dépendants mis de côté, le reste continue.

## 4. Escalade sans bloquer

Question de besoin (analyste ou diagnostic `besoin`) : mettre de côté la `REQ` et tout ce qui en
dépend (`SPEC`, `ACT`, tests), terminer le reste, et placer la question **en tête du rapport** avec
les options proposées. Quand l'utilisateur répond : skill `adr` pour consigner sa décision, il met
à jour le besoin, et une nouvelle passe `/build` traite le delta.

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
| ACT-001 | à faire / en cours / intégrée / failed | dev | | 0,42 $ | |
```

## Références

- `references/lancer-un-agent.md` : commande, lecture du résultat, intégration des worktrees.
- `references/config-exemple.md` : `docs/build/config.md` par défaut, lanceur perso.
- `references/rapport-recette.md` : plan du rapport de recette.
- `references/scenarios.md` : scénarios d'acceptation du pilote.
