---
name: brain
description: Phase 1 du kit brain-build. Réflexion puis passage sur le grill jusqu'à un besoin figé, avec des exigences numérotées REQ-xxx et leurs critères d'acceptation, prêt pour la phase build sans retour vers l'utilisateur. À utiliser quand l'utilisateur lance /brain, veut « poser le besoin », « cadrer un produit », « réfléchir à ce qu'on construit », ou prépare une nouvelle version du besoin d'un produit existant.
---

# Brain : figer le besoin

Tu conduis une session interactive qui aboutit à `docs/besoin.md`. Ce fichier est la seule entrée
de la phase build : un agent qui le lit doit pouvoir travailler **sans revenir vers
l'utilisateur**. Toute ambiguïté laissée ici devient une escalade plus tard.

## Prérequis

Deux plugins tiers, à installer s'ils manquent (vérifie que leurs skills sont disponibles) :

- `superpowers` (skill `superpowers:brainstorming`) ;
- `mattpocock-skills` (skills `grilling` et `domain-modeling`, réunies par `grill-with-docs`).

```
claude plugin install superpowers@claude-plugins-official
claude plugin install mattpocock-skills@claude-plugins-official
```

S'ils manquent : le dire, donner ces commandes, et proposer de continuer en mode dégradé
(mêmes étapes, menées par toi sans ces skills).

## Déroulé

1. **Contexte.** Produit neuf ou nouvelle version ? Si `docs/besoin.md` existe, le lire : la
   nouvelle version garde les ids existants, ajoute les nouvelles `REQ` à la suite, et ne
   renumérote jamais.
2. **Réflexion.** `superpowers:brainstorming` : intention, utilisateurs, ce qui doit exister à la
   fin. Une question à la fois.
3. **Grill.** `grilling` puis `domain-modeling` : chaque exigence est attaquée jusqu'à être
   vérifiable ; le vocabulaire va dans `GLOSSARY.md`, les décisions structurantes dans
   `docs/adr/`.
4. **Normes.** S'il y a du code : demander les normes et conventions (langage, style, outil de
   test, dossiers) ou les pointer dans le repo. Elles alimenteront `docs/build/config.md`.
5. **Rédaction.** Écrire `docs/besoin.md` selon `references/modele-besoin.md`. Pour un sujet qui
   n'est pas un produit à construire, forme libre : le gabarit sert la phase build seulement.
6. **Contrôle.** Si le plugin est disponible :
   `python3 "${CLAUDE_SKILL_DIR}/../../scripts/trace.py" check . --only req_sans_critere`
   doit rendre `{"problems": []}`. Relire chaque critère : observable, sans « rapide »,
   « simple », « intuitif » sans seuil.
7. **Figer.** Faire valider le besoin par l'utilisateur, puis le committer
   (`docs: besoin v<n>`). Dire la suite : `/build`.

## Règles

- Une exigence = un comportement observable, avec au moins une ligne `Critère :`.
- Un critère se vérifie par un test automatique : entrée, action, résultat attendu, chiffres et
  messages exacts.
- Pas de solution technique dans le besoin, sauf contrainte réelle (rubrique Contraintes).
- Pas de `REQ` fourre-tout : deux comportements = deux `REQ`.
- Les non-objectifs et anti-objectifs sont écrits : ils empêchent les agents d'en faire trop.
