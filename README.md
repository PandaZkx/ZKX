# ZKX

trust le boug

ZKX est une appli Windows de conseil pour **Epic Seven** : tier list consensus, teams, stuff conseillé, fiches des 240 persos (compétences en FR/EN), import de ta box depuis Fribbels et mode overlay au-dessus du jeu.

## Télécharger

Va dans **[Releases](https://github.com/PandaZkx/ZKX/releases)**, télécharge le dernier **`ZKX-Setup-X.Y.Z.exe`** et lance-le : il installe ZKX avec un raccourci sur le bureau et dans le menu Démarrer. Pour le désinstaller : Paramètres Windows → Applications → ZKX.
Au premier lancement, Windows peut afficher « Windows a protégé votre ordinateur » (l'appli n'est pas signée) : *Informations complémentaires* → *Exécuter quand même*.

L'appli vérifie toute seule s'il y a une nouvelle version (⚙ → Application).

## Côté Windows

- Icône près de l'horloge (clic droit : overlay, captures, démarrage avec Windows, quitter). Fermer la fenêtre la garde en arrière-plan.
- **Ctrl + Maj + Z** partout : affiche/masque l'overlay au-dessus du jeu.
- Option « Lancer ZKX au démarrage de Windows ».
- Notification Windows quand une nouvelle version sort.

## Mes captures

Onglet **📸 Mes captures** : capture le jeu avec **Win + Maj + S**, puis **Ctrl + V** dans ZKX. Cadre le visage ou l'icône, choisis le perso ou l'artefact, enregistre. Depuis la fiche d'un perso, « 📸 Mettre ma capture » le présélectionne.

## Importer ta box

1. Dans l'optimiseur Fribbels : onglet *Importer* → importe ton stuff → **Save**.
2. Dans ZKX : charge le fichier `.json` obtenu.

ZKX ne lit pas le jeu et n'y touche pas. Ta box et tes images restent sur ton PC.

## Images

⚙ → *Images* : charge le pack e7-sidekick-resources (dossier ou .zip) ou tes propres `.png` / `.webp`, nommés comme le perso, l'artefact ou son code (`c1144.webp`).

## Pour publier une nouvelle version (dev)

1. `python tools/build.py` pour régénérer `app/index.html`, puis envoie les changements.
2. Sur GitHub : *Releases* → *Draft a new release* → tag `v1.0.1` (*Create new tag*) → *Publish release*.

GitHub Actions construit l'installateur et ajoute `ZKX-Setup-1.0.1.exe` à la Release en quelques minutes.

Sources des données : e7rtabot, Pocket Gamer, MMO Culture, Joytify, game.guide, TopUpLive, epic7db, Fribbels. Epic Seven est une marque de Smilegate ; ZKX est un projet de fan non officiel.
