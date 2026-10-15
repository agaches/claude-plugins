import { expect, test } from 'claude-code/testing'

import { browserCommands } from './browser'

const URL = 'https://console.scaleway.com'

test('browserCommands selon le système', () => {
  expect(browserCommands({}, URL)).toEqual([
    ['open', URL],
    ['xdg-open', URL],
  ])
  expect(browserCommands({ os: 'Windows_NT' }, URL)).toEqual([['cmd', '/c', 'start', '""', URL]])
  expect(browserCommands({ wslDistro: 'Ubuntu' }, URL)).toEqual([
    ['wslview', URL],
    ['explorer.exe', URL],
  ])
})

test('browserCommands passe $BROWSER en premier', () => {
  expect(browserCommands({ browser: 'firefox --new-tab' }, URL)[0]).toEqual(['firefox', '--new-tab', URL])
  expect(browserCommands({ browser: 'w3m %s:lynx' }, URL).slice(0, 2)).toEqual([
    ['w3m', URL],
    ['lynx', URL],
  ])
})
