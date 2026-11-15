import sys; sys.path.insert(0,"/home/claude/vid/src")
import random, numpy as np
from PIL import Image
import urban as U, panels as P, anim as A
W,H=1080,1350
C=U.CFG; P.rnd=random.Random(5)
bg=U.concrete(5,(15,10,10)).crop((0,200,W,200+H))
def pst(w,h,col,dots,x,y,r): U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
pst(520,700,(238,196,120),(190,90,40),70,330,-8); pst(520,520,(255,120,190),(120,40,160),1010,520,7)
pst(560,480,(40,100,255),(20,30,110),990,1010,-6); pst(430,560,(0,205,190),(10,80,70),60,1060,6)
for (c,x,y) in ((C[0],340,600),(C[1],740,780),(C[2],340,985)):
    U.paste(bg,U.spray_blob((860,500),c["pal"]["blob"],c["seed"]+3),x,y,0)
for (c,cx,cy,rot,tx,ty) in ((C[0],345,575,-4,175,735),(C[1],735,775,3,930,925),(C[2],345,985,-3,665,1120)):
    sp=A.car_sprite(c,700); U.paste(bg,sp,cx,cy,rot)
    tg=U.hard_shadow(U.label(c["year"],50,(255,255,255),(15,15,15))); U.paste(bg,tg,tx,ty,-6 if cx<500 else 6)
t=U.spray_text("CarEra",250,(255,255,255),seed=3); U.paste(bg,t,540,175,-3)
U.paste(bg,U.marker_line(520,(255,214,40),thick=14,seed=4,wob=9),540,330,-2)
hz=U.hazard(1300,84,(255,200,0),(20,20,20)); U.paste(bg,U.hard_shadow(hz,(6,8)),540,1262,-3)
lab=U.label("CARS THROUGH TIME",54,(255,255,255),(15,15,15)); U.paste(bg,U.hard_shadow(lab,(8,10)),480,1262,-3)
em=Image.open("/home/claude/vid/assets/emblem.png").convert("RGBA").resize((130,130),Image.LANCZOS); U.paste(bg,U.hard_shadow(P.sticker(em,8)),940,1240,6)
a=np.asarray(bg.convert("RGB")).astype(np.float32)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32); dd=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/1.42
a*=(1-0.3*dd**2)[...,None]; a+=np.random.default_rng(1).normal(0,3,(H,W))[...,None]
Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save("/home/claude/vid/urban/final/carera_instagram_banner_1080x1350.png")
print("ok")
