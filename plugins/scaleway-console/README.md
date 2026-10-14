# scaleway-console

Mod Claude Code : **`ctrl+shift+enter`** ouvre la [console Scaleway](https://console.scaleway.com)
dans le navigateur, sans quitter le prompt.

## Usage

| Geste | Effet |
|---|---|
| `ctrl+shift+enter` | ouvre la console (après le réglage du raccourci, ci-dessous) |
| clic sur ☁ au-dessus du prompt | ouvre la console |
| `/scaleway` | ouvre la console |

## Prérequis

- Claude Code avec le support des mods (function hooks, accès anticipé).
- macOS : le mod lance `open https://console.scaleway.com`.

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install scaleway-console@agaches
```

## Régler le raccourci `ctrl+shift+enter`

Un mod ne reçoit pas les touches directement : le bouton ☁ répond à l'action clavier
`app:cycleDiffBase`, libre tant que le panneau diff est fermé. Il reste à lier
`ctrl+shift+enter` à cette action dans `~/.claude/keybindings.json`.

La plupart des terminaux envoient `ctrl+shift+enter` comme un simple Entrée : Claude Code ne
voit pas la différence. Deux cas.

### Terminal qui distingue `ctrl+shift+enter` (protocole clavier kitty : kitty, Ghostty, WezTerm…)

`~/.claude/keybindings.json` :

```json
{
  "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
  "bindings": [
    {
      "context": "Global",
      "bindings": { "ctrl+shift+enter": "app:cycleDiffBase" }
    }
  ]
}
```

Non testé : seule la configuration Tabby ci-dessous l'a été.

### Tabby (testé sur macOS, Tabby 1.0.235)

Tabby ne transmet pas `ctrl+shift+enter`. On lui fait envoyer `meta+d` à la place, via son
action « Delete next word » (qui envoie `\x1bd` sur macOS).

1. Tabby › Settings › Hotkeys › **Delete next word** : ajouter `Ctrl-Shift-Enter`.
   Ou dans `~/Library/Application Support/tabby/config.yaml` :
   ```yaml
   hotkeys:
     delete-next-word:
       - ⌥-Delete
       - Ctrl-Shift-Enter
   ```
2. `~/.claude/keybindings.json` :
   ```json
   {
     "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
     "bindings": [
       {
         "context": "Global",
         "bindings": { "meta+d": "app:cycleDiffBase" }
       }
     ]
   }
   ```
3. Redémarrer Tabby.

Effets de bord : dans Claude Code, `⌥-Delete` ouvre aussi la console ; dans un shell,
`ctrl+shift+enter` supprime le mot suivant.

### Si le raccourci ne fait rien

| Test | Résultat | Cause |
|---|---|---|
| clic sur ☁ | rien | mod non chargé (`/plugin`) |
| `⌥-Delete` (Tabby) | ouvre la console | Tabby n'a pas relu sa config : le redémarrer |
| `⌥-Delete` (Tabby) | rien | `keybindings.json` non pris en compte : redémarrer Claude Code |

Panneau diff ouvert : `ctrl+shift+enter` y change la base de comparaison au lieu d'ouvrir
la console.

## Exemple

En pleine session, `ctrl+shift+enter` : l'onglet `console.scaleway.com` s'ouvre dans le
navigateur par défaut.

## Développement

```
claude plugin validate plugins/scaleway-console
claude plugin test plugins/scaleway-console
```
