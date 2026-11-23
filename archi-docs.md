# archi-docs

> Vos décisions d'architecture consignées avec vos propres modèles.

Plugin Claude Code de la marketplace [agaches/claude-plugins](README.md) : écrire des ADR, et
bientôt des DAT, avec Claude, à partir de modèles qui restent les vôtres.

Les modèles ne sont pas figés dans le plugin. Au premier usage dans un projet, Claude les copie
depuis un repo de modèles, par défaut [agaches/adr](https://github.com/agaches/adr), ou depuis le
vôtre, dans `docs/adr/modeles/`. Ils sont versionnés avec le projet : toute l'équipe écrit avec les
mêmes, et une mise à jour se relit comme n'importe quel diff.

## Ce que fait le plugin

| Skill | Ce qui se passe |
|---|---|
| `/adr` | choix du modèle selon la décision (simple, avancé, exhaustif pour agaches/adr), numérotation `ADR-NNN`, statut, liens, remplacement d'une ADR acceptée par une nouvelle |
| `dat` (à venir) | dossier d'architecture technique depuis [agaches/dat](https://github.com/agaches/dat), modèle LikeC4 avec vues fonctionnelle, solution et technique |

## Les garde-fous

- Rien d'inventé : une rubrique sans matière s'écrit « non renseigné ».
- Une ADR acceptée ne se réécrit pas, elle est remplacée.
- Les modèles ne sont copiés qu'avec votre accord, et la mise à jour conserve vos réglages.

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install archi-docs@agaches
```

Détails et prérequis : [plugins/archi-docs](plugins/archi-docs/README.md).
