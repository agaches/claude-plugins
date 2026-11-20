# brain-build

> Un besoin figé, des agents qui construisent, une recette en quelques minutes.

Plugin Claude Code de la marketplace [agaches/claude-plugins](README.md) : un kit léger pour
construire et maintenir un produit avec des agents, sans perdre ce qui fait un projet bien mené :
un besoin clair, des specs, une traçabilité, des tests qui prouvent quelque chose, une recette.

Un modèle fort travaille déjà bien seul. Les cadres complets (multi-agents, méthodes outillées)
coûtent cher en tokens et deviennent vite une usine à gaz. brain-build garde le minimum de pièces :
deux skills, trois agents, un script.

## Ce que fait le plugin

| Phase | Commande | Qui | Ce qui se passe |
|---|---|---|---|
| Brain | `/brain` | vous et Claude | réflexion, passage sur le grill, relecture critique par personas, besoin `docs/besoin.md` avec exigences `REQ-xxx` et critères d'acceptation |
| Build | `/build` | le pilote et ses agents | specs et plan (`analyst`), tests depuis le besoin (`tester`), code action par action (`dev`), vérifications, PR |
| Recette | rapport | vous | questions en attente, matrice de traçabilité, incidents, avis de relecture ; vous mergez |

Les agents sont des **processus séparés** : chacun a son modèle, son niveau d'effort, sa session
propre. Ils ne discutent pas entre eux, ils travaillent par fichiers et rendent un résultat
structuré au pilote.

## Les garde-fous

- Le testeur ne lit jamais le code ni le plan : ses tests viennent du besoin, pas de
  l'implémentation.
- Chaque test doit **échouer** sur la branche de départ et **passer** sur le résultat : sinon il ne
  prouve rien.
- Aucun agent ne modifie le besoin ; une question de besoin vous remonte, sans bloquer le reste.
- La matrice et les contrôles sont calculés par un script, pas estimés par le modèle.
- Pas de merge ni de déploiement automatique.

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install brain-build@agaches
```

Détails, prérequis et configuration : [plugins/brain-build](plugins/brain-build/README.md).
