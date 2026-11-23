# Retours sur brain-build : trois produits construits avec le kit

Synthèse de trois analyses faites le 2026-11-23 sur des projets réels, à partir des transcriptions de sessions, des états de build et des rapports de recette. Les produits sont anonymisés :

- **Jeu A** : jeu d'arcade web, repris ensuite en application mobile.
- **Jeu B** : jeu d'arcade mobile, quatre langues.
- **Outil C** : outil de veille technique (backend, front, appels à un LLM).

Limites : trois produits seulement, aucune comparaison avec un développement sans le kit, coût du pilote non isolable, coûts en dollars repris des états de build (non recalculés sur les tarifs), durées lues sur les horodatages.

## Comparatif

| | Jeu A | Jeu B | Outil C |
|---|---|---|---|
| Exigences (REQ) | 41 | 21 (81 critères) | 62 (224 critères) |
| Specs / actions | 21 / 22 | 14 / 13 | n/d / 38, puis plus de 59 avec les deltas |
| Tests à la livraison | 541, tous verts | 199 réussis sur 201 | 658 backend et 139 front verts, après une 1re passe à 92 échecs |
| Preuve `proves` | 6 tests déjà verts sur `main` sans rien prouver, repérés | 127 des 129 cas échouent au départ, passent à l'intégration | 64 fichiers sur 64 échouent sans le code, passent avec |
| Coût des agents | environ 37 $ | environ 11 $ | environ 55 $ (dont 20 % de rattrapage) |
| Temps de build | environ 1 h 30 machine | 1 h 25, après 4 h 44 d'arrêt silencieux du pilote | environ 3 h 25 utiles, plus 3 h 13 bloquées par la limite d'usage |
| Taille du produit | environ 2 700 lignes | n/d | n/d |
| Ce que les tests n'ont pas vu | plaisir de jeu, rendu : première version rejetée en 4 minutes de jeu | rythme, tailles, ressenti : 24 commits d'essai hors kit | image Docker, format JSON du prompt, budget de temps du reclassement |
| État après coup | portage et réglages hors kit | 70 tests d'acceptation sur 211 rouges, besoin v2 jamais passé en build | n/d (pas de recette finale visible) |
| Verdict | utile pour la justesse, mal dimensionné pour le plaisir | utile pour le socle, peu pour le jeu | utile avec réserves : le vert ne prouve pas que ça marche |

## Ce qui a payé

Les exemples les plus parlants pour comprendre comment le besoin devient des tests.

### E1. La relecture par personas casse le besoin avant le code

- Jeu A : trois relecteurs sur quatre ont calculé que le bilan de la ressource principale était négatif et qu'un ennemi ne pouvait jamais toucher le joueur. Corrigé dans le besoin, pas dans le code.
- Jeu B : le grill et la relecture ont fait remonter une partie potentiellement infinie, un élément d'interface masqué, et une exigence « jamais plus de 1,5 s d'arrêt » fausse avec un événement tardif.

### E2. Une contradiction entre deux REQ, détectée par le testeur

Jeu B : REQ-001 interdit un mot dans tous les textes, REQ-020 impose un texte qui le contient. En diagnostic, le testeur désigne le besoin comme fautif (ni le code ni le test). La contradiction est placée en tête de la recette au lieu d'être masquée. À consigner ensuite en ADR.

### E3. L'analyste bloque sur ce qui est intenable

Jeu A : deux critères d'un ennemi sont prouvés intenables par simulation avant d'écrire un test. Résultat : deux ADR et un besoin réécrit, au lieu d'un test instable.

### E4. Des tests écrits sans voir le code, puis prouvés

Le testeur écrit depuis le besoin et les specs seulement, chaque test rattaché à une REQ. Le contrôle `proves` rejoue les tests sur le code de départ : ils doivent échouer, puis passer à l'intégration.

- Jeu B : 127 cas sur 129.
- Outil C : 64 fichiers sur 64.
- Jeu A : 6 tests qui passaient déjà sur `main` ont été éliminés, et un vrai bug de code (aléa mal initialisé) a été attrapé par les tests.

### E5. Un diagnostic remonte à la cause, pas au symptôme

Outil C : 71 des 92 échecs de la première passe avaient une seule cause (l'horloge de la base de données au lieu de celle de l'application). Un seul diagnostic l'a trouvée.

### E6. Traçabilité et changements de besoin

Matrice REQ, SPEC, ACT, test avec l'état « échoue au départ, passe à l'intégration » dans la recette. Les changements de besoin passent en deltas (spec, actions, tests, ADR) : outil C de v2 à v5, jeu A absorbé en une passe avec une seule correction de code.

### E7. Parallélisme sans conflit

Jusqu'à 7 dev simultanés sur le jeu A, zéro conflit de merge. 13 actions intégrées en 12 minutes sur le jeu B.

## Ce qui n'a pas payé

| Ref | Constat | Produits |
|---|---|---|
| L1 | Ce qui ne se teste pas n'est pas optimisé : aucun critère pour « joli » ni « fun ». Un test peut même dicter le design (un niveau rendu plat pour satisfaire « franchissable sans pilote »). | A, B |
| L2 | Surdimensionnement : 41 REQ, 541 tests pour 2 700 lignes. Des réglages (un seuil de distance) écrits comme des exigences ont coûté 2 ADR, 2 passes d'analyste et un test de 20 graines. | A |
| L3 | Le vert ne prouve pas que le produit marche : les tests dérivent des specs, et ce que les specs ne disent pas n'est jamais exercé. | C, A, B |
| L4 | Suite d'acceptation périmée : le produit évolue hors kit, les tests ne suivent pas, 70 cas rouges en permanence ne protègent plus rien. | B |
| L5 | Le pilote est aussi le client : il valide son propre besoin, le vrai avis n'arrive qu'après avoir joué. | A |
| L6 | Arrêt silencieux du pilote (4 h 44 sans progrès) et limite d'usage (3 h 13 d'arrêt). | B, C |
| L7 | Outillage fragile : worktrees créés depuis `main` et non depuis la branche d'intégration, projet en sous-dossier non géré, droits de `trace.py`, `proves` qui rejoue sur `main` et ouvre des fenêtres bloquantes. | A, B |
| L8 | Indépendance du testeur non garantie : un testeur a lu le code, un prompt du pilote citait des fichiers du code, `proves` ne le détecte pas. 3 diagnostics sur 4 ont désigné un test faux. | A |

## Bilan

1. **Le kit est le plus rentable en amont du code** : relecture par personas (E1), détection de contradiction (E2), blocage de l'analyste (E3). C'est là que des erreurs de besoin sont attrapées à bas coût.
2. **Les tests écrits à l'aveugle et prouvés (E4) mesurent quelque chose**, ce qui n'est pas acquis avec des tests écrits par le dev. Mais ils mesurent le besoin écrit, pas le besoin réel (L1, L3).
3. **Le kit convient aux produits à règles précises** (calculs, formats, contrats, conformité). Pour un produit dont la qualité se juge à l'usage, il faut un prototype essayé par l'utilisateur avant de figer le besoin.
4. **Un besoin court et une table de paramètres** valent mieux que des REQ pour des valeurs qu'on règle en jouant (L2).
5. **Un test de fumée sur la pile réelle** (construire l'image, appeler le vrai LLM, jouer 30 s) est à faire dès les premières actions intégrées, pas après la dernière.
6. **Si le produit évolue hors kit, il faut décider** : repasser le besoin en `/build` en delta, ou retirer les tests d'acceptation périmés. Les laisser rouges est la pire option.

## Pourquoi autant de tests pour un périmètre aussi petit ?

Mesuré sur les trois produits : le volume de tests d'acceptation suit le **nombre de critères du besoin**, pas la taille du code (25 à 36 lignes de test par critère dans les trois produits, alors que le code vaut de 15 à 33 lignes par critère). Un code très dense en critères, comme les deux jeux, donne des tests qui font 2 à 3 fois le code ; l'outil C, dont le code compte beaucoup d'infrastructure, reste à 1,4.

Autres constats : 5 à 7 assertions et 1,6 à 2,2 cas par critère, des tests unitaires des dev qui ajoutent un tiers à la moitié de cas sans lien avec les REQ, et 10 à 22 % de lignes répétées d'un fichier de test à l'autre (10 % seulement dans le produit B, qui a un banc d'essai partagé).

Détail, tableaux et pistes pour réduire le volume : [volume_des_tests.md](volume_des_tests.md).

## Ce que la version 0.4.0 en tire

Les constats ci-dessus ont donné cinq issues (#12, #13, #14, #16, #17), traitées dans la 0.4.0. Rien
n'est encore mesuré sur un nouveau build : ce sont des consignes et des contrôles, pas des résultats.

| Constat | Changement |
|---|---|
| L1, L5 | Brain : prototype essayé par l'utilisateur pour un produit jugé à l'usage, validation finale du besoin par l'utilisateur même en autonomie. Build : vérifications `pile_reelle` et `humain` remontées par le testeur, revue visuelle des actions de rendu par le pilote |
| L2 | Brain : étape « Dimensionner » (REQ, réglage ou choix de réalisation), rubrique `## Réglages` du besoin, avertissements de `trace.py check` (plus de 15 REQ, constante hors Réglages, critère probabiliste). Analyste : specs par module du code, plan proportionné |
| L3 | Vérifications sur la pile réelle faites dès l'intégration des actions concernées (bilan, point 5) |
| L7 | Worktrees créés par le pilote depuis la branche d'intégration, chemins absolus vers les runs, `trace.py` sur un projet en sous-dossier, motif de cas JS ancré, `< /dev/null` |
| L8 | Testeur verrouillé au lancement (`--disallowedTools` sur le code et le plan, pas d'interpréteur), prompts du pilote sans fichier du code, `trace.py audit` qui relit les transcriptions. Diagnostic : specs en cause dans le prompt, relecture des règles générales |
| Volume des tests | Testeur : une forme de test par forme de critère, un critère = une fonction de test, banc d'essai partagé, critère non testable = blocage. Dev : unitaires rattachés à une action, sans reprendre un critère |
| Coûts (#17) | Modèle et effort du dev par complexité d'action, escalade sur échec, diagnostic en `sonnet` d'abord, `trace.py cost` par rôle et par action dans le rapport, modèles résolus notés |

Rejoué sur les transcriptions du jeu A, `trace.py audit` retrouve les trois fuites décrites en L8 :
exécution du générateur de niveau par le testeur, lecture de `index.html` et de fichiers du code
après un prompt qui les citait, lecture d'un ancien document de conception.

Reste à faire : rejouer un besoin existant (le jeu B, le plus petit) avec la nouvelle consigne du
testeur et au moins deux configurations de modèles, puis consigner cas par critère, reprises, coût
par rôle et défauts attrapés à la recette.
