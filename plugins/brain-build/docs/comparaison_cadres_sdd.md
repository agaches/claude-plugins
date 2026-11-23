# brain-build face aux autres cadres de développement piloté par les specs

Comparaison avec GitHub Spec Kit, BMAD-METHOD, OpenSpec et Kiro. Écrite le 2026-11-23.

Ce qui est mesuré et ce qui ne l'est pas :

- Les chiffres de brain-build viennent de trois produits réels (voir [retours_sur_brain_build.md](retours_sur_brain_build.md)).
- Les descriptions des autres cadres viennent de sources publiques (blogs, documentation, comparatifs), lues en une recherche, **sans les avoir utilisés**. Elles évoluent vite : à revérifier avant de s'en servir pour décider.
- **Aucune comparaison de coût mesurée n'existe ici.** Aucun des autres cadres ne publie de coût par run dans ce qui a été trouvé. Les écarts de coût ci-dessous sont des raisonnements, pas des mesures.

## En bref

| | brain-build | Spec Kit | BMAD-METHOD | OpenSpec | Kiro |
|---|---|---|---|---|---|
| Nature | plugin Claude Code | boîte à outils (CLI `specify` + commandes), multi-assistants | équipe simulée d'agents (analyste, PM, architecte, scrum master, dev...) | boîte à outils légère, par changement | IDE propriétaire |
| Étapes | besoin figé, specs, plan, tests, code, recette | constitution, spec, plan, tâches, implémentation | brief, PRD, architecture, stories, dev | proposition de changement, deltas de specs, tâches | exigences, design, tâches |
| Qui exécute | une session pilote lance des processus `claude -p` séparés par rôle | un seul assistant, guidé | un assistant qui joue des rôles, dialogue avec l'humain à chaque étape | un seul assistant | agents intégrés à l'IDE |
| Tests | écrits par un agent distinct, depuis besoin et specs seulement | écrits dans le flux de l'assistant (pas de séparation imposée, à vérifier) | rôle de QA dans le flux | dans les tâches | dans les tâches |
| Preuve que les tests mesurent quelque chose | oui : `proves` (échec au départ, succès à l'intégration) | non à ma connaissance | non à ma connaissance | non à ma connaissance | non à ma connaissance |
| Traçabilité vérifiée par script | oui : `trace.py` (check, guard, proves, matrix) | non à ma connaissance | non à ma connaissance | non à ma connaissance | non à ma connaissance |
| Parallélisme | oui, worktrees séparés | non | non | non | non à ma connaissance |
| Autonomie | jusqu'à la recette, l'humain tranche les questions de besoin | l'humain relit chaque artefact | l'humain valide chaque étape | l'humain relit les deltas | l'humain valide chaque étape |
| Assistants supportés | Claude Code seulement | plusieurs | plusieurs | plusieurs | Kiro seulement |
| Licence | à voir dans le dépôt | MIT | non précisée dans la source consultée | MIT | propriétaire |

## Mieux ou moins bien ?

| Sur quoi | brain-build | Verdict |
|---|---|---|
| Indépendance des tests vis-à-vis du code | Processus séparé, besoin et specs seulement, `guard` détecte un dev qui touche aux tests. Imparfait : un testeur a lu du code, un prompt citait des fichiers (voir L8). | Mieux, car imposé et contrôlé. Les autres s'en remettent à la discipline de l'assistant. |
| Preuve que les tests sont utiles | `proves` a éliminé 6 tests vides sur le jeu A, validé 127 cas sur 129 et 64 fichiers sur 64. | Mieux, apparemment unique. |
| Autonomie et débit | Parallélisme, build sans l'humain. Mais arrêts silencieux du pilote et limite d'usage constatés. | Mieux sur le papier, avec des défauts réels. |
| Légèreté et souplesse | 41 REQ pour 2 700 lignes (jeu A), cérémonie lourde, outillage fragile (worktrees, sous-dossier). | **Moins bien.** OpenSpec, pensé par changement, est plus adapté aux petits changements. Spec Kit est plus simple à prendre en main. |
| Cadrage amont | `/brain` : grill, relecture par personas. A attrapé des erreurs de besoin avant le code. | Comparable à BMAD (analyste, PM), avec un mécanisme de contradiction entre relecteurs en plus. Pas de comparaison mesurée. |
| Gouvernance transverse | Normes dans la config de build, ADR via une skill externe. | Spec Kit a la « constitution » (principes non négociables) : plus explicite. |
| Portabilité | Claude Code seulement. | **Moins bien** : Spec Kit, BMAD et OpenSpec couvrent plusieurs assistants. |
| Ressenti, rendu, usage réel | Non couvert : les tests mesurent le besoin écrit (L1, L3). | Pas meilleur. Les autres cadres ont probablement le même angle mort : à ma connaissance aucun n'a de test de fumée sur la pile réelle. |
| Maturité et communauté | Un plugin, trois produits d'essai. | **Moins bien** : Spec Kit et BMAD ont des communautés larges et de nombreuses extensions. |

## Plus ou moins cher ?

Verdict : **probablement plus cher en jetons que Spec Kit et OpenSpec, comparable ou moins cher que BMAD, mais ce n'est pas mesuré.**

- **Mesuré pour brain-build** : de 11 $ à environ 55 $ d'agents par produit, dont jusqu'à 20 % de rattrapage. Le pilote n'est pas compté et pèse sans doute autant.
- **Pourquoi plus cher que Spec Kit ou OpenSpec** : plusieurs processus à contexte neuf (analyste, testeur, un dev par action, diagnostics) relisent le besoin et les specs chacun de leur côté. Les cadres à assistant unique partagent un seul contexte.
- **Pourquoi pas forcément plus cher que BMAD** : les sources décrivent BMAD comme gourmand en jetons, parce que chaque agent reçoit beaucoup de contexte (PRD, architecture). Des astuces existent (découpage des documents, planification dans une interface web), sans chiffre officiel vérifié.
- **Ce qui fait baisser le coût de brain-build** : un besoin court (moins de REQ), des réglages dans une table plutôt qu'en exigences, moins de parallélisme quand le quota compte.
- **Ce que le coût achète** : des tests indépendants et prouvés, pas moins de relecture humaine. Pour un produit où une erreur de règle coûte cher, c'est un bon prix. Pour un prototype, c'est du surdimensionnement.

## Quand choisir quoi

1. **Règles précises, conformité, contrats, peu de ressenti** : brain-build, pour les tests indépendants et la preuve.
2. **Petits changements sur un produit existant** : OpenSpec, ou le mode delta de brain-build si le besoin existe déjà.
3. **Démarrer vite avec n'importe quel assistant** : Spec Kit.
4. **Produit à cadrer comme un projet d'équipe (brief, PRD, architecture, stories)** : BMAD.
5. **Écosystème AWS et IDE dédié** : Kiro.
6. **Un jeu ou un produit jugé à l'usage** : prototype jouable d'abord, quel que soit le cadre.

## Sources

Consultées le 2026-11-23, lues rapidement :

- [Spec Kit, présentation officielle](https://github.github.com/spec-kit/)
- [GitHub Blog : Spec-driven development with AI](https://github.blog/news-insights/product-news/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [Spec Kit vs BMAD vs OpenSpec (DEV Community)](https://dev.to/willtorber/spec-kit-vs-bmad-vs-openspec-choosing-an-sdd-framework-in-2026-d3j)
- [Comparatif Spec Kit, Kiro, BMAD](https://medium.com/@visrow/comprehensive-guide-to-spec-driven-development-kiro-github-spec-kit-and-bmad-method-5d28ff61b9b1)
- [Limitations de BMAD Method](https://asantos2000.github.io/blog/post-3/)
