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


import numpy as np
def recolor_green(car):
    a=np.asarray(car.convert("RGBA")).astype(np.float32)
    rgb=Image.fromarray(a[...,:3].astype(np.uint8)).convert("HSV")
    h=np.asarray(rgb).astype(np.float32)
    H_,S_,V_=h[...,0],h[...,1],h[...,2]
    dh=np.minimum(H_,255-H_)               # distance from red (hue wraps)
    w=np.clip(1-(dh-14)/24,0,1)*np.clip((S_-22)/45,0,1)   # soft red mask
    H2=H_*(1-w)+58*w                        # olive/lime green
    S2=S_*(1-w)+np.clip(S_*0.80,0,255)*w
    V2=V_*(1-w)+(V_*0.88)*w
    out=np.stack([H2,S2,V2],-1).astype(np.uint8)
    rgb2=np.asarray(Image.fromarray(out,"HSV").convert("RGB")).astype(np.float32)
    # 70s light: warm cast, faded blacks, warm glow on specular highlights
    rgb2=rgb2*np.array([1.07,1.0,0.88])+np.array([10,6,0])
    lum=rgb2.mean(-1,keepdims=True)
    spec=np.clip((lum-190)/60,0,1)
    rgb2=rgb2*(1-0.35*spec)+np.array([255,222,160])*0.35*spec
    # warm sunset rim light from the right, cooler/darker on the left
    yy,xx=np.mgrid[0:car.height,0:car.width].astype(np.float32)
    g=(xx/car.width)[...,None]
    rgb2=rgb2*(0.86+0.26*g)+np.array([30,14,-6])*(g**2)
    res=np.dstack([np.clip(rgb2,0,255),a[...,3]]).astype(np.uint8)
    return Image.fromarray(res,"RGBA")

def stamp(w,h,scene,inset=30,r=15,gap=42):
    base=Image.new("RGBA",(w,h),(0,0,0,0))
    sheet=Image.new("RGBA",(w,h),(250,247,238,255))
    sheet.paste(scene.convert("RGB").resize((w-2*inset,h-2*inset)),(inset,inset))
    m=Image.new("L",(w,h),255); d=ImageDraw.Draw(m)
    for x in range(gap//2,w,gap):
        for y in (0,h-1): d.ellipse([x-r,y-r,x+r,y+r],fill=0)
    for y in range(gap//2,h,gap):
        for x in (0,w-1): d.ellipse([x-r,y-r,x+r,y+r],fill=0)
    base.paste(sheet,(0,0),m)
    return base

SW,SH=984,1124
sc=Image.new("RGB",(SW,SH)); d=ImageDraw.Draw(sc)
for y in range(SH):
    t=min(1,y/760)
    d.line([0,y,SW,y],fill=(int(250-52*t),int(176-62*t),int(70-16*t)))
d.ellipse([440,190,820,570],fill=(255,226,150))
for i,(x,w_,h_) in enumerate([(0,120,230),(130,90,330),(230,150,200),(390,80,280),(480,110,170),(600,100,300),(710,130,220),(850,140,260)]):
    d.rectangle([x,760-h_,x+w_,760],fill=(120+i%3*8,70,48))
    for wy in range(760-h_+20,740,38):
        for wx in range(x+14,x+w_-14,30):
            if (wx*7+wy*3)%5<2: d.rectangle([wx,wy,wx+12,wy+16],fill=(255,214,120))
d.rectangle([0,760,SW,SH],fill=(66,48,42))
d.rectangle([0,760,SW,772],fill=(180,150,120))
for x in range(-20,SW,230): d.polygon([(x,1060),(x+150,1060),(x+170,1078),(x+20,1078)],fill=(232,204,150))
# car: recolour, shadow, place
car=Image.open("/home/claude/vid/photos/golf_mk1_clean2.png").convert("RGBA")
car=car.resize((920,int(920*car.height/car.width)),Image.LANCZOS)
car=recolor_green(car)
spr=sticker(car,12)
cx,bottom=SW//2+10,975
shadow=Image.new("RGBA",(SW,SH),(0,0,0,0))
ImageDraw.Draw(shadow).ellipse([cx-440,bottom-70,cx+420,bottom+20],fill=(10,6,4,200))
shadow=shadow.filter(ImageFilter.GaussianBlur(22))
sc=sc.convert("RGBA"); sc.alpha_composite(shadow)
sc.alpha_composite(spr,(int(cx-spr.width/2),int(bottom-spr.height+30)))
# film grain + warm fade on whole scene
arr=np.asarray(sc.convert("RGB")).astype(np.float32)
arr+=np.random.default_rng(5).normal(0,7,arr.shape[:2])[...,None]
arr=arr*0.94+12
sc=Image.fromarray(np.clip(arr,0,255).astype(np.uint8))
st=stamp(1040,1180,sc)

bg=paper_bg()
place(bg,st,540,1045,rot=-1.6)
for (x,y,r) in ((120,470,-38),(960,480,34),(110,1590,30),(965,1600,-32)):
    place(bg,tape(),x,y,r,shadow=False)
cols=[((255,255,255),(200,38,38)),((20,20,20),(250,240,200)),((255,220,60),(20,20,20)),((255,255,255),(30,90,170))]
x=105
for i,ch in enumerate("1974"):
    fg,bgc=cols[i]
    t=letter_tile(ch,170+rnd.randint(-12,12),fg,bgc,i*2+1)
    place(bg,t,x+t.width/2-20,250+rnd.randint(-18,18),rot=rnd.uniform(-9,9))
    x+=t.width-44
strip=torn(700,110,(28,28,30),amp=6)
ImageDraw.Draw(strip).text((strip.width/2,strip.height/2),"THE SEVENTIES",font=ImageFont.truetype(FD+"Inter-ExtraBold.otf",48),fill=(250,240,200),anchor="mm")
place(bg,strip,400,470,rot=-2.5)
place(bg,starburst("\u2248 50 HP",125,(255,214,60),(20,20,20)),215,1600,rot=-10)
place(bg,starburst("< 800 KG",125,(240,90,60),(255,255,255)),870,1610,rot=9)
clip=torn(900,170,(252,250,244),edge=(240,236,224),amp=6)
cd=ImageDraw.Draw(clip)
f1=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",34)
f2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",28)
cd.text((clip.width/2,66),"1974. Bell-bottoms, cassette tapes.",font=f1,fill=(30,30,30),anchor="mm")
cd.text((clip.width/2,114),"A boxy, light Golf with just fifty horsepower.",font=f2,fill=(30,30,30),anchor="mm")
place(bg,clip,540,1775,rot=-1.2)
a=np.asarray(bg.convert("RGB"),dtype=np.float32)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
dd=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/1.42
a*=(1-0.35*dd**2)[...,None]
Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save("/home/claude/vid/mock/zine_photo_v2.png")
print("ok")
