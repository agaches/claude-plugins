import { describe, expect, test } from 'claude-code/testing'
import { outline, plain } from './outline'

const deck = (doc: unknown) =>
  `<html><script type="application/bento+json" id="bento-doc">${JSON.stringify(doc).replace(/</g, '\\u003c')}</script></html>`

const DOC = {
  title: 'Demo',
  slides: [
    { id: 'a', notes: 'n', elements: [{ id: 'title', type: 'text', html: 'Hello<br>world' }] },
    { id: 'b', transition: 'morph', elements: [{ id: 'title', type: 'text', html: 'Next' }, { id: 'c', type: 'chart' }] },
    { id: 'b-detail', stateOf: 'b', notes: 'n', elements: [{ id: 'x', type: 'text', role: 'title', html: 'Detail &amp; more' }] },
  ],
}

describe('outline', () => {
  test('titles, numbering, morph, kinds, notes', () => {
    const o = outline('d.bento.html', deck(DOC))
    expect(o.title).toBe('Demo')
    expect(o.slides.map(s => s.title)).toEqual(['Hello world', 'Next', 'Detail & more'])
    expect(o.slides.map(s => s.n)).toEqual([1, 2, 0])
    expect(o.slides[1]?.morphShared).toBe(1)
    expect(o.slides[1]?.kinds).toEqual(['chart'])
    expect(o.slides[1]?.hasNotes).toBe(false)
    expect(o.slides[2]?.isState).toBe(true)
  })

  test('errors are reported, not thrown', () => {
    expect(outline('d', '<html></html>').error).toBe('pas de bloc #bento-doc')
    expect(outline('d', deck(DOC).replace('"title"', 'title')).error).toBe('JSON invalide')
    expect(plain('a&nbsp;<b>b</b>')).toBe('a b')
  })
})

describe('pane', () => {
  test('a Read of a deck fills the pane on every surface', async ($, on) => {
    on('fs.read', () => ({ value: deck(DOC) }))
    on('tool.call', { tool: 'Read' }, () => ({ result: { type: 'text' } as never }))
    await $.tool.call({ tool: 'Read', file_path: 'd.bento.html' })

    for (const surface of ['terminal', 'desktop'] as const) {
      const ui = await $.ui.mount({
        plugin: 'bento-mods', surface, component: 'Pane', requestId: 'bento-outline',
        props: { title: 'x', isFocused: false, bodyColumns: 50, placement: 'dock' } as never,
      })
      // Opens on slide 1: its detail and notes below the navigator.
      expect(await ui.find({ text: /01 · Hello world/ })).toBeDefined()
      expect(await ui.find({ key: 's0', text: '[01]' })).toBeDefined()

      // A click on the state slide's button shows its content.
      await ui.press({ key: 's2' })
      expect(await ui.find({ text: /02\+ \(détail\) · Detail & more/ })).toBeDefined()

      // ‹ walks back to slide 2, whose missing notes are flagged.
      await ui.press({ key: 'prev' })
      expect(await ui.find({ text: /02 · Next/ })).toBeDefined()
      expect(await ui.find({ text: /chart\s*$|bar · 0 série/ })).toBeDefined()
      expect(await ui.find({ text: 'aucune note sur cette slide' })).toBeDefined()
      await ui.press({ key: 's0' })
      await ui.unmount()
    }
  })
})
