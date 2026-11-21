---
name: adr
description: Rédige une ADR (Architecture Decision Record) dans docs/adr/ à partir des modèles du projet (docs/adr/modeles/, copiés au premier usage depuis agaches/adr ou le repo de modèles de l'utilisateur). À utiliser quand une décision mérite d'être consignée (« fais une ADR », « consigne cette décision », « on garde une trace de ce choix »), quand une décision structurante tombe pendant un cadrage ou un build, ou pour « mettre à jour les modèles ADR ».
---

# ADR

Une ADR garde la trace d'une décision : son contexte, les options, le choix et ses conséquences.
Elle se lit des mois plus tard par quelqu'un qui n'était pas là.

## Quand en écrire une

Quand la décision **engage** (coûteuse à défaire) **et** qu'il y avait un vrai choix entre des
options. Une préférence de détail ou une évidence ne fait pas une ADR : elle va dans le besoin,
une spec ou le glossaire.

## Premier usage dans un projet

Les modèles vivent dans le projet, `docs/adr/modeles/`, versionnés avec lui : toute l'équipe écrit
avec les mêmes. Si `docs/adr/modeles/SOURCE.md` est absent :

1. Proposer la source des modèles : `agaches/adr` (défaut), un autre repo GitHub
   (`owner/repo`, `owner/repo@ref` ou son URL), ou un dossier local. Expliquer en une ligne que les
   modèles seront copiés dans `docs/adr/modeles/`.
2. Accord → lancer, depuis la racine du projet, le script fourni avec ce plugin (chemin relatif au
   dossier de cette skill) :

   ```
   python3 <dossier de la skill>/../../scripts/recuperer_modeles.py <source> docs/adr/modeles
   ```

   Repo privé : le script utilise `GH_TOKEN` s'il est défini (par exemple `GH_TOKEN=$(gh auth token)`).
3. Lire les modèles copiés et compléter la section « Quand utiliser chaque modèle » de
   `SOURCE.md` : un tableau `| Modèle | Quand | Fichier |`. Pour `agaches/adr` :

   | Modèle | Quand | Fichier |
   |---|---|---|
   | simple (Nygard) | par défaut : une décision claire, peu d'options | `adr_simple.md` |
   | avancé | au moins deux options sérieuses à comparer, avantages et inconvénients | `adr_avance.md` |
   | exhaustif | décision d'architecture de portée application ou plus large, contraintes et risques à détailler | `adr_exhaustif.md` |

   Pour d'autres modèles, déduire le tableau de leur contenu. Faire valider le tableau, puis
   committer `docs/adr/modeles/` (`docs(adr): modèles ADR depuis <source>`).
4. Refus → s'arrêter sans rien écrire.

## Quel modèle

Choisir dans le tableau de `docs/adr/modeles/SOURCE.md`. Annoncer le modèle choisi en une ligne ;
l'utilisateur peut en demander un autre.

## Rédiger

1. Numéro : le suivant dans `docs/adr/` (3 chiffres, `001` si aucune ADR). Fichier
   `docs/adr/NNN-<sujet-en-kebab-case>.md`, titre `ADR-NNN : <titre>`.
2. Remplir le modèle avec ce qui a été dit et décidé, sans inventer : une rubrique sans matière
   s'écrit « non renseigné », une rubrique optionnelle sans matière se retire.
3. Statut : `proposé` tant que l'utilisateur n'a pas tranché, `accepté` quand il a tranché. Date
   du jour, décideurs = les personnes nommées par l'utilisateur.
4. Relier : citer les ADR concernées par leur id ; si le projet a des exigences ou des specs
   numérotées (`REQ-xxx`, `SPEC-xxx`), citer aussi leurs ids.
5. Faire relire, puis committer (`docs(adr): ADR-NNN <titre>`).

## Changer d'avis

Une ADR acceptée ne se réécrit pas. Une nouvelle ADR la remplace : la nouvelle cite
`Remplace ADR-NNN`, l'ancienne passe au statut `remplacée par ADR-MMM` (seule modification
permise sur l'ancienne).

## Mettre à jour les modèles

« Mets à jour les modèles ADR » → relancer le script avec la source de `SOURCE.md` et `--maj` :

```
python3 <dossier de la skill>/../../scripts/recuperer_modeles.py <source> docs/adr/modeles --maj
```

Le script réécrit les modèles, garde le tableau « Quand utiliser chaque modèle » et liste les
fichiers modifiés ou retirés de la source. Montrer le diff git à l'utilisateur ; adapter le
tableau si un modèle a changé de rôle. Les ADR déjà écrites ne changent pas.
