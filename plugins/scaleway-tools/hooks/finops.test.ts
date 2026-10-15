import { expect, test } from 'claude-code/testing'

import {
  agreger,
  barre,
  baseDuJour,
  commandeScw,
  dansRepertoire,
  empiler,
  eur,
  lireOptions,
  periodesPrecedentes,
  teinte,
} from './finops'

test('options, dossier et commande scw', async () => {
  const o = lireOptions({ repertoire_direnv: '~/infra/ ', organisation_id: 'org-1', projets: 'web, api,,' }, '/home/u')
  expect(o).toEqual({ repertoire: '/home/u/infra', organisation: 'org-1', projets: ['web', 'api'] })
  expect(lireOptions({}, '/home/u')).toEqual({ repertoire: '', organisation: '', projets: [] })
  expect(dansRepertoire('/home/u/infra/sous', '/home/u/infra')).toBe(true)
  expect(dansRepertoire('/home/u/infra2', '/home/u/infra')).toBe(false)
  expect(dansRepertoire('/ailleurs', '')).toBe(true)
  expect(commandeScw(['billing', 'budget', 'list'], '/r', 'org-1')).toEqual([
    'direnv', 'exec', '/r', 'scw', 'billing', 'budget', 'list', 'organization-id=org-1', '-o', 'json',
  ])
  expect(commandeScw(['billing', 'budget', 'list'], '', '')).toEqual(['scw', 'billing', 'budget', 'list', '-o', 'json'])
})

test('montants et agrégation par projet', async () => {
  expect(eur({ units: 2, nanos: 180000000 })).toBe(2.18)
  const a = agreger([
    { value: { units: 13, nanos: 110000000 }, project_name: 'web', product_name: 'Domains Transfer' },
    { value: { units: 2, nanos: 180000000 }, project_name: 'api', product_name: 'VPC Peering' },
    { value: { units: 0, nanos: 260000000 }, project_name: 'api', product_name: 'VPC Public Gateway S' },
  ])
  expect(Math.round(a.moisEur * 100)).toBe(1555)
  expect(a.parProjet[0]?.projet).toBe('web')
  expect(Math.round((a.parProjet[1]?.eur ?? 0) * 100)).toBe(244)
  expect(a.top[0]?.produit).toBe('Domains Transfer')
})

test('base du jour', async () => {
  expect(baseDuJour('2026-10-01', '2026-10', 5, null, '09:00')).toEqual({ eur: 0, depuis: '00:00' })
  const veille = { date: '2026-10-05', periode: '2026-10', eur: 21.42 }
  expect(baseDuJour('2026-10-06', '2026-10', 23, veille, '08:00')).toEqual({ eur: 21.42, depuis: '00:00' })
  expect(baseDuJour('2026-10-07', '2026-10', 25, veille, '08:00')).toEqual({ eur: 25, depuis: '08:00' })
  expect(baseDuJour('2026-10-06', '2026-10', 23, null, '08:00')).toEqual({ eur: 23, depuis: '08:00' })
})

test('historique, barres et couleurs', async () => {
  expect(periodesPrecedentes('2026-10', 3)).toEqual(['2026-08', '2026-09', '2026-10'])
  expect(periodesPrecedentes('2026-01', 3)).toEqual(['2025-11', '2025-12', '2026-01'])
  expect(barre(10, 10, 4)).toBe('████')
  expect(barre(5, 10, 3)).toBe('█▌')
  expect(barre(0, 10, 4)).toBe('')
  const parts = empiler([13.14, 5.66, 2.58, 0.03], 21.42, 20)
  expect(parts.reduce((s, p) => s + p, 0)).toBe(20)
  expect(parts[3]).toBe(1)
  expect(empiler([1.36, 0.4], 21.42, 20).reduce((s, p) => s + p, 0)).toBe(2)
  expect(teinte('api', ['web', 'api'])).toBe('#d95926')
  expect(teinte('inconnu', ['web', 'api'])).toBe('#9085e9')
})

test('/finops hors du dossier configuré', { options: { repertoire_direnv: '~/infra' } }, async ($, on) => {
  on('env.get', () => ({ value: '/home/u' }))
  const { text } = await $.command.run({ command: 'finops', args: '' })
  expect(text).toContain('réservé au dossier /home/u/infra')
})
