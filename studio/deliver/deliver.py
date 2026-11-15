#!/usr/bin/env python3
"""Sends the day's finished CarEra videos + captions to the Telegram chat.
Reads out/deliver.json: {"title": str, "items": [{"video": path, "caption": str, "texts": path_to_md}]}"""
import json, os, sys, requests
T = os.environ["TELEGRAM_TOKEN"]; C = os.environ["TELEGRAM_CHAT_ID"]; API = f"https://api.telegram.org/bot{T}/"
def msg(text):
    for i in range(0, len(text), 3900):
        r = requests.post(API + "sendMessage", data=dict(chat_id=C, text=text[i:i+3900], disable_web_page_preview="true"), timeout=60)
        if not r.ok: print("msg error", r.status_code, r.text[:300], file=sys.stderr)
d = json.load(open("out/deliver.json"))
msg(f"🎬 CarEra – {d['title']}")
for it in d["items"]:
    with open(it["video"], "rb") as f:
        r = requests.post(API + "sendVideo", data=dict(chat_id=C, caption=it.get("caption", "")[:1000], supports_streaming="true"),
                          files=dict(video=(os.path.basename(it["video"]), f, "video/mp4")), timeout=300)
    if not r.ok: print("video error", r.status_code, r.text[:300], file=sys.stderr); msg(f"⚠️ Video {it['video']} konnte nicht gesendet werden ({r.status_code}).")
    if it.get("texts") and os.path.exists(it["texts"]): msg(open(it["texts"]).read())
