# Mesure : le jeu B rejoué avec brain-build 0.4.0

Rejeu du 2026-11-24, pour les issues #16 (consignes du testeur) et #17 (modèle par complexité).
Même besoin que le build d'origine (jeu B, v1 : 21 REQ, 81 critères, moteur de jeu 2D), même lanceur, même
poste. Le rejeu tourne sur une branche à part ; le build d'origine sert de référence.

Limites : une seule exécution par configuration, sur un seul produit. Deux variables changent à la
fois (consignes 0.4.0 et modèles), donc l'écart de coût ne s'attribue pas à l'une seule. Le coût du
pilote n'est pas compté.

## Configurations

| Config | Analyste | Testeur | Dev | Diagnostic | Consignes |
|---|---|---|---|---|---|
| Référence (build d'origine, 0.2.0) | opus high | sonnet high | sonnet medium | opus high | 0.2.0 |
| Économe (rejeu, 0.4.0) | opus high | sonnet high | `simple` haiku medium, `standard` sonnet medium, `difficile` opus high, escalade | sonnet high, opus en escalade | 0.4.0 |

## Volume des tests (#16)

Mesuré sur les fichiers de test, lignes non vides hors commentaires.

| | Référence | Économe |
|---|---|---|
| Tests d'acceptation : fichiers | 13 | 24 (un par REQ, plus banc, banc Android, table du besoin) |
| Cas | 129 | 81 |
| Cas par critère | 1,59 | **1,00** |
| Lignes par critère | 20,5 | 15,4 |
| Assertions par critère | 5,5 | 2,4 |
| Tests unitaires des dev : cas | 72 | 45 |
| Unitaires par critère | 0,89 | 0,56 |
| `proves` : échec au départ, succès à l'intégration | 127 / 129 | 80 / 81 |
| Cas rouges à l'intégration | 2 (contradiction du besoin) | 1 (la même) |

Objectif de l'issue : moins de 1,5 cas par critère, sans perte de détection. Tenu : un cas par
critère, et le seul défaut du besoin attrapé par la référence (une REQ interdit un mot que la table de
textes d'une autre impose) l'est aussi, et plus tôt : par le dev d'ACT-007 pendant l'action, au lieu du diagnostic
final. Aucun autre défaut n'était attrapé par la référence ; l'égalité de détection ne se juge
donc que sur ce cas, sans test de mutation (P5 de [volume_des_tests.md](volume_des_tests.md)).

Le testeur a remonté une vérification `pile_reelle` (REQ-019, export et émulateur), faite par le
pilote dès l'intégration de la dernière action. Le diagnostic qui a suivi a trouvé deux défauts du
banc (dossier de sortie absent d'un clone neuf, appui calculé en portrait) et un défaut
d'environnement (rendu logiciel de l'émulateur), sans se tromper de cause.

## Coût et reprises (#17)

| | Référence | Économe |
|---|---|---|
| Specs / actions | 14 / 13 | 9 / 9 |
| analyst | 3,52 $ (2 lancements) | 2,95 $ (3, dont une correction qui conclut au besoin) |
| tester | 2,23 $ | 1,72 $ |
| dev | 4,46 $ (14 lancements, 1 reprise) | 3,66 $ (9 lancements, 0 reprise) |
| diagnostic | 0,58 $ (opus) | 0,42 $ (sonnet) |
| **Total agents** | **10,79 $** | **8,74 $** (−19 %) |
| Diagnostics erronés | 0 | 0 |
| Durée de bout en bout | 1 h 25 (après 4 h 44 d'arrêt du pilote) | 47 min (33 min de travail d'agents) |
| Tests rouges à la recette | 2 | 1 + 1 unitaire (même contradiction) |

Par palier de dev :

| Palier | Actions | Coût | Reprises | Remarque |
|---|---|---|---|---|
| simple (haiku) | 2 | 0,04 $ | 0 | réglages (33 valeurs = 33 lignes de la spec) et sauvegarde : complets, vérifiés |
| standard (sonnet) | 6 | 1,86 $ | 0 | |
| difficile (opus) | 1 | 1,76 $ | 0 | scène principale ; 48 % du coût des dev à lui seul |

Ce qui baisse le coût est surtout le **découpage** (9 actions au lieu de 13, specs par module) et
le diagnostic en `sonnet`. `haiku` sur les deux actions simples économise peu en valeur (moins de
0,50 $) mais n'a coûté aucune reprise. L'action `difficile` en `opus` est la plus chère du build ;
rien ne dit qu'un `sonnet` aurait échoué : à mesurer avant de garder ce palier par défaut.

Critère de l'issue : une config est retenue si elle ne dégrade ni `proves` ni les défauts attrapés.
Tenu sur ce produit, avec la réserve d'une mesure unique. Les paliers par défaut de
`config-exemple.md` ne changent pas : `simple` reste en `sonnet` low, `haiku` y passe d'« jamais
mesuré » à « essayé sur deux actions simples sans reprise ».

## Indépendance (#14, en passant)

`trace.py audit` sur le testeur : six tentatives hors de sa règle (scripts en ligne qui lisaient le
besoin, écritures du fichier de projet pour faire tourner ses tests sans lanceur), toutes **refusées**
par les verrous au lancement. Le worktree du testeur partait des specs, avant tout code : il n'y
avait aucun code à lire, la mesure ne prouve donc pas que les verrous de lecture tiennent face à
un code présent. Deux faux positifs restent (nettoyage d'un dossier temporaire, écriture d'essai
dans le dossier du jeu), classés à tort en `lecture_code`.

## Ce que le rejeu a changé dans le kit (0.4.1)

- `trace.py audit` marque les tentatives refusées (`"refuse": true`, d'après `permission_denials`)
  et n'échoue que sur un accès qui a abouti.
- Skill `build` : `proves` lancé sans écran quand la commande peut ouvrir une fenêtre (le moteur ouvre
  une alerte par cas sur le départ, où le projet n'existe pas) ; un cas `echoue_integration` qui
  passe dans `test_cmd` signale une préparation absente d'un checkout neuf (ici l'import des
  assets, faute de fichiers `.import` versionnés).
- `--allow` d'`audit` documenté comme liste séparée par des virgules.

## Reste ouvert

- Mesurer l'action `difficile` en `sonnet` (escalade en `opus`) sur le même produit.
- Test de mutation (P5) pour juger la détection au-delà du seul défaut du besoin.
- Un rejeu où le code existe déjà au lancement du testeur (delta), pour éprouver les verrous de
  lecture.
