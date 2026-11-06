# premiers-pas

> « On m'a dit que Claude est top. Je fais quoi, maintenant ? »

Plugin Claude de la marketplace [agaches/claude-plugins](README.md) : un guide de démarrage pour
qui vient d'avoir un accès Claude (compte Team) et ne sait pas par quel bout le prendre.

Souvent, tout commence par une démo : une question posée à la voix sur le téléphone, et quelques
minutes plus tard une recherche sourcée qui débloque un problème. Puis on reçoit son accès, et on
se retrouve devant une page vide, des paramètres qu'on ne comprend pas, des apps dont on ne sait
pas lesquelles installer.

premiers-pas transforme ce démarrage en exercice guidé. On colle un prompt dans claude.ai, on
ouvre les paramètres dans un deuxième onglet placé à côté, et la conversation guide pas à pas.
Elle explique chaque réglage et ses valeurs, et c'est vous qui choisissez.

## Ce que fait le plugin

| Temps | Où | Ce qui se passe |
|---|---|---|
| Réglage de base (environ 5 min) | prompt à coller | réglages de claude.ai (exécution de code, préférences de profil, recherche, mémoire), connecteurs selon votre environnement, ajout du plugin |
| Profil | skill | trois questions : Office ? Chrome ? profil tech ? |
| Apps | skill | une par une, seulement celles qui vous servent : app de bureau, app mobile, Claude pour Excel, PowerPoint ou Word, Claude in Chrome, Claude Code (lien et formation) |
| Revue finale | skill | Claude vérifie lui-même ce qu'il peut détecter et vous demande des captures pour le reste, puis compare avec **vos choix** |
| Programme de formation | skill | cours gratuits de Claude Academy, par chapitres, adaptés à votre profil |

Un réglage grisé ? Il est verrouillé par l'admin de votre organisation : le guide vous dit
exactement quoi lui demander, et passe à la suite.

## Installation

Rien à installer pour commencer : le prompt est dans le [README du plugin](plugins/premiers-pas/README.md).
Ouvrez claude.ai, nouvelle conversation, collez-le. Il vous fera ajouter le plugin à la fin du
réglage de base.

Plugin seul : sur claude.ai ou l'app de bureau, [Personnaliser > Plugins](https://claude.ai/customize/plugins),
**Ajouter une marketplace** `agaches/claude-plugins`, puis ajouter `premiers-pas`.

## Exemples d'utilisation

| Demande | Ce qui se passe |
|---|---|
| « lance premiers-pas » | suite du parcours après le réglage de base |
| « passe à Office » | directement aux compléments Office |
| « la revue » | revue finale de ce que vous avez choisi |
| « le programme » | programme de formation |
| « je reviens pour la suite » | dans une nouvelle conversation : état des lieux et reprise |

Pour continuer plus tard, le plus simple est de revenir dans la même conversation (épinglez-la).

## Limites (v0.1)

- Comptes Team uniquement.
- Plusieurs libellés de menus de claude.ai ne sont pas encore relevés : le guide décrit les
  réglages par leur fonction et vous demande ce que vous voyez.
- Les formations de Claude Academy sont en anglais.
- La configuration de Claude Code n'est pas couverte (lien et formation seulement).

## Désinstallation

[Personnaliser > Plugins](https://claude.ai/customize/plugins), retirer `premiers-pas`. Les réglages
que vous avez faits restent en place.
