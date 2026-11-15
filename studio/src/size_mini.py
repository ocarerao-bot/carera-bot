import sys, os, math, random; sys.path.insert(0,"/home/claude/vid/src")
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import anim as A, urban as U, panels as P, minicfg
from anim import prep, put, ease_out
from anim7 import L7
from price_r5 import tag, Pulse, Delayed
C=minicfg.make()
LEN=[3.055,3.626,3.858]; YRS=["1959","2001","2024"]
PX=235; X0=60
INTER="/usr/share/fonts/opentype/inter/Inter-Black.otf"
SPR={}
def spr(i,w=None):
    w=int(w or LEN[i]*PX); k=(i,w)
    if k not in SPR:
        car=Image.open(f"/home/claude/vid/minisize/u{i+1}.png").convert("RGBA"); car=car.crop(car.getbbox())
        car=car.resize((w,int(w*car.height/car.width)),Image.LANCZOS)
        SPR[k]=U.hard_shadow(P.sticker(car,12))
    return SPR[k]
def ghost(im,a=0.33):
    g=im.copy(); al=np.asarray(g.getchannel("A")).astype(np.float32)*a; g.putalpha(Image.fromarray(al.astype(np.uint8)))
    return g
def tape(m=4.2):
    w=int(m*PX)+20; h=78; im=Image.new("RGBA",(w,h),(255,214,40,255)); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(INTER,30)
    for c in range(0,int(m*100)+1):
        x=10+c*PX/100; L_=34 if c%100==0 else (22 if c%10==0 else 0)
        if L_: d.line([(x,0),(x,L_)],fill=(15,15,15),width=4 if c%100==0 else 2)
        if c%100==0 and c>0: d.text((x,h-6),f"{c//100} m",font=f,fill=(15,15,15),anchor="mb")
    d.rectangle([0,0,w-1,h-1],outline=(15,15,15),width=3)
    return U.hard_shadow(im,(8,10))
def bracket(Lm,col=(230,40,90)):
    w=int(Lm*PX); im=Image.new("RGBA",(w+20,50),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.line([(10,25),(w+10,25)],fill=col+(255,),width=10); d.line([(10,4),(10,46)],fill=col+(255,),width=10); d.line([(w+10,4),(w+10,46)],fill=col+(255,),width=10)
    return U.hard_shadow(im,(5,6))
def lay(im,x,y,t0,dur,kind,frm=(0,0),idle=None): return L7(im,x,y,t0,dur,kind,frm,idle)
def bgc(i):
    cfg=C[i]; P.rnd=random.Random(cfg["seed"]); bg=U.concrete(cfg["seed"],cfg["pal"]["tint"])
    for (w,h,col,dots,x,y,r) in cfg["posters"]: U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
    U.paste(bg,U.spray_blob((1200,820),cfg["pal"]["blob"],cfg["seed"]+7),540,820,-4); return bg
BOT=1110; TY=1150
def era(i):
    bg=bgc(i); ls=[]
    yr=U.spray_text(YRS[i],300,(255,255,255),seed=C[i]["seed"]); im,x,y=prep(yr,540,240,-4); ls.append(lay(im,x,y,0,0.3,"slide",(0,-600)))
    lb=U.hard_shadow(U.label("MINI",58,(255,255,255),(15,15,15))); im,x,y=prep(lb,540,420,-3); ls.append(lay(im,x,y,0.1,0.3,"slide",(-1400,0)))
    tp=tape(); ls.append(lay(tp,X0-10,TY,0,0.35,"wipe"))
    for j in range(i):
        g=ghost(spr(j)); ls.append(lay(g,X0,BOT-g.height,0.1,0.3,"pop"))
        xm=X0+int(LEN[j]*PX)
        mk=Image.new("RGBA",(8,95),(15,15,15,255)); ls.append(lay(mk,xm-4,TY-8,0.3,0.3,"pop"))
        gl=U.hard_shadow(U.label(YRS[j],30,(255,255,255),(15,15,15))); ls.append(lay(gl,xm-gl.width//2,TY+88,0.3,0.3,"pop"))
    c=spr(i); ls.append(lay(c,X0,BOT-c.height,0.15,0.45,"slide",(-1400,0)))
    br=bracket(LEN[i]); ls.append(lay(br,X0-10,TY+150,0.7,0.5,"wipe"))
    m=f"{LEN[i]:.2f} m".replace("3.06","3.05"); ft=f"{LEN[i]*3.2808:.1f} FT"
    tg=tag(m,150).rotate(-4,resample=Image.BICUBIC,expand=True); im,x,y=prep(tg,540,1470); ls.append(lay(im,x,y,1.2,0.35,"pop"))
    fl=U.hard_shadow(U.label(ft,40,(255,255,255),(15,15,15))); im,x,y=prep(fl,540,1595,-2); ls.append(lay(im,x,y,1.6,0.3,"pop"))
    ex=[ "BUILT TO FIT A 10-FOOT BOX","+57 CM · ALMOST 2× HEAVIER","+80 CM · 26% LONGER"][i]
    e2=U.hard_shadow(U.label(ex,46,(15,15,15),(0,235,170))); im,x,y=prep(e2,540,1695,2); ls.append(lay(im,x,y,2.1,0.35,"pop"))
    return bg,ls,4,["70","90","24"][i],10+i
def hook():
    bg=bgc(2); ls=[]
    t1=U.spray_text("HOW MUCH",170,(255,255,255),seed=5); im,x,y=prep(t1,540,190,-4); ls.append(lay(im,x,y,0,0.35,"settle"))
    t2=U.spray_text("BIGGER?",190,(255,214,40),seed=6); im,x,y=prep(t2,560,380,-3); ls.append(lay(im,x,y,0,0.35,"settle"))
    k=0.85
    a=spr(0,LEN[0]*PX*k); ls.append(lay(a,X0,880-a.height,0,0.35,"settle"))
    la=U.hard_shadow(U.label("1959",48,(255,255,255),(15,15,15))); ls.append(lay(la,X0+a.width+25,880-a.height//2-30,0.2,0.3,"pop"))
    b=spr(2,LEN[2]*PX*k); ls.append(lay(b,X0,1400-b.height,0.9,0.4,"slide",(1400,0)))
    lb=U.hard_shadow(U.label("TODAY",48,(15,15,15),(255,214,40))); ls.append(lay(lb,X0+b.width-lb.width+20,1400-b.height-40,1.2,0.3,"pop"))
    ls.append(lay(bracket(LEN[0]*k),X0-10,900,0.4,0.4,"wipe")); ls.append(lay(bracket(LEN[2]*k),X0-10,1420,1.3,0.4,"wipe"))
    q=U.hard_shadow(U.label("GUESS THE DIFFERENCE ↓",50,(15,15,15),(0,235,170))); im,x,y=prep(q,540,1600,2); ls.append(lay(im,x,y,2.2,0.3,"pop"))
    return bg,ls,4,"24",1
def cta():
    P.rnd=random.Random(77); bg=U.concrete(77,(20,10,10))
    for (w,h,col,dots,x,y,r) in [(480,640,(238,196,120),(190,90,40),80,420,-8),(520,460,(255,120,190),(120,40,160),1010,640,7),(560,420,(40,100,255),(20,30,110),980,1150,-6),(420,540,(0,205,190),(10,80,70),70,1200,6)]:
        U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
    ls=[]
    t1=U.spray_text("IS IT STILL",150,(255,255,255),seed=8); im,x,y=prep(t1,540,190,-4); ls.append(lay(im,x,y,0,0.3,"slide",(0,-600)))
    t2=U.spray_text("A MINI?",190,(255,214,40),seed=9); im,x,y=prep(t2,560,380,-3); ls.append(lay(im,x,y,0.15,0.3,"slide",(-1300,0)))
    ys=[730,1010,1330]
    for i in range(3):
        s=spr(i,int(LEN[i]*PX*0.62)); ls.append(lay(s,X0,ys[i]-s.height,0.3+0.2*i,0.35,"slide",(-1400,0)))
        lb=U.hard_shadow(U.label(f"{YRS[i]} · {LEN[i]:.2f} m".replace("3.06","3.05"),36,(255,255,255),(15,15,15))); ls.append(lay(lb,X0+s.width+15,ys[i]-s.height//2-25,0.5+0.2*i,0.3,"pop"))
    q=U.hard_shadow(U.label("STILL MINI? YES OR NO ↓",46,(15,15,15),(255,214,40))); im,x,y=prep(q,540,1480,2); ls.append(lay(im,x,y,1.6,0.35,"pop"))
    f=U.hard_shadow(U.label("FOLLOW +",56,(255,255,255),(230,40,90))); ls.append(Delayed(Pulse(f,780,1620),2.2))
    c=U.hard_shadow(U.label("COMMENT!",50,(15,15,15),(0,235,170))); im,x,y=prep(c,280,1620,-6); ls.append(lay(im,x,y,2.0,0.35,"pop"))
    return bg,ls,4,"24",2
SC={"hook":hook,"e59":lambda:era(0),"e01":lambda:era(1),"e24":lambda:era(2),"cta":cta}
if __name__=="__main__":
    A.OUT="/home/claude/vid/minisize/out/"
    mode=sys.argv[1]; names=sys.argv[2:] or ["hook","e59","e01","e24","cta"]
    for n in names:
        bg,ls,d,st,sd=SC[n]()
        if mode=="preview": A.render_scene(n,bg,ls,d,st,sd,preview={100})
        else: A.render_scene(n,bg,ls,d,st,sd); print("done",n,flush=True)
