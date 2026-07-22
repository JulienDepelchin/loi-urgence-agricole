import csv, json, re, unicodedata
from collections import defaultdict

def norm(s):
    s = s.upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Z]", "", s)  # keep only letters, strip spaces/hyphens/apostrophes
    return s

# --- Load and dedupe CSV rows: keep the most recent mandate start per circonscription ---
rows_by_circo = {}
with open(r"D:\Loi_urgence_agricole\elus-deputes-dep.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        dep_code = row["Code du département"].strip()
        if dep_code not in ("59", "62"):
            continue
        circo_code = row["Code de la circonscription législative"].strip()
        existing = rows_by_circo.get(circo_code)
        if existing is None or row["Date de début du mandat"] > existing["Date de début du mandat"]:
            rows_by_circo[circo_code] = row

deputes = list(rows_by_circo.values())
print(f"Deputes retenus (apres dedup circo 17): {len(deputes)}")

# --- Load AN vote data ---
with open(r"D:\Loi_urgence_agricole\an_votes_8427.json", encoding="utf-8") as f:
    votes = json.load(f)

# Build lookup: normalized "NOM+PRENOM" concatenation isn't reliable due to order;
# instead build a lookup by normalized NOM, then check PRENOM within candidates
votes_by_nom = defaultdict(list)
for v in votes:
    full = v["nom_complet"]
    full = re.sub(r"^(M\.|Mme)\s*", "", full).strip()
    v["full_clean"] = full
    parts = full.split()
    # Try all splits: prenom = first k tokens, nom = rest (AN format is "Prenom Nom", sometimes multi-word)
    votes_by_nom[full].append(v)

matched = []
unmatched = []

for d in deputes:
    nom = d["Nom de l'élu"].strip()
    prenom = d["Prénom de l'élu"].strip()
    nom_n = norm(nom)
    prenom_n = norm(prenom)
    found = None
    for v in votes:
        full = v["full_clean"]
        full_n = norm(full)
        # full_n should contain both nom_n and prenom_n as substrings
        if nom_n in full_n and prenom_n in full_n:
            found = v
            break
    if found:
        matched.append((d, found))
    else:
        unmatched.append(d)

print(f"Matches trouves: {len(matched)} / {len(deputes)}")
print("\n--- NON TROUVES ---")
for d in unmatched:
    print(d["Code du département"], d["Libellé de la circonscription législative"], d["Nom de l'élu"], d["Prénom de l'élu"])

# Save matched results
output = []
for d, v in matched:
    output.append({
        "prenom": d["Prénom de l'élu"].strip(),
        "nom": d["Nom de l'élu"].strip(),
        "qualite": "Député",
        "departement": d["Libellé du département"].strip(),
        "code_departement": d["Code du département"].strip(),
        "circonscription": d["Libellé de la circonscription législative"].strip(),
        "groupe_sigle": v["groupe_sigle"],
        "groupe_nom": v["groupe_nom"],
        "vote": v["vote"],
        "pa_id": v["pa_id"],
    })

with open(r"D:\Loi_urgence_agricole\deputes_59_62_votes.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
