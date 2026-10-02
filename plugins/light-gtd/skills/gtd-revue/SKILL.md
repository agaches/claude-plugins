---
name: gtd-revue
description: Conduit la revue hebdomadaire GTD du fichier de suivi des tâches. À utiliser quand l'utilisateur lance /gtd-revue ou demande la revue de la semaine ("on fait la revue", "revue hebdo", "on range les tâches").
---

# Revue hebdo

Garder le fichier frais et reprioriser. **Claude propose, l'utilisateur valide** : aucune
écriture sans accord explicite, étape par étape.

Charger d'abord la skill `suivi-des-taches` (retrouver le fichier, structure), puis lire le fichier (Suivi et Terminées).

## Déroulé

Une étape par message ; attendre la réponse avant de passer à la suivante. L'utilisateur peut
dire « suivant » pour sauter une étape ou « stop » pour arrêter là (ce qui est validé reste écrit).

1. **Succès de la semaine** : appliquer la skill `succes-de-la-semaine`.
2. **Tâches En cours** : pour chacune, a-t-elle bougé cette semaine ? La prochaine action est-elle
   toujours la bonne ? Ne présenter que celles qui posent question, par lot.
3. **En attente** : pour chacune, proposer relancer (avec rappel dans l'agenda), attendre encore
   ou abandonner.
4. **Ça stagne** : tâches sans « fait » depuis 2 semaines ou plus. Proposer découper, reporter
   (nouvelle deadline) ou abandonner.
5. **Semaine prochaine** : deadlines des 7 prochains jours, proposer un ordre fondé sur les
   deadlines.
6. **Rangement** :
   - tâches finies non encore closes → Terminées (procédure « Clore » de `suivi-des-taches`) ;
   - colonnes de jours de plus de 2 mois → nettoyage (ci-dessous).
7. **Ligne Global** : proposer un statut de la semaine en une phrase, l'écrire dans la colonne du
   jour de la ligne Global.

Abandonner une tâche = la clore avec `abandonnée` après l'intitulé dans Terminées.

## Nettoyage des colonnes de plus de 2 mois

Règle : aucune tâche active ne perd sa prochaine action. Seule opération qui supprime des
colonnes ; l'historique des versions de Google Sheets sert d'archive.

1. **Lister** les colonnes de jours dont la date a plus de 2 mois.
2. **Report** : pour chaque tâche encore dans Suivi dont la dernière case non vide est dans une
   de ces colonnes, recopier ce contenu dans la colonne du jour, préfixé `report du JJ/MM : `
   (date de la case d'origine).
3. **Contrôle** : relire la colonne du jour et vérifier chaque report, un par un.
4. **Suppression** : seulement si tous les reports sont vérifiés, supprimer les colonnes listées.
   Un report manquant : ne rien supprimer, signaler l'écart.
5. **Résumé** : dates des colonnes supprimées, tâches reportées, rappel : « Fichier > Historique
   des versions permet de revenir en arrière. »

Présenter la liste (étape 1) et les reports prévus (étape 2) et obtenir l'accord avant d'écrire.

## Fin de revue

Résumer en 3 à 5 lignes ce qui a été modifié. Proposer de poser dans l'agenda les rappels décidés
pendant la revue qui n'ont pas encore été créés.
