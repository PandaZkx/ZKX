# ZKX

trust le boug

ZKX est une appli Windows de conseil pour **Epic Seven** (et maintenant **Go Next!**) : tier list consensus, teams, stuff conseillé, fiches des 240 persos (compétences en FR/EN), import de ta box depuis Fribbels et mode overlay au-dessus du jeu.

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

## Go Next!

En haut de la fenêtre, passe de **Epic Seven** à **Go Next!** :

- **📚 Données** : persos (passifs), armes, objets et cartes connus d'après la page Steam et les notes de patch. « ＋ Ajouter » / « ✏ Corriger » pour compléter avec ce que tu vois en jeu (reste sur ton PC ; *Infos → Exporter mes ajouts* pour les envoyer).
- **⇄ Comparer** : 2 ou 3 éléments côte à côte.
- **🛠 Builds** : perso, 4 armes, objets clés, stats prioritaires ; ZKX note la cohérence et liste synergies et trous. Code `GN1.…` à partager.
- **🤝 Team up** : jusqu'à 4 joueurs, rôles couverts et ce qui manque.

- **★ Tier list** des persos et **📖 Guide & patchs** (guide intégré au jeu + notes de patch).
- **📸 Build d'un top 1** (onglet Builds) : ouvre une issue GitHub « [Build top 1] » avec le code du build. Pour le publier, mets le label **`build-ok`** sur l'issue : le robot (`.github/workflows/gn-build.yml`) l'ajoute à `data/gonext_community.json` et ferme l'issue ; ZKX le recharge en ligne.

Les données sont dans `data/gonext.json` (rechargé en ligne, pas besoin de nouvelle version). Les noms, descriptions, guides et notes de patch viennent des fichiers du jeu. Les ajouts exportés par les joueurs (`zkx-gonext-ajouts.json`) se recopient dans ce fichier ; pense à changer `updated`.

## Fiches persos

Clique sur un perso : la fiche commence par une vue **guide** (artefacts et sets classés, stats principales par pièce, sous-stats et stats à viser, 3 équipes conseillées, coût pour l'avoir et le monter), puis tous les détails (tiers par source, compétences, builds RTA…).

## Live draft

Onglet **⚔ Live draft** : note la draft RTA au fur et à mesure (pré-bans, picks 1-2-2-2-2-1, ban final). ZKX conseille à chaque étape avec les données RTA de la semaine (Epic7Coach) : force du perso, combos avec ton équipe, counters contre l'adversaire, ordre de pick habituel, et propose seulement tes persos si tu veux. Le bouton « Live Draft Epic7Coach » ouvre leur outil (leur modèle, ton compte, leurs limites).

Les données Epic7Coach sont récupérées deux fois par semaine par `.github/workflows/coach.yml` (`tools/coach_update.py`, une requête par seconde, pages publiques) dans `data/coach.json`, que l'appli recharge en ligne.

## Daily / Hebdo

Onglet **📅 Daily / Hebdo** : la liste de ce qu'il faut faire en priorité à chaque reset (jour, semaine, mois), avec des cases qui se décochent toutes seules, le compte à rebours avant le reset de ton serveur, des alertes sur les bannières qui se terminent ou arrivent, et tes propres tâches.

## Mes captures

Onglet **📸 Mes captures** : capture le jeu avec **Win + Maj + S**, puis **Ctrl + V** dans ZKX. Cadre le visage ou l'icône, choisis le perso ou l'artefact, enregistre. Depuis la fiche d'un perso, « 📸 Mettre ma capture » le présélectionne.

## Importer ta box

1. Dans l'optimiseur Fribbels : onglet *Importer* → importe ton stuff → **Save**.
2. Dans ZKX : charge le fichier `.json` obtenu.

**Import auto** (appli Windows) : clique sur « 🔄 Import auto Fribbels » et choisis ta sauvegarde une fois. Ensuite, chaque « Save » dans Fribbels met ZKX à jour tout seul.

**Repérage à l'écran** (appli Windows, client PC Stove) : « 👁 Repérer ma box à l'écran » lit les noms des héros affichés dans la fenêtre Epic Seven (capture de la fenêtre + lecture du texte sur ton PC, rien n'est envoyé) et coche tes persos tout seul. Ouvre le menu Héros et fais défiler ta liste.

ZKX ne lit pas le jeu et n'y touche pas. Ta box et tes images restent sur ton PC.

## Images

Les images des persos et des artefacts se téléchargent toutes seules (`data/images.json`, rechargé quand il change). Pour mettre à jour le pack partagé : mets les images dans un dossier avec `heroes/` et `artifacts/` (noms comme `abyssal-yufine.webp`), lance `python tools/images_pack.py <dossier>` puis envoie `data/images.json` et `data/images_v.json` sur GitHub. Pas besoin de nouvelle version de l'appli.


⚙ → *Images* : charge le pack e7-sidekick-resources (dossier ou .zip) ou tes propres `.png` / `.webp`, nommés comme le perso, l'artefact ou son code (`c1144.webp`).

## Pour publier une nouvelle version (dev)

1. Modifie `tools/template.html` / `tools/data.json`, lance `python tools/build.py`.
2. Monte la version dans `app/package.json` (ex. `1.3.0` → `1.4.0`) et mets à jour `CHANGELOG-release.md`.
3. Envoie sur GitHub (branche `main`).

C'est tout : GitHub voit la nouvelle version, construit `ZKX-Setup-X.Y.Z.exe` et crée la Release `vX.Y.Z` (avec `latest.yml` pour la mise à jour auto) en une dizaine de minutes. Tous les ZKX installés se mettent ensuite à jour tout seuls. Publier une Release à la main marche toujours aussi.

Sources des données : e7rtabot, Pocket Gamer, MMO Culture, Joytify, game.guide, TopUpLive, epic7db, Fribbels. Epic Seven est une marque de Smilegate ; ZKX est un projet de fan non officiel.
