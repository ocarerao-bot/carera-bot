#!/usr/bin/env python3
"""Download Commons files listed in fetch.txt (one 'File:...' title per line,
optional first line 'dir: name') into photos/<name>/ with credits.json."""
import json, os, re, requests, html
HERE = os.path.dirname(os.path.abspath(__file__))
UA = f"CarEraPhotoBot/1.0 ({os.getenv('CONTACT','https://github.com')})"
S = requests.Session(); S.headers["User-Agent"] = UA
lines = [l.strip() for l in open(os.path.join(HERE, "fetch.txt")) if l.strip()]
name = "batch"
if lines and lines[0].lower().startswith("dir:"): name = lines.pop(0).split(":", 1)[1].strip()
out = os.path.join(HERE, "photos", name); os.makedirs(out, exist_ok=True)
cred = {}
# "car: <name>" lines -> top candidates per era from cars.json (no Telegram post)
titles = []
for l in lines:
    if l.lower().startswith("car:"):
        import bot
        cname = l.split(":", 1)[1].strip().lower()
        car = next(c for c in json.load(open(os.path.join(HERE, "cars.json"))) if c["car"].lower() == cname)
        for era in car["eras"]:
            must = era[2] if len(era) > 2 else []; never = era[3] if len(era) > 3 else []
            pages = {p["title"]: p for p in bot.search(era[1])}
            if must:
                for p in bot.search(f'intitle:"{must[-1][0].rstrip("*")}" {era[1].split()[0]}'): pages.setdefault(p["title"], p)
            for c in bot.candidates(list(pages.values()), set(), must, never)[:5]: titles.append(c["title"])
    else: titles.append(l)
for t in titles:
    r = S.get("https://commons.wikimedia.org/w/api.php", params=dict(action="query", format="json", titles=t,
              prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=2400), timeout=40).json()
    p = next(iter(r["query"]["pages"].values())); ii = p["imageinfo"][0]; md = ii["extmetadata"]
    url = ii.get("thumburl") or ii["url"]
    fn = re.sub(r"[^A-Za-z0-9._-]+", "_", t.split(":", 1)[1])
    open(os.path.join(out, fn), "wb").write(S.get(url, timeout=120).content)
    clean = lambda v: html.unescape(re.sub(r"<[^>]+>", "", v or "")).strip()
    cred[fn] = dict(title=t, page=ii.get("descriptionurl"), author=clean(md.get("Artist", {}).get("value")),
                    license=md.get("LicenseShortName", {}).get("value"), attribution=clean(md.get("Attribution", {}).get("value")))
    print("ok", fn)
json.dump(cred, open(os.path.join(out, "credits.json"), "w"), indent=1, ensure_ascii=False)
