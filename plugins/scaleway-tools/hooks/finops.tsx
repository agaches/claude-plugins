import { atom, read, update } from 'claude-code'
import type { EngineInterface, PluginOptions, Register } from 'claude-code'

import type { Ligne, Mois, Rapport } from '../types'

// Panneau FinOps : dépense Scaleway du jour, du mois, budget et répartition par projet, via la CLI scw.
const PANE = 'finops'
const PERIODE_MS = 60 * 60 * 1000

// Couleur par projet, dans l'ordre de l'option projets (la couleur suit le projet, jamais son rang) : palette
// catégorielle sombre, validée par dataviz/scripts/validate_palette.js --mode dark (7 teintes, toutes OK).
const TEINTES = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300']
const AUTRE = '#9085e9'
const STATUT = { bon: '#0ca30c', alerte: '#fab219', critique: '#d03b3b' }
const NOMS_MOIS = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']

const rapport = atom({ plugin: 'scaleway-tools', key: 'rapport' } as const, null)
const erreur = atom({ plugin: 'scaleway-tools', key: 'erreur' } as const, null)

type Montant = { units?: number | string; nanos?: number }
type Conso = { value: Montant; project_name?: string; project_id?: string; product_name?: string }

export const eur = (v: Montant): number => Number(v.units ?? 0) + (v.nanos ?? 0) / 1e9

// Options du plugin, normalisées : repertoire sans / final, projets en liste.
export const lireOptions = (options: PluginOptions, home: string) => {
  const texte = (k: string) => String(options[k] ?? '').trim()
  return {
    repertoire: texte('repertoire_direnv')
      .replace(/^~(?=\/|$)/, home)
      .replace(/\/+$/, ''),
    organisation: texte('organisation_id'),
    projets: texte('projets')
      .split(',')
      .map(p => p.trim())
      .filter(Boolean),
  }
}

export const dansRepertoire = (racine: string, repertoire: string) =>
  !repertoire || racine === repertoire || racine.startsWith(`${repertoire}/`)

export const commandeScw = (args: string[], repertoire: string, organisation: string) => [
  ...(repertoire ? ['direnv', 'exec', repertoire] : []),
  'scw',
  ...args,
  ...(organisation ? [`organization-id=${organisation}`] : []),
  '-o',
  'json',
]

export const teinte = (projet: string, projets: readonly string[]) => {
  const i = projets.indexOf(projet)
  return i < 0 ? AUTRE : (TEINTES[i] ?? AUTRE)
}

export const agreger = (consos: Conso[]) => {
  const parProjet = new Map<string, number>()
  const lignes: Ligne[] = []
  for (const c of consos) {
    const projet = c.project_name ?? c.project_id?.slice(0, 8) ?? '?'
    const montant = eur(c.value)
    parProjet.set(projet, (parProjet.get(projet) ?? 0) + montant)
    lignes.push({ projet, produit: c.product_name ?? '?', eur: montant })
  }
  return {
    moisEur: lignes.reduce((s, l) => s + l.eur, 0),
    parProjet: [...parProjet].map(([projet, eur]) => ({ projet, eur })).sort((a, b) => b.eur - a.eur),
    top: lignes.sort((a, b) => b.eur - a.eur).slice(0, 5),
  }
}

// Base du jour : dernier relevé de la veille (même période), 0 le 1er du mois, sinon premier relevé du jour.
type Releve = { date: string; periode: string; eur: number }
export const baseDuJour = (date: string, periode: string, total: number, dernier: Releve | null, heure: string) => {
  if (date.endsWith('-01')) return { eur: 0, depuis: '00:00' }
  const veille = new Date(`${date}T00:00:00Z`)
  veille.setUTCDate(veille.getUTCDate() - 1)
  if (dernier && dernier.periode === periode && dernier.date === veille.toISOString().slice(0, 10))
    return { eur: dernier.eur, depuis: '00:00' }
  return { eur: total, depuis: heure }
}

export const periodesPrecedentes = (periode: string, n: number) => {
  const [a, m] = periode.split('-').map(Number) as [number, number]
  return Array.from({ length: n }, (_, i) => {
    const d = new Date(Date.UTC(a, m - 1 - (n - 1 - i), 1))
    return d.toISOString().slice(0, 7)
  })
}

// Barre horizontale en huitièmes de cellule.
const HUITIEMES = ['', '▏', '▎', '▍', '▌', '▋', '▊', '▉']
export const barre = (valeur: number, max: number, largeur: number) => {
  if (max <= 0 || valeur <= 0) return ''
  const h = Math.max(1, Math.round((valeur / max) * largeur * 8))
  return '█'.repeat(Math.floor(h / 8)) + HUITIEMES[h % 8]
}

// Barre empilée : cellules entières réparties au plus fort reste, au moins une cellule par segment non nul.
export const empiler = (valeurs: number[], max: number, largeur: number) => {
  const total = valeurs.reduce((s, v) => s + v, 0)
  if (max <= 0 || total <= 0) return valeurs.map(() => 0)
  const cellules = Math.max(1, Math.round((total / max) * largeur))
  const brut = valeurs.map(v => (v / total) * cellules)
  const parts = brut.map((b, i) => ((valeurs[i] ?? 0) > 0 ? Math.max(1, Math.floor(b)) : 0))
  let reste = cellules - parts.reduce((s, p) => s + p, 0)
  const ordre = brut.map((b, i) => [b - Math.floor(b), i] as const).sort((x, y) => y[0] - x[0])
  for (const [, i] of ordre) {
    if (reste <= 0) break
    if ((valeurs[i] ?? 0) > 0) {
      parts[i] = (parts[i] ?? 0) + 1
      reste--
    }
  }
  return parts
}

const f = (n: number) => `${n.toFixed(2).replace('.', ',')} €`
const nomMois = (periode: string) => NOMS_MOIS[Number(periode.slice(5, 7)) - 1] ?? periode

// Avec repertoire_direnv : actif seulement dans ce dossier (clé du .envrc), panneau ouvert au démarrage.
// Sans : actif partout avec le profil scw par défaut, panneau ouvert par /finops seulement.
// Un module n'a qu'un hook session.start : celui de register.tsx appelle demarrerFinops.
let actif = false
let repertoire = ''
let projets: string[] = []
let rafraichir: () => Promise<void> = async () => {}

export async function demarrerFinops($: EngineInterface, options: PluginOptions) {
  const o = lireOptions(options, (await $.env.get('HOME')) ?? '')
  repertoire = o.repertoire
  projets = o.projets
  actif = dansRepertoire(await $.session.root(), repertoire)
  await $.command.register({ name: 'finops', description: 'Ouvre le panneau FinOps Scaleway et le rafraîchit' })
  if (!actif) return

  const scw = async (args: string[]) => {
    const r = await $.process.run(commandeScw(args, repertoire, o.organisation), { timeoutMs: 60_000 })
    if (r.exitCode !== 0) throw new Error(r.stderr.split('\n').find(l => l.trim()) ?? `exit ${r.exitCode}`)
    return JSON.parse(r.stdout) as unknown
  }

  rafraichir = async () => {
    const now = new Date()
    const date = now.toISOString().slice(0, 10)
    const periode = date.slice(0, 7)
    const heure = now.toISOString().slice(11, 16)
    try {
      const periodes = periodesPrecedentes(periode, 3)
      const consos = await Promise.all(
        periodes.map(p => scw(['billing', 'consumption', 'list', `billing-period=${p}`]) as Promise<Conso[]>),
      )
      const historique: Mois[] = periodes.map((p, i) => {
        const a = agreger(consos[i] ?? [])
        return { periode: p, total: a.moisEur, parProjet: Object.fromEntries(a.parProjet.map(x => [x.projet, x.eur])) }
      })
      const agg = agreger(consos[2] ?? [])
      const budget = ((await scw(['billing', 'budget', 'list']).catch(() => [])) as { consumption_limit: Montant }[])[0]

      const cle = `base:${date}`
      let base = (await $.store.get(cle)) as { eur: number; depuis: string } | undefined
      if (!base) {
        base = baseDuJour(date, periode, agg.moisEur, ((await $.store.get('dernier')) as Releve) ?? null, heure)
        await $.store.set(cle, base)
      }
      await $.store.set('dernier', { date, periode, eur: agg.moisEur } satisfies Releve)

      await update($, rapport, () => ({
        periode,
        majA: `${heure} UTC`,
        moisEur: agg.moisEur,
        jourEur: agg.moisEur - base.eur,
        jourDepuis: base.depuis,
        budgetEur: budget ? eur(budget.consumption_limit) : null,
        parProjet: agg.parProjet,
        top: agg.top,
        historique,
      }))
      await update($, erreur, () => null)
      $.ui.status(`FinOps : ${f(agg.moisEur - base.eur)} aujourd'hui · ${f(agg.moisEur)} en ${nomMois(periode)}`)
    } catch (err) {
      await update($, erreur, () => `${heure} UTC : ${err instanceof Error ? err.message : String(err)}`)
    }
  }

  if (repertoire) void $.ui.open({ id: PANE, title: 'FinOps Scaleway' })
  void rafraichir()
  $.clock.every(PERIODE_MS, () => void rafraichir())
}

export function registerFinops(on: Parameters<Register>[0], options: PluginOptions) {
  on('command.run', { command: 'finops' }, async $ => {
    if (!actif) {
      const o = lireOptions(options, (await $.env.get('HOME')) ?? '')
      return { text: `FinOps : réservé au dossier ${o.repertoire} (option repertoire_direnv).` }
    }
    await $.ui.open({ id: PANE, title: 'FinOps Scaleway' })
    await rafraichir()
    return { text: 'Panneau FinOps rafraîchi.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const r = await read($, rapport)
    const err = await read($, erreur)
    if (!r)
      return (
        <Box flexDirection="column" paddingX={1}>
          <Text dimColor>{err ?? 'Lecture de la facturation…'}</Text>
        </Box>
      )

    const largeur = Math.max(10, Math.min(40, (e.viewport?.columns ?? 48) - 22))
    const titre = (t: string) => (
      <Box marginTop={1}>
        <Text bold>{t}</Text>
      </Box>
    )

    // Jauge de budget : statut en couleur + icône + libellé, jamais la couleur seule.
    const pct = r.budgetEur ? (r.moisEur / r.budgetEur) * 100 : null
    const statut =
      pct === null
        ? null
        : pct >= 100
          ? ['✖ dépassé', STATUT.critique]
          : pct >= 80
            ? ['⚠ proche', STATUT.alerte]
            : ['✓ ok', STATUT.bon]
    const jaugeLargeur = largeur + 8
    const plein = pct === null ? 0 : Math.min(jaugeLargeur, Math.round((pct / 100) * jaugeLargeur))

    // Historique : barres empilées par projet, même échelle pour les trois mois.
    const maxMois = Math.max(...r.historique.map(m => m.total), 0.01)
    const projetsVus = [...new Set(r.historique.flatMap(m => Object.keys(m.parProjet)))].sort(
      (a, b) => ((projets.indexOf(a) + 99) % 99) - ((projets.indexOf(b) + 99) % 99),
    )
    const maxProjet = Math.max(...r.parProjet.map(p => p.eur), 0.01)

    return (
      <Box flexDirection="column" paddingX={1}>
        <Box justifyContent="space-between">
          <Text bold>FinOps · Scaleway</Text>
          <Text dimColor>{r.majA}</Text>
        </Box>

        <Box marginTop={1} gap={2}>
          <Box flexDirection="column" borderStyle="round" paddingX={1}>
            <Text dimColor>Aujourd'hui</Text>
            <Text bold>{r.jourEur === null ? 'n/a' : f(r.jourEur)}</Text>
            <Text dimColor>depuis {r.jourDepuis}</Text>
          </Box>
          <Box flexDirection="column" borderStyle="round" paddingX={1}>
            <Text dimColor>{nomMois(r.periode)} à date</Text>
            <Text bold>{f(r.moisEur)}</Text>
            <Text dimColor>
              {r.historique.length > 1
                ? `${nomMois(r.historique[1]?.periode ?? '')} : ${f(r.historique[1]?.total ?? 0)}`
                : ''}
            </Text>
          </Box>
        </Box>

        {r.budgetEur !== null && statut && (
          <Box flexDirection="column" marginTop={1}>
            <Box justifyContent="space-between">
              <Text dimColor>Budget {f(r.budgetEur)}</Text>
              <Text>
                <Text color={statut[1]}>{statut[0]}</Text> {Math.round(pct ?? 0)} %
              </Text>
            </Box>
            <Text>
              <Text color={statut[1]}>{'█'.repeat(plein)}</Text>
              <Text dimColor>{'░'.repeat(Math.max(0, jaugeLargeur - plein))}</Text>
            </Text>
          </Box>
        )}

        {titre('Trois derniers mois')}
        {r.historique.map(m => {
          const vals = projetsVus.map(p => m.parProjet[p] ?? 0)
          const parts = empiler(vals, maxMois, largeur)
          const courant = m.periode === r.periode
          return (
            <Box>
              <Box width={7}>
                <Text bold={courant} dimColor={!courant}>
                  {nomMois(m.periode)}
                </Text>
              </Box>
              <Text>
                {projetsVus.map((p, i) => (
                  <Text color={teinte(p, projets)}>{'█'.repeat(parts[i] ?? 0)}</Text>
                ))}
                {m.total <= 0 ? <Text dimColor>·</Text> : ''}
              </Text>
              <Text bold={courant}> {f(m.total)}</Text>
              {courant && <Text dimColor> en cours</Text>}
            </Box>
          )
        })}
        <Box flexWrap="wrap" columnGap={2}>
          {projetsVus.map(p => (
            <Text>
              <Text color={teinte(p, projets)}>■</Text> <Text dimColor>{p}</Text>
            </Text>
          ))}
        </Box>

        {titre(`${nomMois(r.periode)} par projet`)}
        {r.parProjet.map(p => (
          <Box>
            <Box width={12}>
              <Text wrap="truncate">{p.projet}</Text>
            </Box>
            <Text color={teinte(p.projet, projets)}>{barre(p.eur, maxProjet, largeur - 2)}</Text>
            <Text> {f(p.eur)}</Text>
          </Box>
        ))}

        {titre('Premiers postes')}
        {r.top.map(l => (
          <Box>
            <Box width={10}>
              <Text>{f(l.eur)}</Text>
            </Box>
            <Text color={teinte(l.projet, projets)}>■ </Text>
            <Text wrap="truncate">{l.produit}</Text>
          </Box>
        ))}

        <Box marginTop={1}>
          <Text dimColor>toutes les heures · /finops pour rafraîchir</Text>
        </Box>
        {err && <Text color={STATUT.critique}>✖ {err}</Text>}
      </Box>
    )
  })
}
