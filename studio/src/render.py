"""CarEra - VW Golf, 30 s vertical (1080x1920 @30). One encoded file per scene.
usage: render.py preview            -> PNG stills of key moments in ../preview
       render.py scene <name>       -> renders one scene to ../scenes/<name>.mp4
"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

sys.path.insert(0, os.path.dirname(__file__))
import cars as C

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = "/usr/share/fonts/opentype/inter/"
F_BLACK, F_XBOLD, F_BOLD, F_MED = FD + "Inter-Black.otf", FD + "Inter-ExtraBold.otf", FD + "Inter-Bold.otf", FD + "Inter-Medium.otf"
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
ORANGE = (255, 138, 61)

GROUND_Y = 1210       # tyre contact line (era scenes)
HORIZON = 1150        # top of sidewalk
ROAD_DASH_Y = 1252
NEAR_Y = HORIZON + 18 - 460   # near layer top; local y=460 is the kerb line

DUR = {"hook": 4.0, "e74": 6.0, "e97": 7.0, "e24": 7.0, "cta": 6.0}


# ---------------------------------------------------------------- helpers
def font(p, s):
    return ImageFont.truetype(p, s)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def vgrad(w, h, stops):
    ys = np.linspace(0, 1, h)
    pos = [s[0] for s in stops]
    cols = np.array([s[1] for s in stops], dtype=np.float32)
    arr = np.stack([np.interp(ys, pos, cols[:, i]) for i in range(3)], axis=1)
    arr = np.repeat(arr[:, None, :], w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def text_img(txt, fpath, size, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=None, spacing=0, align="center", line_gap=1.0):
    f = font(fpath, size)
    lines = txt.split("\n")
    pad = 50
    d0 = ImageDraw.Draw(Image.new("L", (10, 10)))
    widths = []
    for ln in lines:
        if spacing:
            w = sum(d0.textlength(ch, font=f) + spacing for ch in ln) - spacing
        else:
            w = d0.textlength(ln, font=f)
        widths.append(w)
    lh = int(size * 1.18 * line_gap)
    tw, th = int(max(widths)) + 2 * pad, lh * len(lines) + 2 * pad
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("L", (tw, th), 0)
        sd = ImageDraw.Draw(sh)
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        y = pad + i * lh
        if align == "center":
            x0 = (tw - widths[i]) / 2
        elif align == "left":
            x0 = pad
        else:
            x0 = tw - pad - widths[i]
        if spacing:
            x = x0
            for ch in ln:
                if shadow:
                    sd.text((x + shadow[0], y + shadow[1]), ch, font=f, fill=255)
                d.text((x, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
                x += d0.textlength(ch, font=f) + spacing
        else:
            if shadow:
                sd.text((x0 + shadow[0], y + shadow[1]), ln, font=f, fill=255)
            d.text((x0, y), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    if shadow:
        sh = sh.filter(ImageFilter.GaussianBlur(shadow[2]))
        sh = sh.point(lambda v: int(v * shadow[3]))
        shadow_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        shadow_img.putalpha(sh)
        out = Image.alpha_composite(shadow_img, img)
        return out
    return img


def pill(txt, size, fg, bg, padx=34, pady=18, radius=None, border=None):
    f = font(F_XBOLD, size)
    d0 = ImageDraw.Draw(Image.new("L", (10, 10)))
    tw = int(d0.textlength(txt, font=f))
    w, h = tw + 2 * padx, int(size * 1.15) + 2 * pady
    m = 10
    img = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = radius if radius is not None else h // 2
    d.rounded_rectangle([m, m, m + w, m + h], r, fill=bg, outline=border, width=3 if border else 0)
    d.text((m + padx, m + pady - 2), txt, font=f, fill=fg)
    return img


def caption_box(lines, size=46):
    t = text_img("\n".join(lines), F_XBOLD, size, (255, 255, 255), shadow=(0, 3, 3, 0.8), line_gap=1.05)
    t = t.crop(t.getbbox())
    padx, pady = 42, 22
    box = Image.new("RGBA", (t.width + 2 * padx, t.height + 2 * pady), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle([0, 0, box.width - 1, box.height - 1], 34, fill=(8, 10, 16, 160))
    box.alpha_composite(t, (padx, pady))
    return box


def paste_rgba(base, img, x, y, alpha=1.0):
    if alpha <= 0:
        return
    if alpha < 1:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        base.paste(img.convert("RGB"), (int(x), int(y)), a)
    else:
        base.paste(img.convert("RGB"), (int(x), int(y)), img.getchannel("A"))


class Overlay:
    """Animated text/pill element, positioned by its centre."""
    def __init__(self, img, cx, cy, t0, t1=None, dur=0.35, kind="fade", out=0.18):
        self.img, self.cx, self.cy, self.t0, self.t1, self.dur, self.kind, self.out = img, cx, cy, t0, t1, dur, kind, out

    def draw(self, base, t):
        if t < self.t0 or (self.t1 is not None and t > self.t1):
            return
        p = (t - self.t0) / self.dur
        alpha, scale, dy = 1.0, 1.0, 0.0
        if self.kind == "fade":
            alpha, dy = ease_out(p), (1 - ease_out(p)) * 26
        elif self.kind == "pop":
            alpha = clamp(p * 3)
            scale = 0.55 + 0.45 * ease_back(p)
        elif self.kind == "zoom":
            alpha = clamp(p * 2.5)
            scale = 1.0 + 0.30 * (1 - ease_out(p))
        if self.t1 is not None:
            alpha *= clamp((self.t1 - t) / self.out)
        img = self.img
        if abs(scale - 1) > 0.004:
            img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
        paste_rgba(base, img, self.cx - img.width / 2, self.cy - img.height / 2 + dy, alpha)


def wrap_draw(draw_fn, period, x, *a, **k):
    for off in (-period, 0, period):
        draw_fn(x + off, *a, **k)


def ac(dst, src, x, y):
    x, y = int(x), int(y)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(dst.width, x + src.width), min(dst.height, y + src.height)
    if x1 <= x0 or y1 <= y0:
        return
    crop = src.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    region = dst.crop((x0, y0, x1, y1))
    dst.paste(Image.alpha_composite(region, crop), (x0, y0))


def tile2(img):
    t = Image.new("RGBA", (img.width * 2, img.height), (0, 0, 0, 0))
    t.paste(img, (0, 0))
    t.paste(img, (img.width, 0))
    return t


def scroll_paste(base, tile, y, off):
    off = int(off) % (tile.width // 2)
    crop = tile.crop((off, 0, off + W, tile.height))
    base.paste(crop.convert("RGB"), (0, y), crop.getchannel("A"))


def vignette_mask(strength):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.42
    return (1 - strength * d ** 2.2)[..., None].astype(np.float32)


def car_layers(name, scale):
    body, wheel, spec = C.build(name)
    d = ImageDraw.Draw(body)
    r = spec["wheel_r"]
    for cx in (spec["rear_x"], spec["front_x"]):
        rr = (r + 12) * 2
        d.ellipse([cx * 2 - rr, spec["wheel_y"] * 2 - rr, cx * 2 + rr, spec["wheel_y"] * 2 + rr], fill=(14, 14, 16, 255))
    bw, bh = round(C.W * scale), round(C.H * scale)
    body = body.resize((bw, bh), Image.LANCZOS)
    arr = np.asarray(body).astype(np.float32)
    g = (1.14 - 0.36 * np.linspace(0, 1, arr.shape[0]))[:, None, None]
    arr[..., :3] = np.clip(arr[..., :3] * g, 0, 255)
    body = Image.fromarray(arr.astype(np.uint8), "RGBA")
    ws = round(wheel.width / 2 * scale)
    wheel = wheel.resize((ws, ws), Image.LANCZOS)
    centers = [(spec["rear_x"] * scale, spec["wheel_y"] * scale), (spec["front_x"] * scale, spec["wheel_y"] * scale)]
    return body, wheel, centers, spec["wheel_r"] * scale


class Car:
    def __init__(self, name, scale):
        self.body, self.wheel, self.centers, self.r = car_layers(name, scale)
        self.scale = scale
        self.ground = C.GROUND * scale
        self.rot_cache = {}

    def draw(self, base, x, ground_y, angle):
        top = int(round(ground_y - self.ground))
        x = int(round(x))
        base.paste(self.body, (x, top), self.body)
        key = int(angle) % 360
        wr = self.rot_cache.get(key)
        if wr is None:
            wr = self.wheel.rotate(-key, resample=Image.BICUBIC)
            self.rot_cache[key] = wr
        for cx, cy in self.centers:
            base.paste(wr, (int(x + cx - wr.width / 2), int(top + cy - wr.height / 2)), wr)


def shadow_img(w):
    s = Image.new("L", (w + 80, 90), 0)
    ImageDraw.Draw(s).ellipse([40, 24, w + 40, 66], fill=190)
    s = s.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", s.size, (0, 0, 0, 0))
    out.putalpha(s)
    return out


# ---------------------------------------------------------------- era backgrounds
def road_static(img, sidewalk, curb, asphalt_top, asphalt_bot, lane=(255, 255, 255)):
    d = ImageDraw.Draw(img)
    d.rectangle([0, HORIZON, W, HORIZON + 26], fill=sidewalk)
    d.rectangle([0, HORIZON + 26, W, HORIZON + 34], fill=curb)
    img.paste(vgrad(W, H - (HORIZON + 34), [(0, asphalt_top), (1, asphalt_bot)]), (0, HORIZON + 34))
    mix = tuple(int(a * 0.72 + b * 0.28) for a, b in zip(asphalt_top, lane))
    d.rectangle([0, 1690, W, 1698], fill=mix)


def dashes(d, y0, color, h=10, length=100, period=180):
    for k in range(W // period + 1):
        d.rectangle([k * period, y0, k * period + length, y0 + h], fill=color)


def build_74():
    rnd = random.Random(74)
    bg = vgrad(W, HORIZON, [(0, (110, 62, 70)), (0.35, (226, 120, 62)), (0.75, (248, 170, 80)), (1, (255, 206, 120))])
    full = Image.new("RGB", (W, H))
    full.paste(bg, (0, 0))
    road_static(full, (190, 165, 120), (120, 98, 70), (104, 78, 64), (56, 40, 36), (236, 206, 150))
    # sun
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([640 - 330, 780 - 330, 640 + 330, 780 + 330], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    full.paste(Image.new("RGB", (W, H), (255, 190, 90)), (0, 0), glow)
    ImageDraw.Draw(full).ellipse([640 - 175, 790 - 175, 640 + 175, 790 + 175], fill=(255, 226, 150))
    # buildings tile (period 1080)
    TH = 640
    tile = Image.new("RGBA", (W, TH), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    pal = [(104, 62, 42), (138, 82, 50), (168, 104, 58), (90, 52, 34), (125, 74, 44), (150, 96, 60)]
    widths = []
    while sum(widths) < W - 150:
        widths.append(rnd.randint(150, 240))
    widths.append(W - sum(widths))
    x = 0
    base_y = TH  # building bottoms at tile bottom (=HORIZON)
    for w in widths:
        h = rnd.randint(260, 400)
        col = rnd.choice(pal)
        d.rectangle([x, base_y - h, x + w, base_y], fill=col)
        d.rectangle([x, base_y - h, x + w, base_y - h + 14], fill=tuple(int(c * 0.7) for c in col))
        # windows
        for wy in range(base_y - h + 50, base_y - 190, 70):
            for wx in range(x + 22, x + w - 40, 46):
                lit = rnd.random() < 0.62
                d.rectangle([wx, wy, wx + 24, wy + 36], fill=(255, 214, 130) if lit else (70, 42, 32))
        # shop front
        d.rectangle([x, base_y - 150, x + w, base_y], fill=tuple(int(c * 0.82) for c in col))
        aw = rnd.choice([(222, 168, 40), (60, 110, 70), (200, 70, 50)])
        for k in range(0, w, 30):
            d.rectangle([x + k, base_y - 160, x + k + 15, base_y - 118], fill=aw)
            d.rectangle([x + k + 15, base_y - 160, x + k + 30, base_y - 118], fill=(240, 230, 210))
        d.rectangle([x + 18, base_y - 108, x + w - 18, base_y - 12], fill=(255, 220, 150) if rnd.random() < 0.7 else (60, 40, 34))
        # TV antenna (very 70s)
        if rnd.random() < 0.7:
            ax = x + rnd.randint(30, w - 30)
            ay = base_y - h
            d.line([ax, ay, ax, ay - 52], fill=(40, 28, 24), width=4)
            for k, ln in enumerate((34, 26, 18)):
                d.line([ax - ln, ay - 14 - k * 13, ax + ln, ay - 14 - k * 13], fill=(40, 28, 24), width=3)
        x += w
    mid = tile2(tile)
    # near layer: poles + wires + dashes (period 540 for poles; whole tile 1080)
    NH = 600
    near = Image.new("RGBA", (W, NH), (0, 0, 0, 0))
    nd = ImageDraw.Draw(near)

    def pole(px):
        nd.rectangle([px - 8, 20, px + 8, NH - 140], fill=(52, 34, 26))
        nd.rectangle([px - 62, 54, px + 62, 66], fill=(52, 34, 26))
        for ix in (-50, -20, 20, 50):
            nd.rectangle([px + ix - 4, 40, px + ix + 4, 56], fill=(120, 150, 130))

    def wire(x1, x2):
        pts = []
        for k in range(21):
            u = k / 20
            pts.append((x1 + (x2 - x1) * u, 52 + 38 * 4 * u * (1 - u)))
        nd.line(pts, fill=(40, 28, 24), width=3)

    for px in (270, 810):
        for off in (-W, 0, W):
            pole(px + off)
    for off in (-W, 0, W):
        wire(270 + off, 810 + off)
        wire(810 + off, 270 + W + off)
    dashes(nd, ROAD_DASH_Y - NEAR_Y, (236, 206, 150))
    return dict(static=full, mid=mid, mid_y=HORIZON - TH, mid_speed=4.0, near=tile2(near), near_y=NEAR_Y, near_speed=13.0)


def build_97():
    rnd = random.Random(97)
    bg = vgrad(W, HORIZON, [(0, (28, 38, 88)), (0.38, (92, 76, 150)), (0.7, (214, 126, 140)), (1, (246, 182, 130))])
    full = Image.new("RGB", (W, H))
    full.paste(bg, (0, 0))
    road_static(full, (150, 150, 158), (96, 98, 110), (104, 108, 124), (62, 64, 80), (244, 236, 200))
    # hills + trees silhouette (far)
    d = ImageDraw.Draw(full)
    pts = [(0, HORIZON)]
    for xx in range(0, W + 20, 20):
        pts.append((xx, HORIZON - 120 - 40 * math.sin(xx / 150.0) - 24 * math.sin(xx / 53.0)))
    pts.append((W, HORIZON))
    d.polygon(pts, fill=(44, 52, 92))
    # mall (period 1080, seamless flat wall)
    TH = 420
    tile = Image.new("RGBA", (W, TH), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    y0 = TH - 290
    td.rectangle([0, y0, W, TH], fill=(206, 198, 186))
    td.rectangle([0, y0, W, y0 + 26], fill=(150, 142, 134))
    td.rectangle([0, TH - 120, W, TH], fill=(176, 170, 162))
    for gx in range(30, W, 180):
        td.rectangle([gx, TH - 108, gx + 120, TH - 10], fill=(70, 110, 140) if (gx // 180) % 2 else (255, 226, 160))
        td.line([gx + 60, TH - 108, gx + 60, TH - 10], fill=(120, 120, 120), width=4)
    td.rounded_rectangle([250, y0 - 100, 830, y0 + 10], 16, fill=(196, 32, 38))
    td.rectangle([250, y0 - 20, 830, y0 - 6], fill=(30, 70, 170))
    td.text((540, y0 - 62), "MALL", font=font(F_BLACK, 76), fill=(255, 255, 255), anchor="mm")
    for wx in range(40, 230, 70):
        td.rectangle([wx, y0 + 50, wx + 46, y0 + 110], fill=(120, 150, 180))
    for wx in range(870, 1060, 70):
        td.rectangle([wx, y0 + 50, wx + 46, y0 + 110], fill=(120, 150, 180))
    mid = tile2(tile)
    NH = 600
    near = Image.new("RGBA", (W, NH), (0, 0, 0, 0))
    nd = ImageDraw.Draw(near)

    def lamp(px):
        nd.rectangle([px - 6, 40, px + 6, NH - 140], fill=(36, 38, 50))
        nd.rectangle([px - 56, 34, px + 56, 46], fill=(36, 38, 50))
        for ix in (-52, 52):
            nd.rectangle([px + ix - 14, 44, px + ix + 14, 54], fill=(255, 238, 170))
        g = Image.new("L", (240, 240), 0)
        ImageDraw.Draw(g).ellipse([60, 60, 180, 180], fill=110)
        g = g.filter(ImageFilter.GaussianBlur(26))
        glow = Image.new("RGBA", (240, 240), (255, 226, 150, 0))
        glow.putalpha(g)
        for ix in (-52, 52):
            near.alpha_composite(glow, (px + ix - 120, 50 - 120))

    for px in (150, 690):
        for off in (-W, 0, W):
            lamp(px + off)

    def parked(px, col):
        t = Image.new("RGBA", (260, 130), (0, 0, 0, 0))
        td2 = ImageDraw.Draw(t)
        y = 104
        td2.rounded_rectangle([0, y - 56, 250, y], 18, fill=col)
        td2.polygon([(40, y - 56), (70, y - 100), (170, y - 100), (210, y - 56)], fill=col)
        td2.polygon([(78, y - 58), (94, y - 92), (130, y - 92), (130, y - 58)], fill=(160, 190, 220))
        td2.polygon([(138, y - 58), (138, y - 92), (166, y - 92), (196, y - 58)], fill=(160, 190, 220))
        for wx in (52, 196):
            td2.ellipse([wx - 22, y - 22, wx + 22, y + 22], fill=(18, 18, 20))
            td2.ellipse([wx - 10, y - 10, wx + 10, y + 10], fill=(150, 150, 156))
        t = t.resize((182, 91), Image.LANCZOS)
        near.alpha_composite(t, (px, (HORIZON - 4 - NEAR_Y) - 91 + 10)) if 0 <= px < W - 182 else ac(near, t, px, (HORIZON - 4 - NEAR_Y) - 91 + 10)

    for px, col in ((400, (42, 60, 110)), (780, (110, 40, 60)), (40, (56, 92, 74))):
        for off in (-W, 0, W):
            parked(px + off, col)
    dashes(nd, ROAD_DASH_Y - NEAR_Y, (244, 236, 200))
    return dict(static=full, mid=mid, mid_y=HORIZON - TH, mid_speed=3.0, near=tile2(near), near_y=NEAR_Y, near_speed=13.0)


def build_24():
    rnd = random.Random(24)
    bg = vgrad(W, HORIZON, [(0, (52, 118, 214)), (0.5, (128, 184, 240)), (0.85, (214, 226, 240)), (1, (255, 226, 190))])
    full = Image.new("RGB", (W, H))
    full.paste(bg, (0, 0))
    road_static(full, (206, 208, 214), (150, 154, 164), (70, 76, 94), (38, 42, 56), (250, 250, 250))
    d = ImageDraw.Draw(full)
    # soft sun flare
    fl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(fl).ellipse([760 - 220, 860 - 220, 760 + 220, 860 + 220], fill=130)
    fl = fl.filter(ImageFilter.GaussianBlur(80))
    full.paste(Image.new("RGB", (W, H), (255, 236, 200)), (0, 0), fl)
    TH = 600
    tile = Image.new("RGBA", (W, TH), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)

    def tower(x, w, h, top, bot, a):
        g = vgrad(w, h, [(0, top), (1, bot)]).convert("RGBA")
        gd = ImageDraw.Draw(g)
        for yy in range(0, h, 34):
            gd.line([0, yy, w, yy], fill=(255, 255, 255, 40), width=2)
        for xx in range(0, w, 30):
            gd.line([xx, 0, xx, h], fill=(255, 255, 255, 34), width=2)
        # diagonal reflection
        gd.polygon([(w * 0.2, 0), (w * 0.5, 0), (w * 0.1, h), (-w * 0.2, h)], fill=(255, 255, 255, 40))
        g.putalpha(g.getchannel("A").point(lambda v: int(v * a)))
        for off in (-W, 0, W):
            ac(tile, g, x + off, TH - h)

    # far row (lighter)
    x = -40
    while x < W:
        w = rnd.randint(90, 150)
        tower(x, w, rnd.randint(250, 380), (170, 200, 236), (140, 170, 212), 0.9)
        x += w + rnd.randint(0, 20)
    # near row (stronger)
    widths = []
    while sum(widths) < W - 140:
        widths.append(rnd.randint(130, 200))
    widths.append(W - sum(widths))
    x = 0
    for w in widths:
        tower(x, w, rnd.randint(330, 530), (96, 140, 196), (52, 86, 140), 1.0)
        x += w
    mid = tile2(tile)
    NH = 600
    near = Image.new("RGBA", (W, NH), (0, 0, 0, 0))
    nd = ImageDraw.Draw(near)

    def charger(px):
        base = NH - 140
        nd.rounded_rectangle([px - 36, base - 250, px + 36, base], 14, fill=(236, 240, 246))
        nd.rounded_rectangle([px - 26, base - 226, px + 26, base - 150], 8, fill=(22, 30, 44))
        nd.rectangle([px - 20, base - 210, px + 20, base - 198], fill=(80, 220, 150))
        nd.rectangle([px - 20, base - 184, px + 10, base - 176], fill=(120, 140, 170))
        nd.ellipse([px - 8, base - 136, px + 8, base - 120], fill=(80, 220, 150))
        nd.rectangle([px - 36, base - 24, px + 36, base], fill=(190, 196, 206))
        nd.line([px + 36, base - 110, px + 70, base - 80, px + 74, base - 20], fill=(30, 34, 42), width=7)
        g = Image.new("L", (160, 160), 0)
        ImageDraw.Draw(g).ellipse([50, 50, 110, 110], fill=140)
        g = g.filter(ImageFilter.GaussianBlur(20))
        gl = Image.new("RGBA", (160, 160), (80, 240, 160, 0))
        gl.putalpha(g)
        near.alpha_composite(gl, (px - 80, base - 204 - 80 + 10))

    def tree(px):
        base = NH - 140
        nd.rectangle([px - 7, base - 150, px + 7, base], fill=(70, 54, 44))
        nd.ellipse([px - 74, base - 300, px + 74, base - 120], fill=(46, 128, 90))
        nd.ellipse([px - 50, base - 280, px + 20, base - 190], fill=(70, 160, 110))

    for off in (-W, 0, W):
        charger(330 + off)
        tree(840 + off)
        tree(80 + off)
    dashes(nd, ROAD_DASH_Y - NEAR_Y, (250, 250, 250))
    return dict(static=full, mid=mid, mid_y=HORIZON - TH, mid_speed=3.5, near=tile2(near), near_y=NEAR_Y, near_speed=13.0)


# ---------------------------------------------------------------- FX passes
VIG = {}


def vig(s):
    if s not in VIG:
        VIG[s] = vignette_mask(s)
    return VIG[s]


def noise(rng, sigma):
    n = rng.normal(0, sigma, (H // 3 + 1, W // 3 + 1)).astype(np.float32)
    n = n.repeat(3, 0).repeat(3, 1)[:H, :W]
    return n[..., None]


def glitch_strips(a, rng, n, maxshift, hmin=20, hmax=160):
    for _ in range(n):
        y = int(rng.integers(0, H - hmax))
        h = int(rng.integers(hmin, hmax))
        dx = int(rng.integers(-maxshift, maxshift))
        a[y:y + h] = np.roll(a[y:y + h], dx, axis=1)
    return a


def rgb_split(a, dx):
    if dx == 0:
        return a
    a = a.copy()
    a[..., 0] = np.roll(a[..., 0], dx, axis=1)
    a[..., 2] = np.roll(a[..., 2], -dx, axis=1)
    return a


def fx_74(img, f, t, rng):
    a = np.asarray(img, dtype=np.float32)
    a = a * np.array([1.06, 1.0, 0.86], dtype=np.float32)
    a = (a - 128) * 1.06 + 128
    a = a * vig(0.55)
    a = a * (1 + 0.018 * rng.normal())
    a = a + noise(rng, 11)
    if rng.random() < 0.35:  # film scratch
        x = int(rng.integers(0, W - 3))
        a[:, x:x + 2] += 38
    if rng.random() < 0.5:   # dust
        for _ in range(int(rng.integers(1, 5))):
            x, y = int(rng.integers(0, W - 6)), int(rng.integers(0, H - 6))
            a[y:y + int(rng.integers(2, 6)), x:x + int(rng.integers(2, 6))] += 60
    if t < 0.4:
        a = a * (1 + 0.5 * rng.normal()) if t < 0.3 else a
        a = a + 255 * 0.8 * clamp(1 - t / 0.2)
        a = a + noise(rng, 30)
    return a


def fx_97(img, f, t, rng):
    a = np.asarray(img, dtype=np.float32)
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 0.8
    a = a * 0.9 + 16
    a = rgb_split(a, 3)
    a[::4] *= 0.84
    a[1::4] *= 0.92
    a = a * vig(0.28)
    a = a + noise(rng, 7)
    # top wobble
    for y in range(0, 90, 6):
        s = int(4 * math.sin(f * 0.6 + y * 0.2))
        a[y:y + 6] = np.roll(a[y:y + 6], s, axis=1)
    # tracking band
    ph = (t * 0.6) % 1.0
    if 0.0 < ph < 0.35 and rng.random() < 0.8:
        y = int(H * (0.25 + 0.7 * ph / 0.35))
        a[y:y + 40] = np.roll(a[y:y + 40], int(rng.integers(30, 90)), axis=1) * 1.08 + rng.normal(0, 25, (40, W, 1)).astype(np.float32)
    if t < 0.5:
        k = clamp(1 - t / 0.5)
        a = glitch_strips(a, rng, int(2 + 7 * k), int(60 + 260 * k))
        a = rgb_split(a, int(26 * k))
        a = a + 255 * 0.8 * clamp(1 - t / 0.15)
    return a


def fx_24(img, f, t, rng):
    a = np.asarray(img, dtype=np.float32)
    a = (a - 128) * 1.05 + 128
    a = a * vig(0.14)
    if t < 0.45:
        k = clamp(1 - t / 0.45)
        a = glitch_strips(a, rng, int(1 + 6 * k), int(40 + 200 * k), 10, 90)
        a = rgb_split(a, int(22 * k))
        a = a + 255 * 0.85 * clamp(1 - t / 0.15)
    return a


def fx_hook(img, f, t, rng):
    a = np.asarray(img, dtype=np.float32) * vig(0.3)
    return a * clamp(t / 0.25)


def fx_cta(img, f, t, rng):
    a = np.asarray(img, dtype=np.float32) * vig(0.3)
    return a + 255 * 0.85 * clamp(1 - t / 0.2)


# ---------------------------------------------------------------- scenes
EMB = Image.open(os.path.join(ROOT, "assets", "emblem.png")).convert("RGBA").resize((104, 104), Image.LANCZOS)


def brand(base, t, a=1.0):
    paste_rgba(base, EMB, 40, 92, a * clamp(t / 0.3))


def captions(items):
    """items: [(lines, t0, t1)] -> overlays near y=1460"""
    out = []
    for lines, t0, t1 in items:
        box = caption_box(lines)
        out.append(Overlay(box, W // 2, 1458, t0, t1, dur=0.25, kind="fade", out=0.2))
    return out


class EraScene:
    def __init__(self, name, builder, car_name, fx, year, tag, model, chips, caps, year_style, tint):
        self.name, self.dur = name, DUR[name]
        self.n = int(round(self.dur * FPS))
        self.bgd = builder()
        self.car = Car(car_name, 0.95)
        self.fx = fx
        self.shadow = shadow_img(int(C.W * 0.95 * 0.86))
        self.ov = []
        if year_style == "chroma":
            y = Image.new("RGBA", (960, 520), (0, 0, 0, 0))
            for col, dx in (((0, 229, 255, 255), -7), ((255, 45, 149, 255), 7), ((255, 255, 255, 255), 0)):
                ti = text_img(year, F_BLACK, 300, col)
                y.alpha_composite(ti, (y.width // 2 - ti.width // 2 + dx, y.height // 2 - ti.height // 2))
            yimg = y
        else:
            yimg = text_img(year, F_BLACK, 300, tint, shadow=(0, 8, 14, 0.55))
        self.ov.append(Overlay(yimg, W // 2, 404, 0.15, dur=0.5, kind="zoom"))
        self.ov.append(Overlay(text_img(tag, F_XBOLD, 40, (255, 255, 255), shadow=(0, 3, 6, 0.7), spacing=14), W // 2, 596, 0.45, dur=0.4))
        self.ov.append(Overlay(pill(model, 40, (20, 20, 24), (255, 255, 255, 235), padx=34, pady=14), W // 2, 676, 0.6, dur=0.45, kind="pop"))
        for i, (c, bgc, fgc) in enumerate(chips):
            self.ov.append(Overlay(pill(c, 44, fgc, bgc, padx=34, pady=18), 300 + i * 480 if len(chips) > 1 else W // 2, 1326, 1.5 + i * 0.5, dur=0.5, kind="pop"))
        self.ov += captions(caps)

    def frame(self, f):
        t = f / FPS
        rng = np.random.default_rng(1000 + hash(self.name) % 1000 * 10 + f)
        b = self.bgd
        base = b["static"].copy()
        scroll_paste(base, b["mid"], b["mid_y"], t * FPS * b["mid_speed"])
        scroll_paste(base, b["near"], b["near_y"], t * FPS * b["near_speed"])
        # car
        slide = ease_out(t / 0.9)
        cx = -1050 + (65 + 1050) * slide
        bob = 2.0 * math.sin(t * 9) if t > 0.9 else 0
        shx = int(cx + 0.95 * C.W / 2 - self.shadow.width / 2)
        base.paste(self.shadow, (shx, int(GROUND_Y - 44 + bob)), self.shadow)
        dist = 0.0
        speed_deg = 12.0
        angle = speed_deg * f * 1.0 if t > 0.9 else speed_deg * 1.8 * f
        self.car.draw(base, cx, GROUND_Y + bob, angle)
        # zoom
        z = 1.0 + 0.055 * (t / self.dur)
        if z > 1.001:
            cw, ch = W / z, H / z
            x0, y0 = (W - cw) / 2, 1050 - ch * (1050 / H)
            base = base.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)
        if self.name == "e97":
            self._vhs_stamp(base, t)
        a = self.fx(base, f, t, rng)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
        brand(img, t)
        for o in self.ov:
            o.draw(img, t)
        return img

    def _vhs_stamp(self, base, t):
        d = ImageDraw.Draw(base)
        d.text((W - 70, 160), "PLAY ▶", font=font(F_MONO, 44), fill=(235, 235, 235), anchor="ra")
        d.text((W - 70, 214), "OCT 12 1997", font=font(F_MONO, 34), fill=(235, 235, 235), anchor="ra")


class StackScene:
    """hook / cta: three eras stacked."""
    def __init__(self, name, title_lines, caps, fx, cta=False):
        self.name, self.dur = name, DUR[name]
        self.n = int(round(self.dur * FPS))
        self.fx = fx
        self.cta = cta
        self.bg = vgrad(W, H, [(0, (9, 14, 28)), (0.5, (16, 26, 46)), (1, (8, 12, 22))])
        glow = Image.new("L", (W, H), 0)
        ImageDraw.Draw(glow).ellipse([140, 560, 940, 1400], fill=70)
        glow = glow.filter(ImageFilter.GaussianBlur(150))
        self.bg.paste(Image.new("RGB", (W, H), (255, 120, 50)), (0, 0), glow)
        self.scale = 0.66
        self.cars = [Car("mk1", self.scale), Car("mk4", self.scale), Car("mk8", self.scale)]
        self.tops = [540, 800, 1060]
        self.bands = []
        for col in ((150, 70, 30), (66, 60, 130), (30, 100, 190)):
            b = Image.new("RGBA", (1000, 240), (0, 0, 0, 0))
            bd = ImageDraw.Draw(b)
            bd.rounded_rectangle([0, 0, 999, 239], 44, fill=col + (205,))
            self.bands.append(b)
        self.labels = []
        for yr, mk in (("1974", "GOLF MK1"), ("1997", "GOLF MK4"), ("2024", "GOLF MK8")):
            self.labels.append((text_img(yr, F_BLACK, 78, (255, 255, 255), shadow=(0, 3, 5, .6), align="left"),
                                text_img(mk, F_XBOLD, 26, (255, 255, 255), spacing=5, align="left")))
        self.title = Overlay(text_img(title_lines[0], F_BLACK, 118 if not cta else 104, (255, 255, 255), shadow=(0, 6, 12, .6)), W // 2, 330, 0.2, dur=0.5, kind="zoom")
        self.title2 = Overlay(text_img(title_lines[1], F_BLACK, 118 if not cta else 104, ORANGE, shadow=(0, 6, 12, .6)), W // 2, 462, 0.4, dur=0.5, kind="zoom")
        self.ov = captions(caps)
        self.shadow = shadow_img(int(C.W * self.scale * 0.86))
        rnd = random.Random(5)
        L = Image.new("RGBA", (W, 600), (0, 0, 0, 0))
        ld = ImageDraw.Draw(L)
        for _ in range(26):
            x, y, ln = rnd.randint(0, W), rnd.randint(0, 600), rnd.randint(80, 320)
            ld.rectangle([x, y, x + ln, y + 3], fill=(255, 255, 255, rnd.randint(26, 70)))
        self.lines = tile2(L.crop((0, 0, W, 600)))
        if cta:
            self.wordmark = text_img("CarEra", F_BLACK, 66, (255, 255, 255), shadow=(0, 3, 5, .6))

    def frame(self, f):
        t = f / FPS
        rng = np.random.default_rng(5000 + hash(self.name) % 1000 * 10 + f)
        base = self.bg.copy()
        scroll_paste(base, self.lines, 520, t * FPS * 26)
        scroll_paste(base, self.lines, 1100, t * FPS * 18 + 300)
        for i in range(3):
            start = 0.25 + 0.3 * i
            p = ease_out((t - start) / 0.7)
            top = self.tops[i]
            band = self.bands[i]
            bx = 40 + (1 - p) * (-1100 if i != 1 else 1100)
            base.paste(band, (int(bx), top + 30), band)
            yl, ml = self.labels[i]
            paste_rgba(base, yl, 38 + (bx - 40) * 0 + 0, top + 60, clamp(p * 2)) if False else None
            la = clamp((t - start - 0.3) / 0.3)
            paste_rgba(base, yl, 56, top + 62, la)
            paste_rgba(base, ml, 56, top + 168, la)
            cx = 360 + (1 - p) * (-1200 if i != 1 else 1200)
            gy = top + 380 * self.scale + 4
            sx = int(cx + 0.66 * C.W / 2 - self.shadow.width / 2)
            base.paste(self.shadow, (sx, int(gy - 44)), self.shadow)
            self.cars[i].draw(base, cx, gy + 2 * math.sin(t * 8 + i), 12.0 * f * (1.0 if p > 0.98 else 1.8))
        a = self.fx(base, f, t, rng)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
        if self.cta:
            # brand row at top
            paste_rgba(img, EMB.resize((130, 130), Image.LANCZOS), W // 2 - 220, 80, clamp(t / 0.3))
            paste_rgba(img, self.wordmark, W // 2 - 60, 90, clamp(t / 0.3)) if False else None
            img.paste(self.wordmark.convert("RGB"), (W // 2 - 70, 145 - self.wordmark.height // 2), self.wordmark.getchannel("A").point(lambda v: int(v * clamp(t / 0.3))))
        else:
            brand(img, t)
        self.title.draw(img, t)
        self.title2.draw(img, t)
        for o in self.ov:
            o.draw(img, t)
        return img


def make_scene(name):
    if name == "hook":
        return StackScene("hook", ("ONE CAR.", "THREE ERAS."),
                          [(["This little hatchback", "saved Volkswagen."], 0.35, 2.3), (["Meet the Golf,", "in three eras."], 2.3, 3.95)], fx_hook)
    if name == "cta":
        return StackScene("cta", ("WHICH ERA", "IS YOUR GOLF?"),
                          [(["Over thirty-five", "million built."], 0.35, 2.8), (["Which era is your Golf?", "Comment below!"], 2.8, 5.95)], fx_cta, cta=True)
    cream = (255, 240, 205)
    if name == "e74":
        return EraScene("e74", build_74, "mk1", fx_74, "1974", "THE SEVENTIES", "VW GOLF MK1",
                        [("≈ 50 HP", (255, 214, 110, 255), (50, 30, 10)), ("UNDER 800 KG", (255, 255, 255, 235), (40, 30, 20))],
                        [(["1974. Bell-bottoms,", "cassette tapes."], 0.35, 2.7), (["A boxy, light Golf with just", "fifty horsepower."], 2.7, 5.95)],
                        "plain", cream)
    if name == "e97":
        return EraScene("e97", build_97, "mk4", fx_97, "1997", "THE NINETIES", "VW GOLF MK4",
                        [("AIRBAGS", (255, 255, 255, 235), (30, 20, 70)), ("TURBO DIESEL", (255, 70, 150, 255), (255, 255, 255))],
                        [(["1997. CDs and Tamagotchis.", "Now the Golf feels premium:"], 0.35, 3.8), (["airbags, a galvanized body,", "even turbo diesels."], 3.8, 6.95)],
                        "chroma", (255, 255, 255))
    if name == "e24":
        return EraScene("e24", build_24, "mk8", fx_24, "2024", "TODAY", "VW GOLF MK8",
                        [("≈ 130 HP", (255, 255, 255, 235), (14, 40, 90)), ("MILD-HYBRID", (60, 214, 150, 255), (6, 40, 28))],
                        [(["Today: a digital cockpit,", "mild-hybrid power,"], 0.35, 3.5), (["and it can help steer", "on the highway."], 3.5, 6.95)],
                        "plain", (255, 255, 255))
    raise SystemExit("unknown scene")


def encode_scene(name, out):
    sc = make_scene(name)
    tmp = out[:-4] + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(sc.n):
        p.stdin.write(sc.frame(f).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out)
        print("done", name, sc.n, "frames")
    else:
        raise SystemExit("ffmpeg failed for " + name)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "preview":
        pv = os.path.join(ROOT, "preview")
        os.makedirs(pv, exist_ok=True)
        shots = {"hook": [4, 75], "e74": [3, 8, 60], "e97": [3, 9, 80], "e24": [3, 9, 100], "cta": [2, 120]}
        only = sys.argv[2:] or list(shots)
        for n in only:
            sc = make_scene(n)
            for fr in shots[n]:
                sc.frame(fr).save(os.path.join(pv, f"{n}_{fr}.png"))
        print("preview ok")
    elif mode == "scene":
        n = sys.argv[2]
        encode_scene(n, os.path.join(ROOT, "scenes", n + ".mp4"))
