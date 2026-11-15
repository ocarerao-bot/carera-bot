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
    H2=Hh*(1-w)+hue*w; V2=V*(1-w)+np.clip(V*vscale,0,255)*w
    rgb=np.asarray(Image.fromarray(np.stack([H2,S2,V2],-1).astype(np.uint8),"HSV").convert("RGB")).astype(np.float32)
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
    MP="/home/claude/vid/mini/photos/"
    C=copy.deepcopy(U.CFG)
    C[0].update(year="1959",car=MP+"m1_np.png",carw=900,cy=770,trw=540,
      rc2=dict(src=90,width=22,soft=18,hue=124,smin=12,sfloor=150,sscale=2.2,vscale=1.05,tint=(1.06,1.0,0.9),rim=(34,16,-6)),
      strip="THE FIFTIES",w1="ROCK 'N' ROLL",w2="10-inch wheels",s1=("34","HP"),s2=("848","CC"),c1="",c2="")
    C[1].update(year="2001",car=MP+"m2_np.png",carw=1000,cy=800,trw=700,
      rc2=dict(src=0,width=0,soft=1,hue=0,smin=300),
      strip="Y2K",w1="FLIP PHONES & MP3",w2="built in Oxford",s1=("115","HP"),s2=("1.6","LITRE"),c1="",c2="")
    C[2].update(year="2024",car=MP+"m3_np.png",carw=820,cy=790,trw=520,
      rc2=dict(src=165,width=22,soft=18,hue=44,smin=60,sfloor=0,sscale=1.0,vscale=1.25,tint=(1.0,1.02,0.98),rim=(10,16,30)),
      strip="TODAY",w1="FULLY ELECTRIC",w2="round OLED screen",s1=("218","HP"),s2=("MADE IN","CHINA"),c1="",c2="")
    return C
