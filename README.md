# Loi d'urgence agricole — Vote des élus du Nord et du Pas-de-Calais

Jeu de données et prototype pour un moteur de recherche permettant de savoir comment ont voté les
députés et sénateurs élus dans le Nord (59) et le Pas-de-Calais (62) lors de l'adoption du **projet
de loi d'urgence pour la protection et la souveraineté agricoles**.

Deux scrutins couverts :
- **Assemblée nationale**, scrutin n°8427, deuxième séance du lundi 20 juillet 2026 (296 pour, 224
  contre, 41 abstentions, 561 votants — adopté).
- **Sénat**, scrutin n°340, séance du 21 juillet 2026 (214 pour, 111 contre, 20 abstentions, 345
  votants — adopté).

## Structure du repo

```
data/
  elus_votes.json     Jeu de données final (51 élus) — à consommer par l'application
  meta.json           Métadonnées des deux scrutins, sources, avertissements méthodologiques
  photos/
    deputes/           33 portraits officiels (Assemblée nationale), nommés par identifiant PA
    senateurs/         18 portraits officiels (Sénat), nommés par slug sénat.fr
  geo/
    circonscriptions_59_62.geojson   33 circonscriptions législatives (WGS84), vote joint par circo
    departements_59_62.geojson       2 départements (WGS84), agrégats des votes sénatoriaux

sources/               Sources brutes utilisées pour construire le jeu de données (traçabilité)
  elus-deputes-dep.csv         RNE — députés (fourni par l'utilisateur)
  elus-senateurs-sen.csv       RNE — sénateurs (fourni par l'utilisateur)
  an_scrutin_8427.html         Page HTML brute du scrutin Assemblée (détail nominatif par groupe)
  senat_scrutin_340.html       Page HTML brute du scrutin Sénat (détail nominatif + photos)
  senat_scrutin_340_votes_bruts.json   Export JSON brut des votes Sénat (par matricule)

  Fonds de carte sources (non versionnés, trop volumineux — voir note ci-dessous) :
  contours_circonscriptions_legislatives_03052022/   Insee/IGN, circonscriptions légis. (03/05/2022)
  ADE_4-0_GPKG_LAMB93_FXX-ED2026-07-20.gpkg          IGN Admin Express, départements (20/07/2026)

scripts/                Scripts Python ayant servi à construire data/ (reproductibilité)

prototype/
  moteur_recherche_vote_agricole.html   Prototype fonctionnel (recherche + filtres), à titre de
                                         référence de comportement pour la reconstruction dans Lovable
```

## Schéma de `data/elus_votes.json`

Tableau de 51 objets, un par élu :

| Champ              | Description                                                              |
|---------------------|---------------------------------------------------------------------------|
| `prenom`, `nom`     | Identité de l'élu                                                        |
| `qualite`           | `"Député"` ou `"Sénateur"`                                                |
| `departement`       | `"Nord"` ou `"Pas-de-Calais"`                                             |
| `code_departement`  | `"59"` ou `"62"`                                                          |
| `circonscription`   | Circonscription législative (députés uniquement ; vide pour les sénateurs, élus à l'échelle du département) |
| `groupe_sigle`      | Sigle du groupe politique (ex. `RN`, `EPR`, `LFI-NFP`, `LR`, `UC`…)       |
| `groupe_nom`        | Nom complet du groupe politique                                          |
| `vote`              | `"Pour"`, `"Contre"`, `"Abstention"` ou `"Non votant"`                    |
| `photo`             | Chemin relatif vers le portrait, depuis `data/` (ex. `photos/deputes/PA841515.jpg`) |
| `photo_credit`      | `"Assemblée nationale"` ou `"Sénat"` — à afficher en légende de la photo  |
| `photo_source_url`  | URL d'origine de la photo, pour référence                                |
| `fiche_url`         | Lien vers la fiche officielle de l'élu (assemblee-nationale.fr / senat.fr) |
| `note`              | Précision ponctuelle sur le mandat (ex. suppléance) — vide pour la plupart des élus |

## Fonds de carte (`data/geo/`)

Deux fichiers GeoJSON (WGS84 / EPSG:4326, prêts pour Leaflet, Mapbox GL ou tout composant carto web) :

- **`circonscriptions_59_62.geojson`** — 33 circonscriptions législatives (21 pour le Nord, 12 pour
  le Pas-de-Calais), contours simplifiés Insee/IGN. Chaque feature porte déjà les propriétés du
  député correspondant (`prenom`, `nom`, `groupe_sigle`, `groupe_nom`, `vote`, `photo`,
  `photo_credit`, `fiche_url`, `note`) — pas besoin de rejointure côté application pour afficher une
  carte colorée par vote avec infobulle par circonscription.
- **`departements_59_62.geojson`** — les 2 départements (contours IGN Admin Express, simplifiés à 75 m
  pour l'usage web). Les sénateurs n'ayant pas de circonscription, cette couche ne porte que des
  agrégats (`nb_senateurs`, `votes_pour`, `votes_contre`, `votes_abstention`) ; le détail nominatif
  des sénateurs par département s'obtient en filtrant `data/elus_votes.json` sur `qualite = "Sénateur"`
  et `code_departement`.

Les fonds de carte sources (shapefile Insee/IGN des circonscriptions et le GeoPackage Admin Express
complet, ~1,1 Go) ne sont **pas** versionnés dans ce repo — trop volumineux et hors périmètre une
fois le GeoJSON dérivé généré. Le script `scripts/build_geo_data.py` documente comment ils ont été
transformés, si un recalcul est nécessaire.

## Avertissements méthodologiques (voir aussi `data/meta.json`)

Deux erreurs de codification du fichier RNE fourni (`elus-deputes-dep.csv`) ont été identifiées et
corrigées, avec confirmation directe de l'utilisateur :

- **Charlotte Parmentier-Lecocq** (6ᵉ circonscription du Nord) était rattachée par erreur à la
  Moselle (57) / 6ᵉ circonscription dans le RNE — sa ligne (`PA720480`, groupe HOR, vote Pour) a été
  réintégrée manuellement au Nord.
- La **10ᵉ circonscription du Nord** était absente du RNE, et **Vincent Ledoux** (`PA712014`) y
  apparaissait à tort sous la 17ᵉ circonscription, dupliquant la ligne de Thierry Tesson. Vincent
  Ledoux (suppléant de Gérald Darmanin, cf. champ `note`) a été repositionné sur la 10ᵉ
  circonscription ; **Thierry Tesson** (`PA841553`, groupe RN, vote Pour) a été rétabli comme seul
  titulaire de la 17ᵉ circonscription.
- Aucun élu du périmètre Nord / Pas-de-Calais n'était classé « non votant » sur les deux scrutins.

### Vérification complète des 51 fiches officielles

Après ces deux corrections, chacune des 51 fiches (nom, département, circonscription pour les
députés, groupe politique) a été revérifiée individuellement contre sa page officielle
(assemblee-nationale.fr / senat.fr). Aucun autre écart de rattachement n'a été trouvé. Deux sigles
de groupes du Sénat, initialement déduits par erreur, ont été corrigés d'après les URLs et intitulés
utilisés par senat.fr lui-même :
- « Socialiste, Écologiste et Républicain » → sigle **SOC** (et non SER) — concerne Patrick Kanner
  et Audrey Linkenheld.
- « Les Indépendants - République et Territoires » → sigle **RTLI** (et non LIRT) — concerne
  Marie-Claude Lermytte et Dany Wattebled.

## Pour Lovable / reconstruction de l'application

- Le jeu de données est statique (un scrutin passé, pas de mise à jour en direct) : `data/elus_votes.json`
  peut être importé tel quel comme source de données de l'application.
- Les photos sont déjà téléchargées localement dans `data/photos/` — ne pas re-pointer vers les CDN
  externes assemblee-nationale.fr / senat.fr en production (ces URLs restent disponibles dans
  `photo_source_url` à titre de secours ou de crédit uniquement).
- `prototype/moteur_recherche_vote_agricole.html` montre le comportement attendu : recherche par nom
  (insensible aux accents), filtres croisés (qualité / département / groupe politique / vote), et
  compteurs Pour/Contre/Abstention/Non votant recalculés selon les filtres actifs.
- Pour la carte : afficher `data/geo/circonscriptions_59_62.geojson` colorée par `vote` pour les
  députés, et `data/geo/departements_59_62.geojson` en superposition (ou vue basculée) pour donner un
  repère géographique aux sénateurs, dont le mandat n'est pas circonscrit à une portion du département.
