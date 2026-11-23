# Modèle de `docs/besoin.md`

Le format des exigences est lu par `trace.py` : un titre `### REQ-xxx : …` par exigence (3
chiffres), suivi d'au moins une ligne qui commence par `Critère :`.

```markdown
# Besoin : <nom du produit>

Version : <n> · Date : <AAAA-MM-JJ>

## Contexte

<pour qui, quel problème, situation actuelle ; quelques lignes>

## Objectifs

- <résultat attendu, mesurable si possible>

## Non-objectifs

- <ce qu'on ne fait pas dans cette version>

## Anti-objectifs

- <ce qui serait un échec même si ça marche (usine à gaz, coût, dépendance…)>

## Exigences

### REQ-001 : <comportement, en une phrase>
<précisions utiles : règles, cas limites>
Critère : <entrée> → <action> → <résultat observable exact>
Critère : <autre cas, si besoin>

### REQ-002 : <…>
Critère : <…>

## Contraintes

- <technique imposée, plateforme, performance avec seuil, licence, données>

## Décisions

<vide si les décisions sont dans `docs/adr/`. Sinon, une puce par décision : date, contexte,
choix, raison.>

## Références

- Glossaire : `GLOSSARY.md`
- Décisions : `docs/adr/` ou section Décisions ci-dessous
- <documents, maquettes, exemples>
```

## Exemple de critère

| Mauvais | Bon |
|---|---|
| Critère : l'outil est rapide | Critère : `wc.py` sur un fichier de 10 Mo répond en moins de 2 s |
| Critère : gérer les erreurs | Critère : `wc.py absent.txt` affiche `introuvable` et sort en code 2 |

## Nouvelle version

Les `REQ` existantes gardent leur id. Une `REQ` modifiée garde son id et change de texte (le delta
se lit par `git diff`). Une `REQ` abandonnée quitte la rubrique Exigences pour une rubrique
`## Abandonnées` (une puce `REQ-xxx : <titre>, ADR-xxx`, sans titre `###`) : son id n'est jamais
réutilisé et elle n'est plus construite.
