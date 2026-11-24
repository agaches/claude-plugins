---
name: brain
description: Phase 1 du kit brain-build. Réflexion, grill, puis relecture critique par personas jusqu'à un besoin figé, avec des exigences numérotées REQ-xxx et leurs critères d'acceptation, prêt pour la phase build sans retour vers l'utilisateur. À utiliser quand l'utilisateur lance /brain, veut « poser le besoin », « cadrer un produit », « réfléchir à ce qu'on construit », ou prépare une nouvelle version du besoin d'un produit existant.
---

# Brain : figer le besoin

Tu conduis une session interactive qui aboutit à `docs/besoin.md`. Ce fichier est la seule entrée
de la phase build : un agent qui le lit doit pouvoir travailler **sans revenir vers
l'utilisateur**. Toute ambiguïté laissée ici devient une escalade plus tard.

Prérequis : le plugin `superpowers` (skill `superpowers:brainstorming`). S'il manque, le dire,
donner `claude plugin install superpowers@claude-plugins-official`, et mener la réflexion
toi-même.

## Déroulé

1. **Contexte.** Produit neuf ou nouvelle version ? Si `docs/besoin.md` existe, le lire : la
   nouvelle version garde les ids existants, ajoute les nouvelles `REQ` à la suite, et ne
   renumérote jamais. Lire aussi `GLOSSARY.md` et `docs/adr/` s'ils existent.
2. **Réflexion.** `superpowers:brainstorming` : intention, utilisateurs, ce qui doit exister à la
   fin. Fini quand l'utilisateur valide une liste d'exigences candidates.
3. **Grill** (section Grill), jusqu'à son critère de fin.
4. **Dimensionner** (section Dimensionner) : trier chaque exigence candidate entre `REQ`, réglage et
   choix de réalisation, avant d'écrire.
5. **Prototype**, pour un produit dont la qualité se juge à l'usage (jeu, interface, rendu) :
   proposer un prototype rapide, jetable, et le faire essayer **par l'utilisateur** avant de
   figer. Ce qu'il en dit devient des `REQ` sur le comportement ou des réglages, pas des
   impressions. L'utilisateur peut refuser : le noter dans le besoin (Contraintes).
6. **Normes.** S'il y a du code : normes et conventions (langage, style, outil de test, dossiers),
   lues dans le repo d'abord, demandées seulement si absentes. Elles alimenteront
   `docs/build/config.md`.
7. **Rédaction.** Écrire `docs/besoin.md` selon `references/modele-besoin.md`. Pour un sujet qui
   n'est pas un produit à construire, forme libre : le gabarit sert la phase build seulement.
8. **Contrôle.** `python3 "${CLAUDE_SKILL_DIR}/../../scripts/trace.py" check . --only req_sans_critere,besoin_long,critere_constante,critere_probabiliste`
   rend `"problems": []`, et chaque critère a un seuil chiffré là où il dirait « rapide »,
   « simple » ou « intuitif ». Chaque `warnings` se traite avec l'utilisateur :
   - `besoin_long` (plus de 15 `REQ`) : regrouper, ou repasser des `REQ` en réglages ;
   - `critere_constante` : la valeur est-elle une contrainte ferme (elle reste) ou un réglage (elle
     va dans `## Réglages`, et le critère cite son nom) ?
   - `critere_probabiliste` (« 15 graines sur 20 ») : le justifier dans la `REQ` ou le reformuler
     sur un comportement.
9. **Roast.** Skill `roast-me` sur `docs/besoin.md`. Chaque critique retenue devient une question
   d'un nouveau tour de grill ; corriger le besoin selon les réponses, puis refaire le contrôle.
10. **Figer.** Faire valider le besoin par l'utilisateur, le committer (`docs: besoin v<n>`), et
    dire la suite : `/build`. Même quand la session tourne en autonomie (l'agent tient le rôle du
    client pour le grill), cette validation finale revient à l'utilisateur, en une seule question :
    un agent ne valide pas son propre besoin.

## Grill

Mettre chaque exigence à l'épreuve jusqu'à ce qu'elle soit vérifiable par un test, sans rien
laisser supposé.

- **Par tours.** Un tour pose ensemble toutes les questions qui ne dépendent d'aucune réponse
  encore attendue ; celles qui en dépendent attendent le tour suivant. Chaque question est
  numérotée et porte ta recommandation, formulée pour que « oui » l'accepte :

  ```
  **Q1 : <titre>** <question, options s'il y en a>
  → Recommandation : <réponse proposée>
  ```

- **Faits et décisions.** Les faits (ce que fait le code, ce que dit une doc, ce qui existe
  déjà) se cherchent : lis le repo, ou lance un sous-agent si la recherche est longue, et
  continue le tour pendant ce temps. Seules les décisions vont à l'utilisateur.
- **Scénarios.** Pour chaque exigence, proposer un cas limite concret (vide, absent, énorme,
  simultané, erreur) et demander le résultat attendu exact : chiffres, messages, codes.
- **Vocabulaire.** Un terme flou ou employé dans deux sens : proposer un terme unique. Dès qu'un
  terme est tranché, l'écrire dans `GLOSSARY.md` (`**Terme** : définition`, sans détail
  d'implémentation).
- **Décisions qui engagent.** Une décision coûteuse à défaire, prise entre de vraies options :
  si une skill ADR est disponible dans la session (par exemple `archi-docs:adr` ou une skill de
  l'utilisateur), l'invoquer ; sinon consigner la décision dans `docs/besoin.md`, section
  Décisions (contexte, choix, raison, date), et signaler qu'une skill ADR est recommandée.

**Fin du grill** : aucune question ouverte, chaque exigence candidate a au moins un critère avec
un résultat observable exact, et l'utilisateur confirme qu'on s'est compris.

## Dimensionner

Le besoin tient en une lecture de 10 minutes. Trier chaque exigence candidate avec quatre
questions, dans l'ordre :

| Question | Si oui |
|---|---|
| L'utilisateur remarque-t-il son absence en une minute d'usage ? | `REQ`, avec 2 à 4 critères sur le comportement |
| Est-ce une contrainte ferme (légal, plateforme, sécurité, contrat d'interface) ? | `REQ` ou Contraintes, avec un critère exact |
| Est-ce un nombre qu'on ajustera à l'usage (vitesse, points, cadence, seuil) ? | ligne de `## Réglages` (nom, valeur, unité), pas de `REQ` |
| Est-ce un choix de réalisation ? | rien : la décision revient au `dev`, ou à une ADR si elle engage |

Ordre de grandeur : un petit produit tient en 10 à 15 `REQ` et une page de réglages. Un critère trop
précis (« à moins de 40 px pour au moins 15 graines sur 20 ») fait bloquer l'analyste sur un calcul,
pas sur une intention : il porte sur le comportement (« l'ennemi vise le joueur »), la valeur va aux
réglages. Un critère ne doit pas dicter le design (« un pilote automatique sans adresse franchit le
tronçon 1 » a donné un niveau droit et plat).

## Règles du besoin

- Une exigence = un comportement observable, avec au moins une ligne `Critère :`.
- Un critère se vérifie par un test automatique : entrée, action, résultat attendu, chiffres et
  messages exacts.
- Le besoin dit quoi, pas comment ; une technique imposée va dans la rubrique Contraintes.
- Une `REQ` = une chose visible par l'utilisateur ; une mécanique donne une `REQ` avec 2 à 4
  critères, pas une `REQ` par valeur.
- Les valeurs exactes qu'on règle à l'usage vont dans `## Réglages` ; les tests unitaires du `dev`
  les vérifient, les critères citent leur nom.
- Une exigence qui n'existe que pour la recette (exposer l'état, une API de test) va dans les
  Contraintes.
- Les non-objectifs et anti-objectifs sont écrits : ils bornent ce que les agents construisent.
