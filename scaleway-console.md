# scaleway-console

> « Ouvrir la console Scaleway sans lâcher le clavier. »

Plugin Claude Code de la marketplace [agaches/claude-plugins](README.md) : un mod qui ouvre la
[console Scaleway](https://console.scaleway.com) dans le navigateur avec **`ctrl+shift+enter`**,
depuis le prompt de Claude Code.

## Ce que fait le plugin

| Geste | Effet |
|---|---|
| `ctrl+shift+enter` | ouvre la console Scaleway |
| clic sur ☁ au-dessus du prompt | idem |
| `/scaleway` | idem |

## Installation

Le mod est un function hook de **Claude Code** : il ne fonctionne pas dans le chat claude.ai.
Il lance `open`, donc macOS.

```
claude plugin marketplace add agaches/claude-plugins
claude plugin install scaleway-console@agaches
```

Le raccourci `ctrl+shift+enter` demande ensuite un réglage dans `~/.claude/keybindings.json`,
et dans le terminal si celui-ci ne distingue pas `ctrl+shift+enter` d'Entrée (cas de Tabby) :
voir [Régler le raccourci](plugins/scaleway-console/README.md#régler-le-raccourci-ctrlshiftenter).

## Limites (v0.1)

- macOS seulement (`open`).
- Le raccourci réutilise l'action `app:cycleDiffBase` : panneau diff ouvert, il change la base
  du diff au lieu d'ouvrir la console.
- Les mods de Claude Code sont en accès anticipé : leur API peut changer d'une version à
  l'autre.

## Désinstallation

```
claude plugin uninstall scaleway-console@agaches
```

Retirer aussi la ligne ajoutée dans `~/.claude/keybindings.json` (et dans Tabby).

---

[github.com/agaches/claude-plugins](https://github.com/agaches/claude-plugins) · Licence MIT
