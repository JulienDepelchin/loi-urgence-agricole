import csv, json, re, unicodedata

def norm(s):
    s = s.upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Z]", "", s)
    return s

with open(r"D:\Loi_urgence_agricole\elus-senateurs-sen.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    senateurs = [r for r in reader if r["Code du département"].strip() in ("59", "62")]

print(f"Senateurs Nord/Pas-de-Calais dans CSV: {len(senateurs)}")

with open(r"D:\Loi_urgence_agricole\senat_group_records.json", encoding="utf-8") as f:
    group_records = json.load(f)
with open(r"D:\Loi_urgence_agricole\senat_detail_records.json", encoding="utf-8") as f:
    detail_records = json.load(f)

for r in group_records:
    r["name_norm"] = norm(r["name_text"])
for r in detail_records:
    r["name_norm"] = norm(r["name_text"])

matched = []
unmatched = []

for s in senateurs:
    nom = s["Nom de l'élu"].strip()
    prenom = s["Prénom de l'élu"].strip()
    nom_n = norm(nom)
    prenom_n = norm(prenom)

    g_found = None
    for r in group_records:
        if nom_n in r["name_norm"] and prenom_n in r["name_norm"]:
            g_found = r
            break

    d_found = None
    for r in detail_records:
        if nom_n in r["name_norm"] and prenom_n in r["name_norm"]:
            d_found = r
            break

    if g_found and d_found:
        matched.append((s, g_found, d_found))
    else:
        unmatched.append((s, g_found, d_found))

print(f"Matches complets: {len(matched)} / {len(senateurs)}")
print("\n--- INCOMPLETS ---")
for s, g, d in unmatched:
    print(s["Code du département"], s["Nom de l'élu"], s["Prénom de l'élu"], "groupe:", bool(g), "detail:", bool(d))

output = []
for s, g, d in matched:
    output.append({
        "prenom": s["Prénom de l'élu"].strip(),
        "nom": s["Nom de l'élu"].strip(),
        "qualite": "Sénateur",
        "departement": s["Libellé du département"].strip(),
        "code_departement": s["Code du département"].strip(),
        "groupe_nom": g["groupe_nom"],
        "vote": d["vote"],
        "senat_href": d["href"],
        "senat_photo": d["photo"],
    })

with open(r"D:\Loi_urgence_agricole\senateurs_59_62_votes.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
