import type { Register } from 'claude-code'
import { register as guard } from './guard'
import { register as outlinePane } from './outline-pane'

// One module per plugin: each mod registers its own hooks.
export const register: Register = (on, options) => {
  guard(on, options)
  outlinePane(on, options)
}
