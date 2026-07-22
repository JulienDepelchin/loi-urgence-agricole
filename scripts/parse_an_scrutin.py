import re, json
from bs4 import BeautifulSoup

with open(r"D:\Loi_urgence_agricole\scrutin_8427_raw.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

results = []

# Each political group is a <ul id="groupeXXX"> containing one <li data-organe-id="..."> block
group_uls = soup.find_all("ul", id=re.compile(r"^groupe"))

for gul in group_uls:
    top_li = gul.find("li", attrs={"data-organe-id": True})
    if not top_li:
        continue
    group_link = top_li.find("a", class_="h5")
    group_name = group_link.get_text(strip=True) if group_link else None
    group_sigle = gul.get("id", "").replace("groupe", "")

    # Inside top_li, there's a nested <ul> with vote-type sections
    inner_ul = top_li.find("ul", recursive=False)
    if inner_ul is None:
        continue

    for section_li in inner_ul.find_all("li", class_="relative-flex", recursive=False):
        label_span = section_li.find("span", class_="h6")
        vote_label = label_span.get_text(strip=True) if label_span else "Inconnu"

        acteur_lis = section_li.find_all("li", attrs={"data-acteur-id": True})
        for ali in acteur_lis:
            a = ali.find("a", class_="link")
            if not a:
                continue
            href = a.get("href", "")
            pa_id = href.rsplit("/", 1)[-1]
            name = a.get_text(strip=True)
            name = re.sub(r"\s+", " ", name).strip()
            results.append({
                "pa_id": pa_id,
                "nom_complet": name,
                "groupe_sigle": group_sigle,
                "groupe_nom": group_name,
                "vote": vote_label,
            })

print(f"Total votants extraits: {len(results)}")
with open(r"D:\Loi_urgence_agricole\an_votes_8427.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# quick sanity check on vote label distribution
from collections import Counter
print(Counter(r["vote"] for r in results))
