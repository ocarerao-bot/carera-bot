"""Style mock: 2000s torn-magazine / ransom-note collage (one still). Car art is a stand-in for real photos."""
import math, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
sys.path.insert(0, "/home/claude/vid/src")
import cars as C

W, H = 1080, 1920
rnd = random.Random(3)
FD = "/usr/share/fonts/opentype/inter/"
FONTS = [FD + "Inter-Black.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
         FD + "Inter-ExtraBoldItalic.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]

def paper_bg():
    base = np.zeros((H, W, 3), np.float32) + np.array([234, 226, 208], np.float32)
    n = np.random.default_rng(1).normal(0, 6, (H // 2, W // 2)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    base += n[..., None]
    # halftone dots (rotated grid, size grows toward bottom-left)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = math.radians(45)
    u = (xx * math.cos(a) + yy * math.sin(a)) / 22.0
    v = (-xx * math.sin(a) + yy * math.cos(a)) / 22.0
    d = np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2)
    size = np.clip(0.12 + 0.38 * (yy / H) * (1 - xx / W * 0.6), 0, 0.5)
    mask = (d < size).astype(np.float32)[..., None]
    dot = np.array([222, 120, 60], np.float32)
    base = base * (1 - 0.55 * mask) + dot * 0.55 * mask
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")

def torn(w, h, fill, edge=(250, 248, 240), amp=9, step=22):
    pts = []
    def side(x0, y0, x1, y1):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(n):
            t = i / n
            pts.append((x0 + (x1 - x0) * t + rnd.uniform(-amp, amp), y0 + (y1 - y0) * t + rnd.uniform(-amp, amp)))
    m = 24
    side(m, m, w - m, m); side(w - m, m, w - m, h - m); side(w - m, h - m, m, h - m); side(m, h - m, m, m)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=edge + (255,))
    inner = Image.new("L", (w, h), 0)
    ImageDraw.Draw(inner).polygon(pts, fill=255)
    inner = inner.filter(ImageFilter.MinFilter(9))
    if isinstance(fill, Image.Image):
        img.paste(fill.convert("RGB").resize((w, h)), (0, 0), inner)
    else:
        img.paste(Image.new("RGB", (w, h), fill), (0, 0), inner)
    return img

def shadowed(img, off=(8, 12), blur=10, alpha=110):
    a = img.getchannel("A")
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (img.width + 60, img.height + 60), (0, 0, 0, 0))
    out.alpha_composite(sh, (30 + off[0], 30 + off[1]))
    out.alpha_composite(img, (30, 30))
    return out

def place(base, img, cx, cy, rot=0, shadow=True):
    im = shadowed(img) if shadow else img
    im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def letter_tile(ch, size, fg, bg, fi):
    f = ImageFont.truetype(FONTS[fi % len(FONTS)], size)
    d0 = ImageDraw.Draw(Image.new("L", (10, 10)))
    tw = d0.textlength(ch, font=f)
    w, h = int(tw + size * 0.55), int(size * 1.25)
    t = torn(w + 20, h + 20, bg, amp=4, step=18)
    ImageDraw.Draw(t).text((t.width / 2, t.height / 2 - size * 0.04), ch, font=f, fill=fg, anchor="mm")
    return t

def starburst(txt, r, col, fg):
    pts = []
    n = 18
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * 0.78
        a = math.pi * i / n
        pts.append((r + 20 + rr * math.cos(a), r + 20 + rr * math.sin(a)))
    img = Image.new("RGBA", (2 * r + 40, 2 * r + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=(20, 20, 20, 255))
    sm = [(r + 20 + (p[0] - r - 20) * 0.93, r + 20 + (p[1] - r - 20) * 0.93) for p in pts]
    d.polygon(sm, fill=col)
    f = ImageFont.truetype(FD + "Inter-Black.otf", int(r * 0.34))
    d.text((r + 20, r + 20), txt, font=f, fill=fg, anchor="mm")
    return img

def tape(w=190, h=64):
    t = Image.new("RGBA", (w, h), (232, 214, 150, 170))
    d = ImageDraw.Draw(t)
    for x in range(0, w, 6):
        d.line([x, 0, x + rnd.randint(-2, 2), 6], fill=(232, 214, 150, 90))
        d.line([x, h - 6, x + rnd.randint(-2, 2), h], fill=(232, 214, 150, 90))
    return t

def sticker(img, border=16):
    a = img.getchannel("A")
    big = a.filter(ImageFilter.MaxFilter(border * 2 + 1)).filter(ImageFilter.GaussianBlur(2))
    big = big.point(lambda v: 255 if v > 80 else 0)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", img.size, (255, 255, 255, 255)), (0, 0), big)
    out.alpha_composite(img)
    return out

bg = paper_bg()
# --- photo piece (stand-in background for the real photo)
sky = Image.new("RGB", (1000, 640))
d = ImageDraw.Draw(sky)
for y in range(640):
    t = y / 640
    d.line([0, y, 1000, y], fill=(int(246 - 40 * t), int(166 - 50 * t), int(76 - 20 * t)))
d.ellipse([560, 120, 820, 380], fill=(255, 224, 150))
d.rectangle([0, 470, 1000, 640], fill=(62, 46, 40))
for x in range(20, 1000, 180):
    d.rectangle([x, 540, x + 100, 550], fill=(230, 200, 150))
photo = torn(1000, 640, sky, amp=11)
car = C.compose_static("mk1")
car = car.crop(car.getbbox())
car = car.resize((int(car.width * 0.98), int(car.height * 0.98)), Image.LANCZOS)
spr = sticker(car, 12)
photo.alpha_composite(spr, (int(1000 / 2 - spr.width / 2), 430 - spr.height + 40 + 20))
place(bg, photo, 540, 1010, rot=-2.2)
# --- tape pieces on photo
for (x, y, r) in ((110, 700, -38), (960, 720, 32), (96, 1310, 28), (972, 1330, -30)):
    place(bg, tape(), x, y, r, shadow=False)
# --- ransom-note year
cols = [((255, 255, 255), (200, 38, 38)), ((20, 20, 20), (250, 240, 200)), ((255, 220, 60), (20, 20, 20)), ((255, 255, 255), (30, 90, 170))]
x = 105
for i, ch in enumerate("1974"):
    fg, bgc = cols[i]
    t = letter_tile(ch, 185 + rnd.randint(-15, 15), fg, bgc, i * 2 + 1)
    place(bg, t, x + t.width / 2 - 20, 300 + rnd.randint(-22, 22), rot=rnd.uniform(-9, 9))
    x += t.width - 44
# --- subtitle strip
strip = torn(760, 120, (28, 28, 30), amp=6)
ImageDraw.Draw(strip).text((strip.width / 2, strip.height / 2), "THE SEVENTIES", font=ImageFont.truetype(FD + "Inter-ExtraBold.otf", 52), fill=(250, 240, 200), anchor="mm")
place(bg, strip, 540, 590, rot=1.8)
# --- starburst stickers
place(bg, starburst("≈ 50 HP", 150, (255, 214, 60), (20, 20, 20)), 235, 1465, rot=-10)
place(bg, starburst("< 800 KG", 150, (240, 90, 60), (255, 255, 255)), 845, 1485, rot=9)
# --- marker underline
d = ImageDraw.Draw(bg)
pts = [(130 + i * 12, 1352 + 8 * math.sin(i * 0.9) + rnd.uniform(-2, 2)) for i in range(70)]
d.line(pts, fill=(210, 40, 40, 255), width=9, joint="curve")
# --- caption clipping
clip = torn(900, 190, (252, 250, 244), edge=(240, 236, 224), amp=6)
cd = ImageDraw.Draw(clip)
cd.text((clip.width / 2, 72), "1974. Bell-bottoms, cassette tapes.", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 34), fill=(30, 30, 30), anchor="mm")
cd.text((clip.width / 2, 126), "A boxy, light Golf with just fifty horsepower.", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 28), fill=(30, 30, 30), anchor="mm")
place(bg, clip, 540, 1690, rot=-1.2)
# --- vignette + grain
a = np.asarray(bg.convert("RGB"), dtype=np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.42
a *= (1 - 0.35 * dd ** 2)[..., None]
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save("/home/claude/vid/mock/zine_style_mock.png")
print("ok")
