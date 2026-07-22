import json

# Corrections following user-confirmed ground truth for two RNE data errors:
# 1. Charlotte PARMENTIER-LECOCQ (6e circo du Nord) was miscoded in the RNE export
#    under Moselle (57) / 6e circonscription instead of Nord (59) / 6e circonscription.
# 2. Vincent LEDOUX was miscoded under Nord 17e circonscription (duplicating Thierry
#    TESSON's row) when he actually holds the Nord 10e circonscription, as suppléant
#    of Gérald Darmanin. Thierry TESSON is the sole, uncontested holder of the 17e circo.

with open(r"D:\Loi_urgence_agricole\deputes_59_62_votes.json", encoding="utf-8") as f:
    deputes = json.load(f)

for d in deputes:
    if d["nom"] == "LEDOUX":
        d["circonscription"] = "10Ème Circonscription"
        d["note"] = "Suppléant de Gérald Darmanin"

deputes.append({
    "prenom": "Thierry",
    "nom": "TESSON",
    "qualite": "Député",
    "departement": "Nord",
    "code_departement": "59",
    "circonscription": "17Ème Circonscription",
    "groupe_sigle": "RN",
    "groupe_nom": "Rassemblement National",
    "vote": "Pour",
    "pa_id": "PA841553",
    "photo_url": "https://www.assemblee-nationale.fr/dyn/static/tribun/17/photos/carre/841553.jpg",
})

deputes.append({
    "prenom": "Charlotte",
    "nom": "PARMENTIER-LECOCQ",
    "qualite": "Député",
    "departement": "Nord",
    "code_departement": "59",
    "circonscription": "6Ème Circonscription",
    "groupe_sigle": "HOR",
    "groupe_nom": "Horizons & Indépendants",
    "vote": "Pour",
    "pa_id": "PA720480",
    "photo_url": "https://www.assemblee-nationale.fr/dyn/static/tribun/17/photos/carre/720480.jpg",
})

with open(r"D:\Loi_urgence_agricole\deputes_59_62_votes.json", "w", encoding="utf-8") as f:
    json.dump(deputes, f, ensure_ascii=False, indent=2)

print(f"Total deputes apres correction: {len(deputes)}")
