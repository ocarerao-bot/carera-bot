#!/usr/bin/env python3
"""Sends the day's finished CarEra videos + captions to the Telegram chat.
Reads out/deliver.json: {"title": str, "items": [{"video": path (optional), "caption": str, "texts": path_to_md}]}
Every caption piece (TikTok, Instagram, YouTube title / description / tags, pinned comment, voice-over script)
is sent as its OWN message: a bold label plus the text in a code block (Telegram shows a copy button)."""
import html, json, os, re, sys, requests
T = os.environ["TELEGRAM_TOKEN"]; C = os.environ["TELEGRAM_CHAT_ID"]; API = f"https://api.telegram.org/bot{T}/"
ERR = []
def post(method, **kw):
    r = requests.post(API + method, timeout=300, **kw)
    if not r.ok: ERR.append(f"{method} {r.status_code}"); print(method, "error", r.status_code, r.text[:300], file=sys.stderr)
    return r
def msg(text):
    for i in range(0, len(text), 3900):
        post("sendMessage", data=dict(chat_id=C, text=text[i:i+3900], disable_web_page_preview="true"))
def piece(label, text):
    """one copyable piece: label in bold, text in a <pre> block (copy button in Telegram)"""
    text = text.strip()
    if not text: return
    body = f"<b>{html.escape(label)}</b>\n<pre>{html.escape(text)}</pre>"
    if len(body) > 4000:   # too long for one message: label, then plain text
        msg(label); msg(text); return
    r = requests.post(API + "sendMessage", data=dict(chat_id=C, text=body, parse_mode="HTML", disable_web_page_preview="true"), timeout=60)
    if not r.ok: print("html msg error", r.status_code, r.text[:300], file=sys.stderr); msg(label); msg(text)   # fallback: plain
def split_md(md):
    """'## Section' blocks -> [(label, text)]; the YouTube block is split into Title / Description / Tags"""
    out = []
    for blk in re.split(r"(?m)^## ", md)[1:]:
        head, _, body = blk.partition("\n"); head = head.strip(); body = body.strip()
        if head.lower().startswith("youtube"):
            m = re.match(r"(?s)\s*Title:\s*(.*?)\n\s*Description:\s*(.*?)\n\s*Tags:\s*(.*)", body)
            if m:
                out += [(f"{head} – Title", m.group(1)), (f"{head} – Description", m.group(2)), (f"{head} – Tags", m.group(3))]; continue
        out.append((head, body))
    return out
d = json.load(open("out/deliver.json"))
msg(f"🎬 CarEra – {d['title']}")
for it in d["items"]:
    if it.get("video"):
        with open(it["video"], "rb") as f:
            r = post("sendVideo", data=dict(chat_id=C, caption=it.get("caption", "")[:1000], supports_streaming="true"),
                     files=dict(video=(os.path.basename(it["video"]), f, "video/mp4")))
        if not r.ok: msg(f"⚠️ Video {it['video']} ارسال نشد ({r.status_code}).")
    elif it.get("caption"):
        msg(f"📝 {it['caption']}")
    if it.get("texts") and os.path.exists(it["texts"]):
        for label, text in split_md(open(it["texts"]).read()): piece(label, text)
if ERR: print("errors:", ERR, file=sys.stderr); sys.exit(1)
