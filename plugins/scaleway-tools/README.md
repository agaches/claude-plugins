# scaleway-tools

Outils Scaleway pour Claude Code.

## Console Scaleway

Mod Claude Code : **`ctrl+shift+enter`** ouvre la [console Scaleway](https://console.scaleway.com)
dans le navigateur, sans quitter le prompt.

Pourquoi ces trois touches : les thèmes ENTER, SHIFT, CTRL
d'[ai-PULSE 2026](https://www.scaleway.com/en/blog/ai-pulse-2026-themes/)
(détail dans la [page de présentation](../../scaleway-tools.md#pourquoi-ctrlshiftenter)).

### Usage

| Geste | Effet | Prêt |
|---|---|---|
| clic sur ☁ au-dessus du prompt | ouvre la console | dès l'installation |
| `/scaleway` | ouvre la console | dès l'installation |
| `ctrl+shift+enter` | ouvre la console | après `/scaleway-setup` |
| `/scaleway-setup` | vérifie et règle le raccourci | dès l'installation |

### Prérequis

- Claude Code avec le support des mods (function hooks, accès anticipé).
- Pour ouvrir le navigateur, le mod essaie dans l'ordre : `$BROWSER` s'il est défini, puis
  selon le système `open` ou `xdg-open` (macOS, Linux), `wslview` ou `explorer.exe` (WSL),
  `cmd /c start` (Windows). Si aucun ne marche, un toast donne l'URL.

### Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install scaleway-tools@agaches
```

L'installation demande les réglages du FinOps ([Options](#options)), tous facultatifs.
Puis, dans Claude Code :

```
/scaleway-setup
```

Tant que le raccourci n'est pas réglé, un toast le rappelle au démarrage de la session.

### Ce que fait `/scaleway-setup`

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

### Réglage du terminal

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

### Si le raccourci ne fait rien

1. Clic sur ☁ sans effet : le mod n'est pas chargé (`/plugin`, puis `/reload-plugins`).
2. ☁ marche, pas le raccourci : relancer `/scaleway-setup` et traiter les lignes ✗.
3. Tout est ✓ : redémarrer le terminal, puis Claude Code (relecture de `keybindings.json`).

## FinOps

Panneau **FinOps Scaleway** : dépense du jour et du mois à date, jauge du budget, trois derniers
mois empilés par projet, répartition du mois par projet et cinq premiers postes. Rafraîchi
toutes les heures ; `/finops` l'ouvre et le rafraîchit. La barre d'état affiche
`FinOps : x € aujourd'hui · y € en <mois>`.

### Prérequis

- [CLI `scw`](https://github.com/scaleway/scaleway-cli) configurée avec une clé qui lit la
  facturation (`billing consumption list`, `billing budget list`).
- [`direnv`](https://direnv.net) si la clé vit dans un `.envrc` (option `repertoire_direnv`).

### Options

Réglées à l'installation, ou ensuite dans `/config` :

| Option | Effet | Vide |
|---|---|---|
| `repertoire_direnv` | `scw` lancé par `direnv exec <dossier>` ; FinOps actif seulement dans ce dossier, panneau ouvert au démarrage | profil `scw` par défaut, actif partout, panneau ouvert par `/finops` |
| `organisation_id` | `organization-id=` passé à `scw billing` | organisation du profil |
| `projets` | noms de projets séparés par des virgules : fixe leur couleur (6 au plus) | une seule couleur pour tous |

Exemple : `repertoire_direnv` = `~/infra/orga`, `projets` = `prod,staging,outillage`.

### Ce qu'il garde

Le dernier relevé et la base du jour, dans le store du plugin (`~/.claude/plugins/store/`) :
la dépense du jour est le total du mois moins le dernier relevé de la veille. Sans relevé de la
veille, elle part du premier relevé du jour (« depuis HH:MM »).

## Développement

```
claude plugin validate plugins/scaleway-tools
claude plugin test plugins/scaleway-tools
```

Un module de hooks n'a qu'un `session.start` : celui de `hooks/register.tsx` appelle
`demarrerFinops` (`hooks/finops.tsx`).

---

Projet indépendant, non affilié à Scaleway.
