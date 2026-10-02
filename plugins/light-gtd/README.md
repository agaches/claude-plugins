# light-gtd

Gestion des tâches façon GTD, dans un Google Sheets tenu à jour par Claude.

On dicte au fil de l'eau, depuis l'app Claude sur le téléphone : « j'ai envoyé le devis au
plombier », « ajoute : renouveler le passeport avant fin novembre ». Claude range dans un
fichier de suivi (`suivi_taches` par défaut) : une ligne par sujet à mener jusqu'au bout, une colonne par jour, et dans
chaque case ce qui a été fait puis la prochaine action.

Le matin, on demande le point. Le soir, ce qui a été accompli. Le samedi, on fait la revue.

## Usage

| Moment | Exemple de demande | Skill |
|---|---|---|
| Au fil de l'eau | « j'ai appelé la mairie, à faire : envoyer le formulaire » | suivi-des-taches |
| Le matin | « fais-moi le point » | point-du-matin |
| Le soir | « qu'est-ce que j'ai fait aujourd'hui ? » | succes-du-soir |
| La semaine | « mes succès de la semaine » | succes-de-la-semaine |
| Le samedi | `/gtd-revue` ou « on fait la revue » | gtd-revue |
| Une fois | `/gtd-install` | gtd-install |

La revue propose, vous validez : rien n'est modifié sans votre accord. Elle supprime aussi les
colonnes de jours de plus de 2 mois, après avoir reporté la dernière action des tâches
immobiles ; l'historique des versions de Google Sheets garde tout.

## Prérequis

Connecteurs Claude activés sur votre compte : **Google Drive**, **Google Sheets**,
**Google Agenda**. `/gtd-install` vérifie leur présence et explique comment les activer.

## Installation

Claude Code :

```
/plugin marketplace add agaches/claude-plugins
/plugin install light-gtd@agaches
```

Puis lancer `/light-gtd:gtd-install`. Il crée dans votre Google Drive le fichier de suivi, du nom
de votre choix (`suivi_taches` par défaut ; onglets Suivi, Terminées, README) et, dans votre agenda, la revue hebdo du samedi 9h.

App Claude : sur claude.ai ou l'app de bureau, ouvrir
[Personnaliser > Plugins](https://claude.ai/customize/plugins), puis **Ajouter** :

- **Ajouter une marketplace** : `agaches/claude-plugins`, puis ajouter `light-gtd` ;
- ou **Importer un plugin** : télécharger
  [light-gtd.zip](https://github.com/agaches/claude-plugins/releases/download/light-gtd-v0.2.0/light-gtd.zip)
  (release [light-gtd-v0.2.0](https://github.com/agaches/claude-plugins/releases/tag/light-gtd-v0.2.0))
  et l'importer.

Le plugin est enregistré sur le compte : ses skills sont disponibles dans le chat (web, bureau,
mobile), dans Cowork et dans Claude Code (synchronisé au prochain démarrage). Un plugin installé
en ligne de commande dans Claude Code reste sur la machine et n'est pas ajouté au compte.

Ensuite : activer les connecteurs Google, puis demander « installe le suivi des tâches ».

## Données

Le plugin ne contient aucune donnée : tout reste dans votre Google Drive et votre Google Agenda.
Le fichier est retrouvé par un marqueur écrit dans son onglet README : il peut être renommé ou
déplacé, mais ce marqueur ne doit pas être effacé. Vos réglages (agenda,
contextes, section pro) sont dans le bloc « Configuration » de l'onglet README du fichier.

## Limites (v0.2)

- Pas de tâches planifiées ni d'envoi par mail : les points se demandent.
- Un utilisateur, un fichier.
