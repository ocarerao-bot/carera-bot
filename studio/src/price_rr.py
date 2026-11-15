"""CarEra 'Then vs Now: Price' reel (test: Ford Mustang)."""
import sys; sys.path.insert(0,"/home/claude/vid/src")
import os, math, random, numpy as np
from PIL import Image, ImageDraw, ImageFont
import anim as A, urban as U, panels as P, subs
from anim import prep, put, ease_out, ease_out_back
from anim7 import L7
W,H=1080,1920
INTER="/usr/share/fonts/opentype/inter/Inter-Black.otf"
MP="/home/claude/vid/rr/photos/"
ERAS=[dict(year="1970",car=MP+"m1.png",cw=860,cy=830,price=4795,cur="$",note="UK · £1,998",extra="THE VERY FIRST ONE",pal=U.CFG[0]["pal"],posters=U.CFG[0]["posters"],seed=11,style="70"),
      dict(year="1994",car=MP+"m2.png",cw=1000,cy=850,price=48940,cur="$",note="4.0 SE · UK · £31,950",extra="THE \"P38\"",pal=U.CFG[1]["pal"],posters=U.CFG[1]["posters"],seed=21,style="90"),
      dict(year="2026",car=MP+"m3.png",cw=1000,cy=800,price=142160,cur="$",note="D300 SE · UK · £107,530",extra="THE BASE MODEL!",pal=U.CFG[2]["pal"],posters=U.CFG[2]["posters"],seed=31,style="24")]
import fiatcfg
def recolor_white(car,hue,sat,vmul,noglass=False):
    a=np.asarray(car.convert("RGBA")).astype(np.float32)
    hsv=np.asarray(Image.fromarray(a[...,:3].astype(np.uint8)).convert("HSV")).astype(np.float32)
    Hh,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
    w=np.clip((V-105)/35,0,1)*np.clip((125-S)/30,0,1)
    from PIL import ImageDraw, ImageFilter
    gm=Image.new("L",car.size,0); hh,ww=car.height,car.width
    ImageDraw.Draw(gm).polygon([(0.13*ww,0.04*hh),(0.87*ww,0.04*hh),(0.93*ww,0.30*hh),(0.07*ww,0.30*hh)],fill=255)
    if not noglass: w=w*(1-np.asarray(gm.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)/255)   # keep the windscreen glass
    vv=np.clip(V*vmul*1.25*(0.3+0.7*(V/255)**3),0,255)                     # deep paint, keeps the shading
    full=np.asarray(Image.fromarray(np.stack([np.full_like(Hh,hue),np.full_like(S,sat),vv],-1).clip(0,255).astype(np.uint8),"HSV").convert("RGB")).astype(np.float32)
    rgb=a[...,:3]*(1-w[...,None])+full*w[...,None]
    spec=np.clip((V-215)/30,0,1)[...,None]*w[...,None]   # keep the brightest reflections
    rgb=rgb*(1-0.7*spec)+255*0.7*spec
    return Image.fromarray(np.dstack([np.clip(rgb,0,255),a[...,3]]).astype(np.uint8),"RGBA")
def recolor_silver(car,hue,sat,vmul):
    a=np.asarray(car.convert("RGBA")).astype(np.float32)
    hsv=np.asarray(Image.fromarray(a[...,:3].astype(np.uint8)).convert("HSV")).astype(np.float32)
    Hh,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
    w=np.clip((V-75)/30,0,1)*np.clip((115-S)/35,0,1)
    vv=np.clip(V*vmul,0,255); ss=np.clip(sat*(0.55+0.45*(1-V/255)),0,255)
    full=np.asarray(Image.fromarray(np.stack([np.full_like(Hh,hue),ss,vv],-1).astype(np.uint8),"HSV").convert("RGB")).astype(np.float32)
    rgb=a[...,:3]*(1-w[...,None])+full*w[...,None]
    spec=np.clip((V-235)/20,0,1)[...,None]*w[...,None]; rgb=rgb*(1-0.6*spec)+255*0.6*spec
    return Image.fromarray(np.dstack([np.clip(rgb,0,255),a[...,3]]).astype(np.uint8),"RGBA")
def sprite(e,cw):
    car=Image.open(e["car"]).convert("RGBA"); car=car.crop(car.getbbox()); car=car.resize((cw,int(cw*car.height/car.width)),Image.LANCZOS)
    if e.get("rc2"): car=fiatcfg.recolor2(car,**e["rc2"])
    if e.get("silver"): car=recolor_silver(car,*e["silver"])
    if e.get("white"): car=recolor_white(car,*e["white"],noglass=e.get("noglass",False))
    return U.hard_shadow(P.sticker(car,14))
def tag(txt,size=150,bg=(255,214,40),fg=(15,15,15)):
    f=ImageFont.truetype(INTER,size); w=int(f.getlength(txt))+110; h=int(size*1.35)
    im=Image.new("RGBA",(w+20,h+20),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.polygon([(10,10+h//2),(60,10),(w+10,10),(w+10,h+10),(60,h+10)],fill=bg+(255,),outline=(15,15,15,255))
    d.ellipse([40,10+h//2-11,62,10+h//2+11],fill=(15,15,15,255))
    d.text((w//2+40,10+h//2),txt,font=f,fill=fg,anchor="mm"); return U.hard_shadow(im,(10,12))
class Counter:
    """price tag that rolls from 0 to value, then pops"""
    def __init__(s,val,cx,cy,t0,dur=1.3,rot=-4,cur="$"): s.val,s.cx,s.cy,s.t0,s.dur,s.rot,s.cur=val,cx,cy,t0,dur,rot,cur; s.cache={}
    def txt(s,v): return s.cur+f"{v:,}"
    def draw(s,base,t,rng):
        if t<s.t0: return
        u=min(1,(t-s.t0)/s.dur); v=int(round(s.val*(1-(1-u)**3)))
        if u<1: v=int(round(v/7))*7 if v<s.val else v
        key=v if u<1 else "final"
        if key not in s.cache:
            im=tag(s.txt(v if u<1 else s.val)); s.cache[key]=im.rotate(s.rot,resample=Image.BICUBIC,expand=True)
        im=s.cache[key]; sc=1.0
        if u>=1: k=min(1,(t-s.t0-s.dur)/0.25); sc=1+0.18*(1-ease_out_back(k,2.5)) if k<1 else 1
        if sc!=1: im=im.resize((int(im.width*sc),int(im.height*sc)),Image.BILINEAR)
        put(base,im,s.cx-im.width/2,s.cy-im.height/2)
class Pulse:
    def __init__(s,img,cx,cy): s.img,s.cx,s.cy=img,cx,cy
    def draw(s,base,t,rng):
        sc=1+0.05*math.sin(t*9); im=s.img.resize((int(s.img.width*sc),int(s.img.height*sc)),Image.BILINEAR)
        put(base,im,s.cx-im.width/2,s.cy-im.height/2)
def bg_for(e):
    P.rnd=random.Random(e["seed"]); bg=U.concrete(e["seed"],e["pal"]["tint"])
    for (w,h,col,dots,x,y,r) in e["posters"]: U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
    U.paste(bg,U.spray_blob((1200,820),e["pal"]["blob"],e["seed"]+7),540,760,-4); return bg
def era_scene(i):
    e=ERAS[i]; bg=bg_for(e); ls=[]
    yr=U.spray_text(e["year"],300,(255,255,255),seed=e["seed"]); im,x,y=prep(yr,540,250,-4); ls.append(L7(im,x,y,0,0.3,"slide",(0,-600)))
    lab=U.hard_shadow(U.label("RANGE ROVER",58,(255,255,255),(15,15,15))); im,x,y=prep(lab,540,430,-3); ls.append(L7(im,x,y,0.1,0.3,"slide",(-1400,0)))
    car=sprite(e,e["cw"]); im,x,y=prep(car,540,e.get("cy",800),-3); ls.append(L7(im,x,y,0.05,0.4,"slide",((1500 if i%2 else -1500),0),idle=(6,3,0.8)))
    ls.append(Counter(e["price"],540,1245,0.55,cur=e["cur"]))
    nt=U.hard_shadow(U.label(e["note"],40,(255,255,255),(15,15,15))); im,x,y=prep(nt,540,1385,-2); ls.append(L7(im,x,y,1.9,0.3,"pop"))
    if e["extra"]:
        ex=U.hard_shadow(U.label(e["extra"],46,(15,15,15),(0,235,170))); im,x,y=prep(ex,540,1478,2); ls.append(L7(im,x,y,2.3,0.35,"pop"))
    return bg,ls,4,e["style"],10+i
class Zoom:
    """zoom-out from a close-up: scale s0 -> 1 around focus point (fx,fy in sprite coords)"""
    def __init__(s,img,cx,cy,fx,fy,s0=2.6,dur=0.55,idle=(5,3,0.8)): s.img,s.cx,s.cy,s.fx,s.fy,s.s0,s.dur,s.idle=img,cx,cy,fx,fy,s0,dur,idle
    def draw(s,base,t,rng):
        u=min(1,t/s.dur); e=1-(1-u)**3; sc=s.s0+(1-s.s0)*e
        im=s.img if sc==1 else s.img.resize((int(s.img.width*sc),int(s.img.height*sc)),Image.BILINEAR)
        # keep focus point fixed on screen while zooming, ending centred at (cx,cy)
        fx_end=s.cx-s.img.width/2+s.fx; fy_end=s.cy-s.img.height/2+s.fy
        x=fx_end-s.fx*sc; y=fy_end-s.fy*sc
        x+=s.idle[0]*math.sin(t*s.idle[2]); y+=s.idle[1]*math.sin(t*s.idle[2]+1)
        put(base,im,x,y)
def hook():
    e=ERAS[2]; bg=bg_for(e); ls=[]
    new=sprite(e,700); ls.append(Zoom(new,540,620,new.width*0.55,new.height*0.62))
    t1=U.spray_text("GUESS",190,(255,255,255),seed=5); im,x,y=prep(t1,540,175,-4); ls.append(L7(im,x,y,0,0.35,"settle"))
    t2=U.spray_text("THE PRICE",140,(255,214,40),seed=6); im,x,y=prep(t2,560,345,-3); ls.append(L7(im,x,y,0,0.35,"settle"))
    tg=tag("$142,160",120).rotate(-4,resample=Image.BICUBIC,expand=True); im,x,y=prep(tg,640,900); ls.append(L7(im,x,y,0.35,0.25,"pop"))
    old=sprite(ERAS[0],660); im,x,y=prep(old,560,1250,-3); ls.append(L7(im,x,y,1.2,0.3,"slide",(-1500,0),idle=(5,3,0.9)))
    yr=U.spray_text("1970?",150,(255,214,40),seed=6); im,x,y=prep(yr,230,1060,-8); ls.append(L7(im,x,y,1.35,0.3,"pop"))
    q=tag("$ ?,???",110).rotate(4,resample=Image.BICUBIC,expand=True); ls.append(Delayed(Pulse(q,700,1500),1.5))
    g=U.hard_shadow(U.label("ONLY ONE? COMMENT ↓",50,(15,15,15),(0,235,170))); im,x,y=prep(g,540,1620,2); ls.append(L7(im,x,y,2.2,0.3,"pop"))
    return bg,ls,4,"24",1
class Delayed:
    def __init__(s,layer,t0): s.l,s.t0=layer,t0
    def draw(s,base,t,rng):
        if t>=s.t0: s.l.draw(base,t-s.t0,rng)
def cta():
    P.rnd=random.Random(77); bg=U.concrete(77,(20,10,10))
    for (w,h,col,dots,x,y,r) in [(480,640,(238,196,120),(190,90,40),80,420,-8),(520,460,(255,120,190),(120,40,160),1010,640,7),(560,420,(40,100,255),(20,30,110),980,1150,-6),(420,540,(0,205,190),(10,80,70),70,1200,6)]:
        U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
    ls=[]
    t1=U.spray_text("29 OF THESE",150,(255,255,255),seed=8); im,x,y=prep(t1,540,220,-4); ls.append(L7(im,x,y,0,0.3,"slide",(0,-600)))
    small=sprite(ERAS[0],150); rows=[6,6,6,6,5]; k=0
    for r,n in enumerate(rows):
        for j in range(n):
            cx=540+(j-(n-1)/2)*162; cy=380+r*108
            im,x,y=prep(small,cx,cy,random.Random(k).uniform(-6,6)); ls.append(L7(im,x,y,0.15+0.03*k,0.18,"pop")); k+=1
    t2=U.spray_text("= ONE NEW ONE",120,(255,214,40),seed=9); im,x,y=prep(t2,540,960,-3); ls.append(L7(im,x,y,1.2,0.3,"slide",(-1300,0)))
    big=sprite(ERAS[2],470); im,x,y=prep(big,540,1200,-2); ls.append(L7(im,x,y,1.35,0.35,"pop",idle=(4,2,0.8)))
    q=U.hard_shadow(U.label("1970 OR 2026? YOU ONLY GET ONE ↓",42,(15,15,15),(255,214,40))); im,x,y=prep(q,540,1440,2); ls.append(L7(im,x,y,2.0,0.35,"pop"))
    f=U.hard_shadow(U.label("FOLLOW +",50,(255,255,255),(230,40,90))); im,x,y=prep(f,870,1080,8); ls.append(L7(im,x,y,2.6,0.35,"pop"))
    c=U.hard_shadow(U.label("COMMENT!",50,(15,15,15),(0,235,170))); im,x,y=prep(c,200,1110,-8); ls.append(L7(im,x,y,2.8,0.35,"pop"))
    return bg,ls,4,"24",2
SC={"hook":hook,"p1":lambda:era_scene(0),"p2":lambda:era_scene(1),"p3":lambda:era_scene(2),"cta":cta}
if __name__=="__main__":
    A.OUT="/home/claude/vid/rr/out/"; os.makedirs(A.OUT+"scenes",exist_ok=True); os.makedirs(A.OUT+"prev",exist_ok=True)
    mode=sys.argv[1]; names=sys.argv[2:] or ["hook","p3","p2","p1","cta"]
    for n in names:
        bg,ls,d,st,sd=SC[n]()
        if mode=="preview": A.render_scene(n,bg,ls,d,st,sd,preview={0,20,45,100})
        else: A.render_scene(n,bg,ls,d,st,sd); print("done",n,flush=True)
