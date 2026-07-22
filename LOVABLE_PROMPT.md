# Prompt à coller dans Lovable

---

Construis une application web (React + Vite + Tailwind) : un outil de recherche permettant à un lecteur de savoir comment a voté son député ou son sénateur du Nord ou du Pas-de-Calais sur la loi d'urgence pour la protection et la souveraineté agricoles.

**Contrainte de contexte essentielle : cette app sera intégrée en iframe dans un article du site de La Voix du Nord.** Le CMS bloque les balises `<script>` dans le corps de l'article, donc **aucun redimensionnement dynamique de l'iframe n'est possible** (pas de `postMessage`, pas de resize automatique côté parent). Conséquences à respecter dès la conception :
- L'app doit tenir dans une **hauteur totale bornée et prévisible** (viser une hauteur confortable autour de 700-800px maximum au total, hors ajustements mineurs). Pas de page qui grandit sans limite quand on ajoute des résultats : la zone de résultats (liste ou carte) doit avoir sa propre hauteur fixe avec défilement interne, pas le document entier.
- Utilise des **onglets** pour basculer entre les vues ("Recherche", "Carte des députés", "Carte des sénateurs" — voir plus bas), plutôt que d'empiler tout verticalement — ça multiplie la hauteur sinon.
- La largeur de l'iframe dans une colonne d'article fait typiquement **600 à 800px**, bien en dessous des seuils "desktop" habituels. Concrètement : **l'app sera quasi toujours affichée en mode "mobile/étroit", quel que soit l'appareil du lecteur.** Ce n'est pas un cas limite, c'est le mode principal à concevoir — tout doit être pleinement utilisable à la souris dans ce mode (dropdowns cliquables, pas de carrousel qui ne fonctionne qu'au doigt).
- Pour toute détection de largeur en JS, utilise `window.matchMedia` ou des media queries CSS réévaluées en continu — jamais une lecture unique de `window.innerWidth` dans un `useEffect` à dépendances vides (ça capture une valeur avant que l'iframe ait fini de prendre sa taille définitive).

## Données

Toutes les données sont statiques (un scrutin passé, pas de mise à jour en direct) et hébergées sur GitHub. **Utilise des URLs absolues pour tous les assets (JSON, GeoJSON, photos)** — jamais de chemin relatif, sinon il sera mal résolu dans le contexte iframe :

- Jeu de données principal (51 élus) : `https://raw.githubusercontent.com/JulienDepelchin/loi-urgence-agricole/main/data/elus_votes.json`
- Métadonnées des deux scrutins : `https://raw.githubusercontent.com/JulienDepelchin/loi-urgence-agricole/main/data/meta.json`
- Circonscriptions (carte, députés) : `https://raw.githubusercontent.com/JulienDepelchin/loi-urgence-agricole/main/data/geo/circonscriptions_59_62.geojson`
- Départements (carte, sénateurs) : `https://raw.githubusercontent.com/JulienDepelchin/loi-urgence-agricole/main/data/geo/departements_59_62.geojson`
- Photos : préfixer le champ `photo` de chaque élu par `https://raw.githubusercontent.com/JulienDepelchin/loi-urgence-agricole/main/data/` (ex. `photo: "photos/deputes/PA841515.jpg"` → `https://raw.githubusercontent.com/JulienDepelchin/loi-urgence-agricole/main/data/photos/deputes/PA841515.jpg`)

Le README du repo (`https://github.com/JulienDepelchin/loi-urgence-agricole`) documente le schéma complet de chaque fichier — lis-le en premier.

### Schéma résumé de `elus_votes.json`

Tableau de 51 objets : `prenom`, `nom`, `qualite` (`"Député"` ou `"Sénateur"`), `departement` (`"Nord"` ou `"Pas-de-Calais"`), `code_departement` (`"59"`/`"62"`), `circonscription` (texte type `"6e circonscription"`, vide pour les sénateurs), `groupe_sigle`, `groupe_nom`, `vote` (`"Pour"` / `"Contre"` / `"Abstention"` / `"Non votant"`), `photo`, `photo_credit`, `photo_source_url`, `fiche_url`, `note` (précision ponctuelle, ex. suppléance — vide la plupart du temps).

Les deux scrutins couverts : Assemblée nationale (scrutin n°8427, 20 juillet 2026, adopté 296 pour / 224 contre / 41 abstentions) et Sénat (scrutin n°340, 21 juillet 2026, adopté 214 pour / 111 contre / 20 abstentions) — ces chiffres nationaux sont dans `meta.json`, à afficher éventuellement en repère de contexte, mais l'app se concentre sur les 51 élus du Nord et du Pas-de-Calais.

## Fonctionnalités

### Onglet "Recherche"
- Barre de recherche par nom (insensible aux accents et à la casse).
- Filtres croisés : qualité (Député/Sénateur), département (Nord/Pas-de-Calais), groupe politique (liste dynamique déduite des données), vote (Pour/Contre/Abstention/Non votant).
- Compteurs Pour/Contre/Abstention/Non votant, recalculés en direct selon les filtres actifs (mini-barre de proportion par compteur).
- Liste/grille de cartes élu : photo (avec `photo_credit` affiché en petit), prénom + nom (lien vers `fiche_url`), qualité + territoire (circonscription pour les députés, "département (Sénat)" pour les sénateurs), badge groupe politique (sigle, infobulle = nom complet), badge vote coloré.
- Zone de résultats à hauteur fixe avec défilement interne (pas la page entière qui grandit).

Les cartes sont **deux onglets distincts, pas une carte unique combinant les deux** — députés et sénateurs n'ont pas la même échelle géographique (circonscription vs département entier), les mélanger sur un même fond rend les popups ambigus.

### Onglet "Carte des députés"
- Carte Leaflet avec fond **CartoDB Positron** (sobre, clair, gratuit — **jamais Mapbox ni Google Maps**, qui demandent une clé API facturée à l'usage).
- Une seule couche : les 33 circonscriptions (`circonscriptions_59_62.geojson`) en choroplèthe colorée par `vote` (les propriétés du député sont déjà jointes dans le GeoJSON, pas besoin de rejointure côté app). Utilise le composant `<GeoJSON>` de react-leaflet directement à partir du fichier chargé — ne reconstruis jamais un tracé à la main à partir de `geometry.coordinates` (le GeoJSON stocke `[longitude, latitude]`, l'inverse de ce qu'attend Leaflet nativement).
- Au clic sur une circonscription : popup ou panneau latéral avec les infos du député (photo, nom, groupe, vote, lien fiche officielle).
- **Désactive le zoom molette/pincement automatique de la carte**, avec un overlay "cliquer pour activer" avant d'autoriser l'interaction — sinon la carte capture le scroll de la page quand le lecteur fait défiler l'article au clavier tactile.

### Onglet "Carte des sénateurs"
- Même fond Leaflet/CartoDB Positron, même comportement de zoom désactivé par défaut avec overlay "cliquer pour activer".
- Une seule couche, à l'échelle du département : les 2 contours (`departements_59_62.geojson`) — **pas de subdivision par circonscription ici**, les sénateurs sont élus à l'échelle du département entier, afficher les circonscriptions serait trompeur. Colore éventuellement chaque département selon la tendance majoritaire de vote de ses sénateurs (`votes_pour` / `votes_contre` / `votes_abstention` déjà agrégés dans le GeoJSON), ou laisse en neutre avec juste le contour si une couleur "majoritaire" te semble trop réductrice à cette échelle.
- Au clic sur un département : popup ou panneau listant tous les sénateurs de ce département avec leur vote (obtenu en filtrant `elus_votes.json` sur `qualite === "Sénateur"` et `code_departement` — les agrégats `nb_senateurs`/`votes_pour`/`votes_contre`/`votes_abstention` du GeoJSON servent de résumé en tête de popup, le détail nominatif vient du filtrage).

## Style visuel

Palette "papier chaud / encre verte", pas un design IA générique :
- Fond `#f6f3ec` (papier chaud), cartes `#fffdf8`, texte principal `#22302b` (encre verte foncée), texte secondaire `#5b6b62`.
- Accent (liens, éléments actifs) : `#a8702c` (or/blé — clin d'œil au sujet agricole).
- Couleurs sémantiques de vote, distinctes de l'accent : Pour = vert `#3f7a52` (fond `#e3ede4`), Contre = rouille `#a8402f` (fond `#f2e2de`), Abstention = kaki `#8c7431` (fond `#ece5d2`), Non votant = gris `#7a7a74` (fond `#e7e5df`).
- Typographie : **Roboto partout** (titres, corps, badges) — c'est la police du site lavoixdunord.fr, l'app doit s'y fondre visuellement une fois en iframe, pas trancher avec une police différente. Charge-la via Google Fonts (poids 400/500/700). Chiffres des compteurs en police tabulaire (`font-variant-numeric: tabular-nums`).
- Prends en charge le mode sombre (le composant peut être affiché avec `prefers-color-scheme: dark` selon le thème du lecteur) avec une palette équivalente assombrie, mêmes principes de contraste.
- Badges/pills arrondis pour groupe politique (neutre, bordure fine) et vote (fond coloré selon la sémantique ci-dessus).

## Attribution et mentions

Pied de page compact : "Sources : Assemblée nationale, Sénat, Répertoire national des élus (RNE)" avec liens vers `https://www.assemblee-nationale.fr/dyn/17/scrutins/8427` et `https://www.senat.fr/scrutin-public/2025/scr2025-340.html`. Chaque photo doit afficher son `photo_credit` (Assemblée nationale ou Sénat).
