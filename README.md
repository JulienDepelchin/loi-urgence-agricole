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
  elus_votes.json     Jeu de données final (49 élus) — à consommer par l'application
  meta.json           Métadonnées des deux scrutins, sources, avertissements méthodologiques
  photos/
    deputes/           31 portraits officiels (Assemblée nationale), nommés par identifiant PA
    senateurs/         18 portraits officiels (Sénat), nommés par slug sénat.fr

sources/               Sources brutes utilisées pour construire le jeu de données (traçabilité)
  elus-deputes-dep.csv         RNE — députés (fourni par l'utilisateur)
  elus-senateurs-sen.csv       RNE — sénateurs (fourni par l'utilisateur)
  an_scrutin_8427.html         Page HTML brute du scrutin Assemblée (détail nominatif par groupe)
  senat_scrutin_340.html       Page HTML brute du scrutin Sénat (détail nominatif + photos)
  senat_scrutin_340_votes_bruts.json   Export JSON brut des votes Sénat (par matricule)

scripts/                Scripts Python ayant servi à construire data/ (reproductibilité)

prototype/
  moteur_recherche_vote_agricole.html   Prototype fonctionnel (recherche + filtres), à titre de
                                         référence de comportement pour la reconstruction dans Lovable
```

## Schéma de `data/elus_votes.json`

Tableau de 49 objets, un par élu :

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

## Avertissements méthodologiques (voir aussi `data/meta.json`)

- Les **6ᵉ et 10ᵉ circonscriptions du Nord** sont absentes du fichier RNE fourni
  (`elus-deputes-dep.csv`) — siège vacant ou export incomplet à la date de récupération, à vérifier
  avant toute publication.
- La **17ᵉ circonscription du Nord** liste deux titulaires dans le RNE (Thierry Tesson, mandat
  depuis le 08/07/2024, puis Vincent Ledoux, mandat depuis le 24/01/2025). Le titulaire retenu dans
  `elus_votes.json` est celui dont le mandat a débuté le plus récemment (Vincent Ledoux).
- Aucun élu du périmètre Nord / Pas-de-Calais n'était classé « non votant » sur les deux scrutins.

## Pour Lovable / reconstruction de l'application

- Le jeu de données est statique (un scrutin passé, pas de mise à jour en direct) : `data/elus_votes.json`
  peut être importé tel quel comme source de données de l'application.
- Les photos sont déjà téléchargées localement dans `data/photos/` — ne pas re-pointer vers les CDN
  externes assemblee-nationale.fr / senat.fr en production (ces URLs restent disponibles dans
  `photo_source_url` à titre de secours ou de crédit uniquement).
- `prototype/moteur_recherche_vote_agricole.html` montre le comportement attendu : recherche par nom
  (insensible aux accents), filtres croisés (qualité / département / groupe politique / vote), et
  compteurs Pour/Contre/Abstention/Non votant recalculés selon les filtres actifs.
