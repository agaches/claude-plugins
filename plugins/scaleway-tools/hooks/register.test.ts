import { expect, test } from 'claude-code/testing'

const URL = 'https://console.scaleway.com'

test('/scaleway ouvre la console avec la première commande qui marche', async ($, on) => {
  const calls: (readonly string[])[] = []
  on('env.get', () => ({ value: undefined }))
  on('process.run', (_$, e) => {
    calls.push(e.argv)
    const exitCode = e.argv[0] === 'xdg-open' ? 0 : 1
    return { value: { exitCode, stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })

  const { text } = await $.command.run({ command: 'scaleway', args: '' })

  expect(calls).toEqual([
    ['open', URL],
    ['xdg-open', URL],
  ])
  expect(text).toContain('console.scaleway.com')
})

test('/scaleway sous Windows passe par cmd /c start', async ($, on) => {
  const calls: (readonly string[])[] = []
  on('env.get', (_$, e) => ({ value: e.name === 'OS' ? 'Windows_NT' : undefined }))
  on('process.run', (_$, e) => {
    calls.push(e.argv)
    return { value: { exitCode: 0, stdout: '', stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })

  await $.command.run({ command: 'scaleway', args: '' })

  expect(calls).toEqual([['cmd', '/c', 'start', '""', URL]])
})

test('/scaleway signale un échec et donne l\'URL', async ($, on) => {
  const toasts: string[] = []
  on('env.get', () => ({ value: undefined }))
  on('process.run', () => ({
    value: { exitCode: 1, stdout: '', stderr: 'boom\n', isStdoutTruncated: false, isStderrTruncated: false },
  }))
  on('ui.toast', (_$, e) => {
    toasts.push(e.text)
    return { value: undefined }
  })

  const { text } = await $.command.run({ command: 'scaleway', args: '' })

  expect(text).toContain('non ouverte')
  expect(toasts).toEqual([`Scaleway : navigateur non ouvert (open : boom ; xdg-open : boom), ouvrir ${URL}`])
})
