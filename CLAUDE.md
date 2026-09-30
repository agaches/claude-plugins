# CLAUDE.md

Marketplace Claude Code public (`agaches/claude-plugins`).

## Structure

- `.claude-plugin/marketplace.json` : catalogue, une entrée par plugin
- `plugins/<nom>/` : un plugin autonome (`.claude-plugin/plugin.json`, `skills/`, `agents/`, `commands/`, `hooks/`)

## Conventions

- Noms de plugins et skills en kebab-case
- `version` identique dans `marketplace.json` et le `plugin.json` du plugin ; bump à chaque changement publié (semver)
- Chaque plugin a son `README.md` : usage, prérequis, exemple
- Repo public : aucun chemin absolu, donnée perso, secret ou contenu sous droits d'auteur
- Pas de dépendance entre plugins

## Avant chaque commit

- `claude plugin validate .` doit passer sans erreur
- Tableau « Plugins disponibles » du `README.md` à jour
