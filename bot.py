#!/usr/bin/env python3
"""CarEra daily photo bot.
Every run: picks the next car from cars.json, finds freely licensed photos
(CC0 / Public domain / CC BY / CC BY-SA) on Wikimedia Commons for each of
its three eras and posts them to a Telegram chat, with author + licence
for every photo, so they can be used (with credit) in CarEra videos.
Env: TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, optional CONTACT (for the
Wikimedia User-Agent), PHOTOS_PER_ERA (default 3), DRY_RUN=1 to print only.
"""
import html, json, os, random, re, sys, time, datetime
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://commons.wikimedia.org/w/api.php"
UA = f"CarEraPhotoBot/1.0 ({os.getenv('CONTACT','https://github.com')})"
OK_LIC = re.compile(r"^(cc0|public domain|pd|cc by(-sa)?( \d\.\d)?)", re.I)
BAD_LIC = re.compile(r"(nc|nd|fair use|non-free)", re.I)
GOOD = re.compile(r"(front|frontansicht|vorne|three[- ]quarter|\(1\)|[–-] f[ _]\d|_f_)", re.I)
BAD = re.compile(r"(interior|innenraum|cockpit|dashboard|engine|motor(raum)?|heck|rear|rückansicht|[–-] h[ _]\d|"
                 r"detail|wheel|felge|badge|logo|emblem|seat|sitz|trunk|kofferraum|model|toy|lego|crash|wreck|scale)", re.I)
S = requests.Session(); S.headers["User-Agent"] = UA

def load_state(p):
    try: return json.load(open(p))
    except Exception: return {"next": 0, "used": []}

def clean(t):  # Artist field is HTML
    t = re.sub(r"<[^>]+>", "", t or ""); return html.unescape(re.sub(r"\s+", " ", t)).strip() or "unknown"

def search(query, n=40):
    r = S.get(API, params=dict(action="query", format="json", generator="search", gsrnamespace=6,
             gsrsearch=f"{query} filetype:bitmap", gsrlimit=n, prop="imageinfo",
             iiprop="url|size|mime|extmetadata", iiurlwidth=1600), timeout=40)
    r.raise_for_status(); return list((r.json().get("query") or {}).get("pages", {}).values())

def candidates(pages, used):
    out = []
    for p in pages:
        title = p.get("title", ""); ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "")
        if title in used or not OK_LIC.search(lic) or BAD_LIC.search(lic): continue
        if ii.get("mime") not in ("image/jpeg", "image/png"): continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < 1600 or h < 900 or w < h: continue           # big, landscape
        score = (2 if GOOD.search(title) else 0) - (5 if BAD.search(title) else 0) + random.random()
        out.append(dict(title=title, score=score, thumb=ii.get("thumburl") or ii.get("url"),
                        page=ii.get("descriptionurl"), orig=ii.get("url"), lic=lic,
                        licurl=md.get("LicenseUrl", {}).get("value", ""),
                        author=clean(md.get("Artist", {}).get("value")),
                        credit=clean(md.get("Attribution", {}).get("value")) if md.get("Attribution") else ""))
    return sorted(out, key=lambda c: -c["score"])

def credit_line(c):
    return c["credit"] if c["credit"] and c["credit"] != "unknown" else f'{c["author"]} / Wikimedia Commons / {c["lic"]}'

def tg(method, **data):
    if os.getenv("DRY_RUN"): print(method, json.dumps(data, ensure_ascii=False)[:600]); return {}
    r = requests.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/{method}", data=data, timeout=60)
    if not r.ok: print("telegram error", r.status_code, r.text[:300], file=sys.stderr)
    return r.json() if r.ok else {}

def esc(t): return html.escape(t, quote=False)

def run(state_path=os.path.join(HERE, "state.json")):
    cars = json.load(open(os.path.join(HERE, "cars.json")))
    st = load_state(state_path); used = set(st["used"]); per = int(os.getenv("PHOTOS_PER_ERA", "3"))
    chat = os.getenv("TELEGRAM_CHAT_ID", "dry")
    car = cars[st["next"] % len(cars)]
    today = datetime.date.today().isoformat()
    tg("sendMessage", chat_id=chat, parse_mode="HTML",
       text=f"🚗 <b>CarEra photo kit – {esc(car['car'])}</b>\n{today}\n" +
            " · ".join(f"{y}" for y, _ in car["eras"]) + "\n\nOne car. Three eras. 👇")
    credits = []
    for year, q in car["eras"]:
        try: cs = candidates(search(q), used)
        except Exception as e: print("search failed", q, e, file=sys.stderr); cs = []
        pick = cs[:per]
        if not pick:
            tg("sendMessage", chat_id=chat, text=f"{year}: no free photos found for “{q}”"); continue
        media = []
        for i, c in enumerate(pick):
            cap = (f"<b>{year} – {esc(car['car'])}</b>\n" if i == 0 else "") + \
                  f"📸 {esc(credit_line(c))}\n<a href=\"{c['page']}\">Original + licence</a>"
            media.append(dict(type="photo", media=c["thumb"], caption=cap[:1000], parse_mode="HTML"))
            used.add(c["title"]); credits.append((year, c))
        tg("sendMediaGroup", chat_id=chat, media=json.dumps(media))
        time.sleep(1.5)
    if credits:
        lines = [f"{y}: {credit_line(c)}" for y, c in credits]
        tg("sendMessage", chat_id=chat, disable_web_page_preview="true",
           text="Credits (copy into the post, mark edits!):\n" + "\n".join(lines) +
                "\n\nTip: download the ORIGINAL from the Commons page for full resolution.")
    st["next"] += 1; st["used"] = sorted(used)
    json.dump(st, open(state_path, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    run()
