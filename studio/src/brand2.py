import sys; sys.path.insert(0,"/home/claude/vid/src")
import random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import urban as U, panels as P
OUT="/home/claude/vid/brand2/"
ORANGE,PINK,TEAL,BLUE,YEL=(255,128,30),(255,90,170),(0,205,190),(40,100,255),(255,214,40)
def wall(w,h,seed,tint=(20,10,10)):
    # concrete() is 1080x1920: tile/crop to size
    ow,oh=U.W,U.H; U.W,U.H=w,h
    try: return U.concrete(seed,tint).convert("RGBA")
    finally: U.W,U.H=ow,oh
def grain_vig(im,seed,amt=4,vig=0.28):
    a=np.asarray(im.convert("RGB")).astype(np.float32); h,w=a.shape[:2]
    a+=np.random.default_rng(seed).normal(0,amt,(h,w))[...,None]
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32); d=np.sqrt(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2)/1.42
    a*=(1-vig*d**2)[...,None]; return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def profile():
    P.rnd=random.Random(5); W=1080; bg=wall(W,W,5)
    for (w,h,col,dots,x,y,r) in [(560,520,(238,150,60),(190,80,30),150,170,-10),(560,520,PINK,(120,40,160),930,170,9),(560,520,TEAL,(10,80,70),150,910,8),(560,520,BLUE,(20,30,110),930,910,-8)]:
        U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
    U.paste(bg,U.spray_blob((900,760),(18,18,18),9),540,560,-6)
    hz=U.hazard(1500,70,YEL,(20,20,20)); U.paste(bg,U.hard_shadow(hz,(6,8)),540,560,-12)
    t1=U.spray_text("Car",300,(255,255,255),seed=3,drips=True); U.paste(bg,t1,520,420,-6)
    t2=U.spray_text("Era",300,YEL,seed=4,drips=True); U.paste(bg,t2,575,690,-6)
    grain_vig(bg,5).save(OUT+"profile_carera_1080.png")
    # circle preview
    m=Image.new("L",(W,W),0); ImageDraw.Draw(m).ellipse([0,0,W,W],fill=255)
    c=Image.open(OUT+"profile_carera_1080.png").convert("RGBA"); c.putalpha(m); c.save(OUT+"profile_preview_circle.png")
def banner():
    P.rnd=random.Random(11); W,H=2560,1440; bg=wall(W,H,11)
    posters=[(700,900,(238,196,120),(190,90,40),180,720,-7),(620,700,ORANGE,(150,60,20),640,420,6),(640,760,PINK,(120,40,160),1900,430,-6),(700,900,BLUE,(20,30,110),2380,720,7),(600,600,TEAL,(10,80,70),2050,1150,-5),(620,600,(250,230,90),(230,110,40),480,1160,5)]
    for (w,h,col,dots,x,y,r) in posters: U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(10,12),160),x,y,r)
    U.paste(bg,U.spray_blob((1500,640),(18,18,18),7),1280,700,-3)
    hz=U.hazard(3000,90,YEL,(20,20,20)); U.paste(bg,U.hard_shadow(hz,(6,8)),1280,905,-3)
    t=U.spray_text("CarEra",330,(255,255,255),seed=12,drips=True); U.paste(bg,t,1250,640,-3)
    lab=U.hard_shadow(U.label("ONE CAR. THREE ERAS.",72,(255,255,255),(15,15,15))); U.paste(bg,lab,1080,905,-3)
    mk=U.hard_shadow(U.marker_text("new car every week",64,(255,255,255),seed=4),(5,6),200); U.paste(bg,mk,1660,1005,-4)
    for (txt1,txt2,col,fg,x,y,r) in [("60s","OLDTIMER",ORANGE,(15,15,15),560,640,-8),("90s","YOUNGTIMER",PINK,(255,255,255),2000,600,8),("NOW","TODAY",BLUE,(255,255,255),2010,820,-6)]:
        U.paste(bg,U.hard_shadow(U.stat_disc(txt1,txt2,100,col,fg)),x,y,r)
    img=grain_vig(bg,11,4,0.22); img.save(OUT+"youtube_banner_2560x1440.png")
    # preview with safe zones
    pv=img.copy(); d=ImageDraw.Draw(pv)
    d.rectangle([(W-1546)//2,(H-423)//2,(W+1546)//2,(H+423)//2],outline=(0,255,0),width=6)
    d.rectangle([(W-2560)//2,(H-423)//2,(W+2560)//2,(H+423)//2],outline=(255,0,0),width=4)
    pv.thumbnail((1280,720)); pv.save(OUT+"banner_preview_safezones.png")
profile(); banner()
