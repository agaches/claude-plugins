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
- Tu ne vois pas mon écran. Sur un compte Team, les menus ne sont pas aux mêmes endroits que dans la doc publique, et la traduction française ne suit pas l'anglais mot à mot : ne cite aucun chemin de menu ni libellé. Décris ce que fait le réglage et ce qu'il faut chercher, demande-moi ce que je vois, puis reprends mes mots à moi.
- Si un réglage est grisé ou absent, il est verrouillé par l'admin de mon organisation : dis-moi exactement quoi lui demander, puis passe à la suite.
- Le tout doit tenir en 5 minutes environ : sois bref.

Déroulé :

0. Fais-moi ouvrir un 2e onglet sur claude.ai, ouvrir les paramètres (en général via mon nom ou mon avatar), et placer les deux onglets côte à côte : cette conversation à gauche, les paramètres à droite. Demande-moi de te lister les rubriques que je vois : tu t'en serviras pour me guider.

1. Réglages, dans cet ordre :
   a. Exécution de code et création de fichiers : permet à Claude de créer des fichiers et d'exécuter du code. Précise qu'il est nécessaire pour l'étape 3. Si verrouillé : demander à l'admin d'activer l'exécution de code et les Skills pour l'organisation.
   b. Préférences de profil : un texte que tu liras dans toutes mes conversations. Propose de m'aider à le rédiger en 2-3 questions (mon rôle, la langue, mes exigences, par ex. « source tes affirmations »).
   c. Recherche web, puis Research (recherche approfondie, qui s'active par conversation).
   d. Mémoire : retrouver mes conversations passées, garder du contexte d'une conversation à l'autre.
   e. Usage : où voir ma consommation et mes limites. Rien à régler, juste savoir où regarder.
   f. App mobile et vocal : poser mes questions à la voix depuis le téléphone (l'installation se fera plus tard, cite-la seulement).
   Cite les autres réglages (styles, apparence…) en une ligne, sans détailler.

2. Connecteurs : demande-moi mon environnement de travail (Microsoft 365, Google Workspace, Slack, autre) et présente seulement les connecteurs correspondants (Microsoft 365 : connecteur Microsoft 365 ; Google Workspace : Gmail, Google Drive, Google Agenda ; Slack : Slack ; autre : ceux de la liste affichée). Précise que les connecteurs activés ici sont aussi disponibles dans Claude Code, Cowork et l'app de bureau. Si verrouillé : demander à l'admin d'autoriser le connecteur.

3. Plugin premiers-pas, pour la suite (apps, vérification finale, formations) : dans claude.ai, la section des plugins, ajouter la marketplace agaches/claude-plugins (à saisir tel quel), puis ajouter le plugin premiers-pas. Si l'ajout est impossible : demander à l'admin d'autoriser les plugins personnels. Une fois ajouté, dis-moi d'écrire « lance premiers-pas » dans cette conversation. Si rien ne se déclenche (plugin ou exécution de code tout juste activés), ouvrir une nouvelle conversation et écrire « je reviens pour la suite ».

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

- Comptes Team uniquement : la configuration d'un compte Pro/Max est très différente, le guide
  ne s'y applique pas.
- Sur un compte Team, les menus ne sont pas aux mêmes endroits que dans la doc publique, et la
  traduction française ne suit pas l'anglais mot à mot : le guide ne cite aucun chemin de menu,
  il décrit chaque réglage par sa fonction et vous demande ce que vous voyez.
- Les formations de Claude Academy sont en anglais.
