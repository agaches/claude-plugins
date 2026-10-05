export type OutlineItem = {
  type: string
  text: string
}

export type OutlineSlide = {
  n: number
  parentN: number
  id: string
  title: string
  transition: string
  isState: boolean
  isHidden: boolean
  hasNotes: boolean
  notes: string
  morphShared: number
  kinds: string[]
  items: OutlineItem[]
}

export type Outline = {
  path: string
  title: string
  slides: OutlineSlide[]
  error?: string
}

declare module 'claude-code' {
  interface PluginState {
    'bento-mods': { deck: Outline | null; selected: number }
  }
}
