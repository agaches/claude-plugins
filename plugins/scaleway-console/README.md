# scaleway-console

Mod Claude Code : **`ctrl+shift+enter`** ouvre la [console Scaleway](https://console.scaleway.com)
dans le navigateur, sans quitter le prompt.

Pourquoi ces trois touches : les thèmes ENTER, SHIFT, CTRL
d'[ai-PULSE 2026](https://www.scaleway.com/en/blog/ai-pulse-2026-themes/)
(détail dans la [page de présentation](../../scaleway-console.md#pourquoi-ctrlshiftenter)).

## Usage

| Geste | Effet | Prêt |
|---|---|---|
| clic sur ☁ au-dessus du prompt | ouvre la console | dès l'installation |
| `/scaleway` | ouvre la console | dès l'installation |
| `ctrl+shift+enter` | ouvre la console | après `/scaleway-setup` |
| `/scaleway-setup` | vérifie et règle le raccourci | dès l'installation |

## Prérequis

- Claude Code avec le support des mods (function hooks, accès anticipé).
- macOS : le mod lance `open https://console.scaleway.com`.

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install scaleway-console@agaches
```

Puis, dans Claude Code :

```
/scaleway-setup
```

Tant que le raccourci n'est pas réglé, un toast le rappelle au démarrage de la session.

## Ce que fait `/scaleway-setup`

Un mod ne reçoit pas les touches directement : le bouton ☁ répond à l'action clavier
`app:cycleDiffBase`, libre tant que le panneau diff est fermé. `/scaleway-setup` :

1. **Claude Code** : ajoute dans `~/.claude/keybindings.json`, contexte `Global`,
   `ctrl+shift+enter` et `meta+d` → `app:cycleDiffBase`. Le reste du fichier est conservé ;
   une touche déjà liée à autre chose est signalée et laissée telle quelle.
2. **Terminal** (détecté par `TERM_PROGRAM`) : vérifie qu'il transmet la combinaison, et sinon
   donne l'étape à faire à la main (le mod n'écrit pas la config du terminal).

Exemple de sortie :

```
✓ keybindings.json : ajouté ctrl+shift+enter, meta+d → app:cycleDiffBase
✗ iTerm : iTerm › Settings › Profiles › Keys › Key Mappings › + : raccourci ctrl+shift+enter, action « Send Escape Sequence », Esc+ d.

Reste à faire : les lignes ✗ ci-dessus, puis relancer /scaleway-setup.
```

## Réglage du terminal

Beaucoup de terminaux envoient `ctrl+shift+enter` comme un simple Entrée : Claude Code ne voit
pas la différence. On fait alors envoyer `meta+d` (Esc+d) au terminal pour cette combinaison.

| Terminal | Réglage | Testé |
|---|---|---|
| iTerm 3.7 | Settings › Profiles › Keys › Key Mappings › **+** : raccourci `ctrl+shift+enter`, action **Send Escape Sequence**, Esc+ `d` | oui |
| Tabby 1.0 | Settings › Hotkeys › **Delete next word** : ajouter `Ctrl-Shift-Enter` (cette action envoie Esc+d), puis redémarrer Tabby | oui |
| autre | s'il transmet `ctrl+shift+enter` (protocole clavier kitty), rien à faire ; sinon lui faire envoyer Esc+d. Si le terminal a déjà un raccourci sur cette combinaison, le libérer. | non |

Tabby, à la main dans `~/Library/Application Support/tabby/config.yaml` :

```yaml
hotkeys:
  delete-next-word:
    - ⌥-Delete
    - Ctrl-Shift-Enter
```

Effets de bord : dans un shell, `ctrl+shift+enter` agit comme `meta+d` (supprime le mot
suivant) ; avec Tabby, `⌥-Delete` ouvre aussi la console dans Claude Code ; panneau diff
ouvert, `ctrl+shift+enter` y change la base de comparaison au lieu d'ouvrir la console.

## Si le raccourci ne fait rien

1. Clic sur ☁ sans effet : le mod n'est pas chargé (`/plugin`, puis `/reload-plugins`).
2. ☁ marche, pas le raccourci : relancer `/scaleway-setup` et traiter les lignes ✗.
3. Tout est ✓ : redémarrer le terminal, puis Claude Code (relecture de `keybindings.json`).

## Développement

```
claude plugin validate plugins/scaleway-console
claude plugin test plugins/scaleway-console
```

---

Projet indépendant, non affilié à Scaleway.
