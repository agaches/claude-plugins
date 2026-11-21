# archi-docs

Documentation d'architecture avec Claude : ADR aujourd'hui, DAT à venir.

Les modèles ne sont pas dans le plugin : ils viennent d'un repo de modèles, par défaut
[agaches/adr](https://github.com/agaches/adr), ou du vôtre, et sont copiés dans le projet au premier
usage (`docs/adr/modeles/`). Toute l'équipe écrit avec les mêmes modèles, visibles en revue.

## Prérequis

- Claude Code, `git`, Python 3 (le script n'utilise que la bibliothèque standard).
- Accès réseau à github.com pour copier les modèles depuis un repo GitHub.
- Repo de modèles privé : `GH_TOKEN` défini (par exemple `GH_TOKEN=$(gh auth token)`).

## Installation

```
/plugin marketplace add agaches/claude-plugins
/plugin install archi-docs@agaches
```

## Usage

| Skill | Rôle |
|---|---|
| `/adr` | ADR dans `docs/adr/NNN-<sujet>.md`, modèle choisi selon la décision ; numérotation, statut et remplacement gérés |

1. Premier `/adr` dans un projet : Claude propose la source des modèles (`agaches/adr`, un autre
   repo `owner/repo[@ref]`, ou un dossier local), les copie dans `docs/adr/modeles/` et y écrit
   `SOURCE.md` : source, commit, date, et un tableau « quand utiliser chaque modèle » que vous
   validez.
2. Ensuite : décrivez la décision, Claude choisit le modèle, rédige `docs/adr/NNN-<sujet>.md`, vous
   relisez, il committe.
3. « Mets à jour les modèles ADR » : nouvelle copie depuis la source, tableau conservé, diff à
   relire.

Le script se lance aussi seul, depuis un clone de ce repo :

```
python3 plugins/archi-docs/scripts/recuperer_modeles.py agaches/adr docs/adr/modeles
python3 plugins/archi-docs/scripts/recuperer_modeles.py mon-org/mes-modeles@v2 docs/adr/modeles --maj
```

Il copie les `*.md` à la racine de la source, sauf `README*` et `exemple*`.

## Exemple

```
> fais une ADR : on garde PostgreSQL plutôt que MongoDB pour les commandes, c'est tranché
Modèles absents : je propose agaches/adr (copie dans docs/adr/modeles/). On y va ?
> oui
[copie, tableau d'usage validé]
Modèle avancé (deux options sérieuses). docs/adr/001-postgresql-pour-les-commandes.md, statut accepté.
```

## À venir

- Skill `dat` : dossier d'architecture technique depuis [agaches/dat](https://github.com/agaches/dat),
  avec un modèle LikeC4 et ses vues fonctionnelle, solution et technique.
