import json, os, re, time
import urllib.request

REPO_PHOTOS_DEPUTES = r"D:\Loi_urgence_agricole\repo_build\data\photos\deputes"
REPO_PHOTOS_SENATEURS = r"D:\Loi_urgence_agricole\repo_build\data\photos\senateurs"
os.makedirs(REPO_PHOTOS_DEPUTES, exist_ok=True)
os.makedirs(REPO_PHOTOS_SENATEURS, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VDN-Lab-DataTool/1.0"}

def download(url, dest_path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    with open(dest_path, "wb") as f:
        f.write(data)
    return len(data)

with open(r"D:\Loi_urgence_agricole\deputes_59_62_votes.json", encoding="utf-8") as f:
    deputes = json.load(f)
with open(r"D:\Loi_urgence_agricole\senateurs_59_62_votes.json", encoding="utf-8") as f:
    senateurs = json.load(f)

results = {"deputes": {}, "senateurs": {}}

for d in deputes:
    pa_id = d["pa_id"]
    fname = f"{pa_id}.jpg"
    dest = os.path.join(REPO_PHOTOS_DEPUTES, fname)
    size = download(d["photo_url"], dest)
    results["deputes"][pa_id] = {"filename": fname, "size": size}
    print(f"OK depute {pa_id} ({size} bytes)")

for s in senateurs:
    # derive slug from senat_href e.g. /senateur/basquin_alexandre21460q.html
    slug = s["senat_href"].rsplit("/", 1)[-1].replace(".html", "")
    fname = f"{slug}.jpg"
    dest = os.path.join(REPO_PHOTOS_SENATEURS, fname)
    size = download(s["photo_url"], dest)
    results["senateurs"][slug] = {"filename": fname, "size": size}
    print(f"OK senateur {slug} ({size} bytes)")

with open(r"D:\Loi_urgence_agricole\photo_download_manifest.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nTotal deputes: {len(results['deputes'])}, senateurs: {len(results['senateurs'])}")
