import { expect, test } from 'claude-code/testing'

import { ACTION, KEYS, detectTerminal, itermHasMapping, mergeKeybindings, tabbyHasHotkey } from './setup'

test('detectTerminal', () => {
  expect(detectTerminal('Tabby')).toBe('tabby')
  expect(detectTerminal('iTerm.app')).toBe('iterm')
  expect(detectTerminal('ghostty')).toBe('other')
  expect(detectTerminal(undefined)).toBe('other')
})

test('mergeKeybindings crée le fichier quand il manque', () => {
  const merge = mergeKeybindings(undefined, KEYS)
  if (!merge.ok) throw new Error(merge.error)
  expect(merge.added).toEqual(KEYS)
  expect(JSON.parse(merge.text).bindings).toEqual([
    { context: 'Global', bindings: { 'ctrl+shift+enter': ACTION, 'meta+d': ACTION } },
  ])
})

test('mergeKeybindings garde l\'existant et signale les conflits', () => {
  const text = JSON.stringify({
    bindings: [
      { context: 'Chat', bindings: { 'ctrl+e': 'chat:externalEditor' } },
      { context: 'Global', bindings: { 'meta+d': 'app:toggleTodos', 'ctrl+shift+enter': ACTION } },
    ],
  })
  const merge = mergeKeybindings(text, KEYS)
  if (!merge.ok) throw new Error(merge.error)
  expect(merge.added).toEqual([])
  expect(merge.conflicts).toEqual(['meta+d → app:toggleTodos'])
  expect(JSON.parse(merge.text).bindings[0]).toEqual({ context: 'Chat', bindings: { 'ctrl+e': 'chat:externalEditor' } })
})

test('mergeKeybindings refuse un JSON invalide', () => {
  expect(mergeKeybindings('{ oups', KEYS).ok).toBe(false)
})

test('tabbyHasHotkey', () => {
  const on = 'hotkeys:\n  delete-next-word:\n    - ⌥-Delete\n    - Ctrl-Shift-Enter\n  search:\n    - ⌘-F\n'
  const off = 'hotkeys:\n  delete-next-word:\n    - ⌥-Delete\n  search:\n    - Ctrl-Shift-Enter\n'
  expect(tabbyHasHotkey(on)).toBe(true)
  expect(tabbyHasHotkey(off)).toBe(false)
})

test('itermHasMapping', () => {
  const entry = (text: string) =>
    `<key>0xd-0x60000-0x24</key>\n<dict>\n<key>Action</key>\n<integer>10</integer>\n<key>Text</key>\n<string>${text}</string>\n</dict>`
  expect(itermHasMapping(`<dict>${entry('d')}</dict>`)).toBe(true)
  expect(itermHasMapping(`<dict>${entry('x')}</dict>`)).toBe(false)
  expect(itermHasMapping('<dict></dict>')).toBe(false)
})
