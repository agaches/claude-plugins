import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'
import type { Outline } from '../types'
import { BENTO_FILE, bentoPaths, outline } from './outline'

const PANE = 'bento-outline'
const TITLE = 'Bento · plan du deck'
const deck = atom({ plugin: 'bento-mods', key: 'deck' } as const, null as Outline | null)
const selected = atom({ plugin: 'bento-mods', key: 'selected' } as const, 0)

const pad2 = (n: number) => String(n).padStart(2, '0')
const cut = (text: string, width: number) => (text.length > width ? text.slice(0, Math.max(1, width - 1)) + '…' : text)

// Reads the deck host-side and publishes its outline; the pane redraws on the write.
const load = async ($: EngineInterface, path: string) => {
  const html = await $.fs.read(path).catch(() => undefined)
  if (html === undefined) return false
  await update($, deck, () => outline(path, html))
  return true
}

const afterTool = async ($: EngineInterface, paths: string[]) => {
  for (const p of paths.filter(p => BENTO_FILE.test(p))) await load($, p)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'bento-outline', description: 'Show the outline of a Bento deck in a side pane' })
    // A deck in the working directory: show it right away (seats from 144 columns).
    const found = (await $.fs.list().catch(() => [])).find(f => BENTO_FILE.test(f.name))
    if (found && (await load($, found.name))) void $.ui.open({ id: PANE, title: TITLE })
    return next(e)
  })

  on('command.run', { command: 'bento-outline' }, async ($, e) => {
    const asked = e.args.trim()
    const current = await read($, deck)
    const path = asked || current?.path
    if (!path) return { text: 'bento-outline: aucun deck connu. Usage : /bento-outline <fichier.bento.html>' }
    if (!(await load($, path))) return { text: `bento-outline: impossible de lire ${path}` }
    await $.ui.open({ id: PANE, title: TITLE })
    return { text: `bento-outline: panneau ouvert sur ${path}` }
  })

  // Every tool that touches a deck refreshes the outline once it has run.
  on('tool.call', { tool: 'Read' }, async ($, e, next) => {
    const ran = await next(e)
    await afterTool($, [e.file_path])
    return ran
  })
  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    const ran = await next(e)
    await afterTool($, [e.file_path])
    return ran
  })
  on('tool.call', { tool: 'Edit' }, async ($, e, next) => {
    const ran = await next(e)
    await afterTool($, [e.file_path])
    return ran
  })
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    await afterTool($, bentoPaths(e.command))
    return ran
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const d = await read($, deck)
    if (!d) return <Text dimColor>Aucun deck. /bento-outline &lt;fichier.bento.html&gt;</Text>

    const file = d.path.split('/').pop()
    if (d.error) return (
      <Box flexDirection="column">
        <Text bold>{file}</Text>
        <Text color="red">{d.error}</Text>
      </Box>
    )

    const cols = Math.max(20, e.props.bodyColumns)
    const rows = e.viewport?.rows ?? 40
    const total = d.slides.length
    const sel = Math.min(await read($, selected), Math.max(0, total - 1))
    const s = d.slides[sel]
    const select = (i: number) => () => update($, selected, () => Math.min(Math.max(0, i), total - 1))
    const main = d.slides.filter(x => !x.isState).length

    // Top: one plain Button per slide, the selected one bracketed.
    const nav = (
      <Box flexDirection="row" flexWrap="wrap" columnGap={1}>
        <Button key="prev" plain hotkey="p" label="‹" onPress={select(sel - 1)} />
        {d.slides.map((x, i) => {
          const label = x.isState ? `${pad2(x.parentN)}+` : pad2(x.n)
          return (
            <Button key={`s${i}`} plain label={i === sel ? `[${label}]` : label}
              dimColor={i !== sel && (x.isState || x.isHidden)} onPress={select(i)} />
          )
        })}
        <Button key="next" plain hotkey="n" label="›" onPress={select(sel + 1)} />
      </Box>
    )

    if (!s) return <Box flexDirection="column"><Text bold>{d.title || file}</Text>{nav}</Box>

    // Bottom: the selected slide, element by element, then its notes.
    const head = s.isState ? `${pad2(s.parentN)}+ (détail)` : pad2(s.n)
    const meta = [
      s.transition === 'morph' ? `morph · ${s.morphShared} élément(s) partagé(s)` : `transition ${s.transition}`,
      `${s.items.length} élément(s)`,
      s.isHidden ? 'masquée' : '',
    ].filter(Boolean).join(' · ')
    const items = s.items.slice(0, Math.max(3, rows - 14))

    return (
      <Box flexDirection="column">
        <Text bold wrap="truncate-end">{d.title || file}</Text>
        <Text dimColor wrap="truncate-end">{file} · {main} slides · p/n ou clic pour naviguer</Text>
        {nav}
        <Text dimColor>{'─'.repeat(cols)}</Text>
        <Text bold color="yellow" wrap="truncate-end">{head} · {s.title}</Text>
        <Text dimColor wrap="truncate-end">{meta}</Text>
        <Text> </Text>
        {items.map(it => (
          <Box flexDirection="row" columnGap={1}>
            <Text dimColor>{it.type.padEnd(5).slice(0, 5)}</Text>
            <Text wrap="truncate-end">{cut(it.text || '—', cols - 6)}</Text>
          </Box>
        ))}
        {s.items.length > items.length && <Text dimColor>… {s.items.length - items.length} élément(s) de plus</Text>}
        <Text> </Text>
        <Text dimColor bold>Notes</Text>
        {s.hasNotes
          ? <Text wrap="wrap">{s.notes}</Text>
          : <Text color="red">aucune note sur cette slide</Text>}
      </Box>
    )
  })
}
