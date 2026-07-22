import json
import re
import geopandas as gpd

with open(r"D:\Loi_urgence_agricole\repo_clone\data\elus_votes.json", encoding="utf-8") as f:
    elus = json.load(f)

deputes = [e for e in elus if e["qualite"] == "Député"]
senateurs = [e for e in elus if e["qualite"] == "Sénateur"]

def circo_num(label):
    m = re.match(r"(\d+)", label)
    return int(m.group(1)) if m else None

deputes_by_id_circo = {}
for d in deputes:
    n = circo_num(d["circonscription"])
    id_circo = f"{d['code_departement']}{n:02d}"
    deputes_by_id_circo[id_circo] = d

# --- 1. Circonscriptions (deputies) ---
circo = gpd.read_file(
    r"D:\Loi_urgence_agricole\contours_circonscriptions_legislatives_03052022\circonscriptions_legislatives_030522.shp"
)
circo_5962 = circo[circo["dep"].isin(["59", "62"])].copy()
print(f"Circonscriptions trouvees pour 59/62 : {len(circo_5962)}")

missing = []
def join_depute(id_circo):
    d = deputes_by_id_circo.get(id_circo)
    if d is None:
        missing.append(id_circo)
        return None
    return d

records = []
for _, row in circo_5962.iterrows():
    d = join_depute(row["id_circo"])
    records.append(d)

if missing:
    print("ATTENTION - id_circo sans depute correspondant :", missing)

circo_5962["prenom"] = [r["prenom"] if r else None for r in records]
circo_5962["nom"] = [r["nom"] if r else None for r in records]
circo_5962["groupe_sigle"] = [r["groupe_sigle"] if r else None for r in records]
circo_5962["groupe_nom"] = [r["groupe_nom"] if r else None for r in records]
circo_5962["vote"] = [r["vote"] if r else None for r in records]
circo_5962["photo"] = [r["photo"] if r else None for r in records]
circo_5962["photo_credit"] = [r["photo_credit"] if r else None for r in records]
circo_5962["fiche_url"] = [r["fiche_url"] if r else None for r in records]
circo_5962["note"] = [r["note"] if r else None for r in records]
circo_5962 = circo_5962.rename(columns={"dep": "code_departement", "libelle": "libelle_circonscription"})

assert circo_5962.crs is not None
circo_5962 = circo_5962.to_crs(epsg=4326)

out_path = r"D:\Loi_urgence_agricole\repo_clone\data\geo\circonscriptions_59_62.geojson"
circo_5962.to_file(out_path, driver="GeoJSON")
print(f"Ecrit : {out_path} ({len(circo_5962)} features)")

# --- 2. Departements (senateurs, contexte) ---
dep = gpd.read_file(
    r"D:\Loi_urgence_agricole\ADE_4-0_GPKG_LAMB93_FXX-ED2026-07-20.gpkg", layer="departement"
)
dep_5962 = dep[dep["code_insee"].isin(["59", "62"])].copy()
dep_5962 = dep_5962[["code_insee", "nom_officiel", "geometry"]].rename(
    columns={"code_insee": "code_departement", "nom_officiel": "departement"}
)
# Simplifie les contours (tolerance en metres, CRS source Lambert-93) pour un usage web leger.
dep_5962["geometry"] = dep_5962["geometry"].simplify(tolerance=75, preserve_topology=True)

sen_stats = {}
for code in ["59", "62"]:
    sens = [s for s in senateurs if s["code_departement"] == code]
    votes = {"Pour": 0, "Contre": 0, "Abstention": 0, "Non votant": 0}
    for s in sens:
        votes[s["vote"]] = votes.get(s["vote"], 0) + 1
    sen_stats[code] = {
        "nb_senateurs": len(sens),
        "votes_pour": votes["Pour"],
        "votes_contre": votes["Contre"],
        "votes_abstention": votes["Abstention"],
    }

dep_5962["nb_senateurs"] = dep_5962["code_departement"].map(lambda c: sen_stats[c]["nb_senateurs"])
dep_5962["votes_pour"] = dep_5962["code_departement"].map(lambda c: sen_stats[c]["votes_pour"])
dep_5962["votes_contre"] = dep_5962["code_departement"].map(lambda c: sen_stats[c]["votes_contre"])
dep_5962["votes_abstention"] = dep_5962["code_departement"].map(lambda c: sen_stats[c]["votes_abstention"])

dep_5962 = dep_5962.to_crs(epsg=4326)

out_path2 = r"D:\Loi_urgence_agricole\repo_clone\data\geo\departements_59_62.geojson"
dep_5962.to_file(out_path2, driver="GeoJSON")
print(f"Ecrit : {out_path2} ({len(dep_5962)} features)")
