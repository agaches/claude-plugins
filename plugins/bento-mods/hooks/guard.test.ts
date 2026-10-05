import { describe, expect, test } from 'claude-code/testing'
import { audit, bashWrites, bentoPaths, collabSecrets, shell } from './audit'

const deck = (doc: unknown) =>
  `<html><head><script type="application/bento+json" id="bento-doc">${JSON.stringify(doc)}</script>` +
  `<script>/* runtime */</script></head></html>`

const VALID = {
  format: 'bento/slides',
  size: { width: 1280, height: 720 },
  theme: { fontFamily: 'system-ui' },
  slides: [
    { id: 's1', notes: 'hi', elements: [{ id: 't1', type: 'text', x: 96, w: 1088 }] },
    { id: 's2', notes: 'hi', transition: 'morph', elements: [{ id: 't1', type: 'text', x: 96, w: 500 }] },
  ],
}

describe('audit', () => {
  test('a valid deck has no errors', () => {
    const a = audit(deck(VALID))
    expect(a.errors).toEqual([])
    expect(a.warnings).toEqual([])
    expect(a.slides).toBe(2)
    expect(a.morphs).toBe(1)
  })

  test('flags missing theme, raw "<", bad chart data, orphan morph, margin, notes', () => {
    const bad = {
      format: 'bento/slides',
      size: { width: 1280, height: 720 },
      theme: {},
      slides: [
        { id: 's1', elements: [{ id: 'c', type: 'chart', preset: 'bar', option: { series: [{ type: 'bar', data: [1, { value: 2 }] }] } }] },
        { id: 's2', notes: '<b>x</b>', transition: 'morph', elements: [{ id: 'z', type: 'text', x: 900, w: 380 }] },
      ],
    }
    const a = audit(deck(bad))
    expect(a.errors.some(m => m.includes('fontFamily'))).toBe(true)
    expect(a.errors.some(m => m.includes('\\u003c'))).toBe(true)
    expect(a.errors.some(m => m.includes('non-number'))).toBe(true)
    expect(a.warnings.some(m => m.includes('no element id shared'))).toBe(true)
    expect(a.warnings.some(m => m.includes('1184'))).toBe(true)
    expect(a.missingNotes).toBe(1)
  })

  test('invalid JSON is an error, empty block is fine', () => {
    expect(audit(deck(VALID).replace('"format"', 'format')).errors[0]).toContain('not valid JSON')
    expect(audit(deck(VALID).replace(JSON.stringify(VALID), '')).errors).toEqual([])
  })
})

describe('collab and shell', () => {
  test('detects collab secrets', () => {
    expect(collabSecrets(deck({ ...VALID, collab: { room: 'r', writerPriv: 'k' } }))).toEqual(['writerPriv'])
    expect(collabSecrets(deck({ ...VALID, collab: { room: 'r' } }))).toEqual([])
  })

  test('shell ignores the document, sees the runtime', () => {
    expect(shell(deck(VALID))).toBe(shell(deck({ ...VALID, title: 'x' })))
    expect(shell(deck(VALID))).not.toBe(shell(deck(VALID).replace('runtime', 'other')))
  })
})

// The test environment has no file system: the hooks' $.fs.read is answered from memory.
const withFile = (on: any, text: string) => on('fs.read', () => ({ value: text }))

describe('hooks', () => {
  test('first Read of a deck with keys is denied, the second passes', async ($, on) => {
    withFile(on, deck({ ...VALID, collab: { ownerPriv: 'k' } }))
    on('tool.call', { tool: 'Read' }, () => ({ result: { type: 'text' } as never }))

    const first = await $.tool.call({ tool: 'Read', file_path: 'a.bento.html' })
    expect(first.isError ?? first.deny !== undefined).toBe(true)
    const second = await $.tool.call({ tool: 'Read', file_path: 'a.bento.html' })
    expect(second.deny).toBe(undefined)
    expect(second.isError).toBe(undefined)
  })

  test('Write that changes the runtime is denied, a doc-only Write passes', async ($, on) => {
    withFile(on, deck(VALID))
    on('tool.call', { tool: 'Write' }, () => ({ result: {} as never }))

    const broken = await $.tool.call({ tool: 'Write', file_path: 'a.bento.html', content: deck(VALID).replace('runtime', 'gone') })
    expect(broken.isError ?? broken.deny !== undefined).toBe(true)
    const ok = await $.tool.call({ tool: 'Write', file_path: 'a.bento.html', content: deck({ ...VALID, title: 'x' }) })
    expect(ok.isError).toBe(undefined)
  })
})

describe('bash', () => {
  test('spots writes to a deck, not reads or the app download', () => {
    expect(bentoPaths('python3 build.py deck.bento.html && open deck.bento.html')).toEqual(['deck.bento.html'])
    expect(bashWrites('python3 build.py deck.bento.html')).toBe(true)
    expect(bashWrites("sed -i '' 's/a/b/' x.bento.html")).toBe(true)
    expect(bashWrites('echo hi > x.bento.html')).toBe(true)
    expect(bashWrites('grep -c ownerPriv x.bento.html 2>/dev/null')).toBe(false)
    expect(bashWrites('curl -fsSL https://bento.page/releases/slides/Bento_Slides.bento.html -o x.bento.html')).toBe(false)
    expect(bashWrites('python3 other.py notes.md')).toBe(false)
  })

  test('a writing Bash command is denied once, then passes', async ($, on) => {
    withFile(on, deck(VALID))
    on('tool.call', { tool: 'Bash' }, () => ({ result: {} as never }))

    const cmd = 'python3 build.py a.bento.html'
    const first = await $.tool.call({ tool: 'Bash', command: cmd })
    expect(first.isError ?? first.deny !== undefined).toBe(true)
    const second = await $.tool.call({ tool: 'Bash', command: cmd })
    expect(second.isError).toBe(undefined)
  })

  test('a plain read of a keyless deck passes', async ($, on) => {
    withFile(on, deck(VALID))
    on('tool.call', { tool: 'Bash' }, () => ({ result: {} as never }))
    const ran = await $.tool.call({ tool: 'Bash', command: 'grep -c slides a.bento.html' })
    expect(ran.isError).toBe(undefined)
  })
})
