import type { EngineInterface, Register, ToolCallResult } from 'claude-code'
import { audit, bashWrites, BENTO_FILE, bentoPaths, collabSecrets, shell, summary } from './audit'

const readText = ($: EngineInterface, path: string) => $.fs.read(path).catch(() => undefined)

const SHELL_DENY =
  'bento-guard: this change touches the Bento runtime outside the #bento-doc block. ' +
  'Edit only the JSON inside <script id="bento-doc">, never regenerate the HTML file.'

export const register: Register = on => {
  // Paths whose collab keys were already flagged: the second Read goes through.
  // Module state on purpose: a reload re-arms the warning.
  const flagged = new Set<string>()

  on('tool.call', { tool: 'Read' }, async ($, e, next) => {
    if (!BENTO_FILE.test(e.file_path) || flagged.has(e.file_path)) return next(e)
    const html = await readText($, e.file_path)
    const keys = html ? collabSecrets(html) : []
    if (!keys.length) return next(e)

    flagged.add(e.file_path)
    $.ui.toast(`bento-guard: ${e.file_path.split('/').pop()} contient des clés de session live (${keys.join(', ')})`)
    return {
      deny:
        `bento-guard: ${e.file_path} carries live-collaboration credentials in doc.collab (${keys.join(', ')}). ` +
        'Anything that reads this file can join and write to the session. Tell the user before reading it, ' +
        'and offer a keyless copy (Save > Save read-only copy, or Share > Stop sharing on a duplicate). ' +
        'Only if the user agrees, Read the file again: the next Read is allowed.',
    }
  })

  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    if (!BENTO_FILE.test(e.file_path)) return next(e)
    const before = await readText($, e.file_path)
    if (before !== undefined && shell(before) !== shell(e.content)) return { deny: SHELL_DENY }
    return withAudit($, [e.file_path], await next(e))
  })

  on('tool.call', { tool: 'Edit' }, async ($, e, next) => {
    if (!BENTO_FILE.test(e.file_path)) return next(e)
    const before = await readText($, e.file_path)
    if (before !== undefined) {
      const after = e.replace_all
        ? before.split(e.old_string).join(e.new_string)
        : before.replace(e.old_string, () => e.new_string)
      if (shell(before) !== shell(after)) return { deny: SHELL_DENY }
    }
    return withAudit($, [e.file_path], await next(e))
  })

  // Bash reaches the same files around the three tools above: cat leaks the keys,
  // python/sed/redirects rewrite the runtime. Deny once, the user decides, the
  // identical command then passes and its result is audited.
  const confirmed = new Set<string>()

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const paths = bentoPaths(e.command)
    if (!paths.length || confirmed.has(e.command)) return withAudit($, paths, await next(e))

    const leaks: string[] = []
    for (const p of paths) {
      const html = await readText($, p)
      if (html && collabSecrets(html).length && !flagged.has(p)) leaks.push(p)
    }
    const writes = bashWrites(e.command)
    if (!leaks.length && !writes) return next(e)

    confirmed.add(e.command)
    leaks.forEach(p => flagged.add(p))
    const reasons = [
      ...leaks.map(p => `${p} carries live-collaboration credentials (doc.collab)`),
      ...(writes ? ['this command looks like it writes a .bento.html outside the guarded Edit tool'] : []),
    ]
    $.ui.toast(`bento-guard: commande Bash sur un deck bloquée (${reasons.length} raison(s))`)
    return {
      deny:
        `bento-guard: ${reasons.join('; ')}. Prefer Read / Edit on the #bento-doc block, which bento-guard checks. ` +
        'If Bash is really needed, tell the user why and ask; only if they agree, run the identical command again: it is then allowed and audited.',
    }
  })
}

// After a successful write: audit each deck, show the summary, hand problems to the model.
const withAudit = async <T extends string>($: EngineInterface, paths: string[], ran: ToolCallResult<T>) => {
  if (ran.deny !== undefined || ran.isError) return ran
  const notes: string[] = []
  for (const path of paths) {
    const html = await readText($, path)
    if (html === undefined) continue

    const a = audit(html)
    $.ui.status(summary(path, a))
    const lines = [...a.errors.map(m => `ERROR ${m}`), ...a.warnings.map(m => `WARN ${m}`)]
    if (a.missingNotes) lines.push(`WARN ${a.missingNotes} slide(s) without speaker notes`)
    if (lines.length) notes.push(`bento-guard audit of ${path}:\n${lines.join('\n')}`)
  }
  return notes.length ? { ...ran, context: [...(ran.context ?? []), ...notes] } : ran
}
