# idees-repas

> « C'est quoi qu'on mange ? »

Skill Claude de la marketplace [agaches/claude-plugins](README.md) : idées de plats et menus de la
semaine, selon la saison, le temps disponible et les présences.

Comme beaucoup de familles, nous sommes un couple où les deux travaillent. En rentrant, cette
question fâche. Alors on a pris l'habitude de poser les menus de la semaine : plus de question le
soir, des courses au strict nécessaire, moins de gâchis.

Sauf qu'une autre question arrive, chaque semaine : « il faut trouver 14 idées de repas, tu as
des idées ? ». On aime cuisiner, mais pas tous les soirs, et il faut composer avec le télétravail
et les midis à la maison.

Cette skill y répond depuis l'app Claude sur le téléphone. Elle pioche dans un vivier d'environ
600 plats, filtre selon la saison, l'envie et le temps disponible, et propose des idées pour ce
soir ou pour toute la semaine. Les plats au four sont repérés : quelques minutes de préparation,
le four travaille, et c'est prêt.

## Installation

**Claude Code**, dans une session :

```
/plugin marketplace add agaches/claude-plugins
/plugin install idees-repas@agaches
```

Ou depuis le terminal :

```
claude plugin marketplace add agaches/claude-plugins
claude plugin install idees-repas@agaches
```

**App Claude (web et mobile)** : télécharger
[idees-repas.zip](https://github.com/agaches/claude-plugins/releases/download/idees-repas-v0.1.1/idees-repas.zip)
(aussi sur la page [Releases](https://github.com/agaches/claude-plugins/releases) du repo), puis
sur claude.ai « + » → « Create skill » → importer le zip. La skill est ensuite disponible dans
l'app mobile.

## Ajouter ou retirer un plat

Le vivier est le tableau `idees-repas/references/plats.md`, une ligne par plat. Exemple : ajouter
le gratin de coquillettes de la maison.

1. Dézipper `idees-repas.zip` et ouvrir `idees-repas/references/plats.md`.
2. Ajouter une ligne à la fin du tableau :

   ```
   | Gratin de coquillettes au jambon | Quiches, tartes, pâtes et riz | Four | Perso | coquillettes, jambon, gruyère |
   ```

   Colonnes : nom, catégorie, cuisson (`Four`, `Poêle`, `Sans cuisson` ou `Autre`), source
   (`Perso` ou `Livre p.X`), ingrédients clés (facultatif).
3. Rezipper le dossier `idees-repas` et l'importer à nouveau sur claude.ai en remplaçant
   l'ancienne skill.

Pour retirer un plat, supprimer sa ligne. Dans Claude Code, faire la même modification dans un
fork du repo et installer le plugin depuis ce fork.

Ensuite : « une idée avec des pâtes au four » peut proposer votre gratin de coquillettes.

## Exemples d'utilisation

*Réponses illustratives, pour une demande faite en octobre.*

**Vous :** On mange quoi ce soir ? Un truc au four, on rentre tard.

> **Claude**
>
> - Poulet coco pesto · *Simplissime au four p.40*
> - Carré de porc à la moutarde · *Simplissime au four p.102*
> - Daurade à la chinoise · *Simplissime au four p.198 · poisson*
> - Gratin pommes de terre-andouille · *Simplissime au four p.68 · réconfortant*

**Vous :** Les repas de la semaine : télétravail mardi et jeudi, on mange dehors samedi soir.

> **Claude**
>
> - Lundi soir : Poireaux au jambon · *Simplissime au four p.62*
> - Mardi midi : Poke bowl (poulet cuit) · *perso*
> - Mardi soir : Bar à la thaïe · *Simplissime au four p.204*
> - Mercredi soir : Fricassée de poulet forestière · *Simplissime au four p.42*
> - Jeudi midi : Velouté de chou-fleur · *Companion XL p.92*
> - Jeudi soir : Lentilles, carottes et épices · *Companion XL p.171 · végétarien*
> - Vendredi soir : Tian au chorizo · *Simplissime au four p.64*
> - Samedi midi : Tortilla épinard/chèvre (quiche sans pâte) · *perso*
> - Dimanche midi : Pommes de terre au confit de canard · *Simplissime au four p.146*
> - Dimanche soir : Quiche bretonne au saumon · *perso*

## Désinstallation

**Claude Code** : retirer le plugin, puis, si vous n'utilisez plus aucun plugin de ce catalogue,
le marketplace lui-même.

```
claude plugin uninstall idees-repas@agaches
claude plugin marketplace remove agaches
```

En session, la commande `/plugin` ouvre le gestionnaire où l'on peut faire la même chose.

**App Claude (web et mobile)** : sur claude.ai, supprimer la skill `idees-repas` de votre liste
de skills. La suppression vaut pour tous vos appareils.

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

---

[github.com/agaches/claude-plugins](https://github.com/agaches/claude-plugins) · Licence MIT
