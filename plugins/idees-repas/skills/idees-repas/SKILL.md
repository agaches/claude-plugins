---
name: idees-repas
description: Propose des idées de plats et de repas tirées d'un répertoire familial (~600 plats), en tenant compte de la saison, du temps disponible et des présences. À utiliser dès que l'utilisateur demande une idée de repas, de plat, de dessert ou d'entrée, ou les idées de menu de la semaine ("on mange quoi ce soir ?", "une idée avec du poulet", "un truc rapide au four", "idée de dessert", "14 idées pour la semaine", "donne-moi les repas de la semaine, je suis en télétravail mardi et jeudi").
---

# Idées de repas

Répertoire de plats de la famille. Le but : donner vite des idées pertinentes, pour ce soir ou
pour la semaine, sans avoir à y réfléchir.

## Fichiers

| Fichier | Contenu | Quand le lire |
|---|---|---|
| `references/plats.md` | ~600 plats : Nom, Catégorie, Cuisson (`Four` / `Poêle` / `Sans cuisson` / `Autre`), Source (`<Livre> p.<page>` ou `Perso`), ingrédients clés parfois ; en tête, la liste des livres cités avec leur ISBN | Toujours, c'est le vivier |
| `references/saisonnalite.md` | Fruits et légumes frais par mois (France) | Dès qu'un plat repose sur un produit frais |

## Comment répondre

1. Lire `references/plats.md` et filtrer selon la demande : ingrédient, type de plat, envie
   (léger, réconfortant, rapide, enfants, végétarien, asiatique…), cuisson.
2. Écarter les plats dont le produit frais principal est hors saison pour le mois courant
   (`references/saisonnalite.md`). Riz, pâtes, viande, poisson, surgelés, conserves et fruits
   exotiques ne sont pas concernés.
3. Proposer **exactement le nombre d'idées demandé** (« 10 idées », « 2 repas » → 10, 2), à
   défaut 3 à 5. Varier protéines, types de plats et cuissons (pas cinq variantes du même plat).
   Critères fréquents :
   - « chaud » = cuisson autre que `Sans cuisson` ;
   - « au four », « je n'ai pas le temps de surveiller » = `Four` : on enfourne, le four fait
     le reste, le plat reste chaud ;
   - « léger » ou « midi » = estimé d'après le nom et la catégorie (salades, crudités, soupes,
     poisson, bols…), aucune donnée calorique n'existe.
   Une ligne par idée : nom du plat · source (`Livre p.X`, ou « perso ») · un mot sur
   pourquoi il colle à la demande si ce n'est pas évident. Si une page est inconnue, écrire `p.?`,
   ne jamais inventer un numéro.
4. Si l'utilisateur veut un repas complet, suggérer entrée/crudités et dessert pris aussi dans
   le vivier (catégories Crudités, Entrées, Desserts…).

## Idées pour la semaine

Demande du type « les repas de la semaine », « 14 idées » :

- Compter les repas à prévoir : 7 soirs, plus les midis où quelqu'un mange à la maison
  (télétravail, week-end). Si l'utilisateur donne les présences, les appliquer ; sinon
  proposer 14 idées (midi et soir) et le signaler en une ligne.
- Midis de semaine : plats rapides ou légers. Soirs de semaine : de préférence `Four` ou rapides.
  Plats longs ou mijotés : week-end.
- Pas deux fois la même protéine d'affilée, au moins un soir poisson et un soir végétarien.
- Présenter par jour, une ligne par repas avec sa source : `Lundi soir : gratin de… · Simplissime au four p.42`.
- Liste de courses seulement si elle est demandée : regrouper par rayon, sans quantités
  inventées (le vivier n'en contient pas).

## Style

- Réponses courtes, lisibles sur téléphone : liste simple, pas de tableau large.
- Si la demande est vague (« une idée pour ce soir »), proposer directement des idées variées
  plutôt que poser des questions.
