# Référence premiers-pas : liens, menus, formations

Relevé le : 2026-11-06

Source unique des liens et formations.

**Comptes Team uniquement.** La configuration d'un compte Team n'a rien à voir avec celle d'un
compte Pro/Max. Sur Team, les menus ne sont pas aux mêmes endroits que dans la doc publique,
et la traduction française ne suit pas l'anglais mot à mot. La colonne « Indice doc publique »
sert seulement à reconnaître ce que l'utilisateur décrit : **ne jamais la lui citer** comme
chemin ou libellé. Décrire le réglage par sa fonction, demander ce qu'il voit, reprendre ses mots.

Vérifier les liens : `python3 scripts/verifier_liens.py <ce fichier>` (depuis la racine du repo).

## Réglages claude.ai

Cible : compte Team. L'utilisateur choisit chaque valeur ; la skill explique.

| Réglage | Indice doc publique (pas Team, ne pas citer) | À quoi ça sert | Valeurs | Détectable par Claude |
|---|---|---|---|---|
| Exécution de code | Settings > Capabilities > « Code execution and file creation » / « Create and edit files » | Créer et modifier des fichiers, analyser des données. **Prérequis des skills et plugins.** | activé / désactivé | oui (outil d'exécution présent) |
| Préférences de profil | profil, préférences | Texte lu par Claude dans toutes les conversations : rôle, langue, exigences (ex. « source tes affirmations ») | texte libre, vide par défaut | oui (texte injecté dans le contexte) |
| Recherche web | outils de la conversation | Claude cherche sur le web et cite ses sources | activé / désactivé | oui (outil de recherche présent) |
| Research (recherche approfondie) | outils de la conversation | Recherche longue, plusieurs sources, rapport sourcé ; s'active par conversation | activé / désactivé, par conversation | incertain |
| Mémoire | Settings > « Your Claude » ou « Memory » : « Search and reference chats », « Generate memory from chats » | Retrouver les conversations passées, garder du contexte d'une conversation à l'autre. Désactivable pour une conversation (menu « + ») ; mode incognito (icône fantôme) | chaque bascule activée / désactivée | en partie (outils de recherche dans l'historique) |
| Usage | Settings > Usage | Voir sa consommation et où on en est de ses limites, pour savoir quand on approche du plafond | consultation seulement | non (capture ou déclaration) |
| Vocal et app mobile | app mobile | Poser ses questions à la voix depuis le téléphone | app installée ou non | non (capture ou déclaration) |

Autres réglages (citer en une ligne, ne pas détailler) : styles, langue de l'interface,
apparence, notifications.

## Connecteurs

Les connecteurs distants activés sur claude.ai sont aussi disponibles dans Claude Code, Cowork
et l'app de bureau (source : https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors).
Les extensions de bureau, elles, ne marchent que dans l'app de bureau et Claude Code.

Emplacement du menu : demander à l'utilisateur. Doc : https://support.claude.com/en/articles/11176164

| Environnement | Connecteurs à présenter |
|---|---|
| Microsoft 365 | Microsoft 365 (Outlook, OneDrive, SharePoint, Teams : à confirmer dans la liste de l'UI) |
| Google Workspace | Gmail, Google Drive, Google Agenda |
| Slack | Slack |
| Autre | montrer la liste des connecteurs de l'UI, l'utilisateur choisit |

Détectable par Claude : oui, les outils du connecteur apparaissent.

## Apps

| App | Prérequis | Où l'installer | Doc |
|---|---|---|---|
| App de bureau | macOS, Windows ; Linux en bêta (Ubuntu 22.04+, Debian 12+, via le dépôt apt d'Anthropic) | https://claude.ai/download | https://support.claude.com/en/articles/10065433-install-claude-desktop |
| App mobile | iOS ou Android | App Store ou Google Play, chercher « Claude » (éditeur Anthropic) | https://claude.ai/download |
| Claude pour Excel, PowerPoint, Word | Offre Pro et plus (Team inclus) ; Microsoft 365 ; parfois déployé par l'admin Microsoft 365 | Microsoft Marketplace (AppSource), puis connexion avec le compte Claude | https://claude.com/docs/office-agents/overview |
| Claude in Chrome | Offre payante ; navigateur Chrome uniquement (pas les autres Chromium, pas le mobile) | Chrome Web Store | https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome |
| Claude Code | Terminal ; profil tech. Ici : lien et formation seulement, pas de configuration | voir la doc | https://code.claude.com/docs |

Office : le réglage qui laisse Claude travailler sur plusieurs fichiers (doc publique : « Let
Claude work across files », ne pas citer) est désactivé par défaut sur Team
(activé sur Pro/Max) ; qui peut l'activer (utilisateur ou admin) : non documenté.

## Admin Team

Quand un réglage est grisé ou absent, c'est en général l'admin de l'organisation (souvent la
personne qui a donné l'accès). Lui demander le réglage par sa fonction (l'admin retrouve le menu ; chemins de la doc publique,
non garantis sur Team) :

| Bloqué | À demander à l'admin |
|---|---|
| Exécution de code, skills | Paramètres de l'organisation > Plugins & skills > onglet Policy : activer l'exécution de code et les Skills (activés par défaut sur Team, selon la doc) |
| Ajout d'une marketplace ou d'un plugin | Paramètres de l'organisation > Plugins & skills : autoriser les plugins personnels |
| Connecteurs | Paramètres de l'organisation > connecteurs : autoriser le connecteur voulu |
| Compléments Office | Admin Microsoft 365 (Microsoft 365 Admin Center) : déployer ou autoriser le complément Claude |
| Claude in Chrome | Paramètres de l'organisation : autoriser Claude in Chrome |

Doc : https://support.claude.com/en/articles/12512180-use-skills-in-claude ·
https://support.claude.com/en/articles/13837440-use-plugins-in-claude

## Programme de formation

Cours gratuits de Claude Academy, **tous en anglais**. Catalogue : https://academy.claude.com/all

| Chapitre | Pour qui | Cours |
|---|---|---|
| 1. Les bases | tous | [AI Fluency: Framework and foundations](https://academy.claude.com/courses/ai-fluency-framework-foundations) (les 4D : Delegation, Description, Discernment, Diligence) · [AI capabilities and limitations](https://academy.claude.com/courses/ai-capabilities-and-limitations) |
| 2. Bien utiliser Claude au quotidien | tous | [Claude 101](https://academy.claude.com/courses/claude-101) (prompts, projets, outils connectés) |
| 3. Par outil | selon les apps installées | [Introduction to Claude Cowork](https://academy.claude.com/courses/introduction-to-claude-cowork) (app de bureau) ; Office et Chrome : pas de cours officiel, renvoyer à la doc de la section Apps |
| 4. Tech | profil tech | [Claude Code 101](https://academy.claude.com/courses/claude-code-101) · [Claude Code in action](https://academy.claude.com/courses/claude-code-in-action) · [Introduction to agent skills](https://academy.claude.com/courses/introduction-to-agent-skills) · [Introduction to Model Context Protocol](https://academy.claude.com/courses/introduction-to-model-context-protocol) |

Variantes AI Fluency selon le profil, à proposer à la place ou en plus du chapitre 1 :
[small businesses](https://academy.claude.com/courses/ai-fluency-for-small-businesses) ·
[builders](https://academy.claude.com/courses/ai-fluency-for-builders) ·
[creative work](https://academy.claude.com/courses/ai-fluency-for-creative-work) ·
[educators](https://academy.claude.com/courses/ai-fluency-for-educators).

## Sources

- Skills : https://support.claude.com/en/articles/12512180-use-skills-in-claude
- Plugins : https://support.claude.com/en/articles/13837440-use-plugins-in-claude
- Connecteurs partout : https://support.claude.com/en/articles/11725091-when-to-use-desktop-and-web-connectors
- Mémoire : https://support.claude.com/en/articles/11817273
- App de bureau : https://support.claude.com/en/articles/10065433-install-claude-desktop
- Office : https://claude.com/docs/office-agents/overview
- Claude in Chrome : https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome
- Claude Code : https://code.claude.com/docs
- Academy : https://academy.claude.com/all
