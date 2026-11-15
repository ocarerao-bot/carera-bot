"""Draws three Golf generations as side-view illustrations (facing right).
Sprite canvas: 1000 x 420, ground line at y=380.
Outputs body PNGs (transparent, without wheels) and wheel PNGs (square, for rotation)."""
import cairosvg, io, sys
from PIL import Image

RED = "#d7261e"
RED_DARK = "#8f1410"
RED_LIGHT = "#ef4a40"
W, H = 1000, 420
GROUND = 380

CARS = {
    # ---- Golf Mk1, 1974: boxy, round headlights, chrome bumpers
    "mk1": dict(
        wheel_r=66, rear_x=185, front_x=770, wheel_y=GROUND - 66,
        svg=f"""
<path d="M24 334 L12 262 L16 196 L30 180 L58 174 L132 70 Q136 62 150 62 L496 62 Q514 62 526 74
 L646 178 L846 196 Q874 200 886 218 L894 262 L888 334 Z" fill="{RED}"/>
<path d="M24 334 L12 262 L16 196 L30 180 L58 174 L132 70 Q136 62 150 62 L496 62 Q514 62 526 74
 L646 178 L846 196 Q874 200 886 218 L894 262 L888 334 Z" fill="none" stroke="{RED_DARK}" stroke-width="3"/>
<path d="M150 66 L496 66" stroke="{RED_LIGHT}" stroke-width="4" opacity=".6"/>
<!-- glass -->
<path d="M72 170 L140 82 L298 82 L298 170 Z" fill="#1f2a33"/>
<path d="M312 170 L312 82 L492 82 L512 86 L626 170 Z" fill="#1f2a33"/>
<path d="M142 82 L186 82 L132 170 L84 170 Z" fill="#ffffff" opacity=".10"/>
<!-- door lines, handles -->
<path d="M305 176 L305 322" stroke="{RED_DARK}" stroke-width="3"/>
<path d="M566 182 L570 322" stroke="{RED_DARK}" stroke-width="3"/>
<rect x="268" y="198" width="28" height="7" rx="3" fill="#c9ced3"/>
<rect x="520" y="202" width="28" height="7" rx="3" fill="#c9ced3"/>
<!-- sill -->
<path d="M110 318 L850 318 L850 334 L110 334 Z" fill="#1a1a1a"/>
<!-- headlight (round) + grille -->
<circle cx="860" cy="232" r="20" fill="#f3efe0" stroke="#9aa0a6" stroke-width="4"/>
<rect x="868" y="214" width="24" height="46" rx="4" fill="#161616"/>
<rect x="874" y="234" width="14" height="4" fill="#d5d9dd"/>
<rect x="844" y="262" width="38" height="12" rx="3" fill="#f0a020"/>
<!-- tail light -->
<rect x="12" y="204" width="20" height="50" rx="3" fill="#b3120e"/>
<rect x="12" y="204" width="20" height="15" rx="3" fill="#f0a020"/>
<!-- chrome bumpers -->
<rect x="828" y="290" width="76" height="22" rx="8" fill="#cfd3d7" stroke="#8b9096" stroke-width="2"/>
<rect x="0" y="290" width="62" height="22" rx="8" fill="#cfd3d7" stroke="#8b9096" stroke-width="2"/>
<!-- mirror -->
<path d="M632 176 L662 168 L666 182 L636 186 Z" fill="#1a1a1a"/>
""", ),
    # ---- Golf Mk4, 1997: rounded, smooth, bulbous nose
    "mk4": dict(
        wheel_r=70, rear_x=190, front_x=812, wheel_y=GROUND - 70,
        svg=f"""
<path d="M24 340 C12 306 12 236 22 190 L32 162 C62 118 124 52 236 38 L520 36
 C640 58 726 118 770 160 C832 168 930 184 968 216 C988 238 992 296 978 340 Z" fill="{RED}"/>
<path d="M24 340 C12 306 12 236 22 190 L32 162 C62 118 124 52 236 38 L520 36
 C640 58 726 118 770 160 C832 168 930 184 968 216 C988 238 992 296 978 340 Z" fill="none" stroke="{RED_DARK}" stroke-width="3"/>
<path d="M236 42 C330 34 440 34 520 40" stroke="{RED_LIGHT}" stroke-width="5" opacity=".55" fill="none"/>
<!-- glass -->
<path d="M72 156 C104 104 160 68 238 56 L400 54 L400 156 Z" fill="#1b2630"/>
<path d="M426 156 L426 54 L518 52 C612 70 676 112 724 156 Z" fill="#1b2630"/>
<path d="M92 150 C118 112 164 82 214 70 L176 70 C140 90 112 120 96 150 Z" fill="#fff" opacity=".10"/>
<!-- door lines, handles -->
<path d="M413 160 L413 322" stroke="{RED_DARK}" stroke-width="3"/>
<path d="M650 164 C654 230 656 290 656 322" stroke="{RED_DARK}" stroke-width="3" fill="none"/>
<rect x="364" y="182" width="36" height="8" rx="4" fill="{RED_DARK}"/>
<rect x="590" y="186" width="36" height="8" rx="4" fill="{RED_DARK}"/>
<!-- lower plastic -->
<path d="M36 316 L968 316 L976 340 L26 340 Z" fill="#1d1d1d"/>
<!-- headlight (swept) -->
<path d="M896 196 C930 198 960 206 972 222 L968 236 C940 228 912 222 888 224 Z" fill="#e8ecef" stroke="#9aa0a6" stroke-width="3"/>
<path d="M905 206 C930 208 950 212 960 220" stroke="#f6c244" stroke-width="3" fill="none"/>
<!-- grille / air intake -->
<path d="M930 262 L982 262 L984 300 L936 300 Z" fill="#171717"/>
<!-- tail light -->
<path d="M18 176 L34 170 L34 228 L18 230 Z" fill="#b3120e"/>
<!-- mirror -->
<path d="M706 156 L742 150 L746 166 L710 170 Z" fill="{RED_DARK}"/>
""", ),
    # ---- Golf Mk8, 2024: sleek, LED light strip, big wheels
    "mk8": dict(
        wheel_r=76, rear_x=192, front_x=815, wheel_y=GROUND - 76,
        svg=f"""
<path d="M28 344 C14 310 14 238 30 194 C70 128 150 60 292 44 L470 42
 C592 48 692 98 764 150 C846 166 934 186 968 222 C992 250 994 300 978 344 Z" fill="{RED}"/>
<path d="M28 344 C14 310 14 238 30 194 C70 128 150 60 292 44 L470 42
 C592 48 692 98 764 150 C846 166 934 186 968 222 C992 250 994 300 978 344 Z" fill="none" stroke="{RED_DARK}" stroke-width="3"/>
<path d="M300 46 C380 40 440 40 480 44" stroke="{RED_LIGHT}" stroke-width="5" opacity=".6" fill="none"/>
<!-- shoulder crease -->
<path d="M40 214 C300 190 620 190 900 232" stroke="{RED_DARK}" stroke-width="3" fill="none" opacity=".8"/>
<path d="M44 208 C300 184 620 184 900 226" stroke="{RED_LIGHT}" stroke-width="2" fill="none" opacity=".5"/>
<!-- glass -->
<path d="M90 160 C128 108 190 72 296 60 L408 58 L408 160 Z" fill="#0f1720"/>
<path d="M432 160 L432 58 L476 56 C584 62 672 104 730 158 Z" fill="#0f1720"/>
<path d="M120 152 C148 118 190 90 240 76 L206 76 C170 94 142 122 126 152 Z" fill="#fff" opacity=".12"/>
<!-- door lines -->
<path d="M420 164 L420 326" stroke="{RED_DARK}" stroke-width="3"/>
<path d="M664 166 C668 240 670 296 670 326" stroke="{RED_DARK}" stroke-width="3" fill="none"/>
<!-- flush handles -->
<rect x="372" y="196" width="34" height="6" rx="3" fill="{RED_DARK}"/>
<rect x="600" y="200" width="34" height="6" rx="3" fill="{RED_DARK}"/>
<!-- lower black trim -->
<path d="M40 322 L970 322 L980 344 L30 344 Z" fill="#17191b"/>
<!-- LED headlight, slim -->
<path d="M876 196 C920 198 954 206 972 224 L966 232 C936 222 904 216 872 218 Z" fill="#f4f8ff" stroke="#8d96a1" stroke-width="2"/>
<path d="M880 206 C920 206 950 212 966 222" stroke="#7fd3ff" stroke-width="3" fill="none"/>
<!-- light strip / lower intake -->
<path d="M930 268 L986 268 L986 308 L938 308 Z" fill="#101214"/>
<path d="M936 278 L984 278" stroke="#3a3f45" stroke-width="2"/>
<!-- LED tail strip -->
<path d="M20 186 L44 176 L46 206 L22 214 Z" fill="#d1121b"/>
<path d="M22 196 L44 190" stroke="#ff8a8a" stroke-width="3"/>
<!-- mirror -->
<path d="M716 162 L752 154 L758 170 L720 176 Z" fill="#0f1720"/>
""", ),
}


def render_svg(inner, w=W, h=H, scale=1):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{inner}</svg>'
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=int(w * scale), output_height=int(h * scale))
    return Image.open(io.BytesIO(png)).convert("RGBA")


def wheel_svg(kind, r):
    c = r + 4
    size = 2 * c
    inner = ""
    if kind == "mk1":  # steel wheel with chrome hubcap
        inner = f"""
<circle cx="{c}" cy="{c}" r="{r}" fill="#101010"/>
<circle cx="{c}" cy="{c}" r="{r*0.64}" fill="#aeb4ba"/>
<circle cx="{c}" cy="{c}" r="{r*0.50}" fill="#d9dde0"/>
<circle cx="{c}" cy="{c}" r="{r*0.20}" fill="#8a9097"/>
""" + "".join(
            f'<circle cx="{c + r*0.56*__import__("math").cos(a)}" cy="{c + r*0.56*__import__("math").sin(a)}" r="{r*0.05}" fill="#6f757b"/>'
            for a in [i * 6.2832 / 5 for i in range(5)])
    elif kind == "mk4":  # 5-spoke alloy
        import math
        spokes = ""
        for i in range(5):
            a = i * 2 * math.pi / 5 + 0.3
            x1, y1 = c + r * 0.14 * math.cos(a), c + r * 0.14 * math.sin(a)
            x2, y2 = c + r * 0.62 * math.cos(a), c + r * 0.62 * math.sin(a)
            spokes += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#c8ccd0" stroke-width="{r*0.17}" stroke-linecap="round"/>'
        inner = f"""
<circle cx="{c}" cy="{c}" r="{r}" fill="#0e0e0e"/>
<circle cx="{c}" cy="{c}" r="{r*0.68}" fill="#6b7076"/>
<circle cx="{c}" cy="{c}" r="{r*0.64}" fill="#3a3e42"/>
{spokes}
<circle cx="{c}" cy="{c}" r="{r*0.13}" fill="#9aa0a6"/>
"""
    else:  # mk8: big dark multi-spoke alloy
        import math
        spokes = ""
        for i in range(10):
            a = i * 2 * math.pi / 10
            x1, y1 = c + r * 0.18 * math.cos(a), c + r * 0.18 * math.sin(a)
            x2, y2 = c + r * 0.70 * math.cos(a), c + r * 0.70 * math.sin(a)
            spokes += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#d9dee3" stroke-width="{r*0.08}" stroke-linecap="round"/>'
        inner = f"""
<circle cx="{c}" cy="{c}" r="{r}" fill="#0c0c0d"/>
<circle cx="{c}" cy="{c}" r="{r*0.74}" fill="#2a2d31"/>
<circle cx="{c}" cy="{c}" r="{r*0.71}" fill="#15171a"/>
{spokes}
<circle cx="{c}" cy="{c}" r="{r*0.14}" fill="#c9ced3"/>
"""
    return inner, size


def build(name):
    spec = CARS[name]
    body = render_svg(spec["svg"], scale=2)  # 2x supersample
    inner, size = wheel_svg(name, spec["wheel_r"])
    wheel = render_svg(inner, w=size, h=size, scale=2)
    return body, wheel, spec


def compose_static(name, wheel_angle=0):
    body, wheel, spec = build(name)
    # wheel wells (dark) under tyres
    img = Image.new("RGBA", body.size, (0, 0, 0, 0))
    img.alpha_composite(body)
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    r = spec["wheel_r"]
    for cx in (spec["rear_x"], spec["front_x"]):
        rr = (r + 12) * 2
        d.ellipse([cx * 2 - rr, spec["wheel_y"] * 2 - rr, cx * 2 + rr, spec["wheel_y"] * 2 + rr], fill=(14, 14, 16, 255))
    for cx in (spec["rear_x"], spec["front_x"]):
        wr = wheel.rotate(-wheel_angle, resample=Image.BICUBIC)
        x = int(cx * 2 - wr.width / 2)
        y = int(spec["wheel_y"] * 2 - wr.height / 2)
        img.alpha_composite(wr, (x, y))
    return img.resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    out = sys.argv[1]
    sheet = Image.new("RGB", (W, H * 3 + 40), (60, 70, 85))
    for i, n in enumerate(["mk1", "mk4", "mk8"]):
        car = compose_static(n)
        sheet.paste(car, (0, i * (H + 20)), car)
    sheet.save(out)
    print("ok")
