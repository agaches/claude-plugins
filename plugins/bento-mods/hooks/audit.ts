// Pure checks on a .bento.html file: no engine calls, so tests run them directly.

export const BENTO_FILE = /\.bento\.html$/

const DOC_BLOCK = /(<script[^>]*id=["']bento-doc["'][^>]*>)([\s\S]*?)(<\/script>)/

const SECRET_KEYS = ['ownerPriv', 'writerPriv', 'invite'] as const

const RIGHT_EDGE = 1184

export type Audit = {
  errors: string[]
  warnings: string[]
  slides: number
  morphs: number
  missingNotes: number
}

// Bash is guarded by spelling, not by effect: a command that builds the path at
// run time (variables, cd, find -exec) slips through.
// ponytail: regex over the command line, upgrade path = sandbox/fs-level write hook.
const BENTO_PATH = /[^\s'"`;|&<>()]*\.bento\.html/g
const WRITES = /(>>?\s*[^\s|;&]*\.bento\.html|\btee\b|\bsed\b[^|;&]*\s-i|\b(python3?|node|perl|ruby|bun|deno)\b|\b(cp|mv|rsync|dd|truncate)\b)/
const APP_DOWNLOAD = /\b(curl|wget|iwr)\b[^|;&]*https:\/\/bento\.page\/releases\//

export const bentoPaths = (command: string): string[] => [...new Set(command.match(BENTO_PATH) ?? [])]

export const bashWrites = (command: string): boolean =>
  bentoPaths(command).length > 0 && WRITES.test(command) && !APP_DOWNLOAD.test(command)

export const docBlock =(html: string): string | undefined => DOC_BLOCK.exec(html)?.[2]

// The file with its document emptied: what must stay identical across edits.
export const shell = (html: string): string => html.replace(DOC_BLOCK, '$1$3')

export const collabSecrets = (html: string): string[] => {
  const block = docBlock(html)
  if (!block?.trim()) return []
  try {
    const collab = JSON.parse(block)?.collab ?? {}
    return SECRET_KEYS.filter(k => collab[k] !== undefined)
  } catch {
    // Unparseable block: fall back to a textual scan, a false positive beats a leak.
    return SECRET_KEYS.filter(k => block.includes(`"${k}"`))
  }
}

type El = { id?: string; type?: string; x?: number; w?: number; preset?: string; option?: any }
type Slide = { id?: string; transition?: string; notes?: string; elements?: El[] }

export const audit = (html: string): Audit => {
  const errors: string[] = []
  const warnings: string[] = []
  const result: Audit = { errors, warnings, slides: 0, morphs: 0, missingNotes: 0 }

  const block = docBlock(html)
  if (block === undefined) return { ...result, errors: ['no #bento-doc block found'] }
  if (!block.trim()) return result
  if (block.includes('<')) errors.push('literal "<" in #bento-doc: escape it as \\u003c')

  let doc: any
  try {
    doc = JSON.parse(block)
  } catch (err) {
    return { ...result, errors: [...errors, `#bento-doc is not valid JSON: ${(err as Error).message}`] }
  }

  if (doc.format !== 'bento/slides') warnings.push(`format is ${JSON.stringify(doc.format)}, this audit knows bento/slides only`)
  if (!doc.size?.width || !doc.size?.height) errors.push('size.width/size.height missing (app will not boot)')
  if (!doc.theme?.fontFamily) errors.push('theme.fontFamily missing (app will not boot)')

  const slides: Slide[] = Array.isArray(doc.slides) ? doc.slides : []
  result.slides = slides.length

  slides.forEach((slide, i) => {
    const name = `slide ${i + 1}${slide.id ? ` (${slide.id})` : ''}`
    const elements = slide.elements ?? []

    if (!slide.notes?.trim()) result.missingNotes++

    if (slide.transition === 'morph') {
      result.morphs++
      const before = new Set((slides[i - 1]?.elements ?? []).map(el => el.id))
      if (!elements.some(el => before.has(el.id))) warnings.push(`${name}: morph but no element id shared with the previous slide`)
    }

    for (const el of elements) {
      if (el.type === 'text' && typeof el.x === 'number' && typeof el.w === 'number' && el.x + el.w > RIGHT_EDGE)
        warnings.push(`${name}: text ${el.id} ends at x=${el.x + el.w}, past the ${RIGHT_EDGE} margin`)

      if (el.type === 'chart' && el.preset !== 'pie') {
        const series = el.option?.series ?? []
        for (const s of Array.isArray(series) ? series : [series])
          if ((s?.data ?? []).some((d: unknown) => typeof d !== 'number'))
            errors.push(`${name}: chart ${el.id} series "${s?.name ?? s?.type}" has non-number data (renders as 0)`)
      }
    }
  })

  return result
}

export const summary = (file: string, a: Audit): string => {
  const base = file.split('/').pop()
  const issues = a.errors.length ? ` · ${a.errors.length} erreur(s)` : ''
  return `${base} · ${a.slides} slides · ${a.morphs} morph · ${a.missingNotes} sans notes${issues}`
}
