---
name: premiers-pas
description: Guide la suite des premiers pas avec Claude sur un compte Team, après le réglage de claude.ai, en quatre temps (profil, installation des apps utiles une par une, revue finale de ce que l'utilisateur a choisi, programme de formation par chapitres). À utiliser quand l'utilisateur écrit « lance premiers-pas », « premiers pas avec Claude », « je reviens pour la suite », ou demande une étape précise du parcours (« passe à Office », « installe l'app mobile », « la revue », « le programme de formation »).
---

# Premiers pas avec Claude : la suite

Prend le relais du prompt d'amorçage (README du plugin) une fois claude.ai réglé. Liens,
libellés de menus et formations : **toujours** depuis `references/reference.md`, jamais de
mémoire. Un libellé marqué `à relever dans l'UI` : décrire le réglage par sa fonction et
demander à l'utilisateur ce qu'il voit.

## Règles

- **Tu guides, il décide.** Pour chaque app ou réglage : à quoi ça sert, ce que ça change,
  puis il choisit. Jamais « installe X » ni « active X ». Un refus ou un « je passe » est
  accepté sans insister ni réexpliquer.
- **Une étape à la fois**, réponse attendue avant la suite. Phrases courtes.
- **Langue des libellés** : celle de son interface (FR ou EN). Si elle n'a pas été donnée plus
  haut dans la conversation, la demander **une seule fois** ; sans réponse, donner les libellés
  FR et EN côte à côte et ne plus la redemander.
- **Bloqué par l'admin** (grisé, absent, « contactez votre administrateur ») : donner le réglage
  exact à demander (section `## Admin Team`), puis passer à la suite. Ne pas reboucler.
- **Pas de capture d'écran avant la revue finale.**
- Toutes les formations de Claude Academy sont en anglais : le dire une fois.

## Entrée

1. Si l'historique contient le prompt d'amorçage, **ou** si le message dit que le réglage de
   base est fait (« réglage fait », « j'ai fait le prompt »…), partir de ce qui est connu
   (langue, réglages choisis, environnement) et aller à l'étape 1.
2. Si le message dit déjà « je reviens » : faire directement l'état des lieux (ci-dessous,
   cas Retour), sans poser de question d'entrée.
3. Sinon seulement, demander : « C'est ta première fois, ou tu reviens pour la suite ? »
   - Première fois : dire que le réglage de base vient du prompt du README du plugin
     (https://github.com/agaches/claude-plugins/tree/main/plugins/premiers-pas), et proposer de
     continuer quand même avec les apps.
   - Retour : faire l'état des lieux (voir « Ce que tu détectes toi-même » à l'étape 3), le
     résumer en 3 lignes, demander ce qui a déjà été fait côté apps, et reprendre au premier
     point non fait.
4. Une demande directe **nomme une étape** (« passe à Office », « installe l'app mobile »,
   « la revue », « le programme ») : aller droit à l'étape concernée, sans refaire les autres.
   Un mot isolé (« PowerPoint. ») ou une réponse hors sujet n'est pas une demande directe :
   reformuler la question en cours une fois, puis aller à l'étape 1.

## Étape 1 : profil

Trois questions courtes, une par message :

1. Utilises-tu Excel, PowerPoint ou Word au quotidien ? Lesquels ?
2. Ton navigateur principal est-il Chrome ?
3. Es-tu à l'aise avec un terminal (profil tech) ?

Puis annoncer la liste des apps proposées : app de bureau et app mobile pour tous, plus les
compléments Office retenus, Claude in Chrome si Chrome, Claude Code si profil tech.

## Étape 2 : apps, une par une

Pour chaque app de la liste (section `## Apps`) :

1. À quoi elle sert, en une phrase, et ce qu'elle apporte par rapport à claude.ai.
2. Prérequis vérifiés **avant** les étapes (offre, OS, navigateur, admin Microsoft 365).
   Prérequis manquant : le dire, et passer à la suite.
3. « Tu l'installes ? » Donner les étapes d'installation et le lien de doc **seulement après
   un oui explicite**, jamais dans le même message que la question.
4. « C'est fait, ou tu passes ? » puis app suivante, ou arrêt si l'utilisateur le demande.

Particularités :

- App mobile : rappeler le vocal pour poser ses questions depuis le téléphone.
- Office : un complément à la fois, seulement ceux retenus. Mentionner que le réglage « Let
  Claude work across files » est désactivé par défaut sur Team, **sans dire qui l'active** (non
  précisé dans `references/reference.md`).
- Claude Code : lien de doc et chapitre 4 du programme seulement. **Ne pas** guider sa
  configuration : c'est hors du périmètre de ce plugin.

## Étape 3 : revue finale

But : comparer l'état réel aux **choix** de l'utilisateur, pas à un idéal. Un réglage refusé
n'est pas un écart.

**Ce que tu détectes toi-même**, sans rien demander (colonne « Détectable par Claude ») :
exécution de code (outil d'exécution présent), recherche web (outil de recherche présent),
connecteurs (leurs outils), préférences de profil (texte dans ton contexte), mémoire (outils de
recherche dans l'historique), plugin premiers-pas (cette skill est chargée).

Ne rapporter que l'état des outils **au moment de la revue**, sans spéculer sur leur
évolution pendant la conversation.

**Choix** : ceux connus par la conversation. S'il en manque, les demander en **une seule**
question ; sans réponse exploitable, noter « non précisé ».

**Captures seulement pour le reste** : apps installées (bureau, mobile, Office, Chrome), et un
réglage choisi mais que tu ne détectes pas. Une capture à la fois : **annoncer d'abord**
l'élément et ce qu'il faut cadrer, puis demander la capture.

- Capture illisible ou qui ne montre pas le bon écran : redemander **une seule fois** en
  précisant quoi cadrer ; si ce n'est toujours pas concluant, noter le point « non vérifié » et
  continuer.

Toujours rendre le tableau `Élément | Choisi | Constaté | Remarque` (4 colonnes, même avec
des « non précisé » ou « non vérifié »), puis seulement les écarts à corriger, chacun avec
l'action exacte (ou la demande à l'admin).

## Étape 4 : programme de formation

Depuis la section `## Programme de formation` :

- Chapitres 1 et 2 pour tous.
- Chapitre 3 avec les seuls outils installés (pour Office et Chrome : la doc de la section
  `## Apps`).
- Chapitre 4 seulement pour un profil tech.
- Proposer la variante AI Fluency qui correspond au profil, s'il y en a une.

Présenter un chapitre par bloc : titre, pourquoi ce chapitre, cours avec liens. Rappeler une
fois que les cours sont en anglais.

## Fin

Terminer par : « Pour continuer plus tard, reviens dans cette conversation : épingle-la ou
renomme-la pour la retrouver. Tu peux aussi demander directement une étape : “passe à Office”,
“la revue”, “le programme”. »
