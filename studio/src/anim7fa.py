import sys; sys.path.insert(0,"/home/claude/vid/src")
import math, random, numpy as np
from PIL import Image
import anim as A, urban as U, panels as P
from PIL import ImageFont as _IF
U.F=lambda name,size: _IF.truetype("/home/claude/vid/fonts/Lalezar-Regular.ttf",int(size*1.05))
import beetlecfg; A.car_sprite=beetlecfg.car_sprite
from anim import L, prep, ease_out, ease_out_back, put
W,H=1080,1920
class L7(L):
    def draw(s,base,t,rng):
        if s.kind=="settle":
            u=min(1,max(0,(t-s.t0)/s.dur)); sc=1+0.13*(1-ease_out(u)); im=s.img; x,y=s.x,s.y
            if sc>1.002:
                w,h=im.size; nw,nh=int(w*sc),int(h*sc); im=im.resize((nw,nh),Image.BILINEAR); x-=(nw-w)/2; y-=(nh-h)/2
            if s.idle: x+=s.idle[0]*math.sin(t*s.idle[2]); y+=s.idle[1]*math.sin(t*s.idle[2]+1)
            put(base,im,x,y)
        else: super().draw(base,t,rng)
def caption7(c1,c2,t0,cy):
    c=A.caption(c1,c2,t0,cy); c.dur=0.35; return c
def era7(cfg,side):
    seed=cfg["seed"]; pal=cfg["pal"]; P.rnd=random.Random(seed)
    bg=U.concrete(seed,pal["tint"])
    for (w,h,col,dots,x,y,r) in cfg["posters"]: U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
    U.paste(bg,U.spray_blob((1200,820),pal["blob"],seed+7),540,740,-4)
    sgn=1 if side=="right" else -1; ls=[]
    yr=U.spray_text(cfg["year"],330,(255,255,255),seed=seed); im,x,y=prep(yr,540,270,-4); ls.append(L7(im,x,y,0.0,0.3,"slide",(0,-600)))
    ml=U.marker_line(560,pal["acc"],thick=14,seed=seed,wob=9); im,x,y=prep(ml,520,425,-3); ls.append(L7(im,x,y,0.3,0.25,"wipe"))
    car=A.car_sprite(cfg,cfg["carw"]); im,x,y=prep(car,540,cfg["cy"],cfg.get("rot",-3)); ls.append(L7(im,x,y,0.05,0.4,"slide",(1500*sgn,0),idle=(7,3,0.8)))
    hz=U.hazard(1300,92,pal["hz1"],(20,20,20)); im,x,y=prep(U.hard_shadow(hz,(6,8)),540,1040,-5); ls.append(L7(im,x,y,0.45,0.3,"slide",(-1500,0)))
    lab=U.label(cfg["strip"],64,(255,255,255),(15,15,15)); im,x,y=prep(U.hard_shadow(lab,(8,10)),360,1040,-5); ls.append(L7(im,x,y,0.55,0.3,"slide",(-1500,0)))
    w1=U.fit(U.spray_text(cfg["w1"],110,pal["acc"],seed=seed+3,drips=True),700); im,x,y=prep(w1,400,1150,3); ls.append(L7(im,x,y,0.8,0.3,"slide",(-1200,0)))
    w2=U.fit(U.marker_text(cfg["w2"],86,(255,255,255),seed=seed+5),760); im,x,y=prep(U.hard_shadow(w2,(5,6),200),620,1245,-5); ls.append(L7(im,x,y,1.0,0.3,"slide",(1200,0)))
    d1=U.hard_shadow(U.stat_disc(*cfg["s1"],98,pal["d1"],(15,15,15))); im,x,y=prep(d1,225,1385,-8); ls.append(L7(im,x,y,1.25,0.35,"pop"))
    d2=U.hard_shadow(U.stat_disc(*cfg["s2"],98,pal["d2"],(255,255,255))); im,x,y=prep(d2,840,1375,8); ls.append(L7(im,x,y,1.45,0.35,"pop"))
    ls.append(caption7(cfg["c1"],cfg["c2"],1.75,1555)); return bg,ls
def trio7(cfgs,kind):
    seed=77; P.rnd=random.Random(seed); bg=U.concrete(seed,(20,10,10))
    for (w,h,col,dots,x,y,r) in [(480,640,(238,196,120),(190,90,40),80,420,-8),(520,460,(255,120,190),(120,40,160),1010,640,7),(560,420,(40,100,255),(20,30,110),980,1150,-6),(420,540,(0,205,190),(10,80,70),70,1200,6)]:
        U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
    for (c,x,y) in ((cfgs[0],360,760),(cfgs[1],720,1020),(cfgs[2],360,1290)): U.paste(bg,U.spray_blob((900,520),c["pal"]["blob"],c["seed"]+3),x,y,0)
    ls=[]; dy=-40 if kind=="cta" else 0
    cars=[(cfgs[0],370,740+dy,-4,-1),(cfgs[1],715,1000+dy,3,1),(cfgs[2],365,1255+dy,-3,-1)]
    if kind=="hook":
        t1=U.spray_text("یه ماشین.",190,(255,255,255),seed=5); im,x,y=prep(t1,540,230,-4); ls.append(L7(im,x,y,0,0.4,"settle"))
        t2=U.spray_text("سه دوره.",150,(255,214,40),seed=6); im,x,y=prep(t2,560,430,-3); ls.append(L7(im,x,y,0,0.4,"settle"))
        pk=U.hard_shadow(U.label("فقط یکیش اصلیه؟",44,(15,15,15),(255,214,40))); im,x,y=prep(pk,800,585,5); ls.append(L7(im,x,y,0,0.4,"settle"))
        capt=caption7("One car. Three eras.","Pick yours: 1, 2 or 3!",0.0,1555)
    else:
        t1=U.spray_text("کدومش",140,(255,255,255),seed=8); im,x,y=prep(t1,540,215,-4); ls.append(L7(im,x,y,0,0.3,"slide",(0,-600)))
        t2=U.spray_text("بیتلِ واقعیه؟",100,(255,214,40),seed=9); im,x,y=prep(t2,550,400,-3); ls.append(L7(im,x,y,0.15,0.3,"slide",(-1300,0)))
        capt=caption7("Which era is your Beetle?","Comment 1, 2 or 3 below!",0.9,1555)
    tg=[]
    for i,(c,cx,cy,rot,sg) in enumerate(cars):
        sp=A.car_sprite(c,c['trw']); im,x,y=prep(sp,cx,cy,rot)
        if kind=="hook": ls.append(L7(im,x,y,0,0.4,"settle",idle=(6,3,0.7+i*0.15)))
        else: ls.append(L7(im,x,y,0.3+0.2*i,0.35,"slide",(1500*sg*-1,0),idle=(6,3,0.7+i*0.15)))
        tx,ty=[(205,905),(925,1150),(670,1415)][i]; ty+=dy
        t_=U.hard_shadow(U.label(f"{c['year']}",52,(255,255,255),(15,15,15))); im,x,y=prep(t_,tx,ty,-6*sg)
        tg.append(L7(im,x,y,0 if kind=="hook" else 0.5+0.2*i,0.3,"settle" if kind=="hook" else "pop"))
    ls+=tg
    if kind=="cta":
        em=Image.open("/home/claude/vid/assets/emblem.png").convert("RGBA").resize((150,150),Image.LANCZOS); em=U.hard_shadow(P.sticker(em,10))
        im,x,y=prep(em,880,1285,0); ls.append(L7(im,x,y,0.8,0.35,"pop"))
        wm=U.label("CarEra",58,(255,255,255),(15,15,15)); im,x,y=prep(U.hard_shadow(wm),880,1395,4); ls.append(L7(im,x,y,0.9,0.35,"pop"))
    ls.append(capt); return bg,ls
import copy, beetlecfg
C=beetlecfg.make()
for c,d in zip(C,[dict(year="۱۹۵۰",strip="دههٔ پنجاه",w1="هواخنک",w2="موتورِ عقب",s1=("۲۵","اسب بخار"),s2=("۱٫۱","لیتر")),
                  dict(year="۱۹۹۹",strip="دههٔ نود",w1="رترو برگشت",w2="گلدون روی داشبورد",s1=("پایه","گلف"),s2=("موتور","جلو")),
                  dict(year="۲۰۱۲",strip="آخرین نسل",w1="آخرین نسخه",w2="ساخت مکزیک",s1=("۲۰۱۹","پایان"),s2=("پوئبلا","مکزیک"))]): c.update(d)
def build(name):
    if name=="hook": return trio7(C,"hook")+(4,"90",1)
    if name=="cta": return trio7(C,"cta")+(4,"24",2)
    i={"e74":0,"e97":1,"e24":2}[name]; return era7(C[i],["left","right","left"][i])+(4,["70","90","24"][i],10+i)
if __name__=="__main__":
    import os
    A.OUT="/home/claude/vid/fa/out/"; os.makedirs(A.OUT+"scenes",exist_ok=True); os.makedirs(A.OUT+"prev",exist_ok=True)
    mode=sys.argv[1]; names=sys.argv[2:] or ["hook","e74","e97","e24","cta"]
    for n in names:
        bg,ls,d,st,sd=build(n)
        if mode=="preview": A.render_scene(n,bg,ls,d,st,sd,preview={0,6,15,30,60,100})
        else: A.render_scene(n,bg,ls,d,st,sd); print("done",n,flush=True)
