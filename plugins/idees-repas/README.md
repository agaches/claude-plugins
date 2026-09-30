# idees-repas

« C'est quoi qu'on mange ? »

Comme beaucoup de familles, nous sommes un couple où les deux travaillent. En rentrant, cette
question fâche. Alors on a pris l'habitude de poser les menus de la semaine : plus de question
le soir, des courses au strict nécessaire, moins de gâchis.

Sauf qu'une autre question arrive, chaque semaine : « bon, il faut trouver 14 idées de repas,
tu as des idées ? ». On aime cuisiner, mais pas tous les soirs. Il faut composer avec le
télétravail, les midis à la maison ou non, la saison.

Cette skill répond à ces deux questions depuis l'app Claude sur le téléphone. Elle pioche dans
un vivier d'environ 600 plats, filtre selon la saison, l'envie et le temps disponible, et
propose des idées pour ce soir ou pour toute la semaine. Les plats au four sont repérés : 5 minutes
de préparation, le four travaille, et c'est prêt (et ça reste chaud).

## Usage

Exemples de demandes :

- « On mange quoi ce soir ? »
- « Une idée avec du poulet, au four »
- « 3 idées de dessert »
- « Les repas de la semaine : télétravail mardi et jeudi, on mange dehors samedi soir »

## Installation

Claude Code :

```
/plugin marketplace add agaches/claude-plugins
/plugin install idees-repas@agaches
```

App Claude (web ou mobile) : zipper le dossier `skills/idees-repas/`, puis sur claude.ai
« + » → « Create skill » → importer le zip. La skill est ensuite disponible dans l'app mobile.

```
cd plugins/idees-repas/skills && python3 -m zipfile -c idees-repas.zip idees-repas
```

## Prérequis

Aucun. Pas de connecteur, pas de dépendance.

## Personnaliser avec vos plats

Le vivier est `skills/idees-repas/references/plats.md`, un simple tableau Markdown :

```
| Nom | Catégorie | Cuisson | Source | Ingrédients clés |
|---|---|---|---|---|
| Gratin de courgettes | Légumes | Four | Perso | courgettes, gruyère |
```

Ajoutez vos plats de famille, retirez ceux que vous n'aimez pas : une ligne par plat, rien
d'autre à modifier.

## Sources

Le vivier cite, pour chaque plat tiré d'un livre, le livre et la page. Pour le cuisiner, il faut
le livre. Ils le valent bien.

| Livre | Éditeur | ISBN |
|---|---|---|
| *Mes 300 recettes*, Companion XL | Moulinex | 978-2-37247-062-9 |
| *Simplissime, Enfournez et c'est prêt !!!*, Jean-François Mallet | Hachette Pratique | 978-2-01-946242-0 |
| *Simplissime, Les recettes asiatiques les + faciles du monde*, Jean-François Mallet | Hachette Pratique | 978-2-01-716846-1 (éd. 2021) |

Calendrier de saison : [Que Choisir](https://www.quechoisir.org/conseils-alimentation-le-calendrier-des-fruits-et-legumes-de-saison-n51036/),
d'après les données ADEME.
