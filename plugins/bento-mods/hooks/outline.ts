// Pure parsing of a .bento.html into the outline the pane draws.
import type { Outline, OutlineItem, OutlineSlide } from '../types'

export const BENTO_FILE = /\.bento\.html$/
const BENTO_PATH = /[^\s'"`;|&<>()]*\.bento\.html/g
const DOC_BLOCK = /<script[^>]*id=["']bento-doc["'][^>]*>([\s\S]*?)<\/script>/

// ponytail: chrome is recognised by the ids this deck uses; a generic version would
// detect elements repeated identically on every slide.
const CHROME = new Set(['brand', 'pageno', 'dismiss'])

const KIND_ICON: Record<string, string> = { chart: 'chart', table: 'table', image: 'image', media: 'media', svg: 'svg' }

export const bentoPaths = (command: string): string[] => [...new Set(command.match(BENTO_PATH) ?? [])]

export const plain = (html: string): string =>
  html
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]*>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim()

type El = {
  id?: string; morphId?: string; type?: string; role?: string; html?: string; link?: string
  shape?: string; preset?: string; option?: any; rows?: { cells?: unknown[] }[]; kind?: string; src?: string
}

// One line per element: what it is and what it says.
export const describeEl = (el: El): OutlineItem => {
  const link = el.link ? ` → ${el.link}` : ''
  const type = el.type ?? '?'
  const text = (() => {
    switch (type) {
      case 'text': return plain(el.html ?? '')
      case 'shape': return el.shape ?? ''
      case 'chart': {
        const series = Array.isArray(el.option?.series) ? el.option.series : []
        return `${el.preset ?? ''} · ${series.length} série(s)`
      }
      case 'table': return `${el.rows?.length ?? 0} lignes × ${el.rows?.[0]?.cells?.length ?? 0} colonnes`
      case 'image': return el.src?.startsWith('asset:') ? el.src : 'image intégrée'
      case 'media': return el.kind ?? ''
      default: return ''
    }
  })()
  return { type, text: text + link }
}
type Slide = { id?: string; name?: string; transition?: string; stateOf?: string; hidden?: boolean; notes?: string; elements?: El[] }

const slideTitle = (s: Slide): string => {
  const els = s.elements ?? []
  const pick = els.find(e => e.role === 'title') ?? els.find(e => e.id === 'title') ?? els.find(e => e.type === 'text' && e.html)
  return plain(pick?.html ?? '') || s.name || s.id || '(sans titre)'
}

export const outline = (path: string, html: string): Outline => {
  const block = DOC_BLOCK.exec(html)?.[1]
  if (block === undefined) return { path, title: '', slides: [], error: 'pas de bloc #bento-doc' }
  if (!block.trim()) return { path, title: '', slides: [], error: 'deck vide' }

  let doc: any
  try {
    doc = JSON.parse(block)
  } catch {
    return { path, title: '', slides: [], error: 'JSON invalide' }
  }

  const raw: Slide[] = Array.isArray(doc.slides) ? doc.slides : []
  let n = 0
  let prevKeys = new Set<string>()
  const slides: OutlineSlide[] = raw.map(s => {
    const els = s.elements ?? []
    const keys = els.map(e => e.morphId ?? e.id ?? '')
    const morphShared = s.transition === 'morph' ? keys.filter(k => k && prevKeys.has(k)).length : 0
    prevKeys = new Set(keys)
    const isState = Boolean(s.stateOf)
    if (!isState) n++
    return {
      n: isState ? 0 : n,
      parentN: n,
      notes: plain(s.notes ?? ''),
      // The repeated chrome (footer, page number) says nothing about this slide.
      items: els.filter(e => !CHROME.has(e.id ?? '')).map(describeEl),
      id: s.id ?? '',
      title: slideTitle(s),
      transition: s.transition ?? 'none',
      isState,
      isHidden: Boolean(s.hidden),
      hasNotes: Boolean(s.notes?.trim()),
      morphShared,
      kinds: [...new Set(els.map(e => KIND_ICON[e.type ?? '']).filter((k): k is string => Boolean(k)))],
    }
  })

  return { path, title: String(doc.title ?? ''), slides }
}
