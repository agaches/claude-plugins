# light-gtd

> « Qu'est-ce que j'avais encore à faire, déjà ? »

Plugin Claude de la marketplace [agaches/claude-plugins](README.md) : gestion des tâches façon GTD
dans un Google Sheets tenu par Claude. On dicte, Claude range.

Les tâches arrivent n'importe quand : en voiture, entre deux réunions, en rangeant la cuisine. Les
noter demande de s'arrêter, d'ouvrir une appli, de choisir une liste. Alors on ne note pas, et on
garde tout en tête.

light-gtd supprime cette friction. On dicte à Claude, depuis le téléphone, comme on parlerait à
quelqu'un : « j'ai envoyé le devis au plombier, maintenant j'attends sa réponse ». Claude range
dans un simple Google Sheets : une ligne par sujet à mener jusqu'au bout, une colonne par jour, et
dans chaque case ce qui a été fait puis la prochaine action.

C'est le cœur de la méthode GTD (*Getting Things Done*) : tout sortir de sa tête pour le mettre
dans un système de confiance. Avec un bonus que GTD n'offre pas : l'historique jour par jour, qui
montre ce qui avance et ce qui stagne. Et, le soir, ce qui a été accompli.

## Le fichier `suivi_taches`

Un Google Sheets dans votre Drive, lisible par vous comme par Claude, sur tous vos appareils.
Onglet **Suivi** (exemple fictif) :

| Actions | Deadline | Statut | Contexte | 14/10 | 15/10 |
|---|---|---|---|---|---|
| **Tâches récurrentes** | | | | | |
| Perso : sortir les poubelles | Chaque jour | Routine | Maison | fait | |
| **Actions perso** | | | | | |
| Perso : faire réparer la porte du garage | 31/10/2026 | En attente | Tél | devis demandé, à faire : attendre le devis | devis reçu, à faire : valider le devis |
| Perso : renouveler le passeport | 30/11/2026 | En cours | Ordi | | à faire : prendre rendez-vous en mairie |
| **Actions pro** | | | | | |
| Pro : préparer la présentation trimestrielle | 24/10/2026 | En cours | Ordi | plan fait, à faire : rédiger les slides | |
| **Global** | | | | | |

Deux autres onglets : **Terminées** (les tâches bouclées, avec des compteurs) et **README** (le
mode d'emploi, et vos réglages : agenda, contextes, section pro).

## Ce que fait le plugin

| Moment | Vous dites | Claude |
|---|---|---|
| Au fil de l'eau | « j'ai appelé la mairie, à faire : envoyer le formulaire » | Écrit dans la bonne ligne, colonne du jour. Ajoute, met en attente, clôt une tâche, pose un rappel dans l'agenda. |
| Le matin | « fais-moi le point » | Les grands sujets, les deadlines proches, ce qui attend une relance ou stagne, et 3 actions suggérées regroupées par contexte. |
| Le soir | « qu'est-ce que j'ai fait aujourd'hui ? » | Le bilan positif de la journée, sans culpabiliser. |
| La semaine | « mes succès de la semaine » | Les tâches bouclées, celles qui ont avancé, le total d'actions. |
| Le samedi | `/light-gtd:revue` | La revue GTD, pas à pas. Claude propose, vous validez : rien n'est modifié sans votre accord. |

## Installation

**App Claude** (claude.ai ou app de bureau) : ouvrir
[Personnaliser > Plugins](https://claude.ai/customize/plugins), puis **Ajouter** :

- **Ajouter une marketplace** : `agaches/claude-plugins`, puis ajouter `light-gtd` (les mises à
  jour suivent le repo) ;
- ou **Importer un plugin** : télécharger
  [light-gtd.zip](https://github.com/agaches/claude-plugins/releases/download/light-gtd-v0.1.0/light-gtd.zip)
  (aussi sur la page [Releases](https://github.com/agaches/claude-plugins/releases) du repo) et
  l'importer.

Le plugin est enregistré sur votre compte : il est ensuite disponible dans le chat sur le web, le
bureau et le mobile, dans Cowork et dans Claude Code.

**Claude Code** seul, dans une session :

```
/plugin marketplace add agaches/claude-plugins
/plugin install light-gtd@agaches
```

Installé ainsi, le plugin reste sur la machine et n'est pas ajouté à votre compte claude.ai.

## Premier lancement

1. Activer les connecteurs **Google Drive**, **Google Sheets** et **Google Agenda**
   (Personnaliser > Connecteurs).
2. Demander « installe le suivi des tâches » (ou `/light-gtd:installer`). Claude vérifie les
   connecteurs, demande trois réglages (agenda des tâches, contextes, section pro), crée le
   fichier `suivi_taches` dans votre Drive et la revue hebdo du samedi 9h dans votre agenda.
3. Dicter une première tâche : « ajoute : renouveler le passeport avant fin novembre ».

L'installation est relançable sans risque : elle ne recrée jamais ce qui existe et n'efface rien.
Relancée sur un fichier existant, elle vérifie sa structure et propose les corrections.

## Exemples d'utilisation

*Réponses illustratives, sur le fichier d'exemple ci-dessus, le 15/10.*

**Vous :** Le plombier a validé, il passe jeudi. C'est bon pour la porte du garage.

> **Claude**
>
> Noté dans *Perso : faire réparer la porte du garage*, 15/10 : devis validé, passage jeudi, à
> faire : être présent jeudi. Statut repassé en *En cours*. Je pose un rappel jeudi matin dans
> votre agenda ?

**Vous :** Fais-moi le point.

> **Claude**
>
> **En cours** : la maison avance (porte du garage calée jeudi), le passeport attend un
> rendez-vous, et côté pro la présentation trimestrielle est l'échéance la plus proche.
>
> **Deadlines** : rien dans les 3 prochains jours.
>
> **Ça stagne** : la présentation trimestrielle, « rédiger les slides » depuis le 14/10.
>
> **Pour aujourd'hui** :
> - À l'ordi : prendre rendez-vous en mairie pour le passeport, puis attaquer les slides.
> - À la maison : vérifier que l'accès au garage est dégagé pour jeudi.

**Vous :** Qu'est-ce que j'ai fait aujourd'hui ?

> **Claude**
>
> Aujourd'hui : 3 actions faites, dont 1 routine. La porte du garage est débloquée : devis validé
> et intervention calée. Belle journée.

## La revue du samedi

`/light-gtd:revue` déroule la revue GTD, une étape à la fois : succès de la semaine, tâches en
cours, attentes à relancer, ce qui stagne, deadlines de la semaine suivante, rangement. Vous
pouvez dire « suivant » pour passer une étape ou « stop » pour arrêter.

Au rangement, les colonnes de jours de plus de 2 mois sont supprimées pour garder le fichier
lisible. Avant cela, la dernière action de chaque tâche qui n'a pas bougé depuis est recopiée dans
la colonne du jour : aucune tâche ne perd sa prochaine action. L'historique des versions de Google
Sheets (Fichier > Historique des versions) garde tout le reste.

## Vos données

Le plugin ne contient aucune donnée : tout reste dans votre Google Drive et votre Google Agenda.
Le fichier est retrouvé par son nom, `suivi_taches` : ne pas le renommer. Vos réglages sont dans
le bloc « Configuration » de l'onglet README du fichier ; vous pouvez les modifier à la main.

## Limites (v0.1)

- Pas de tâches planifiées ni d'envoi par mail : le point du matin et les succès se demandent.
- Un utilisateur, un fichier. L'usage familial est prévu pour une version suivante.

## Désinstallation

**App Claude** : dans [Personnaliser > Plugins](https://claude.ai/customize/plugins), ouvrir
`light-gtd`, puis son menu, puis **Supprimer**. La suppression vaut pour tous vos appareils. Le
fichier `suivi_taches` et vos événements d'agenda restent en place : à supprimer vous-même si
besoin.

**Claude Code** : retirer le plugin, puis, si vous n'utilisez plus aucun plugin de ce catalogue,
le marketplace lui-même.

```
claude plugin uninstall light-gtd@agaches
claude plugin marketplace remove agaches
```

---

[github.com/agaches/claude-plugins](https://github.com/agaches/claude-plugins) · Licence MIT
