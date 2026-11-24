# Scénarios d'acceptation du pilote

Repo jouet : une CLI `wc.py` qui compte les mots. Besoin à deux exigences :

```markdown
### REQ-001 : compter les mots
Critère : `python3 wc.py f.txt` affiche le nombre de mots de `f.txt`.

### REQ-002 : fichier absent
Critère : `python3 wc.py absent.txt` affiche `introuvable` et sort en code 2.
```

| Id | Scénario | Mise en place | Attendu |
|---|---|---|---|
| S1 | Nominal | besoin ci-dessus, `/build` | matrice complète, `guard` vide, chaque test du testeur `échec` au départ et `passe` à l'intégration, PR ouverte, rapport lisible en quelques minutes, coût total noté |
| S2 | Test faux | après S1, modifier un test pour qu'il attende `Introuvable` | diagnostic `test`, corrigé par le testeur, `proves` repasse, incident au rapport |
| S3 | `REQ` ambiguë | ajouter `REQ-003 : gérer les gros fichiers` avec `Critère : rapide` | escalade `besoin` en tête du rapport avec options, REQ-001 et REQ-002 terminées |
| S4 | Boucle > 2 | spec et test contradictoires impossibles à concilier sans le besoin | trois cycles au plus, puis `REQ` « bloquée » au rapport, le reste terminé |
| S5 | Agent sans résultat (`agent_sans_resultat`) | `agent_timeout: 1s` pour un `dev` | `failed` avec la fin de la sortie, une relance au plus, aucune attente infinie |
| S6 | Conflit entre deux `dev` | plan à deux actions indépendantes qui modifient `wc.py` | `merge --abort`, seconde action relancée sur la branche intégrée, aucun `--force`, incident au rapport |
| S7 | Lanceur absent ou refusé | `agent_cmd: lanceur-inexistant` | arrêt au premier agent, message exact cité, aucune relance |
| S8 | Deux facturations | rejouer S1 avec `agent_cmd: claude -p` puis avec un lanceur sur clé API | même résultat, aucun fichier du plugin modifié |
| S9 | Fuite d'indépendance | prompt du testeur qui cite `wc.py`, ou testeur lancé sans les verrous du mode `ecrire` | `trace.py audit` liste la lecture, cas concernés relus, fuite au rapport |
| S10 | Escalade d'un dev | action `Complexité : simple` qu'un palier bas rate deux fois | une reprise au même palier, une au palier `Escalade`, puis `REQ` bloquée ; reprises visibles dans `trace.py cost` |
| S11 | Projet en sous-dossier | même repo jouet dans `outil/`, `projet_dir: outil` | worktrees créés depuis l'intégration, agents lancés dans `outil/`, `guard`, `proves` et `matrix` avec des chemins relatifs à `outil/` |
