import re, json, unicodedata
from bs4 import BeautifulSoup

def norm(s):
    s = s.upper()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^A-Z]", "", s)
    return s

with open(r"D:\Loi_urgence_agricole\scrutin_senat_340_raw.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# --- Part 1: "Analyse par groupes politiques" -> group name + vote category + names (plain text) ---
group_records = []  # list of dicts: name_text, groupe_nom, vote

accordion_items = soup.select("h2")
groupes_h2 = None
for h2 in accordion_items:
    if "Analyse par groupes" in h2.get_text():
        groupes_h2 = h2
        break

groupes_accordion = groupes_h2.find_next_sibling("div", class_="accordion")

for item in groupes_accordion.find_all("div", class_="accordion-item", recursive=False):
    title_el = item.find("h3", class_="accordion-title")
    groupe_nom_full = title_el.get_text(" ", strip=True) if title_el else ""
    groupe_nom = re.sub(r"\s*:\s*\d+.*$", "", groupe_nom_full).replace("Groupe ", "").strip()

    body = item.find("div", class_="accordion-body")
    if not body:
        continue
    ul = body.find("ul")
    for li in ul.find_all("li", recursive=False):
        b = li.find("b")
        if not b:
            continue
        vote_label = b.get_text(strip=True)
        # text after the <b> tag within this li
        full_text = li.get_text(" ", strip=True)
        names_text = full_text.split(":", 1)[-1] if ":" in full_text else full_text
        # Remove civility markers M./Mme/MM./Mmes and split on commas
        names_text = re.sub(r"\bMM?\.\s*|\bMmes?\s*", "", names_text)
        # split on comma, but names might contain "Président du Sénat" etc trailing after comma - keep as is, filter later
        parts = [p.strip() for p in names_text.split(",") if p.strip()]
        for p in parts:
            # strip trailing role descriptions like "Président du Sénat" / "Président de séance"
            p_clean = re.sub(r",?\s*(Pr[ée]sident(e)?\s+d[eu].*)$", "", p).strip()
            if not p_clean:
                continue
            group_records.append({
                "name_text": p_clean,
                "groupe_nom": groupe_nom,
                "vote": vote_label,
            })

print(f"Enregistrements 'par groupe': {len(group_records)}")

# --- Part 2: "Analyse détaillée" -> name + senator page link + photo url ---
detail_h2 = None
for h2 in soup.select("h2"):
    if "Analyse d" in h2.get_text() and "taill" in h2.get_text():
        detail_h2 = h2
        break

detail_accordion = detail_h2.find_next_sibling("div", class_="accordion")

vote_map = {"1": "Pour", "2": "Contre", "3": "Abstention", "4": "Non votant"}
detail_records = []  # name_text, href, photo, vote

for item in detail_accordion.find_all("div", class_="accordion-item", recursive=False):
    header = item.find("h3", class_="accordion-header")
    header_id = header.get("id", "")
    num = header_id.rsplit("-", 1)[-1]
    vote_label = vote_map.get(num, "?")
    for a in item.find_all("a", class_="senator_lnk"):
        href = a.get("href")
        img = a.find("img")
        photo = img.get("src") if img else None
        span = a.find("span")
        name_text = span.get_text(" ", strip=True) if span else a.get_text(" ", strip=True)
        detail_records.append({
            "name_text": name_text,
            "href": href,
            "photo": photo,
            "vote": vote_label,
        })

print(f"Enregistrements 'detailles': {len(detail_records)}")

with open(r"D:\Loi_urgence_agricole\senat_group_records.json", "w", encoding="utf-8") as f:
    json.dump(group_records, f, ensure_ascii=False, indent=2)
with open(r"D:\Loi_urgence_agricole\senat_detail_records.json", "w", encoding="utf-8") as f:
    json.dump(detail_records, f, ensure_ascii=False, indent=2)
