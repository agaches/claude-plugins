// Commandes qui ouvrent une URL dans le navigateur, par ordre d'essai. Fonction pure, testée dans browser.test.ts.

export type BrowserEnv = { browser?: string; os?: string; wslDistro?: string }

// $BROWSER : liste séparée par « : », %s remplacé par l'URL, sinon l'URL en dernier argument.
function fromBrowserVar(browser: string, url: string): string[][] {
  return browser
    .split(':')
    .map(c => c.trim().split(/\s+/).filter(Boolean))
    .filter(argv => argv.length > 0)
    .map(argv => (argv.some(a => a.includes('%s')) ? argv.map(a => a.replaceAll('%s', url)) : [...argv, url]))
}

export function browserCommands(env: BrowserEnv, url: string): string[][] {
  const own = env.browser ? fromBrowserVar(env.browser, url) : []
  // start est interne à cmd ; le "" vide est le titre de la fenêtre, sinon l'URL serait prise pour le titre.
  if (env.os === 'Windows_NT') return [...own, ['cmd', '/c', 'start', '""', url]]
  if (env.wslDistro) return [...own, ['wslview', url], ['explorer.exe', url]]
  // macOS puis Linux : le premier qui répond 0 l'emporte, sans détecter le système.
  return [...own, ['open', url], ['xdg-open', url]]
}
