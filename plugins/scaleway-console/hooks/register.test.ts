import { expect, test } from 'claude-code/testing'

test('/scaleway ouvre la console dans le navigateur', async ($, on) => {
  const calls: (readonly string[])[] = []
  on('process.run', (_$, e) => {
    calls.push(e.argv)
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })

  const { text } = await $.command.run({ command: 'scaleway', args: '' })

  expect(calls).toEqual([['open', 'https://console.scaleway.com']])
  expect(text).toContain('console.scaleway.com')
})

test('/scaleway signale un échec de open', async ($, on) => {
  const toasts: string[] = []
  on('process.run', () => ({ value: { exitCode: 1, stdout: '', stderr: 'boom\n' } }))
  on('ui.toast', (_$, e) => {
    toasts.push(e.text)
    return { value: undefined }
  })

  const { text } = await $.command.run({ command: 'scaleway', args: '' })

  expect(text).toContain('non ouverte')
  expect(toasts).toEqual(['Scaleway : échec de open (boom)'])
})
