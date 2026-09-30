---
name: installer
description: Initialise light-gtd pour l'utilisateur. À utiliser quand l'utilisateur lance /installer, veut installer, configurer ou réparer son suivi des tâches, ou quand le fichier `suivi_taches` est introuvable dans son Google Drive ("installe le suivi des tâches", "crée mon fichier de tâches", "vérifie que mon fichier de tâches est en ordre").
---

# Installer light-gtd

Prépare tout ce dont le plugin a besoin. Relançable sans risque : ne recrée jamais ce qui
existe, n'efface jamais rien.

## Étapes

### 1. Connecteurs

Requis : **Google Drive**, **Google Sheets**, **Google Agenda**. Tester chacun par un appel en
lecture (recherche Drive, liste des agendas). Les noms des outils varient selon l'environnement
(chat, Cowork, Claude Code) : chercher les outils Google disponibles avant de conclure qu'un
connecteur manque.

Pour chaque connecteur absent ou en erreur : expliquer comment l'activer (Paramètres >
Connecteurs, ou `/mcp` dans Claude Code), puis attendre que l'utilisateur confirme et retester.
Le plugin ne peut pas activer un connecteur lui-même. Ne pas continuer sans les trois.

### 2. Préférences

Demander en un seul message, avec les défauts :

- nom de l'agenda des tâches (défaut `Tâches`) ;
- contextes (défaut `Tél, Ordi, Maison, Dehors, Courses, Voiture`) ;
- section Actions pro (défaut oui).

« OK » ou « par défaut » = garder les défauts. Si le fichier existe déjà, proposer ses valeurs
de Configuration comme défauts.

### 3. Fichier `suivi_taches`

Chercher dans Drive un Google Sheets titré exactement `suivi_taches`.

- **Trouvé (1)** : appliquer la « Vérification de structure » du modèle, présenter les écarts et
  les corrections proposées, n'appliquer qu'après accord. Mettre à jour le bloc Configuration
  du README si les préférences ont changé.
- **Plusieurs** : demander lequel garder ; ne rien supprimer.
- **Absent** : le créer d'après le modèle (skill `suivi-des-taches`, fichier
  `references/modele-suivi-taches.md`) :
  1. créer un Google Sheets vide titré `suivi_taches` ;
  2. renommer la première feuille en `Suivi` (son nom dépend de la langue, `Feuille 1` ou
     `Sheet1`, mais son `sheetId` est `0`), ajouter `Terminées` et `README` ;
  3. écrire les valeurs des trois onglets (formules de Terminées écrites comme formules) ;
  4. appliquer la mise en forme et les validations ;
  5. relire les trois onglets et comparer au modèle ; corriger ce qui manque.

### 4. Agenda

Retrouver l'agenda des tâches par son nom dans la liste des agendas, et garder son identifiant.
Absent : le connecteur ne sait pas créer d'agenda. Proposer à l'utilisateur de le créer dans
Google Agenda puis de relancer, ou de choisir un agenda existant (l'agenda principal par
défaut) ; écrire le nom retenu dans la Configuration.

Chercher l'événement « Revue hebdo des tâches (GTD) » **dans cet agenda** : lister ses événements
avec la recherche plein texte `Revue hebdo`. La recherche d'événements « générale » ne couvre que
l'agenda principal et ne le trouverait pas. Absent : le créer dans cet agenda, récurrent
(`RRULE:FREQ=WEEKLY;BYDAY=SA`) de 9h00 à 9h30, fuseau de l'agenda, à partir du prochain samedi,
description : `Lancer /light-gtd:revue dans Claude.`

### 5. Résumé

Terminer par :

- le lien vers le fichier ;
- ce qui a été créé, corrigé ou laissé tel quel ;
- deux exemples pour démarrer :
  « ajoute : renouveler le passeport avant fin novembre » et « fais-moi le point ».

## Erreurs fréquentes

| Erreur | Correction |
|---|---|
| Créer un second `suivi_taches` alors qu'un existe | Toujours chercher avant de créer |
| Créer la revue en double | Chercher l'événement dans l'agenda des tâches, pas dans l'agenda principal |
| Formules de Terminées écrites en texte (`'=COUNTA…`) | Les écrire comme formules, vérifier que B1 et B2 affichent un nombre |
| Corriger la structure d'un fichier existant sans demander | Lister les écarts, attendre l'accord |
| Continuer sans un connecteur | S'arrêter à l'étape 1 tant qu'il manque |
