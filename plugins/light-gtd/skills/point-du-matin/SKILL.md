---
name: point-du-matin
description: Donne le point du jour à partir du fichier de tâches `suivi_taches`. À utiliser quand l'utilisateur demande un point, un brief, sa journée ou quoi faire aujourd'hui ("fais-moi le point", "c'est quoi ma journée ?", "qu'est-ce que je fais aujourd'hui ?", "le point du matin", "j'ai 1 h, je fais quoi ?").
---

# Point du matin

Une vue qualitative pour démarrer la journée, pas une liste brute. Lecture seule : ne rien
écrire dans le fichier.

Charger d'abord la skill `suivi-des-taches` (retrouver le fichier, structure), puis lire le fichier (onglet Suivi en
entier). Ignorer les lignes de section et la ligne Global.

## Contenu, dans cet ordre

1. **Les grands sujets en cours** : 2 ou 3 phrases qui regroupent (« la maison : 3 sujets, dont
   deux en attente de devis »), pas une ligne par tâche.
2. **Deadlines** : dépassées, du jour et des 3 prochains jours, avec la prochaine action.
3. **À relancer** : tâches `En attente` sans mouvement depuis 3 jours ou plus.
4. **Ça stagne** : tâches `En cours` dont le même `à faire` revient depuis 3 jours ou plus.
5. **3 actions suggérées pour aujourd'hui**, regroupées par contexte (« au téléphone : … et … »).
   Priorité : deadline la plus proche, puis ce qui débloque une attente, puis ce qui stagne.

La prochaine action d'une tâche = le dernier `à faire : …` de sa ligne, en lisant les colonnes
de jours de droite à gauche. Les routines n'apparaissent que si elles sont en retard ou si
l'utilisateur les demande.

## Format

Lisible sur téléphone : 15 lignes maximum, titres courts en gras, pas de tableau. Section vide :
l'omettre. Terminer par la question « Je note quelque chose ? » seulement si une action
suggérée est déjà faite ou datée d'aujourd'hui.
