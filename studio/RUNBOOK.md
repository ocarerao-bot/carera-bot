# CarEra daily studio – runbook

Read this whole file before starting. It is the brief for the daily automatic run
(scheduled 07:15 Europe/Berlin). The user is Rashid («رشید», CarEra channel: TikTok, Instagram,
YouTube Shorts). **Talk to him in Farsi (Persian).** The videos themselves are in **English**.

Goal of every run: from the bot's *car of the day* make **two finished videos**
(1080×1920, 30 fps, exactly 20.0 s, 5 scenes × 4 s) plus caption texts, and deliver them.

1. **"One car. Three eras."** (tech/unique facts per generation)
2. **"Guess the price"** (new-car list prices then vs now)

**Always make exactly these two formats (user, 2026-11-25). Never switch to "How much bigger did it get?" or any
other format.** If a price is hard to find, research harder (period brochures/price lists, period road tests,
de/fr/it/ja Wikipedia, ADAC/Autobild/classic price guides, archive.org). If one era really has no verifiable price,
pick another generation of the same model that has one. Never invent prices.

**Fixed voice openings (user, 2026-11-27) – ALWAYS, no exceptions:**
- "One car. Three eras." video: the very first words of the voice are **"One car. Three eras."**, then the make + model
  (e.g. "One car. Three eras. The Range Rover...").
- "Guess the price" video: the very first words are **"Guess how much the <Make Model> cost in <19xx>!"**
  (e.g. "Guess how much the Range Rover cost in nineteen seventy!"), then go on with the hints as usual.
- The user called the Mazda 3 and BMW 3 Series videos "excellent" – keep that quality and tone as the reference.

**Look & layout rules (user, 2026-11-27 – the corrected BMW M5 videos are the visual reference, "عالی شد"):**
- **White sticker frame must be complete around EVERY car** – roof, nose, tail and wheels included, in the single-era
  scenes AND in both collages (hook + CTA). `panels.sticker()` now pads the cut-out before drawing the outline (the old
  version clipped it wherever the car touched its cropped image edge – that was the M5 roof bug). Never draw a sticker
  without padding. In every preview, zoom into the collage frames and check the roof line of all three cars.
- **No dark cars.** If a photo looks dark/underexposed (or the paint is black/navy), pick a brighter photo or recolour
  to a bright factory colour (see `templates/prep_example_m5_black.py` for black paint: tint glass, mask out the front
  light/grille band and wheels with polygons, map paint luminance onto the new colour and keep reflections).
- **CTA collage layout:** FOLLOW + sticker at (860,1468), CTA subtitle at y=1640 (as in `anim7ks.py`) so the "2024"
  year tag and the cars are never covered.
- **Photos the user sends in chat** replace the Commons photo for that era. Clean them like any other (people/reflections
  of people, number plates or show plates removed, glass tinted). Credit line: "photo supplied by CarEra" unless the
  user names the photographer.

**Rules from the user's feedback (2026-11-25) – check them before rendering:**
- **Say the car's name out loud.** Both videos: the hook voice names make + model ("The Mazda 323...",
  "Toyota Celica..."), and when a generation has a different model name, the voice says it in that scene
  ("...today it's called the Mazda 3"). The name must also be on screen. A whole video without the name is a failure.
- **Facts must be strong.** Each era fact must be surprising or story-worthy: a first, a record, motorsport wins,
  famous film/owner, a clever engineering idea, a shocking number. Never trivial facts such as "10 cm longer",
  "a bit wider", "more airbags", "new headlights". If the only difference you find is size, research more.

---

## 0. Setup (≈3 min)

```bash
cd /home/claude && git clone https://github.com/ocarerao-bot/carera-bot.git carera_bot   # if not there yet (add_repo with push access first)
bash /home/claude/carera_bot/studio/setup.sh      # copies scripts to /home/claude/vid, downloads Kokoro voice model
```
All scripts use absolute paths under `/home/claude/vid/`. Per car, work in `/home/claude/vid/<slug>/`
(e.g. `vid/rr/`): `photos/`, `out/scenes`, `out/prev`, `out/final`, `sub/`.

## 1. Car of the day

**First thing (user, 2026-11-25): post today's photo kit yourself** – the task starts at 07:15 Berlin and the user wants
the photos at 07:15 and video work from ~07:30. Dispatch the bot (its own cron is only a late backup and skips if
already posted today):
`gh api -X POST repos/ocarerao-bot/carera-bot/actions/workflows/daily.yml/dispatches -f ref=main`
then poll `git pull` until the "daily photos <date>" commit is there (~1–2 min) and start working right away.
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
Worked examples: `studio/templates/prep_example_*.py` (newest: `prep_example_m5_black.py` = clean-up + black→colour
recolour, `prep_example_m5_plates.py` = plate removal with inpaint / flat fill and alpha hardening).
Coordinates: the grid crops label ABSOLUTE pixel positions – read the labels, not the position inside the crop.
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

**Reference template = the BMW M5 set (user, 2026-11-27: "the M5 video is the template from now on").**
Copy and adapt: `src/m5cfg.py` → `src/<slug>cfg.py`, `src/anim7k.py` → `src/anim7<x>.py`,
`src/anim7ks.py` → `src/anim7<x>s.py`, `templates/mix_eras_m5.py` → `vid/<slug>/mix.py`. Replace every path/name
(`/vid/m5/`, `m5cfg`, `anim7k`, the hook label "THE BMW M5", LINES/CHUNKS). The M5 mix already sets `cta[-1].t1 = 4.0`.
(The older Land Rover set `lrcfg.py` / `anim7l.py` / `anim7ls.py` / `mix_eras.py` is kept only for reference.)
- Per era: `year`, `car` (cut-out png), `carw` (~860–1000; oldtimer slightly smaller), `strip` (era label),
  `w1` (big word), `w2` (handwritten line), `s1`/`s2` (two short stat discs, ≤5 chars each line).
- Content: one **real, strong technical/unique fact per generation** (verify with sources; see "Rules from the user's
  feedback" at the top – never trivial size facts). **No prices. No "1/2/3" numbering.** Hook voice says make + model.
- Hook label (short teaser). CTA is FIXED (user's choice, 2026-11-16): big text **"WHICH ERA" / "IS YOUR ERA?"**,
  subtitle "WHICH ERA IS / YOUR ERA? ↓", voice e.g. "So... which era is your era?". Do not use "be honest" / debate lines.
- Voice lines in `LINES` (hook, e74, e97, e24, cta) + subtitle `CHUNKS` (style C, as in the template).
  After the mix: `sub/timing.json` → set `cta[-1].t1 = 4.0` (see history in Opel run).

## 5. Video 2 – "Guess the price 2.0" (NEW FORMAT, user approved 2026-11-22 – replaces the old price video)

The OLD car is the riddle; the answer comes at 13.5 s. **18.0 s**, 5 scenes: `hook` 3.5 s, `h1` 4 s, `h2` 4 s, `cd` 2 s, `rv` 4.5 s.
**Reference template = `src/price2_m5.py`** (user, 2026-11-27): copy it → `src/price2_<slug>.py` and edit only the block
at the top (`MP`, `ERAS` = [oldest, middle, today] with year/car/cw/cy/price/note, `NAME`, `OUTDIR` = `/home/claude/vid/<slug>p/out/`). Copy `templates/mix_price2.py` →
`vid/<slug>p/mixp.py`, replace paths and the `LINES`. Make `out/scenes`, `out/prev`, `out/final`.
- `hook`: oldest car big, "GUESS THE PRICE", year + NAME, pulsing "$ ?,???", "COMMENT YOUR GUESS ↓".
  Voice (fixed opening): "Guess how much the <Make Model> cost in <year>!" (add "Comment your guess!" if it fits).
- `h1` = "HINT 1: TODAY" (today's price), `h2` = "HINT 2" (middle era price); small old car + "AND <year>?".
  Voice: "Hint: today's <Model> is <full number> dollars." / "<Year>, the <Model>? <full number>." (say the model
  name, especially when it changed, e.g. "today's Mazda 3").
- `cd`: "LAST" (white) / "CHANCE!" (red), price tag spinning like a slot machine, drumroll, logo timer grows to the
  centre. Voice ONLY "Last chance..." (never count "three, two, one" – user found it robotic).
- `rv`: "<YEAR> PRICE:", price counts up, note line, "N OF THESE = 1 NEW ONE" (N = floor(today/oldest)),
  "DID YOU GUESS RIGHT? ↓", COMMENT!, pulsing FOLLOW +. Voice: "<full number> dollars! Did you guess right?"
- **Logo timer** (`src/logotimer.py`, style "A" = spray clock in the profile colours, user's choice) sits top right
  (930,300, size 210) the whole time, counts down to the reveal; texts stay on the LEFT. Do not move or restyle it.
- Pinned comment suggestion: "Closest guess gets pinned 📌 No googling! 😅".
- deliver.json: duration 18 for this video. Output name stays `carera_<slug>_price.mp4`.

(Old 20 s format, kept for reference only: `src/price_rr.py` + `templates/mix_price.py`.)
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

**Units (user, 2026-11-21): the channel is English – always HP (not PS), mph / km/h, never German words
like "PS", "Getriebe", "Liter" on screen or in the voice.**

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
   Outputs: ONLY `carera_<slug>_eras.mp4` and `carera_<slug>_price.mp4` (with music). **No `_ohne_musik` versions any more (user, 2026-11-22).**
4. ffprobe = 20.0 s (price 2.0: 18.0 s); grab 2–3 frames of the final file and look at them.

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

a) Send the 2 videos (with music) + captions in this session with SendUserFile, and a short Farsi summary
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

c) **Archive (user, 2026-11-22):** nothing extra to do – the `deliver` workflow uploads every delivered mp4 with the
   date in front to the GitHub release `videos` (sessions cannot create releases; Actions can). For a re-edited video
   from a chat: push an orphan branch `archive-in` that contains `.github/workflows/archive.yml` (copy from main) and the mp4(s) named `<YYYY-MM-DD>_carera_<slug>_<x>.mp4`
   → workflow `archive.yml` uploads them. Bundle of the last 14 days: dispatch `bundle.yml` → release `bundle-<date>`.

## Never
- Never write the Telegram token or the user's e-mail into any file, message or log. Secrets stay in GitHub.
- Never invent prices, facts or photo credits. Never use photos with people inside the cars.
- Never push to `main` anything except `fetch.txt` (and fixes to the studio if really needed).
