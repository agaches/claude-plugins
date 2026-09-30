---
name: succes-du-soir
description: Fait le bilan positif de la journée à partir du fichier de tâches `suivi_taches`. À utiliser quand l'utilisateur demande ce qu'il a fait ou accompli aujourd'hui, ses succès ou le bilan du jour ("qu'est-ce que j'ai fait aujourd'hui ?", "mes succès du jour", "le bilan de la journée", "j'ai avancé sur quoi ?").
---

# Succès du soir

Finir la journée sur ce qui a été accompli. Lecture seule.

Charger d'abord la skill `suivi-des-taches` (retrouver le fichier, structure), puis lire le fichier, puis la colonne dont
l'en-tête est la date du jour. Pas de colonne du jour : le dire simplement et proposer de noter
ce qui a été fait.

## Compter

Dans chaque case du jour, le « fait » = tout ce qui précède `à faire :` (« fait », « envoyé »,
« calé », « payé », « réglé »…). Une case qui ne contient que `à faire : …` ne compte pas.
Ajouter les tâches closes aujourd'hui (onglet Terminées, date de fin = aujourd'hui).

Compter séparément routines (section Tâches récurrentes) et projets (autres sections).

## Format

3 à 6 lignes, ton chaleureux et sobre :

1. le total : « Aujourd'hui : 5 actions faites, dont 2 routines. » ;
2. les 1 à 3 plus marquantes (tâche close, attente débloquée, deadline tenue) ;
3. ce qui est prêt pour demain, en une phrase, seulement si une deadline tombe demain.

Moins de 3 actions : mettre en avant ce qui a été fait, sans reproche ni « mais ». Aucune
action : une phrase bienveillante, et proposer de noter ce qui a été fait mais pas encore écrit.
