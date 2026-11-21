# CarEra daily studio – runbook

Read this whole file before starting. It is the brief for the daily automatic run
(scheduled 08:30 Europe/Berlin). The user is Rashid («رشید», CarEra channel: TikTok, Instagram,
YouTube Shorts). **Talk to him in Farsi (Persian).** The videos themselves are in **English**.

Goal of every run: from the bot's *car of the day* make **two finished videos**
(1080×1920, 30 fps, exactly 20.0 s, 5 scenes × 4 s) plus caption texts, and deliver them.

1. **"One car. Three eras."** (tech/unique facts per generation)
2. **"Guess the price"** (new-car list prices then vs now)

If the prices for all three eras cannot be verified from real sources, do NOT invent them:
make "How much bigger did it get?" instead (only if usable side/3-4 photos exist), otherwise
deliver only video 1 and say why.

---

## 0. Setup (≈3 min)

```bash
cd /home/claude && git clone https://github.com/ocarerao-bot/carera-bot.git carera_bot   # if not there yet (add_repo with push access first)
bash /home/claude/carera_bot/studio/setup.sh      # copies scripts to /home/claude/vid, downloads Kokoro voice model
```
All scripts use absolute paths under `/home/claude/vid/`. Per car, work in `/home/claude/vid/<slug>/`
(e.g. `vid/rr/`): `photos/`, `out/scenes`, `out/prev`, `out/final`, `sub/`.

## 1. Car of the day

The bot (GitHub Action `daily.yml`, 06:17 UTC) already posted today's photo kit to Telegram.
```bash
cd /home/claude/carera_bot && git pull
python3 -c "import json;c=json.load(open('cars.json'));s=json.load(open('state.json'));x=c[(s['next']-1)%len(c)];print(x['car'],x['eras'])"
git log -1 --format=%H -- state.json | xargs -I{} git show {} -- state.json | grep '^+ '   # file titles the bot picked
```
If the daily commit is not there yet, wait (poll every 2 min, max 30 min).
If the car entry has a `"note"` field, read it and follow it (user requests / special cases).

## 2. Photos (Wikimedia Commons via GitHub Actions – the sandbox cannot reach Commons)

Write `fetch.txt`, commit, push → workflow `fetch.yml` commits `photos/<dir>/` + `credits.json`.
```
dir: <slug>
File:<exact title from the bot>          (one line per photo)
search: <query> || <must tokens; groups separated by ;, alternatives by ,> || <never tokens, comma separated>
```
Poll `git pull` until `photos/<dir>` exists (~3–5 min). Copy to `/home/claude/vid/<slug>/photos/`.
Make a contact sheet and LOOK at it. Choose per era one photo:
- whole car visible, landscape, big; front three-quarter view preferred (side view is OK).
- **No people inside the car.** People visible *through* the glass → tint the glass (`glass()` / `glass2()`).
- Avoid busy dealer/show photos with other cars glued to the outline, protective films, rally stickers if possible.
- Licence must be CC0 / PD / CC BY / CC BY-SA (fetch already filters). Note author + licence from `credits.json`.

## 3. Cut-outs and clean-up

`rembg` (u2net) → `largest()` → fix remnants. Helpers live in `src/r5prep.py` (everything above `# 1972`):
`largest`, `fill` (plate removal with sampled colour + shading), `glass` (dark tinted glass).
Worked examples: `studio/templates/prep_example_*.py`.
- **Remove every number plate** (fill with bumper/body colour; a blank black plate is OK for old cars).
- Use grid crops (lines every 50/100 px) to find exact coordinates; then check the result visually.
- Mirror (`ImageOps.mirror`) so that cars face sensible directions.

**Colours (user is strict about this):** colour must be one the brand really offered in that era.
Oldtimer → 60s/70s colours; youngtimer → 80s/90s/2000s colours; today → elegant metallic
(lapis/deep blue, cherry-red metallic, deep green). Keep the original colour when
it already fits AND is expressive; recolour only when needed (examples: `recolor_silver` in `price_sl.py`, red recolour in
`r5prep.py`-era code, grey recolour in `prep_example_rangerover.py`). Two eras should not share a colour.
**More expressive colours (user, 2026-11-16):** every car must have a strong, saturated factory colour of its era
(e.g. red, orange, yellow, bright/deep blue, green, bronze/sand, cherry-red metallic, lapis blue). Avoid plain silver,
white, grey and black: prefer a photo in a bold colour, otherwise recolour to a bold colour the brand really offered
in that era (name it in the captions). Elegant metallic for today's car is fine only if it is clearly coloured
(deep blue, cherry red, deep green), not grey/anthracite.
Recolour must not tint glass, lights, tyres or bumpers – exclude them with polygons and check.

## 4. Video 1 – "One car. Three eras."

Copy the Land Rover set and adapt: `src/lrcfg.py` → `src/<slug>cfg.py`, `src/anim7l.py` → `src/anim7<x>.py`,
`src/anim7ls.py` → `src/anim7<x>s.py`, `templates/mix_eras.py` → `vid/<slug>/mix.py`. Replace every path/name.
- Per era: `year`, `car` (cut-out png), `carw` (~860–1000; oldtimer slightly smaller), `strip` (era label),
  `w1` (big word), `w2` (handwritten line), `s1`/`s2` (two short stat discs, ≤5 chars each line).
- Content: one **real technical/unique fact per generation** (verify with sources). **No prices. No "1/2/3" numbering.**
- Hook label (short teaser). CTA is FIXED (user's choice, 2026-11-16): big text **"WHICH ERA" / "IS YOUR ERA?"**,
  subtitle "WHICH ERA IS / YOUR ERA? ↓", voice e.g. "So... which era is your era?". Do not use "be honest" / debate lines.
- Voice lines in `LINES` (hook, e74, e97, e24, cta) + subtitle `CHUNKS` (style C, as in the template).
  After the mix: `sub/timing.json` → set `cta[-1].t1 = 4.0` (see history in Opel run).

## 5. Video 2 – "Guess the price"

Copy `src/price_rr.py` → `src/price_<slug>.py`, `templates/mix_price.py` → `vid/<slug>/mixp.py`.
- Order **expensive → cheap**: today → middle era → oldest (scenes `p3`, `p2`, `p1`).
- Hook: "GUESS THE PRICE" big from frame 0, zoom-out on the new car with its price tag, old car with "$ ?,???".
- Prices: official **new list price of the base model in the home market** (DE: DM/€, UK: £, US: $), each from a
  real source. Convert to **USD at that year's annual average rate** (FRED, e.g. `AEXUSUK`, `CCUSMA02DEA618N`;
  1970 GBP = 2.40) and today's rate (ECB / Trading Economics). Show the local price small in the note line.
  Not inflation-adjusted (say so in the captions).
- Voice says the **full number with "dollars"** ("Twenty-nine thousand, four hundred eighty dollars").
- CTA: "N OF THESE = ONE NEW ONE" with N = floor(new/old) small cars in a grid, plus
  the FIXED question label **"WHAT'S YOUR PRICE ERA? ↓"** (user's choice, 2026-11-16; replaces "YEAR OR YEAR? YOU ONLY GET ONE"),
  COMMENT!, pulsing FOLLOW +. Voice e.g. "N old ones for one new one... what's your price era?". Never "what was your first car".

**The two videos differ ONLY in the car colours (user, 2026-11-17 – replaces the 2026-11-16 note):** keep the template
backgrounds exactly as in the templates (eras: `U.CFG` palettes/posters/seeds unchanged as in `lrcfg.py`; price: era i uses
`U.CFG[i]` palette/posters with seeds 11/21/31 as in `price_rr.py`). Do NOT rotate palettes, posters or seeds. What changes between
the two videos is the car colour (another bold photo of the same generation, or a recolour to another real factory colour).
Never mirror a car that shows lettering (badges read backwards).

**Cars big (user, 2026-11-17: "the cars got a bit small"):** eras `carw` ≈ 1000–1060 (near-square front-on photos ≥ 900),
trio `trw` ≈ 520–650; price `cw` ≈ 880–1020, hook new car 800 / old car 760, CTA grid cars ≥ 320, CTA new car ≈ 560.
Check in the preview that nothing is cut off at the edges and the texts stay readable.

## 6. Voice and sound (both videos)

Kokoro `am_adam`, speed **0.97**. Short, natural spoken sentences, unhurried, ≤ ~3.8 s per scene.
If a line is too long, **shorten the text** – do not push the speed above 1.0.
Music a bit louder, SFX quieter (templates already balanced). Mixes: `mix10_am_adam.wav` (with music) and
`voice_sfx_nomusic.wav`.

## 7. Check, render, mux

1. `python3 -I <script> preview` → build a sheet of the key frames (e.g. `*_100.png`) and LOOK at it:
   texts not covered by cars, nothing cut off at the edges, cars big, no people, no plates.
2. `python3 -I <script> render` (one mp4 per scene in `out/scenes/`).
3. concat (`list.txt`, `-c copy`), then mux each audio with `-c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -shortest`.
   Add `-movflags +faststart` to the mux (Telegram streaming/preview).
   Outputs: `carera_<slug>_eras.mp4`, `carera_<slug>_eras_ohne_musik.mp4`, `carera_<slug>_price.mp4`, `carera_<slug>_price_ohne_musik.mp4`.
4. ffprobe = 20.0 s; grab 2–3 frames of the final file and look at them.

## 8. Captions (one markdown file per video, English, ready to paste)

TikTok (short line + hashtags incl. #carera), Instagram (facts/prices list, question, **photo credits:
author, licence, "via Wikimedia Commons, edited (cut-out, plates removed, …)"**, "Voice & graphics AI-assisted",
hashtags), YouTube Shorts (`Title:` / `Description:` / `Tags:` lines, title with #shorts, description with credits), pinned comment
(answer the CTA yourself first, e.g. "My era: 1960 🟥 What's yours? 👇" / "My price era: 1979 💸 Yours? 👇"),
and a `## Voice-over script` section (the LINES of the mix with their time slots).
Keep one `## ` heading per piece: `deliver.py` sends EVERY piece as its own Telegram message (label + code block with
copy button; YouTube split into title / description / tags) – the user wants to copy them one by one.
Remind the user (Farsi) to set the AI label on all three platforms. List sources (links) in the Farsi message.

## 9. Delivery

a) Send the 4 videos + captions in this session with SendUserFile, and a short Farsi summary
   (what the car is, which colours/photos, anything to know, captions in code blocks).
b) Telegram: create an orphan branch `deliver` containing ONLY `deliver.py`, `.github/workflows/deliver.yml`
   (copy from `studio/deliver/`) and `out/` (videos with music + caption .md files + `out/deliver.json`), force-push it:
```bash
D=/home/claude/deliver && rm -rf $D && mkdir -p $D/out && cp -r /home/claude/carera_bot/studio/deliver/. $D/
cp <final mp4s with music> <caption mds> $D/out/
cat > $D/out/deliver.json <<J
{"title": "<Car> – <date>", "items": [
 {"video": "out/carera_<slug>_eras.mp4", "thumb": "out/<slug>_eras_thumb.jpg", "width": 1080, "height": 1920, "duration": 20, "caption": "One car. Three eras. – <Car>", "texts": "out/<slug>_eras_texts.md"},
 {"video": "out/carera_<slug>_price.mp4", "thumb": "out/<slug>_price_thumb.jpg", "width": 1080, "height": 1920, "duration": 20, "caption": "Guess the price – <Car>", "texts": "out/<slug>_price_texts.md"}]}
J
cd $D && git init -q -b deliver && git add -A && git commit -qm "Deliver <Car> <date>" \
  && git push -f https://github.com/ocarerao-bot/carera-bot.git deliver
```
   Thumbs: `ffmpeg -ss 1 -i <video> -frames:v 1 -vf scale=320:-2 -q:v 4 out/<slug>_<x>_thumb.jpg` (Telegram needs width/height/duration +
   thumbnail, otherwise the 9:16 video looks distorted in the chat – user, 2026-11-18).
   (use the same git credentials/remote as the clone; end commit messages with the attribution lines of the session).
   Check the Action run (`gh run list --branch deliver -L 1`) succeeded (deliver.py exits 1 if any Telegram call failed).
   An item without `"video"` sends only its texts (useful to resend captions without the videos).

## Never
- Never write the Telegram token or the user's e-mail into any file, message or log. Secrets stay in GitHub.
- Never invent prices, facts or photo credits. Never use photos with people inside the cars.
- Never push to `main` anything except `fetch.txt` (and fixes to the studio if really needed).
