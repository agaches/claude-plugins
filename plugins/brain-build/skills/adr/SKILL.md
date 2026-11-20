---
name: adr
description: Rédige une ADR (Architecture Decision Record) dans docs/adr/ à partir des modèles de référence (simple, avancé, exhaustif). À utiliser quand une décision mérite d'être consignée (« fais une ADR », « consigne cette décision », « on garde une trace de ce choix »), pendant /brain quand une décision structurante tombe, ou dans /build quand l'utilisateur tranche une question de besoin.
---

# ADR

Une ADR garde la trace d'une décision : son contexte, les options, le choix et ses conséquences.
Elle se lit des mois plus tard par quelqu'un qui n'était pas là.

## Quand en écrire une

Quand la décision **engage** (coûteuse à défaire) **et** qu'il y avait un vrai choix entre des
options. Une préférence de détail ou une évidence ne fait pas une ADR : elle va dans le besoin,
une spec ou le glossaire.

## Quel modèle

| Modèle | Quand | Fichier |
|---|---|---|
| simple (Nygard) | par défaut : une décision claire, peu d'options | `references/adr_simple.md` |
| avancé | au moins deux options sérieuses à comparer, avantages et inconvénients | `references/adr_avance.md` |
| exhaustif | décision d'architecture de portée application ou plus large, contraintes et risques à détailler | `references/adr_exhaustif.md` |

Annoncer le modèle choisi en une ligne ; l'utilisateur peut en demander un autre.

## Rédiger

1. Numéro : le suivant dans `docs/adr/` (3 chiffres, `001` si le dossier est vide ou absent).
   Fichier `docs/adr/NNN-<sujet-en-kebab-case>.md`, titre `ADR-NNN : <titre>`.
2. Remplir le modèle avec ce qui a été dit et décidé, sans inventer : une rubrique sans matière
   s'écrit « non renseigné », une rubrique optionnelle sans matière se retire.
3. Statut : `proposé` tant que l'utilisateur n'a pas tranché, `accepté` quand il a tranché. Date
   du jour, décideurs = les personnes nommées par l'utilisateur.
4. Relier : citer les `REQ`, `SPEC` ou ADR concernées par leur id.
5. Faire relire, puis committer (`docs(adr): ADR-NNN <titre>`).

## Changer d'avis

Une ADR acceptée ne se réécrit pas. Une nouvelle ADR la remplace : la nouvelle cite
`Remplace ADR-NNN`, l'ancienne passe au statut `remplacée par ADR-MMM` (seule modification
permise sur l'ancienne).
