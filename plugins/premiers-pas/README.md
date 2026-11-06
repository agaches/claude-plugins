# premiers-pas

Vous venez d'avoir un accès Claude et vous ne savez pas par quel bout le prendre ? Ouvrez
claude.ai, collez le prompt ci-dessous dans une nouvelle conversation, et laissez-vous guider.

La conversation vous guide pas à pas, pendant que vous réglez claude.ai dans un deuxième onglet
placé à côté. Elle explique chaque paramètre et ses valeurs, et c'est vous qui choisissez. Comptez
environ 5 minutes pour le réglage de base. Ensuite, le plugin installé à la fin du réglage prend le
relais : installation des apps qui vous servent vraiment, vérification finale, et programme de
formation.

## Prérequis

- Un compte Claude **Team**.
- Si un réglage est grisé ou absent, il est verrouillé par l'admin de votre organisation (souvent la
  personne qui vous a donné l'accès). Le guide vous dit quoi lui demander.

## Le prompt à coller

Ouvrez https://claude.ai, démarrez une nouvelle conversation, collez :

<!-- prompt:debut -->
```
Je débute avec Claude (compte Team). Guide-moi pour régler claude.ai, étape par étape, en français.

Règles pour toi :
- Une étape à la fois. Attends ma réponse avant de passer à la suite.
- Pour chaque réglage : explique en 1-2 phrases à quoi il sert, les valeurs possibles et ce que ça change. Puis laisse-moi choisir. Ne me dis jamais « active X » : c'est moi qui décide.
- Tu ne vois pas mon écran. Décris où trouver le réglage par sa fonction ; si le libellé que je vois diffère, demande-moi ce que je vois.
- Si un réglage est grisé ou absent, il est verrouillé par l'admin de mon organisation : dis-moi exactement quoi lui demander, puis passe à la suite.
- Le tout doit tenir en 5 minutes environ : sois bref.

Déroulé :

0. Demande-moi si mon interface claude.ai est en français ou en anglais. Ce prompt ne contient que les libellés anglais : si mon interface est en français, ne traduis pas les menus toi-même, donne le libellé anglais entre parenthèses et décris la fonction pour que je la repère. Puis fais-moi ouvrir un 2e onglet sur claude.ai, aller dans les Paramètres (Settings), et placer les deux onglets côte à côte : cette conversation à gauche, les paramètres à droite.

1. Réglages, dans cet ordre :
   a. Exécution de code et création de fichiers (Settings > Capabilities > « Code execution and file creation », ou « Create and edit files »). Précise qu'il est nécessaire pour l'étape 3. Si verrouillé : demander à l'admin « Paramètres de l'organisation > Plugins & skills > Policy : activer l'exécution de code et les Skills ».
   b. Préférences de profil : un texte que tu liras dans toutes mes conversations. Propose de m'aider à le rédiger en 2-3 questions (mon rôle, la langue, mes exigences, par ex. « source tes affirmations »).
   c. Recherche web, puis Research (recherche approfondie, qui s'active par conversation).
   d. Mémoire (Settings > « Your Claude » ou « Memory ») : retrouver mes conversations passées, garder du contexte d'une conversation à l'autre.
   e. App mobile et vocal : poser mes questions à la voix depuis le téléphone (l'installation se fera plus tard, cite-la seulement).
   Cite les autres réglages (styles, apparence…) en une ligne, sans détailler.

2. Connecteurs : demande-moi mon environnement de travail (Microsoft 365, Google Workspace, Slack, autre) et présente seulement les connecteurs correspondants. Précise que les connecteurs activés ici sont aussi disponibles dans Claude Code, Cowork et l'app de bureau. Si verrouillé : demander à l'admin d'autoriser le connecteur.

3. Plugin premiers-pas, pour la suite (apps, vérification finale, formations) : dans claude.ai, Personnaliser (Customize) > Plugins > Ajouter une marketplace : agaches/claude-plugins, puis ajouter le plugin premiers-pas. Si l'ajout est impossible : demander à l'admin d'autoriser les plugins personnels. Une fois ajouté, dis-moi d'écrire « lance premiers-pas » dans cette conversation. Si rien ne se déclenche (plugin ou exécution de code tout juste activés), ouvrir une nouvelle conversation et écrire « je reviens pour la suite ».

Si l'étape 3 est bloquée, termine en me donnant le catalogue des formations gratuites (en anglais) : https://academy.claude.com/all, en commençant par « AI Fluency: Framework and foundations » et « Claude 101 ».

Commence par l'étape 0.
```
<!-- prompt:fin -->

## Ensuite : la skill premiers-pas

Une fois le plugin ajouté, écrivez « lance premiers-pas » dans la même conversation. La skill :

1. vous pose quelques questions (Office ? Chrome ? profil tech ?) ;
2. vous guide pour installer, une par une, seulement les apps retenues : app de bureau, app
   mobile, Claude pour Excel, PowerPoint ou Word, Claude in Chrome, et Claude Code (lien et
   formation seulement) ;
3. fait une revue finale de ce que vous avez choisi : elle vérifie elle-même ce qu'elle peut
   détecter, et vous demande des captures d'écran pour le reste ;
4. vous propose un programme de formation par chapitres, adapté à votre profil.

Pour continuer plus tard, revenez dans la même conversation (épinglez-la ou renommez-la pour la
retrouver). Dans une nouvelle conversation, « je reviens pour la suite » relance la skill, qui
vérifie où vous en êtes. Une étape peut être demandée directement : « passe à Office », « la
revue », « le programme ».

## Installation du plugin seul

Sur claude.ai ou l'app de bureau : [Personnaliser > Plugins](https://claude.ai/customize/plugins),
**Ajouter une marketplace** `agaches/claude-plugins`, puis ajouter `premiers-pas`.

Claude Code :

```
/plugin marketplace add agaches/claude-plugins
/plugin install premiers-pas@agaches
```

## Limites (v0.1)

- Comptes Team uniquement.
- Plusieurs libellés de menus de claude.ai ne sont pas encore relevés : le guide décrit les
  réglages par leur fonction et vous demande ce que vous voyez.
- Les formations de Claude Academy sont en anglais.
