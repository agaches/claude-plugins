# scaleway-tools

> « Combien m'a coûté le lab aujourd'hui ? »

Plugin Claude Code de la marketplace [agaches/claude-plugins](README.md) : des outils Scaleway
dans Claude Code, sans quitter le prompt.

Quand on construit une infra Scaleway avec Claude, deux gestes reviennent sans cesse : ouvrir la
console pour vérifier ce qui a été créé, et regarder la facture pour savoir ce que coûte ce qui
tourne. Les deux font sortir du terminal, et le second se fait rarement : on découvre le coût
d'une ressource oubliée en fin de mois.

scaleway-tools ramène les deux dans Claude Code. La console s'ouvre en trois touches. La
dépense du jour et du mois s'affiche dans un panneau et dans la barre d'état, relue toutes les
heures.

## Ce que fait le plugin

| Outil | Rôle |
|---|---|
| **Console** | `ctrl+shift+enter`, le bouton ☁ au-dessus du prompt ou `/scaleway` ouvrent la [console Scaleway](https://console.scaleway.com) dans le navigateur. |
| **FinOps** | Panneau latéral : dépense du jour et du mois à date, jauge du budget, trois derniers mois par projet, répartition du mois et premiers postes. `/finops` l'ouvre et le rafraîchit. |

Le détail (réglage du terminal, options, calcul de la dépense du jour) est dans le
[README du plugin](plugins/scaleway-tools/README.md).

## Pourquoi `ctrl+shift+enter`

Les trois thèmes d'[ai-PULSE 2026](https://www.scaleway.com/en/blog/ai-pulse-2026-themes/),
l'événement IA de Scaleway qui s'est tenu le 13 octobre 2026 à STATION F, portent le nom de
trois touches :
**ENTER ⏎. SHIFT ⇧. CTRL ⌃.**

| Touche | Thème ai-PULSE |
|---|---|
| ENTER | l'IA abaisse les barrières pour lancer un produit ou entrer sur un marché |
| SHIFT | positions, modèles et catégories de produits bougent plus vite que les roadmaps |
| CTRL | garder la main sur ses systèmes : qui opère le modèle, où vont les données, ce que les agents peuvent faire |

Le mod prend la formule au pied de la lettre : les trois touches ensemble ouvrent la console
Scaleway.

## Installation

Les outils sont des mods (function hooks) de **Claude Code** : ils ne fonctionnent pas dans le
chat claude.ai. Prérequis du FinOps : la [CLI `scw`](https://github.com/scaleway/scaleway-cli)
avec une clé qui lit la facturation, et [`direnv`](https://direnv.net) si cette clé vit dans le
`.envrc` d'un repo.

Dans une session Claude Code :

```
/plugin marketplace add agaches/claude-plugins
/plugin install scaleway-tools@agaches
```

L'installation demande les trois réglages du FinOps. Tous sont facultatifs :

| Réglage | Exemple | Effet | Laissé vide |
|---|---|---|---|
| Dossier direnv | `~/infra/orga` | `scw` lancé par `direnv exec` dans ce dossier, FinOps actif seulement là, panneau ouvert au démarrage | profil `scw` par défaut, FinOps actif partout, panneau ouvert par `/finops` |
| ID d'organisation | `11111111-2222-…` | organisation dont on lit la facturation | celle du profil `scw` |
| Projets (couleurs) | `prod,staging,outillage` | une couleur fixe par projet, dans cet ordre (6 au plus) | une seule couleur |

Pour les changer ensuite : `/config`, section du plugin.

## Premier lancement

1. Régler le raccourci : `/scaleway-setup`. La commande ajoute les touches dans
   `~/.claude/keybindings.json`, détecte le terminal et dit s'il reste un réglage à faire de
   son côté (iTerm et Tabby demandent un mapping d'une ligne, décrit dans le
   [README du plugin](plugins/scaleway-tools/README.md#réglage-du-terminal)). Tant que ce n'est
   pas fait, un toast le rappelle au démarrage.
2. Ouvrir Claude Code dans le dossier direnv configuré (ou n'importe où, sans dossier) :
   `/finops` ouvre le panneau. La barre d'état affiche par exemple
   `FinOps : 1,24 € aujourd'hui · 21,42 € en oct.`.
3. `ctrl+shift+enter` : la console Scaleway s'ouvre dans le navigateur.

## Exemple

*Panneau illustratif, chiffres fictifs.*

```
FinOps · Scaleway                         09:12 UTC

╭─────────────╮  ╭──────────────────╮
│ Aujourd'hui │  │ oct. à date      │
│ 1,24 €      │  │ 21,42 €          │
│ depuis 00:00│  │ sept. : 18,03 €  │
╰─────────────╯  ╰──────────────────╯

Budget 30,00 €                      ✓ ok 71 %
█████████████████████░░░░░░░░░

Trois derniers mois
août   ███████████          14,60 €
sept.  █████████████        18,03 €
oct.   ███████████████      21,42 € en cours
■ prod  ■ staging  ■ outillage

oct. par projet
prod        █████████████   13,14 €
staging     █████▋           5,66 €
outillage   ██▌              2,62 €
```

## Vos données

Le FinOps lit la facturation avec la clé de `scw` (ou celle du `.envrc` du dossier direnv) et
n'envoie les montants nulle part : ils restent dans Claude Code. Il garde le dernier relevé et
la base du jour dans le store du plugin (`~/.claude/plugins/store/`), pour calculer la dépense
du jour. Le plugin ne contient aucun identifiant ni aucune clé.

## Limites (v0.1)

- Console : testée à la main sous macOS. Sous Linux, WSL et Windows, les commandes lancées
  (`xdg-open`, `wslview`, `explorer.exe`, `cmd /c start`) ne sont vérifiées que par les tests.
- Le raccourci réutilise l'action `app:cycleDiffBase` : panneau diff ouvert, il change la base
  du diff au lieu d'ouvrir la console.
- FinOps : la dépense du jour part du dernier relevé de la veille. Sans session ouverte la
  veille, elle part du premier relevé du jour (« depuis 09:12 »).
- Les mods de Claude Code sont en accès anticipé : leur API peut changer d'une version à
  l'autre.

## Désinstallation

```
claude plugin uninstall scaleway-tools@agaches
```

Retirer aussi `ctrl+shift+enter` et `meta+d` de `~/.claude/keybindings.json`, et le mapping
ajouté dans le terminal.

---

Projet indépendant, non affilié à Scaleway.

[github.com/agaches/claude-plugins](https://github.com/agaches/claude-plugins) · Licence MIT
