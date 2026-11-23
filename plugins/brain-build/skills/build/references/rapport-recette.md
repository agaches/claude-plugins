# Rapport de recette

Fichier `docs/recette/<AAAA-MM-JJ>-<sujet>.md`, committé sur la branche d'intégration. Il doit se
lire en quelques minutes : l'utilisateur décide de la recette à partir de lui seul.

Ordre imposé :

```markdown
# Recette : <sujet> (<date>)

PR : <lien> · Départ : <branche> @ <sha> · Intégration : build/<sujet> @ <sha>

## 1. À décider par vous

- **REQ-00x : <question de besoin>** (mise de côté avec : SPEC-…, ACT-…)
  Options : a) … b) … · Ce que ça change : …
- **REQ-00y bloquée** après 3 cycles diagnostic → correction : <cause, dernier état>
- **REQ-00z à vérifier par vous** (rendu, ressenti) : <ce qu'il faut regarder, comment le lancer>

(« Rien à décider. » si vide.)

## 2. Matrice

<sortie de `trace.py matrix . --tests <tests_dir> --proves docs/build/runs/proves.json`>

Contrôles : check ✅/❌ · guard ✅/❌ · proves ✅/❌ · audit ✅/❌ · non-régression (`test_cmd`) ✅/❌

Vérifications sur la pile réelle :

| REQ | Commande | Résultat |
|---|---|---|

## 3. Specs modifiées pendant la construction

| Spec | Pourquoi | Diagnostic d'origine |
|---|---|---|

## 4. Incidents

| Quand | Agent | Incident | Cause désignée | Suite |
|---|---|---|---|---|

Y figurent aussi les avertissements de `trace.py check` et les fuites d'indépendance de
`trace.py audit` (run, outil, cible, cas relus).

## 5. Relecture de la PR par le pilote

<avis en quelques lignes : conforme / écarts relevés, fichiers hors périmètre, points à regarder>

## 6. Coûts

<sortie de `trace.py cost docs/build/runs` : par rôle (lancements, reprises, coût, modèles) et par
action>

Modèles : <alias → identifiant, d'après la config> · Pilote : <modèle, coût estimé ou « non mesuré »>
```

Règles :

- Pas de résumé narratif du déroulé : ce qui compte est dans les sections ci-dessus.
- Chaque ligne cite ses ids (`REQ`, `SPEC`, `ACT`) pour que l'utilisateur retrouve les fichiers.
- Une section vide s'écrit « Aucun. », elle ne disparaît pas.
