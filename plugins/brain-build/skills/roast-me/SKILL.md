---
name: roast-me
description: Relecture critique d'un document par des personas (métier, architecte, chef de projet, test « 12 ans », détecteur de bullshit…) lancés chacun en sous-agent à contexte vierge ; seules les critiques soulevées par au moins deux personas sont retenues. À utiliser quand l'utilisateur demande « roast-me », « démonte ce document », « relecture critique », « fais-le relire par des personas », et avant de figer le besoin dans /brain.
---

# Roast-me

Faire démonter un document par des relecteurs volontairement sévères, pour trouver ses failles
avant qu'elles coûtent. Les prompts des personas sont dans `references/catalogue.md` : les
utiliser tels quels, sans les réécrire.

## Personas

Sélection par défaut pour un besoin ou une spec (sections du catalogue) :

| Persona | Section du catalogue | Ce qu'il attrape |
|---|---|---|
| Cohérence globale | 1. Analyse de Cohérence Globale | contradictions, ruptures, redondances |
| Métier | 3. Le Métier (Utilisateur Final) | besoin réel, gadgets, effort de changement |
| Architecte | 4. L'Architecte Technique Rigoureux | faisabilité, dépendances cachées, simplifications |
| Chef de projet | 4. Le Chef de Projet Terrain | réalisme, dépendances critiques, risques |
| Test « 12 ans » | 5. Le Test "12 ans" (Clarté) | jargon, phrases obscures, schémas manquants |
| Bullshit detector | 5. Le Bullshit Detector avec echelle | promesses vides, affirmations sans preuve, note sur 10 |

Pour un autre type de document (proposition, article), prendre dans le reste du catalogue (DAF,
DSI, Concurrent, Caméléon, kit article). L'utilisateur peut imposer ses personas.

## Déroulé

1. **Choisir** des personas **opposés** : au moins deux, quatre au plus pour garder la relecture
   lisible. Pour un besoin, par défaut : Métier, Architecte, Chef de projet, Bullshit detector.
   Annoncer le choix en une ligne.
2. **Lancer** un sous-agent par persona (outil Agent, `general-purpose`), tous en parallèle. Chacun
   part d'un contexte vierge : son prompt contient seulement le prompt du persona copié du
   catalogue, le chemin du document à lire, et la consigne de ne lire que ce document (ni le
   reste du repo, ni la conversation) et de rendre ses critiques en liste numérotée, chacune avec
   la section visée.
3. **Compiler** : regrouper les critiques qui disent la même chose. Retenir celles soulevées par
   **au moins deux** personas ; le reste est du bruit, compté mais pas détaillé.
4. **Rendre** un tableau court :

   | Ref | Critique retenue | Section | Soulevée par | Proposition |
   |---|---|---|---|---|
   | R1 | … | … | Métier, Architecte | … |

   puis une ligne : `Écartées (une seule voix) : N`, et la note du Bullshit detector s'il a été
   lancé. L'utilisateur peut demander à voir les critiques écartées.

Le document n'est pas modifié par cette skill : les corrections se décident avec l'utilisateur.
