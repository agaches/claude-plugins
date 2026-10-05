# bento-mods

Mods Claude Code pour les présentations [Bento](https://bento.page) (`*.bento.html`).
Un deck Bento est un seul fichier : un runtime compressé plus un bloc JSON
`<script id="bento-doc">`. La skill `bento-slides` donne des règles à l'agent ; ces mods
les font respecter à chaque appel d'outil, et montrent le deck en cours dans un panneau.

## Les mods

### bento-guard : garde-fous et audit

| Outil intercepté | Contrôle | Effet |
|---|---|---|
| `Read` | clés de session live dans `doc.collab` (`ownerPriv`, `writerPriv`, `invite`) | 1re lecture refusée + toast ; la suivante passe |
| `Write` / `Edit` | le fichier hors bloc `#bento-doc` (le runtime) doit rester identique | écriture refusée avant d'avoir lieu |
| `Bash` | commande qui écrit un `.bento.html` (`python`, `sed -i`, `>`…) ou lit un deck à clés | 1re exécution refusée ; la commande identique passe ensuite, auditée |
| après écriture | audit du `#bento-doc` | résumé en ligne de statut, erreurs remises à Claude |

Audit : bloc absent, JSON invalide, `<` non échappé (`<`), `size` ou
`theme.fontFamily` manquant, données de graphique non numériques (erreurs) ; morph sans id
partagé, texte au-delà de x = 1184, slides sans notes (avertissements).

Exemple de ligne de statut : `deck.bento.html · 12 slides · 3 morph · 2 sans notes`

Limites : l'audit lit le JSON, pas le rendu (débordements à vérifier à l'écran). Le garde-fou
Bash lit la ligne de commande, pas son effet : un chemin construit à l'exécution passe.

### bento-outline : plan du deck

Panneau latéral « Bento · plan du deck » : navigation slide par slide (`p` / `n` ou clic),
éléments de la slide (texte, graphique, tableau, image…), transition morph et nombre
d'éléments partagés, notes de l'orateur (signalées en rouge si absentes).

- S'ouvre au démarrage si un `.bento.html` est dans le dossier (terminal de 144 colonnes ou plus).
- `/bento-outline <fichier.bento.html>` l'ouvre à la demande.
- Se met à jour après chaque `Read`, `Write`, `Edit` ou `Bash` qui touche un deck.

## Prérequis

- Claude Code avec le support des mods (function hooks, accès anticipé).
- Recommandé : la skill `bento-slides` (`/plugin marketplace add nyblnet/bento`).

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install bento-mods@agaches
```

## Exemple

« Ajoute une slide de graphique en barres au deck `bilan.bento.html` » : le panneau affiche
la nouvelle slide, la ligne de statut se met à jour, et si une valeur du graphique est un
objet au lieu d'un nombre, Claude reçoit l'erreur d'audit et corrige au tour suivant.

## Développement

```
claude plugin validate plugins/bento-mods
claude plugin test plugins/bento-mods
```
