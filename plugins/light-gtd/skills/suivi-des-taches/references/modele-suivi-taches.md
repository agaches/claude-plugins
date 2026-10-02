# Modèle du fichier de suivi des tâches

Source unique pour la création du fichier (skill `gtd-install`) et pour la vérification de sa
structure. Tous les exemples sont fictifs, à remplacer par l'utilisateur.

`JJ/MM` = date du jour de création. Couleurs en RVB 0-1 (format de l'API Google Sheets).

## Onglet `Suivi`

Valeurs (A1:E9) :

| | A | B | C | D | E |
|---|---|---|---|---|---|
| 1 | Actions | Deadline | Statut | Contexte | JJ/MM |
| 2 | Tâches récurrentes | | | | |
| 3 | Perso : exemple de routine (à remplacer) | Chaque jour | Routine | Maison | |
| 4 | Actions perso | | | | |
| 5 | Perso : exemple de tâche (à remplacer) | JJ/MM/AAAA (dans 7 jours) | En cours | IT | à faire : première action |
| 6 | Actions pro | | | | |
| 7 | Pro : exemple de tâche pro (à remplacer) | | En cours | IT | à faire : première action |
| 8 | Global | | | | init fichier |

Sans section pro (choix fait à l'installation) : supprimer les lignes 6 et 7, Global passe en ligne 6.

Mise en forme :

| Zone | Format |
|---|---|
| A1 | fond `{red: 0.714, green: 0.843, blue: 0.659}` (vert clair), gras |
| B1:D1 | fond `{red: 0.812, green: 0.886, blue: 0.953}` (bleu clair), gras |
| En-têtes de jours (E1 et suivants) | fond `{red: 1, green: 0.949, blue: 0.8}` (jaune clair), gras |
| Lignes de section (A:E) | fond `{red: 0.898, green: 0.898, blue: 0.898}` (gris clair), gras |
| Ligne 1 | figée (`gridProperties.frozenRowCount: 1`) |
| Colonne A | figée (`gridProperties.frozenColumnCount: 1`), largeur 380 px |
| Colonnes de jours | largeur 220 px, retour à la ligne automatique |
| C2:C | validation liste : `En cours`, `En attente`, `Routine` (avertissement, pas de rejet) |
| D2:D | validation liste : contextes de la configuration (avertissement, pas de rejet) |

## Onglet `Terminées`

| | A | B | C |
|---|---|---|---|
| 1 | Terminées au total | `=COUNTA(A4:A)-1` | |
| 2 | Terminées cette semaine | `=COUNTIFS(B4:B;">="&(TODAY()-WEEKDAY(TODAY();2)+1);B4:B;"<="&TODAY())` | |
| 3 | | | |
| 4 | Tâche | Date de fin | Deadline initiale |

A1:A2 en gras. A4:C4 gras, fond gris clair. Ligne 4 figée. Les formules s'écrivent comme
formules (pas comme texte). Le séparateur d'arguments suit la langue du tableur
(`properties.locale`) : `;` pour `fr_FR` (testé), `,` pour `en_US`. Vérifier que B1 et B2
affichent un nombre et non une erreur.

Écriture des valeurs : dates (`JJ/MM`, `JJ/MM/AAAA`) envoyées en texte, le tableur les convertit
en vraies dates (testé en `fr_FR`). Ne pas forcer de format texte sur ces colonnes.

## Onglet `README`

Une ligne par paragraphe, colonne A. Titres en gras.

```
Suivi des tâches : mode d'emploi

Principe
Ce fichier est le seul endroit de capture des tâches. Elles sont dictées au fil de l'eau à Claude, qui les range dans l'onglet Suivi.
Une ligne correspond à une tâche globale : un sujet à mener jusqu'au bout, pas une action isolée.
Une colonne correspond à un jour. Claude ajoute la colonne du jour quand c'est nécessaire.

Sections de l'onglet Suivi (de haut en bas)
1. Tâches récurrentes : les routines quotidiennes (préfixe Perso : ).
2. Actions perso : les tâches personnelles (préfixe Perso : ).
3. Actions pro : les tâches professionnelles (préfixe Pro : ).
4. Global : dernière ligne, statut d'ensemble du fichier.

Colonnes de l'onglet Suivi
Actions : la tâche globale, préfixée Perso : ou Pro : . Exemple : Perso : faire réparer le lave-linge.
Deadline : la date limite (JJ/MM/AAAA), ou Chaque jour pour les routines.
Statut : En cours, En attente ou Routine.
Contexte : où ou avec quoi l'action se fait (voir Configuration).
Colonne d'un jour : ce qui a été fait ce jour-là, puis la prochaine action.

Règles de saisie
Dans chaque case : ce qui a été fait, puis la prochaine action précédée de « à faire : ». Exemple : mail envoyé, à faire : attendre la réponse.
Si rien n'a été fait ce jour-là : seulement la prochaine action. Exemple : à faire : appeler pour prendre rendez-vous.
Nouvelle tâche : à la fin de sa section, avec deadline, statut, contexte et préfixe.
Tâche finie : déplacée dans l'onglet Terminées avec sa date de fin.
Colonnes de jours de plus de 2 mois : supprimées pendant la revue hebdo, après report de la dernière action des tâches immobiles. L'historique des versions (Fichier > Historique des versions) garde tout.

Configuration
Agenda des tâches : Tâches
Contextes : Appels, IT, Maison, Pro, Dehors, Achats, Corvées, Partout
Section Actions pro : oui

Marqueur (ne pas modifier) : light-gtd-fichier-de-suivi
```

Le bloc « Configuration » est lu par toutes les skills du plugin : garder le format
`Clé : valeur`, une clé par ligne.

La ligne « Marqueur » permet aux skills de retrouver le fichier par une recherche plein texte
Drive, quel que soit son titre : l'écrire telle quelle, en dernière ligne de la colonne A.

## Vérification de structure (fichier existant)

Contrôler, sans rien modifier :

1. Les trois onglets existent (`Suivi`, `Terminées`, `README`).
2. Suivi, ligne 1 : `Actions`, `Deadline`, `Statut`, `Contexte`, puis des dates.
3. Suivi, colonne A : titres `Tâches récurrentes`, `Actions perso`, (`Actions pro`), `Global`, dans cet ordre, `Global` en dernier.
4. Terminées, ligne 4 : `Tâche`, `Date de fin`, `Deadline initiale`.
5. README : bloc `Configuration` présent.
6. README : ligne `Marqueur (ne pas modifier) : light-gtd-fichier-de-suivi` présente (absente
   des fichiers créés par la v0.1).

Chaque écart est listé avec la correction proposée. Aucune correction sans accord, aucun
contenu effacé.
