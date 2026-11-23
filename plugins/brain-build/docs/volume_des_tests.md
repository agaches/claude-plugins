# Pourquoi brain-build produit autant de tests : mesure sur trois produits

Complément de [retours_sur_brain_build.md](retours_sur_brain_build.md). La question : un jeu de 2 700 lignes
a reçu 541 tests, soit plus de trois fois le code en lignes. Est-ce de la surproduction, ou la conséquence
normale d'un cycle en V où les tests dérivent du besoin et des specs, pas du code ?

Réponse courte : **le volume de tests suit le nombre de critères d'acceptation, pas la taille du code.**
Ce qui paraît disproportionné vient d'un code très petit par critère, pas de tests gonflés. Deux leviers
restent à tester pour le réduire (section « Ce qui reste à essayer »).

## Méthode et limites

- Mesure par script sur le code et les tests **à l'état de la recette** de chaque produit (extraits du
  commit de recette), pas sur l'état actuel, pour ne pas compter les itérations faites hors kit.
- Un « cas » = une définition de test (`it(`, `def test_`, `func test_`). Un test paramétré ou qui boucle
  compte pour 1 : le nombre de vérifications réelles est plus grand.
- Les « critères » sont les lignes `Critère :` du besoin.
- Les tests d'acceptation sont ceux du testeur. Les tests unitaires sont ceux des dev.
- Le produit C a continué après le build : à la recette, il compte 65 REQ et 260 critères (62 et 224 au
  rapport initial). Les chiffres ci-dessous sont ceux de la recette.
- Rien ici ne dit quels tests sont **inutiles**. Seul un test de mutation le dirait (voir fin de document).

## Les chiffres

| Mesure | Jeu A | Jeu B | Outil C |
|---|---|---|---|
| REQ / critères | 41 / 179 | 21 / 81 | 65 / 260 |
| Code (lignes) | 2 714 | 1 249 | 8 556 |
| Tests d'acceptation (cas / lignes) | 392 / 6 182 | 129 / 2 019 | 502 / 9 454 |
| Tests unitaires des dev (cas / lignes) | 149 / 2 169 | 72 / 877 | 160 / 2 380 |
| Lignes de test / lignes de code | 3,1 | 2,3 | 1,4 |
| **Lignes de code par critère** | **15** | **15** | **33** |
| **Lignes de test d'acceptation par critère** | **35** | **25** | **36** |
| Lignes de code par REQ | 66 | 59 | 132 |
| Lignes de test d'acceptation par REQ | 151 | 96 | 145 |
| Cas d'acceptation par critère | 2,2 | 1,6 | 1,9 |
| Assertions d'acceptation par critère | 7,4 | 5,4 | 6,8 |
| Lignes d'acceptation par assertion | 4,6 | 4,6 | 5,4 |
| Cas unitaires / cas d'acceptation | 0,38 | 0,56 | 0,32 |
| Lignes d'acceptation répétées d'un fichier à l'autre | 20 % | 10 % | 22 % |
| Mentions de REQ dans les tests unitaires | 0 | 4 | 0 |

## Ce que ça montre

### M1. Le volume suit les critères, pas le code

Les lignes de test d'acceptation par critère sont stables (25 à 36), alors que les lignes de code par
critère varient de 15 à 33. Quand le code est dense en critères (jeux A et B : 15 lignes de code par
critère), les tests font 2 à 3 fois le code. Quand il l'est moins (outil C : 33 lignes par critère,
beaucoup de code d'infrastructure sans critère propre), ils font 1,4 fois le code.

Autrement dit, « disproportionné » est un effet de la comparaison avec les lignes de code. Rapporté au
besoin, chaque critère coûte à peu près la même taille de test dans les trois produits.

### M2. Chaque critère donne plusieurs assertions et près de deux cas

De 5,4 à 7,4 assertions et de 1,6 à 2,2 cas par critère. Le testeur a pour consigne d'écrire au moins un
test par critère, et les critères sont déjà chiffrés et bornés (seuils, cas limites, avant/après). Un
critère à deux issues donne deux cas ; un critère avec un seuil en donne autour du seuil.

### M3. L'écriture « sans voir le code » ne gonfle pas les tests autant que je l'avais écrit

La première version de l'analyse (jeu A seul) attribuait une part du volume à la reconstruction d'un
banc d'essai par chaque fichier de test. Les trois produits corrigent ce point :

- Les lignes par assertion (4,6 ; 4,6 ; 5,4) sont **les mêmes** dans les trois produits : ce n'est pas
  une anomalie du jeu A.
- La duplication entre fichiers est de 20 % (A), 22 % (C) et **10 % dans le produit B**, qui a une aide
  partagée dans les tests d'acceptation. Le banc partagé divise la duplication par deux. Il ne réduit pas
  le volume : B a encore 1,6 cas et 5,4 assertions par critère.

La duplication est donc réelle, mais ce n'est pas elle qui explique l'essentiel.

### M4. Les tests unitaires des dev ajoutent un tiers à la moitié, sans lien avec le besoin

32 à 56 % de cas unitaires en plus des tests d'acceptation (0,38 ; 0,56 ; 0,32). Presque aucun ne cite une
REQ (0, 4 et 0 mentions). C'est une deuxième couche de vérification, rattachée à une action du plan, qui
recoupe en partie la première. Le kit ne dit pas lesquels doublent un test d'acceptation.

### M5. Le produit B a une aide partagée écrite pour l'indépendance

Dans B, l'aide commune des tests d'acceptation indique qu'elle « ne dépend du produit que par
l'interface décrite dans les specs » et charge les scripts du produit à l'exécution. Un script absent
fait échouer le cas qui s'en sert, pas tout le fichier. C'est le montage que visent le cycle en V et
l'indépendance du testeur : un banc d'essai qui ne connaît que le contrat des specs.

### M6. Dans l'outil C, des doublures de test vivent dans le code du produit

Le fichier de configuration des tests d'acceptation de C charge un plugin de test qui se trouve dans le
code du produit (`app.testing.pytest_plugin`), avec ses propres tests unitaires (`test_testing_doubles.py`).
Les tests d'acceptation dépendent donc de code écrit par les dev. Ce n'est pas forcément faux (une doublure
d'horloge ou de LLM est une interface), mais c'est un point où l'indépendance se joue et que `proves` et
`guard` ne surveillent pas.

## Pourquoi ce n'est pas du gaspillage par nature

- Le testeur n'a que le besoin et les specs. Il ne peut pas « se contenter » de la structure du code : il
  vérifie chaque critère. Le volume est la conséquence du nombre de critères que le besoin a posés.
- C'est cette lecture contre les specs qui a fait remonter des erreurs de besoin ou de spec (voir les
  exemples E2 et E3 du document principal). Moins de critères, moins de ces détections.
- `proves` garantit que chaque test échoue sans le code et passe avec : un test inutile par construction
  (déjà vert) est éliminé. Ce qui reste peut être redondant entre cas, pas vide.

## Ce qui reste à essayer

Aucune de ces pistes n'a été testée. Elles sont classées par gain attendu, d'après les mesures ci-dessus.

| Ref | Piste | Gain attendu |
|---|---|---|
| P1 | **Réduire le nombre de critères au besoin** : moins de critères, moins de tests. Regrouper ceux d'une même règle en une table de cas (entrée, attendu) et mettre les réglages numériques dans une table de paramètres hors REQ. | Fort : c'est le facteur dominant (M1, M2). |
| P2 | **Distinguer acceptation et unitaire** : tests d'acceptation rattachés à une REQ, tests unitaires rattachés à une action, et interdiction pour un dev d'écrire un unitaire qui reprend un critère déjà couvert. | Moyen : un tiers à la moitié des cas (M4). |
| P3 | **Section « interface de test » imposée aux specs**, et un banc d'essai partagé écrit une fois par le testeur (comme dans B). | Faible sur le volume, utile pour la maintenance : la duplication passe de 20 % à 10 % (M3). |
| P4 | **Mettre sous contrôle les doublures de test** écrites par les dev : les déclarer dans les specs, et faire vérifier par `guard` qu'un test d'acceptation n'importe que ce qui est déclaré. | Indépendance plutôt que volume (M6). |
| P5 | **Test de mutation** sur un produit : modifier le code à la main ou par outil, et compter les tests qui ne détectent jamais rien d'unique. | Mesure, pas réduction : dit quels tests sont redondants avant d'en retirer. |

## Corrections apportées à la première analyse

La section correspondante du document principal avait été écrite sur le seul jeu A. Après mesure des
trois produits :

- « 4,6 lignes de test par assertion » ne prouve pas que le volume est de la préparation : la valeur est la
  même dans les trois produits.
- La reconstruction du banc d'essai par fichier (jeu A : `partie` redéfinie 17 fois) est réelle, mais
  secondaire par rapport au nombre de critères.
