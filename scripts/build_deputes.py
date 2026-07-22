import csv, json, re, unicodedata

def normalize(s):
    s = s.upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Z\s\-']", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

deputes = []
with open(r"D:\Loi_urgence_agricole\elus-deputes-dep.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        dep_code = row["Code du département"].strip()
        if dep_code in ("59", "62"):
            deputes.append(row)

print(f"Deputes Nord/Pas-de-Calais trouves dans CSV: {len(deputes)}")
for d in deputes:
    print(d["Code du département"], d["Libellé de la circonscription législative"], d["Nom de l'élu"], d["Prénom de l'élu"])

with open(r"D:\Loi_urgence_agricole\deputes_59_62.json", "w", encoding="utf-8") as f:
    json.dump(deputes, f, ensure_ascii=False, indent=2)
