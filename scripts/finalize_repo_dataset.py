import json

with open(r"D:\Loi_urgence_agricole\deputes_59_62_votes.json", encoding="utf-8") as f:
    deputes = json.load(f)
with open(r"D:\Loi_urgence_agricole\senateurs_59_62_votes.json", encoding="utf-8") as f:
    senateurs = json.load(f)

import re

def clean_circo(label):
    m = re.match(r"(\d+)", label)
    if m:
        n = m.group(1)
        suffix = "re" if n == "1" else "e"
        return f"{n}{suffix} circonscription"
    return label

def clean_departement(label):
    return label.replace("Pas-De-Calais", "Pas-de-Calais")

def clean_groupe(label):
    return re.sub(r"\s+", " ", label).strip()

SENAT_SIGLES = {
    "Les Républicains": "LR",
    "Union Centriste": "UC",
    "Communiste Républicain Citoyen et Écologiste - Kanaky": "CRCE-K",
    "Socialiste, Écologiste et Républicain": "SER",
    "Les Indépendants - République et Territoires": "LIRT",
    "Sénateurs ne figurant sur la liste d'aucun groupe": "NI",
}

final = []

for d in deputes:
    final.append({
        "prenom": d["prenom"],
        "nom": d["nom"],
        "qualite": "Député",
        "departement": clean_departement(d["departement"]),
        "code_departement": d["code_departement"],
        "circonscription": clean_circo(d["circonscription"]),
        "groupe_sigle": d["groupe_sigle"],
        "groupe_nom": clean_groupe(d["groupe_nom"]),
        "vote": d["vote"],
        "photo": f"photos/deputes/{d['pa_id']}.jpg",
        "photo_credit": "Assemblée nationale",
        "photo_source_url": d["photo_url"],
        "fiche_url": f"https://www.assemblee-nationale.fr/dyn/deputes/{d['pa_id']}",
        "note": d.get("note", ""),
    })

for s in senateurs:
    slug = s["senat_href"].rsplit("/", 1)[-1].replace(".html", "")
    final.append({
        "prenom": s["prenom"],
        "nom": s["nom"],
        "qualite": "Sénateur",
        "departement": clean_departement(s["departement"]),
        "code_departement": s["code_departement"],
        "circonscription": "",
        "groupe_sigle": SENAT_SIGLES.get(clean_groupe(s["groupe_nom"]), ""),
        "groupe_nom": clean_groupe(s["groupe_nom"]),
        "vote": s["vote"],
        "photo": f"photos/senateurs/{slug}.jpg",
        "photo_credit": "Sénat",
        "photo_source_url": s["photo_url"],
        "fiche_url": f"https://www.senat.fr{s['senat_href']}",
        "note": "",
    })

final.sort(key=lambda x: (x["code_departement"], x["qualite"] != "Député", x["nom"]))

with open(r"D:\Loi_urgence_agricole\repo_build\data\elus_votes.json", "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

meta = {
    "perimetre": "Députés et sénateurs élus dans le Nord (59) et le Pas-de-Calais (62)",
    "genere_le": "2026-07-22",
    "scrutin_assemblee_nationale": {
        "numero": 8427,
        "legislature": 17,
        "titre": "Scrutin public sur l'ensemble du projet de loi d'urgence pour la protection et la souveraineté agricoles (texte de la commission mixte paritaire)",
        "seance": "Deuxième séance du lundi 20 juillet 2026",
        "resultat": {"pour": 296, "contre": 224, "abstention": 41, "votants": 561, "suffrages_exprimes": 520, "majorite_absolue": 261, "adopte": True},
        "source_url": "https://www.assemblee-nationale.fr/dyn/17/scrutins/8427"
    },
    "scrutin_senat": {
        "numero": 340,
        "titre": "Scrutin sur l'ensemble du projet de loi d'urgence pour la protection et la souveraineté agricoles",
        "seance": "Séance du 21 juillet 2026",
        "resultat": {"pour": 214, "contre": 111, "abstention": 20, "votants": 345, "suffrages_exprimes": 325, "non_votants": 3, "adopte": True},
        "source_url": "https://www.senat.fr/scrutin-public/2025/scr2025-340.html"
    },
    "sources_elus": "Répertoire national des élus (RNE) — fichiers elus-deputes-dep.csv et elus-senateurs-sen.csv fournis par l'utilisateur",
    "avertissements": [
        "Deux erreurs de codification ont été identifiées et corrigées dans le fichier RNE fourni (elus-deputes-dep.csv), confirmées par l'utilisateur : (1) Charlotte Parmentier-Lecocq, députée de la 6e circonscription du Nord, y était rattachée par erreur à la Moselle (57) / 6e circonscription — elle a été réintégrée manuellement avec son vote (PA720480, HOR, Pour) ; (2) la 10e circonscription du Nord était absente et Vincent Ledoux (PA712014) y apparaissait à tort sous la 17e circonscription, dupliquant la ligne de Thierry Tesson — Vincent Ledoux (suppléant de Gérald Darmanin) a été repositionné sur la 10e circonscription et Thierry Tesson (PA841553, RN, Pour) rétabli comme seul titulaire de la 17e circonscription.",
        "Le fichier Scrutins.xml.zip initialement fourni ne couvrait que la 16e législature (2022-2024, scrutins jusqu'au n°4105) et n'a pas pu être utilisé pour ce scrutin de la 17e législature ; les données de vote ont été extraites directement des pages HTML officielles de l'Assemblée nationale et du Sénat.",
        "Les photos sont d'origine officielle (assemblee-nationale.fr / senat.fr) et sont fournies dans data/photos/ ; conserver le crédit photo indiqué dans chaque enregistrement (photo_credit)."
    ]
}

with open(r"D:\Loi_urgence_agricole\repo_build\data\meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"elus_votes.json: {len(final)} enregistrements")
print("meta.json ecrit")
