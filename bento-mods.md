# bento-mods

> « Claude a encore cassé le deck ? »

Plugin Claude Code de la marketplace [agaches/claude-plugins](README.md) : des mods qui
surveillent les présentations [Bento](https://bento.page) (`*.bento.html`) pendant que Claude
les écrit.

Un deck Bento tient dans un seul fichier HTML : un runtime compressé, plus le document lui-même
dans un bloc JSON `<script id="bento-doc">`. La skill `bento-slides` donne des règles à Claude :
ne toucher qu'au bloc JSON, échapper `<`, ne jamais lire en clair les clés d'une session de
collaboration. Ce sont des consignes, rien ne les fait respecter. Les mods de bento-mods
interceptent chaque appel d'outil et les appliquent.

## Ce que fait le plugin

| Mod | Rôle |
|---|---|
| **bento-guard** | Refuse les écritures qui touchent le runtime, prévient avant de lire un deck qui contient des clés de session live, audite le JSON après chaque écriture. |
| **bento-outline** | Panneau latéral avec le plan du deck : slides, éléments, transitions morph, notes de l'orateur. |

Le détail des contrôles est dans le [README du plugin](plugins/bento-mods/README.md).

## Installation

Les mods sont des function hooks de **Claude Code** : ils ne fonctionnent pas dans le chat
claude.ai ni dans l'app de bureau hors onglet Code. Recommandé : installer aussi la skill
`bento-slides` (`/plugin marketplace add nyblnet/bento`).

Le marketplace s'ajoute une seule fois :

```
claude plugin marketplace add agaches/claude-plugins
```

### Choisir où les mods sont actifs

Le scope d'installation détermine où les mods tournent. Pour les limiter à un repo, lancer la
commande **depuis la racine de ce repo** avec le scope `local` ou `project`.

| Scope | Actif | Réglage écrit dans |
|---|---|---|
| `local` | dans ce repo, pour vous seul | `.claude/settings.local.json` (non versionné) |
| `project` | dans ce repo, pour tous ceux qui le clonent | `.claude/settings.json` (à commiter) |
| `user` (par défaut) | dans tous vos projets | `~/.claude/settings.json` |

Dans un seul repo, pour vous :

```
claude plugin install bento-mods@agaches --scope local
```

Dans un seul repo, pour toute l'équipe (puis commiter `.claude/settings.json`) :

```
claude plugin install bento-mods@agaches --scope project
```

Partout :

```
claude plugin install bento-mods@agaches
```

Dans une session, `/plugin` propose le même choix de scope. Après un changement, `/reload-plugins`
le prend en compte.

### Déjà installé partout ? Le restreindre à un repo

```
claude plugin disable bento-mods@agaches --scope user
claude plugin enable bento-mods@agaches --scope local
```

La seconde commande se lance depuis la racine du repo visé.

### Essayer sans installer

```
claude --plugin-dir plugins/bento-mods
```

Le plugin n'est chargé que pour cette session, depuis un clone du repo.

## Premier lancement

1. Ouvrir Claude Code dans un dossier qui contient un `.bento.html`. Si le terminal fait au
   moins 144 colonnes, le panneau « Bento · plan du deck » s'ouvre seul. Sinon :
   `/bento-outline <fichier.bento.html>`.
2. Demander une modification du deck. Après l'écriture, la ligne de statut affiche le résumé,
   par exemple `deck.bento.html · 12 slides · 3 morph · 2 sans notes`.
3. Si l'audit trouve une erreur (JSON invalide, `<` non échappé, données de graphique non
   numériques…), Claude la reçoit avec le résultat de l'outil et la corrige au tour suivant.

## Exemples

*Réponses illustratives.*

**Vous :** Ouvre `bilan.bento.html` et résume-le.

> **bento-guard** (toast) : bilan.bento.html contient des clés de session live (writerPriv)
>
> **Claude**
>
> Ce deck contient les clés de sa session de collaboration : le lire les ferait entrer dans
> mon contexte. Je peux travailler sur une copie sans clés (*Save > Save read-only copy*).
> Vous préférez que je le lise quand même ?

**Vous :** Régénère le fichier avec un script Python.

> **bento-guard** : la commande est refusée une première fois. Claude explique pourquoi et
> demande votre accord ; la même commande passe ensuite, et son résultat est audité.

## Limites (v0.1)

- L'audit lit le JSON, pas le rendu : un texte qui déborde se vérifie à l'écran.
- Le garde-fou Bash lit la ligne de commande, pas son effet : un chemin construit à l'exécution
  passe.
- Les mods de Claude Code sont en accès anticipé : leur API peut changer d'une version à
  l'autre.

## Désinstallation

Avec le scope utilisé à l'installation :

```
claude plugin uninstall bento-mods@agaches --scope local
```

---

[github.com/agaches/claude-plugins](https://github.com/agaches/claude-plugins) · Licence MIT
