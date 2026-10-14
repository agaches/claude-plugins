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
