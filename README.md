# ZKX

trust le boug

ZKX est une appli Windows de conseil pour **Epic Seven** : tier list consensus, teams, stuff conseillé, fiches des 240 persos (compétences en FR/EN), import de ta box depuis Fribbels et mode overlay au-dessus du jeu.

## Télécharger

Va dans **[Releases](https://github.com/PandaZkx/ZKX/releases)**, télécharge le dernier **`ZKX-Setup-X.Y.Z.exe`** et lance-le : il installe ZKX avec un raccourci sur le bureau et dans le menu Démarrer. Pour le désinstaller : Paramètres Windows → Applications → ZKX.
Au premier lancement, Windows peut afficher « Windows a protégé votre ordinateur » (l'appli n'est pas signée) : *Informations complémentaires* → *Exécuter quand même*.

Ensuite, plus besoin de revenir ici : ZKX se met à jour tout seul (il télécharge la nouvelle version en fond et l'installe quand tu le fermes).

## Côté Windows

- Icône près de l'horloge (clic droit : overlay, captures, démarrage avec Windows, quitter). Fermer la fenêtre la garde en arrière-plan.
- **Ctrl + Maj + Z** partout : affiche/masque l'overlay au-dessus du jeu.
- Option « Lancer ZKX au démarrage de Windows ».
- Notification Windows quand une nouvelle version sort.

## Invocations

Onglet **🎰 Invocations** :

- **toutes les bannières du jeu** (alliance, drop rate up, limitées, collabs, classe, mystique, Moonlight) avec un avis (fonce / bon pull / passe ton tour), les chances et la garantie ;
- **« Où mettre tes bookmarks ? »** : comparatif de rentabilité entre les bannières (valeur du perso pour toi ÷ bookmarks moyens pour l'avoir) ;
- la **wish list conseillée** de l'invocation d'alliance (7 persos + 7 artefacts 5★), avec % de victoires, % de jeu et pré-ban en RTA.

Les bannières se mettent à jour toutes seules : un robot GitHub (`.github/workflows/banners.yml`) lit les annonces du jeu toutes les 6 h et met à jour `data/banners.json`, que l'appli recharge en ligne. Pour corriger une bannière à la main, modifie ce fichier et ajoute `"manual": true` à l'entrée.

## Fiches persos

Clique sur un perso : la fiche commence par une vue **guide** (artefacts et sets classés, stats principales par pièce, sous-stats et stats à viser, 3 équipes conseillées, coût pour l'avoir et le monter), puis tous les détails (tiers par source, compétences, builds RTA…).

## Daily / Hebdo

Onglet **📅 Daily / Hebdo** : la liste de ce qu'il faut faire en priorité à chaque reset (jour, semaine, mois), avec des cases qui se décochent toutes seules, le compte à rebours avant le reset de ton serveur, des alertes sur les bannières qui se terminent ou arrivent, et tes propres tâches.

## Mes captures

Onglet **📸 Mes captures** : capture le jeu avec **Win + Maj + S**, puis **Ctrl + V** dans ZKX. Cadre le visage ou l'icône, choisis le perso ou l'artefact, enregistre. Depuis la fiche d'un perso, « 📸 Mettre ma capture » le présélectionne.

## Importer ta box

1. Dans l'optimiseur Fribbels : onglet *Importer* → importe ton stuff → **Save**.
2. Dans ZKX : charge le fichier `.json` obtenu.

ZKX ne lit pas le jeu et n'y touche pas. Ta box et tes images restent sur ton PC.

## Images

⚙ → *Images* : charge le pack e7-sidekick-resources (dossier ou .zip) ou tes propres `.png` / `.webp`, nommés comme le perso, l'artefact ou son code (`c1144.webp`).

## Pour publier une nouvelle version (dev)

1. Modifie `tools/template.html` / `tools/data.json`, lance `python tools/build.py`.
2. Monte la version dans `app/package.json` (ex. `1.3.0` → `1.4.0`) et mets à jour `CHANGELOG-release.md`.
3. Envoie sur GitHub (branche `main`).

C'est tout : GitHub voit la nouvelle version, construit `ZKX-Setup-X.Y.Z.exe` et crée la Release `vX.Y.Z` (avec `latest.yml` pour la mise à jour auto) en une dizaine de minutes. Tous les ZKX installés se mettent ensuite à jour tout seuls. Publier une Release à la main marche toujours aussi.

Sources des données : e7rtabot, Pocket Gamer, MMO Culture, Joytify, game.guide, TopUpLive, epic7db, Fribbels. Epic Seven est une marque de Smilegate ; ZKX est un projet de fan non officiel.
