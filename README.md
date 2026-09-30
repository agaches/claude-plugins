# claude-plugins

Marketplace Claude Code d'agaches : skills et plugins prêts à installer.

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install <plugin>@agaches
```

Mise à jour du catalogue : `/plugin marketplace update agaches`

## Plugins disponibles

| Plugin | Description |
|---|---|
| _(aucun pour l'instant)_ | |

## Ajouter un plugin

1. Créer `plugins/<nom>/` (kebab-case) :
   ```
   plugins/<nom>/
   ├── .claude-plugin/plugin.json
   ├── skills/<skill>/SKILL.md
   └── README.md
   ```
2. Déclarer l'entrée dans `.claude-plugin/marketplace.json` :
   ```json
   {
     "name": "<nom>",
     "source": "./plugins/<nom>",
     "description": "...",
     "version": "0.1.0"
   }
   ```
3. Valider : `claude plugin validate .`
4. Ajouter une ligne au tableau « Plugins disponibles ».

## Licence

MIT
