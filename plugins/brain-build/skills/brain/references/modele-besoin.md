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

## Réglages

Valeurs qu'on ajustera à l'usage. Les critères les citent par leur nom ; elles ne sont pas des `REQ`.

| Nom | Valeur | Unité | Note |
|---|---|---|---|
| <vitesse_ennemi> | <120> | <px/s> | <à régler après un essai> |

## Contraintes

- <technique imposée, plateforme, performance avec seuil, licence, données>
- <ce qui n'existe que pour la recette : état exposé, API de test>

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
| Critère : l'ennemi part quand le joueur est à moins de 300 px | Critère : l'ennemi part quand le joueur entre dans sa portée (`portee_ennemi`, Réglages) |
| Critère : passe à moins de 40 px pour au moins 15 graines sur 20 | Critère : l'ennemi se dirige vers la position du joueur au moment du départ |

`trace.py check` signale (sans bloquer) les constantes d'un critère absentes de `## Réglages`, hors
littéraux entre backticks, et les critères probabilistes : à confirmer comme contrainte ferme ou à
déplacer.

## Nouvelle version

Les `REQ` existantes gardent leur id. Une `REQ` modifiée garde son id et change de texte (le delta
se lit par `git diff`). Une `REQ` abandonnée quitte la rubrique Exigences pour une rubrique
`## Abandonnées` (une puce `REQ-xxx : <titre>, ADR-xxx`, sans titre `###`) : son id n'est jamais
réutilisé et elle n'est plus construite.
