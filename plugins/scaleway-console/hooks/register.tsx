import type { EngineInterface, Register } from 'claude-code'

const URL = 'https://console.scaleway.com'
// ctrl+shift+enter : Tabby (hotkey delete-next-word) envoie ESC d = meta+d,
// lié à cette action dans ~/.claude/keybindings.json
const ACTION = 'app:cycleDiffBase'

async function openConsole($: EngineInterface) {
  const { exitCode, stderr } = await $.process.run(['open', URL])
  if (exitCode !== 0) $.ui.toast(`Scaleway : échec de open (${stderr.trim()})`)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'scaleway', description: 'Ouvre la console Scaleway' })

    return next(e)
  })

  on('command.run', { command: 'scaleway' }, async $ => {
    await openConsole($)

    return { text: `Console Scaleway ouverte : ${URL}` }
  })

  on('ui.render', { component: 'AbovePrompt' }, ($, e, next) => {
    if (e.props.hasSurvey) return next(e)
    const { Button } = $.ui.resolve(e)

    return (
      <Button key="scaleway" label="☁" plain dimColor action={ACTION} onPress={() => openConsole($)} />
    )
  })
}
