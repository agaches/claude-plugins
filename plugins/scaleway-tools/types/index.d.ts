export type Ligne = { projet: string; produit: string; eur: number }

export type Mois = { periode: string; total: number; parProjet: Record<string, number> }

export type Rapport = {
  periode: string
  majA: string
  moisEur: number
  jourEur: number | null
  jourDepuis: string
  budgetEur: number | null
  parProjet: { projet: string; eur: number }[]
  top: Ligne[]
  historique: Mois[]
}

declare module 'claude-code' {
  interface PluginState {
    'scaleway-tools': { rapport: Rapport | null; erreur: string | null }
  }
}
