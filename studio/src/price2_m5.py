"""Guess the price v2: old car = the riddle, two hints, countdown, reveal at 13.5 s."""
import sys; sys.path.insert(0,"/home/claude/vid/src")
import math, random
from PIL import Image, ImageDraw, ImageFont
import anim as A, urban as U, panels as P
from anim import prep, put, ease_out_back
from anim7 import L7
import price_r5 as B
from logotimer import Timer
from price_r5 import sprite, tag, Counter, Pulse, Delayed, bg_for, Zoom
# ---- EDIT PER CAR (copy this file to price2_<slug>.py) ----
import urban as U
MP="/home/claude/vid/m5/photos/"
ERAS=[dict(year="1985",car=MP+"e28_blue.png",cw=960,cy=820,price=27430,cur="$",note="M5 E28 · DM 80,750",pal=U.CFG[0]["pal"],posters=U.CFG[0]["posters"],seed=11,style="70"),
      dict(year="1998",car=MP+"e39_red.png",cw=980,cy=830,price=79580,cur="$",note="M5 E39 · DM 140,000",pal=U.CFG[1]["pal"],posters=U.CFG[1]["posters"],seed=21,style="90"),
      dict(year="2024",car=MP+"g90_green.png",cw=1000,cy=800,price=158240,cur="$",note="M5 G90 · €144,000",pal=U.CFG[2]["pal"],posters=U.CFG[2]["posters"],seed=31,style="24")]
NAME="BMW M5"
OUTDIR="/home/claude/vid/m5p/out/"
import m5cfg
def sprite(e,cw):
    car=Image.open(e["car"]).convert("RGBA"); car=car.crop(car.getbbox()); car=car.resize((cw,int(cw*car.height/car.width)),Image.LANCZOS)
    return U.hard_shadow(m5cfg.sticker_pad(car,14))
# -------------------------------------------------------------
REVEAL=13.5
OFF={"hook":0,"h1":3.5,"h2":7.5,"cd":11.5,"rv":13.5}
class Bar:
    """countdown bar at the top: 'ANSWER IN Ns'"""
    def __init__(s,off): s.off=off; s.cache={}; s.f=ImageFont.truetype(B.INTER,44)
    def draw(s,base,t,rng):
        g=s.off+t; rem=max(0,REVEAL-g); n=math.ceil(rem)
        frac=rem/REVEAL; key=(n,int(frac*200))
        if key not in s.cache:
            w,h=900,92; im=Image.new("RGBA",(w+16,h+16),(0,0,0,0)); d=ImageDraw.Draw(im)
            d.rounded_rectangle([8,8,w+8,h+8],46,fill=(15,15,15,235))
            fw=int((w-16)*frac)
            if fw>40: d.rounded_rectangle([16,16,16+fw,h],38,fill=(255,214,40,255) if n>3 else (235,50,80,255))
            d.text((w//2+8,h//2+8),f"ANSWER IN {n}s" if n>0 else "ANSWER!",font=s.f,fill=(255,255,255),anchor="mm",stroke_width=4,stroke_fill=(15,15,15))
            s.cache[key]=im
        im=s.cache[key]; put(base,im,540-im.width/2,40)
class Shake:
    def __init__(s,img,cx,cy,amp=6): s.img,s.cx,s.cy,s.amp=img,cx,cy,amp
    def draw(s,base,t,rng): put(base,s.img,s.cx-s.img.width/2+rng.uniform(-s.amp,s.amp),s.cy-s.img.height/2+rng.uniform(-s.amp,s.amp))
class Scramble:
    """slot-machine price tag: random digits spinning, slowing down"""
    def __init__(s,cx,cy,t0=0.0): s.cx,s.cy,s.t0=cx,cy,t0; s.cache={}
    def draw(s,base,t,rng):
        if t<s.t0: return
        step=int((t-s.t0)*(30 if t<1.4 else 15)); r=random.Random(step)
        v=r.randint(1000,9999); k=f"${v:,}"
        if k not in s.cache:
            if len(s.cache)>60: s.cache={}
            s.cache[k]=tag(k,150).rotate(-4,resample=Image.BICUBIC,expand=True)
        im=s.cache[k]; a=4+6*min(1,t/2)
        put(base,im,s.cx-im.width/2+rng.uniform(-a,a),s.cy-im.height/2+rng.uniform(-a,a))
class PushIn:
    def __init__(s,img,cx,cy,s1=1.12,dur=2.0): s.img,s.cx,s.cy,s.s1,s.dur=img,cx,cy,s1,dur
    def draw(s,base,t,rng):
        sc=1+(s.s1-1)*min(1,t/s.dur)**2; im=s.img.resize((int(s.img.width*sc),int(s.img.height*sc)),Image.BILINEAR)
        a=3*min(1,t/s.dur); put(base,im,s.cx-im.width/2+rng.uniform(-a,a),s.cy-im.height/2+rng.uniform(-a,a))
class Big321:
    def __init__(s,t0): s.t0=t0; s.ims={k:U.spray_text(str(k),520,(255,214,40) if k>1 else (235,50,80),seed=k) for k in (3,2,1)}
    def draw(s,base,t,rng):
        u=t-s.t0
        if u<0 or u>=1.95: return
        k=3-int(u/0.65); v=(u%0.65)/0.65; sc=1.35-0.35*min(1,v*3); im=s.ims[k]
        im=im.resize((int(im.width*sc),int(im.height*sc)),Image.BILINEAR); put(base,im,540-im.width/2,1000-im.height/2)
def L(img,x,y,r,t0,dur,kind,frm=(0,0),idle=None):
    im,px,py=prep(img,x,y,r); return L7(im,px,py,t0,dur,kind,frm,idle)
def mini_q(t0):
    old=sprite(ERAS[0],400); g=Image.new("RGBA",(460,380),(0,0,0,0)); g.alpha_composite(old,(0,0))
    q=tag("$?,???",70).rotate(6,resample=Image.BICUBIC,expand=True); g.alpha_composite(q,(min(460-q.width,110),old.height-30))
    return L(g,280,1610,-5,t0,0.3,"pop")
def hook():
    e=ERAS[0]; bg=bg_for(e); ls=[]
    ls.append(L(U.spray_text("GUESS",190,(255,255,255),seed=5),400,250,-4,0,0.35,"settle"))
    ls.append(L(U.spray_text("THE PRICE",140,(255,214,40),seed=6),420,420,-3,0,0.35,"settle"))
    ls.append(L(sprite(e,900),540,860,-3,0,0.35,"settle",idle=(6,3,0.8)))
    ls.append(L(U.spray_text(ERAS[0]["year"],170,(255,255,255),seed=7),210,1130,-8,0.15,0.3,"pop"))
    ls.append(L(U.hard_shadow(U.label(NAME,52,(255,255,255),(15,15,15))),760,1150,4,0.2,0.3,"pop"))
    ls.append(Pulse(tag("$ ?,???",150).rotate(-4,resample=Image.BICUBIC,expand=True),540,1350))
    ls.append(L(U.hard_shadow(U.label("COMMENT YOUR GUESS ↓",56,(15,15,15),(0,235,170))),540,1540,2,0.6,0.3,"pop"))
    ls.append(Timer(OFF["hook"],REVEAL,930,300,210))
    return bg,ls,3.5,"70",1
def hint(i,lab,key):
    e=ERAS[i]; bg=bg_for(e); ls=[]
    ls.append(L(U.hard_shadow(U.label(lab,60,(15,15,15),(255,214,40))),400,210,-3,0,0.3,"slide",(-1400,0)))
    ls.append(L(U.spray_text(e["year"],250,(255,255,255),seed=e["seed"]),400,390,-4,0.05,0.3,"slide",(0,-600)))
    ls.append(L(sprite(e,e["cw"]),540,e.get("cy",800)+20,-3,0.05,0.4,"slide",((1500 if i%2 else -1500),0),idle=(6,3,0.8)))
    ls.append(Counter(e["price"],540,1265,0.55,cur=e["cur"]))
    ls.append(L(U.hard_shadow(U.label(e["note"].replace(" · GERMANY",""),38,(255,255,255),(15,15,15))),540,1400,-2,1.9,0.3,"pop"))
    ls.append(mini_q(0.3))
    ls.append(L(U.hard_shadow(U.label(f"AND {ERAS[0]['year']}?",64,(255,255,255),(230,40,90))),780,1600,4,0.5,0.3,"pop"))
    ls.append(Timer(OFF[key],REVEAL,930,300,210))
    return bg,ls,4,e["style"],10+i
def countdown():
    e=ERAS[0]; bg=bg_for(e); ls=[]
    ls.append(L(U.spray_text("LAST",200,(255,255,255),seed=11),330,230,-4,0,0.25,"slide",(-1400,0)))
    ls.append(L(U.spray_text("CHANCE!",180,(235,50,80),seed=12),420,410,-3,0.1,0.25,"slide",(1400,0)))
    ls.append(PushIn(sprite(e,700),540,760))
    ls.append(Scramble(540,1130))
    ls.append(Timer(OFF["cd"],REVEAL,540,1480,330,grow=(0.35,930,300,210)))
    return bg,ls,2,"70",4
def reveal():
    e=ERAS[0]; bg=bg_for(e); ls=[]
    ls.append(L(U.spray_text(f"{e['year']} PRICE:",150,(255,255,255),seed=13),540,230,-4,0,0.3,"settle"))
    ls.append(L(sprite(e,820),540,620,-3,0,0.3,"settle",idle=(5,3,0.8)))
    ls.append(Counter(e["price"],540,1000,0.1,dur=0.9,cur=e["cur"]))
    ls.append(L(U.hard_shadow(U.label(e["note"].replace(" · GERMANY",""),38,(255,255,255),(15,15,15))),540,1135,-2,1.1,0.3,"pop"))
    n=ERAS[2]["price"]//e["price"]
    ls.append(L(U.hard_shadow(U.label(f"{n} OF THESE = 1 NEW ONE",54,(15,15,15),(0,235,170))),540,1270,2,1.5,0.3,"pop"))
    ls.append(Delayed(Pulse(U.hard_shadow(U.label("DID YOU GUESS RIGHT? ↓",62,(255,255,255),(15,15,15))),540,1420),2.0))
    ls.append(L(U.hard_shadow(U.label("COMMENT!",52,(15,15,15),(255,214,40))),270,1580,-6,2.4,0.3,"pop"))
    ls.append(Delayed(Pulse(U.hard_shadow(U.label("FOLLOW +",56,(255,255,255),(230,40,90))),790,1580),2.7))
    return bg,ls,4.5,"24",5
SC={"hook":hook,"h1":lambda:hint(2,"HINT 1: TODAY","h1"),"h2":lambda:hint(1,"HINT 2","h2"),"cd":countdown,"rv":reveal}
if __name__=="__main__":
    A.OUT=OUTDIR
    mode=sys.argv[1]; names=[n for n in sys.argv[2:] if not n.startswith("/")] or ["hook","h1","h2","cd","rv"]
    for n in names:
        bg,ls,d,st,sd=SC[n]()
        if mode=="preview": A.render_scene(n,bg,ls,d,st,sd,preview={0,15,40,58,100,130})
        else: A.render_scene(n,bg,ls,d,st,sd); print("done",n,flush=True)
