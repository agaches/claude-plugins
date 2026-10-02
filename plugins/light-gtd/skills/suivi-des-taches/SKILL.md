---
name: suivi-des-taches
description: Tient à jour le fichier Google Sheets de suivi des tâches de l'utilisateur, `suivi_taches` par défaut (méthode GTD, une ligne par sujet, une colonne par jour). À utiliser dès que l'utilisateur dicte ou écrit quelque chose sur ses tâches, actions ou choses à faire, ce qu'il a fait, une nouvelle tâche, une tâche finie, en attente ou à relancer, un rappel à poser ("j'ai envoyé le mail au plombier", "ajoute : renouveler le passeport avant fin novembre", "le devis est validé, c'est bouclé", "rappelle-moi de relancer la mairie jeudi"). Sert aussi de référence (fichier, structure, règles) aux skills point-du-matin, succes-du-soir, succes-de-la-semaine et gtd-revue.
---

# Suivi des tâches

Le fichier de suivi est le système de confiance de l'utilisateur : il dicte, Claude range.
Une ligne = un sujet à mener jusqu'au bout. Une case de jour = ce qui a été fait ce jour-là,
puis la prochaine action.

## 1. Retrouver le fichier

Aucun identifiant n'est connu à l'avance, et le titre est choisi par l'utilisateur (défaut
`suivi_taches`) : chercher le fichier par le marqueur écrit dans son onglet README, pas par son
titre.

1. Recherche Drive : `fullText contains 'light-gtd-fichier-de-suivi' and owner = 'me' and mimeType = 'application/vnd.google-apps.spreadsheet'`.
2. 0 résultat : chercher un fichier créé par la v0.1, sans marqueur :
   `title = 'suivi_taches' and owner = 'me' and mimeType = 'application/vnd.google-apps.spreadsheet'`.
   Trouvé : l'utiliser et proposer de relancer l'installation pour ajouter le marqueur.
3. Toujours rien : un fichier tout juste créé peut ne pas être encore indexé. Demander le titre
   du fichier et le chercher par titre exact. Sinon proposer l'installation (skill
   `gtd-install`), ne rien créer soi-même.

Plusieurs résultats : demander lequel utiliser.

Connecteur Google Drive ou Google Sheets absent : le dire et renvoyer vers l'installation.

Lire ensuite l'onglet **README**, bloc « Configuration » : nom de l'agenda des tâches, liste
des contextes, section pro oui ou non. Ces valeurs priment sur les défauts ci-dessous.

## 2. Structure

Onglets : **Suivi** (tâches actives), **Terminées** (archive), **README** (mode d'emploi et
configuration). Détail complet et contenu initial : `references/modele-suivi-taches.md`.

**Suivi**, ligne 1 = en-têtes :

| Colonne | Contenu |
|---|---|
| Actions | Le sujet, préfixé `Perso : ` ou `Pro : ` |
| Deadline | `JJ/MM/AAAA`, ou `Chaque jour` pour une routine |
| Statut | `En cours`, `En attente` ou `Routine` |
| Contexte | Défaut : `Appels`, `IT`, `Maison`, `Pro`, `Dehors`, `Achats`, `Corvées`, `Partout` |
| Puis une colonne par jour | En-tête = date `JJ/MM` |

Sections, de haut en bas, chacune ouverte par une ligne titre dont seule la colonne Actions est
remplie : `Tâches récurrentes`, `Actions perso`, `Actions pro` (si activée), `Global` (toujours
la dernière ligne, statut d'ensemble).

**Terminées** : lignes 1-2 = compteurs (formules, ne pas toucher), ligne 4 = en-têtes
`Tâche` · `Date de fin` · `Deadline initiale`, tâches closes à partir de la ligne 5.

## 3. Règles de saisie

- Case de jour : ce qui a été fait, puis `à faire : ` et la prochaine action.
  `mail envoyé, à faire : attendre la réponse`
- Rien de fait ce jour-là : seulement `à faire : appeler pour prendre rendez-vous`.
- Case déjà remplie aujourd'hui : compléter à la suite, en remplaçant l'ancien `à faire : …`
  s'il est accompli ou dépassé. Ne jamais effacer ce qui a été fait.
- Routine faite : `fait` (ou le détail dicté).

## 4. Procédures

Toujours commencer par relire l'onglet Suivi en entier (en-têtes et colonne Actions). Repérer
les colonnes et les sections par leur texte, jamais par une position supposée : le fichier a pu
être modifié à la main.

| Geste | Faire |
|---|---|
| **Colonne du jour** | Si aucune colonne n'a la date du jour en en-tête, en créer une à droite de la dernière colonne de jour (ajouter une colonne à la grille si elle est pleine). En-tête `JJ/MM`. |
| **Ajouter une tâche** | Insérer une ligne à la fin de sa section (juste avant le titre de section suivant). Remplir : `Perso : …` ou `Pro : …`, deadline, `En cours`, contexte déduit de la nature de l'action (demander si doute), et la première action dans la colonne du jour. |
| **Mettre à jour** | Retrouver la ligne par le sens, pas par une égalité stricte. Si plusieurs lignes correspondent, demander. Écrire dans la colonne du jour selon les règles de saisie. |
| **Passer en attente** | Statut `En attente`, noter ce qu'on attend dans la case du jour. Proposer un rappel de relance. |
| **Clore** | Ajouter la tâche dans Terminées (intitulé, date du jour, deadline initiale), relire pour vérifier, puis seulement supprimer la ligne de Suivi. |
| **Poser un rappel** | Événement dans l'agenda des tâches : retrouver son identifiant par son nom (lu dans la Configuration) dans la liste des agendas, puis créer l'événement dans cet agenda, pas dans l'agenda principal. Titre = intitulé de la tâche, à la date demandée. |

Deadline dictée en relatif (« avant vendredi ») : la convertir en `JJ/MM/AAAA` à partir de la
date du jour.

## 5. Règles de prudence

- Relire avant d'écrire, à chaque fois.
- Ne jamais effacer de contenu d'une case ; la seule suppression autorisée hors revue est celle
  d'une ligne close, après sa copie vérifiée dans Terminées.
- Ne pas toucher aux formules de Terminées ni à la ligne Global (sauf pendant la revue hebdo).
- Doute sur la ligne, la section ou le contexte : demander plutôt que deviner.
- Après chaque modification, résumer en une ou deux lignes ce qui a été écrit, et où.
  Exemple : « Noté dans *Perso : faire réparer la porte*, 30/09 : devis reçu, à faire : valider le devis. »
