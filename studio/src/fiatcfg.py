import sys; sys.path.insert(0,"/home/claude/vid/src")
import copy, numpy as np
from PIL import Image
import urban as U, panels as P
FP="/home/claude/vid/fiat/photos/"
def recolor2(car,src,width,soft,hue,smin=18,sfloor=0,sscale=1.0,vscale=1.0,tint=(1,1,1),rim=(0,0,0)):
    a=np.asarray(car.convert("RGBA")).astype(np.float32)
    hsv=np.asarray(Image.fromarray(a[...,:3].astype(np.uint8)).convert("HSV")).astype(np.float32)
    Hh,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
    d=np.abs(Hh-src); d=np.minimum(d,255-d)
    w=np.clip(1-(d-width)/soft,0,1)*np.clip((S-smin)/30,0,1)
    S2=S*(1-w)+np.clip(np.maximum(S*sscale,sfloor),0,255)*w
    S3=np.clip(np.maximum(S*sscale,sfloor),0,255); V3=np.clip(V*vscale,0,255)
    full=np.asarray(Image.fromarray(np.stack([np.full_like(Hh,hue),S3,V3],-1).astype(np.uint8),"HSV").convert("RGB")).astype(np.float32)
    rgb=a[...,:3]*(1-w[...,None])+full*w[...,None]   # blend in RGB: no in-between hues
    lum=rgb.mean(-1,keepdims=True); spec=np.clip((lum-205)/45,0,1)
    rgb=rgb*(1-0.4*spec)+255*0.4*spec
    g=(np.mgrid[0:car.height,0:car.width][1].astype(np.float32)/car.width)[...,None]
    rgb=rgb*(np.array(tint)*(0.88+0.24*g))+np.array(rim)*(g**2)
    return Image.fromarray(np.dstack([np.clip(rgb,0,255),a[...,3]]).astype(np.uint8),"RGBA")
def car_sprite(cfg,cw):
    car=Image.open(cfg["car"]).convert("RGBA"); car=car.crop(car.getbbox()); car=car.resize((cw,int(cw*car.height/car.width)),Image.LANCZOS)
    car=recolor2(car,**cfg["rc2"])
    if cfg.get("glass"):
        from PIL import ImageDraw,ImageFilter
        w,h=car.size; m=Image.new("L",car.size,0); [ImageDraw.Draw(m).polygon([(x*w,y*h) for x,y in pg],fill=255) for pg in cfg["glass"]]; m=m.filter(ImageFilter.GaussianBlur(5))
        bl=car.filter(ImageFilter.GaussianBlur(9)); flat=Image.new("RGBA",car.size,(38,28,72,255))
        bl=Image.blend(bl,flat,0.6); bl.putalpha(car.getchannel("A")); car=Image.composite(bl,car,m)
    return U.hard_shadow(P.sticker(car,14))
def make():
    C=copy.deepcopy(U.CFG)
    C[0].update(year="1957",car=FP+"f1_np.png",carw=720,cy=770,trw=540,
      rc2=dict(src=52,width=14,soft=16,hue=124,smin=14,sfloor=165,sscale=3.0,vscale=0.92,tint=(1.06,1.0,0.9),rim=(34,16,-6)),
      strip="THE FIFTIES",w1="DOLCE VITA",w2="espresso & vespa",s1=("13","HP"),s2=("≈ 500","KG"),
      c1="1957. Dolce vita on four wheels,",c2="13 HP, and nearly 4 million built.")
    C[1].update(glass=[[(0.19,0.34),(0.37,0.07),(0.62,0.07),(0.60,0.31)],[(0.625,0.115),(0.755,0.12),(0.77,0.37),(0.60,0.335)],[(0.78,0.09),(0.92,0.13),(0.935,0.345),(0.775,0.345)]],year="1997",car=FP+"f2_np.png",carw=1000,cy=790,trw=640,
      rc2=dict(src=157,width=20,soft=14,hue=232,smin=95,sfloor=0,sscale=1.0,vscale=1.15,tint=(1.0,0.98,1.06),rim=(10,0,30)),
      strip="THE NINETIES",w1="DISCMAN & DIAL-UP",w2="built in Poland",s1=("≈ 39","HP"),s2=("≈ 700","KG"),
      c1="1997. Built in Poland, galvanized body,",c2="and just 39 horsepower.")
    C[2].update(year="2026",car=FP+"f3_np.png",carw=1000,cy=800,trw=700,
      rc2=dict(src=28,width=16,soft=18,hue=44,smin=40,sscale=1.0,vscale=1.12,tint=(1.0,1.02,0.98),rim=(10,16,30)),
      strip="TODAY",w1="MADE IN TORINO",w2="hybrid or electric",s1=("EV","OR HYBRID"),s2=("TURIN","BUILT"),
      c1="Today: built back home in Turin,",c2="as a hybrid or fully electric.")
    return C
