import type { EngineInterface, Register } from 'claude-code'

import {
  ACTION,
  KEYS,
  TERMINAL_STEPS,
  detectTerminal,
  itermHasMapping,
  mergeKeybindings,
  tabbyHasHotkey,
} from './setup'

const URL = 'https://console.scaleway.com'

async function openConsole($: EngineInterface): Promise<boolean> {
  try {
    const { exitCode, stderr } = await $.process.run(['open', URL])
    if (exitCode === 0) return true
    $.ui.toast(`Scaleway : échec de open (${stderr.trim()})`)
  } catch {
    $.ui.toast('Scaleway : commande open introuvable (macOS seulement)')
  }

  return false
}

async function readOr($: EngineInterface, path: string): Promise<string | undefined> {
  try {
    return await $.fs.read(path)
  } catch {
    return undefined
  }
}

// État du raccourci ; avec write, ajoute les touches manquantes dans keybindings.json.
async function checkSetup($: EngineInterface, write: boolean) {
  const home = (await $.env.get('HOME')) ?? ''
  const terminal = detectTerminal(await $.env.get('TERM_PROGRAM'))
  const lines: string[] = []

  const kbPath = `${home}/.claude/keybindings.json`
  const merge = mergeKeybindings(await readOr($, kbPath), KEYS)
  let isClaudeOk = false
  if (!merge.ok) {
    lines.push(`✗ ${kbPath} : ${merge.error}, à corriger à la main.`)
  } else if (merge.added.length === 0) {
    isClaudeOk = true
    lines.push(`✓ keybindings.json : ${KEYS.join(', ')} → ${ACTION}`)
  } else if (write) {
    await $.fs.write(kbPath, merge.text)
    isClaudeOk = true
    lines.push(`✓ keybindings.json : ajouté ${merge.added.join(', ')} → ${ACTION}`)
  } else {
    lines.push(`✗ keybindings.json : manque ${merge.added.join(', ')}`)
  }
  if (merge.ok && merge.conflicts.length > 0) {
    lines.push(`! déjà lié à autre chose, laissé tel quel : ${merge.conflicts.join(', ')}`)
  }

  let isTerminalOk: boolean | undefined
  if (terminal === 'tabby') {
    const yaml = await readOr($, `${home}/Library/Application Support/tabby/config.yaml`)
    isTerminalOk = yaml !== undefined && tabbyHasHotkey(yaml)
  } else if (terminal === 'iterm') {
    try {
      const { stdout } = await $.process.run(['defaults', 'export', 'com.googlecode.iterm2', '-'])
      isTerminalOk = itermHasMapping(stdout)
    } catch {
      isTerminalOk = false
    }
  }
  const name = { tabby: 'Tabby', iterm: 'iTerm', other: 'terminal' }[terminal]
  if (isTerminalOk === true) lines.push(`✓ ${name} : ctrl+shift+enter envoie meta+d`)
  else if (isTerminalOk === false) lines.push(`✗ ${name} : ${TERMINAL_STEPS[terminal]}`)
  else lines.push(`? ${TERMINAL_STEPS.other}`)

  return { isReady: isClaudeOk && isTerminalOk !== false, lines }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'scaleway', description: 'Ouvre la console Scaleway' })
    await $.command.register({
      name: 'scaleway-setup',
      description: 'Vérifie et règle le raccourci ctrl+shift+enter (terminal, keybindings.json)',
    })
    const { isReady } = await checkSetup($, false)
    if (!isReady) $.ui.toast('Scaleway : ctrl+shift+enter pas encore réglé, lancer /scaleway-setup')

    return next(e)
  })

  on('command.run', { command: 'scaleway' }, async $ => {
    const isOpen = await openConsole($)

    return { text: isOpen ? `Console Scaleway ouverte : ${URL}` : 'Console Scaleway non ouverte (voir le toast).' }
  })

  on('command.run', { command: 'scaleway-setup' }, async $ => {
    const { isReady, lines } = await checkSetup($, true)
    const end = isReady
      ? 'Prêt : ctrl+shift+enter ouvre la console (redémarrer Claude Code si rien ne se passe).'
      : 'Reste à faire : les lignes ✗ ci-dessus, puis relancer /scaleway-setup.'

    return { text: [...lines, '', end].join('\n') }
  })

  on('ui.render', { component: 'AbovePrompt' }, ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const { Button } = $.ui.resolve(e)

    return (
      <Button key="scaleway" label="☁" plain dimColor action={ACTION} onPress={() => openConsole($)} />
    )
  })
}
