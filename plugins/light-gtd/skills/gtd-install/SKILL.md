---
name: gtd-install
description: Initialise light-gtd pour l'utilisateur. À utiliser quand l'utilisateur lance /gtd-install, veut installer, configurer ou réparer son suivi des tâches, ou quand son fichier de suivi des tâches est introuvable dans son Google Drive ("installe le suivi des tâches", "crée mon fichier de tâches", "vérifie que mon fichier de tâches est en ordre").
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

### 2. Fichier existant

Chercher le fichier de suivi comme décrit dans la skill `suivi-des-taches` (§1) : par son
marqueur, sinon par le titre `suivi_taches` (fichier créé par la v0.1, sans marqueur).

- **Trouvé (1)** : lire ses valeurs de Configuration, elles servent de défauts à l'étape 3.
- **Plusieurs** : demander lequel garder ; ne rien supprimer.
- **Absent** : le fichier sera créé à l'étape 4.

### 3. Préférences

Demander en un seul message, avec les défauts :

- nom du fichier de suivi (défaut `suivi_taches`) ; fichier existant : son titre actuel ;
- nom de l'agenda des tâches (défaut `Tâches`) ;
- contextes (défaut `Appels, IT, Maison, Pro, Dehors, Achats, Corvées, Partout`) ;
- section Actions pro (défaut oui).

« OK » ou « par défaut » = garder les défauts.

### 4. Fichier de suivi

- **Existant** : appliquer la « Vérification de structure » du modèle (marqueur compris),
  présenter les écarts et les corrections proposées, n'appliquer qu'après accord. Mettre à jour
  le bloc Configuration du README si les préférences ont changé. Nom changé : renommer le
  fichier dans Drive, après accord ; le marqueur permet de le retrouver sous son nouveau nom.
- **Absent** : le créer d'après le modèle (skill `suivi-des-taches`, fichier
  `references/modele-suivi-taches.md`) :
  1. créer un Google Sheets vide titré du nom choisi ;
  2. renommer la première feuille en `Suivi` (son nom dépend de la langue, `Feuille 1` ou
     `Sheet1`, mais son `sheetId` est `0`), ajouter `Terminées` et `README` ;
  3. écrire les valeurs des trois onglets, marqueur compris (formules de Terminées écrites comme
     formules) ;
  4. appliquer la mise en forme et les validations ;
  5. relire les trois onglets et comparer au modèle ; corriger ce qui manque.

### 5. Agenda

Retrouver l'agenda des tâches par son nom dans la liste des agendas, et garder son identifiant.
Absent : le connecteur ne sait pas créer d'agenda. Proposer à l'utilisateur de le créer dans
Google Agenda puis de relancer, ou de choisir un agenda existant (l'agenda principal par
défaut) ; écrire le nom retenu dans la Configuration.

Chercher l'événement « Revue hebdo des tâches (GTD) » **dans cet agenda** : lister ses événements
avec la recherche plein texte `Revue hebdo`. La recherche d'événements « générale » ne couvre que
l'agenda principal et ne le trouverait pas. Absent : le créer dans cet agenda, récurrent
(`RRULE:FREQ=WEEKLY;BYDAY=SA`) de 9h00 à 9h30, fuseau de l'agenda, à partir du prochain samedi,
description : `Lancer /gtd-revue dans Claude.`

### 6. Résumé

Terminer par :

- le lien vers le fichier ;
- ce qui a été créé, corrigé ou laissé tel quel ;
- le fichier peut être renommé ou déplacé dans Drive : il est retrouvé par son marqueur, à ne
  pas effacer de l'onglet README ;
- deux exemples pour démarrer :
  « ajoute : renouveler le passeport avant fin novembre » et « fais-moi le point ».

## Erreurs fréquentes

| Erreur | Correction |
|---|---|
| Créer un second fichier de suivi alors qu'un existe | Toujours chercher (marqueur, puis `suivi_taches`) avant de créer |
| Oublier le marqueur dans le README | Les autres skills ne retrouveraient pas un fichier renommé : vérifier sa présence à la relecture |
| Créer la revue en double | Chercher l'événement dans l'agenda des tâches, pas dans l'agenda principal |
| Formules de Terminées écrites en texte (`'=COUNTA…`) | Les écrire comme formules, vérifier que B1 et B2 affichent un nombre |
| Corriger la structure d'un fichier existant sans demander | Lister les écarts, attendre l'accord |
| Continuer sans un connecteur | S'arrêter à l'étape 1 tant qu'il manque |
