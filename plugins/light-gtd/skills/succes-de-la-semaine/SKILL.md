---
name: succes-de-la-semaine
description: Fait le bilan positif de la semaine à partir du fichier de suivi des tâches. À utiliser quand l'utilisateur demande ses succès, son bilan ou le chemin parcouru sur la semaine ("mes succès de la semaine", "qu'est-ce que j'ai fait cette semaine ?", "le bilan de la semaine"), et en ouverture de la revue hebdo.
---

# Succès de la semaine

Voir le chemin parcouru. Lecture seule.

Charger d'abord la skill `suivi-des-taches` (retrouver le fichier, structure), puis lire le fichier. Semaine = du lundi
au jour même (ou les 7 derniers jours si l'utilisateur le demande).

## Contenu

1. **Tâches bouclées** : onglet Terminées, date de fin dans la semaine.
2. **Tâches qui ont nettement avancé** : au moins 2 cases de la semaine avec du « fait », ou une
   attente débloquée.
3. **Total d'actions faites** : même règle de comptage que la skill `succes-du-soir`, sur toutes
   les colonnes de la semaine, routines comptées à part.
4. **1 ou 2 faits marquants** mis en avant, en une phrase chacun.

## Format

8 à 12 lignes, ton chaleureux et sobre, lisible sur téléphone. Semaine calme : mettre en avant
ce qui a été tenu (routines, attentes gérées), sans reproche.
