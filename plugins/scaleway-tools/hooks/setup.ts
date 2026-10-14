// Vérification du raccourci ctrl+shift+enter : terminal, ~/.claude/keybindings.json.
// Fonctions pures, testées dans setup.test.ts.

// Action clavier détournée : libre tant que le panneau diff est fermé.
export const ACTION = 'app:cycleDiffBase'

export type Terminal = 'tabby' | 'iterm' | 'other'

export function detectTerminal(termProgram: string | undefined): Terminal {
  if (termProgram === 'Tabby') return 'tabby'
  if (termProgram === 'iTerm.app') return 'iterm'
  return 'other'
}

// ctrl+shift+enter pour un terminal qui le transmet ; meta+d pour Tabby, iTerm et tout terminal
// réglé pour envoyer Esc+d sur cette combinaison.
export const KEYS = ['ctrl+shift+enter', 'meta+d']

type Block = { context: string; bindings: Record<string, string | null> }
type Keybindings = { bindings: Block[] } & Record<string, unknown>

export type Merge =
  | { ok: true; text: string; added: string[]; conflicts: string[] }
  | { ok: false; error: string }

// Ajoute les touches manquantes au contexte Global, sans écraser une touche déjà liée ailleurs.
export function mergeKeybindings(text: string | undefined, keys: string[]): Merge {
  let doc: Keybindings
  try {
    doc = text === undefined
      ? {
          $schema: 'https://www.schemastore.org/claude-code-keybindings.json',
          $docs: 'https://code.claude.com/docs/en/keybindings',
          bindings: [],
        }
      : JSON.parse(text)
  } catch {
    return { ok: false, error: 'keybindings.json illisible (JSON invalide)' }
  }
  if (!Array.isArray(doc.bindings)) return { ok: false, error: 'keybindings.json sans tableau "bindings"' }

  let global = doc.bindings.find(b => b.context === 'Global')
  if (global === undefined) {
    global = { context: 'Global', bindings: {} }
    doc.bindings.push(global)
  }
  const added: string[] = []
  const conflicts: string[] = []
  for (const key of keys) {
    const bound = global.bindings[key]
    if (bound === ACTION) continue
    if (bound !== undefined && bound !== null) {
      conflicts.push(`${key} → ${bound}`)
      continue
    }
    global.bindings[key] = ACTION
    added.push(key)
  }

  return { ok: true, text: JSON.stringify(doc, null, 2) + '\n', added, conflicts }
}

// config.yaml de Tabby : Ctrl-Shift-Enter dans la liste du hotkey delete-next-word.
export function tabbyHasHotkey(yaml: string): boolean {
  const list = /^ {2}delete-next-word:\n((?: {4}- .*\n?)*)/m.exec(yaml)
  return list !== null && /- Ctrl-Shift-Enter\s*$/m.test(list[1])
}

// Préférences iTerm (defaults export, XML) : ctrl+shift+enter (0xd-0x60000) qui envoie Esc+d.
export function itermHasMapping(plistXml: string): boolean {
  return /<key>0xd-0x60000[^<]*<\/key>\s*<dict>(?:(?!<\/dict>)[\s\S])*<key>Text<\/key>\s*<string>d<\/string>/.test(plistXml)
}

export const TERMINAL_STEPS: Record<Terminal, string> = {
  tabby:
    'Tabby › Settings › Hotkeys › « Delete next word » : ajouter Ctrl-Shift-Enter, puis redémarrer Tabby.',
  iterm:
    'iTerm › Settings › Profiles › Keys › Key Mappings › + : raccourci ctrl+shift+enter, action « Send Escape Sequence », Esc+ d.',
  other:
    'Terminal non reconnu : il doit distinguer ctrl+shift+enter d\'Entrée (protocole clavier kitty), sinon lui faire envoyer Esc+d (meta+d) pour cette combinaison. Voir le README.',
}
