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

def tok_re(t):
    pre = t.endswith("*"); t = t.rstrip("*")
    return re.compile(r"(?<![0-9a-z])" + re.escape(t) + ("" if pre else r"(?![0-9a-z])"), re.I)

def title_ok(title, must, never):
    name = title.replace("_", " ")
    if any(tok_re(t).search(name) for t in never): return False
    return all(any(tok_re(t).search(name) for t in grp) for grp in must)

def candidates(pages, used, must=(), never=()):
    out = []
    for p in pages:
        title = p.get("title", ""); ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "")
        if title in used or not OK_LIC.search(lic) or BAD_LIC.search(lic): continue
        if not title_ok(title, must, never): continue
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

def post_prices(car, chat):
    pr = car.get("prices") or {}
    if not pr: return
    missing = [e[0] for e in car["eras"] if e[0] not in pr]
    lines = [f"<b>{e[0]}</b>: {esc(pr[e[0]]['price'])} – {esc(pr[e[0]]['note'])}" for e in car["eras"] if e[0] in pr]
    src = "\n".join(f'<a href="{pr[e[0]]["src"]}">source {e[0]}</a>' for e in car["eras"] if e[0] in pr)
    tg("sendMessage", chat_id=chat, parse_mode="HTML", disable_web_page_preview="true",
       text="💰 <b>What it cost new</b>\n" + "\n".join(lines) +
            (f"\n{', '.join(missing)}: price still being checked" if missing else "") + "\n\n" + src)

def prices_only(names):
    cars = json.load(open(os.path.join(HERE, "cars.json"))); chat = os.getenv("TELEGRAM_CHAT_ID", "dry")
    for c in cars:
        if c["car"].lower() in names: post_prices(c, chat)

def run(state_path=os.path.join(HERE, "state.json")):
    cars = json.load(open(os.path.join(HERE, "cars.json")))
    st = load_state(state_path); used = set(st["used"]); per = int(os.getenv("PHOTOS_PER_ERA", "3"))
    chat = os.getenv("TELEGRAM_CHAT_ID", "dry")
    car = cars[st["next"] % len(cars)]
    today = datetime.date.today().isoformat()
    tg("sendMessage", chat_id=chat, parse_mode="HTML",
       text=f"🚗 <b>CarEra photo kit – {esc(car['car'])}</b>\n{today}\n" +
            " · ".join(e[0] for e in car["eras"]) + "\n\nOne car. Three eras. 👇")
    credits = []
    for era in car["eras"]:
        year, q = era[0], era[1]; must = era[2] if len(era) > 2 else []; never = era[3] if len(era) > 3 else []
        try:
            pages = {p["title"]: p for p in search(q)}
            if must:   # second search: titles that contain the most specific token
                tok = must[-1][0].rstrip("*")
                for p in search(f'intitle:"{tok}" {q.split()[0]}'): pages.setdefault(p["title"], p)
            cs = candidates(list(pages.values()), used, must, never)
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
    post_prices(car, chat)
    st["next"] += 1; st["used"] = sorted(used)
    json.dump(st, open(state_path, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    trig = open(os.path.join(HERE, "trigger.txt")).read().strip() if os.path.exists(os.path.join(HERE, "trigger.txt")) else ""
    if os.getenv("GITHUB_EVENT_NAME") == "push" and trig.lower().startswith("prices:"):
        prices_only({n.strip().lower() for n in trig.split(":", 1)[1].split(",")})
    else:
        run()
