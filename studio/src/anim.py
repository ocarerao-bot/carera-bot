import sys; sys.path.insert(0,"/home/claude/vid/src")
import math, random, subprocess, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import urban as U, panels as P
W,H,FPS=1080,1920,30
POSE=1   # new drawing every 2 frames => 15 fps stop-motion
OUT="/home/claude/vid/urban/"
MONO=U.MONO
def ease_out_back(t,s=1.55):
    t=min(1,max(0,t)); c=t-1; return 1+c*c*((s+1)*c+s)
def ease_out(t): t=min(1,max(0,t)); return 1-(1-t)**3

def prep(img,cx,cy,rot=0):
    im=img.rotate(rot,resample=Image.BICUBIC,expand=True) if rot else img
    return im,cx-im.width/2,cy-im.height/2

def put(base,im,x,y):
    x,y=int(round(x)),int(round(y)); w,h=im.size
    x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+w),min(H,y+h)
    if x1<=x0 or y1<=y0: return
    base.alpha_composite(im.crop((x0-x,y0-y,x1-x,y1-y)),(x0,y0))

def car_sprite(cfg,cw):
    car=Image.open(cfg["car"]).convert("RGBA"); car=car.crop(car.getbbox()); car=car.resize((cw,int(cw*car.height/car.width)),Image.LANCZOS)
    if cfg.get("wisp"):
        arr=np.array(car); hs=np.asarray(Image.fromarray(arr[...,:3]).convert("HSV")); box=np.zeros(arr.shape[:2],bool); box[:int(arr.shape[0]*0.115),:int(arr.shape[1]*0.24)]=True
        arr[...,3]=np.where(box&(hs[...,1]<110),0,arr[...,3]); car=Image.fromarray(arr)
    car=U.recolor(car,**cfg["rc"]); return U.hard_shadow(P.sticker(car,14))

class L:
    def __init__(s,img,x,y,t0,dur=0.5,kind="slide",frm=(0,0),idle=None):
        s.img,s.x,s.y,s.t0,s.dur,s.kind,s.frm,s.idle=img,x,y,t0,dur,kind,frm,idle
    def draw(s,base,t,rng):
        if t<s.t0: return
        u=(t-s.t0)/s.dur; x,y=s.x,s.y; im=s.img
        if s.kind=="slide":
            e=ease_out_back(u,1.2); x+=s.frm[0]*(1-e); y+=s.frm[1]*(1-e)
        elif s.kind=="pop":
            e=ease_out_back(u,2.0); sc=max(0.05,e)
            if sc<0.999 or u<1:
                w,h=im.size; nw,nh=max(2,int(w*sc)),max(2,int(h*sc)); im=im.resize((nw,nh),Image.BILINEAR); x+=(w-nw)/2; y+=(h-nh)/2
        elif s.kind=="wipe":
            e=ease_out(u); w,h=im.size; cw=max(2,int(w*e)); im=im.crop((0,0,cw,h))
        if s.idle: x+=s.idle[0]*math.sin((t-s.t0)*s.idle[2]); y+=s.idle[1]*math.sin((t-s.t0)*s.idle[2]+1)
        if u>=1 and not s.idle:
            j=random.Random(int((t-s.t0)*6)*977+int(s.x)%89); x+=j.uniform(-1.2,1.2); y+=j.uniform(-1.2,1.2)
        put(base,im,x,y)

def vignette():
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); dd=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/1.42
    return (1-0.32*dd**2)[...,None]
VIG=vignette()

def era_scene(cfg,side):
    seed=cfg["seed"]; pal=cfg["pal"]; P.rnd=random.Random(seed)
    bg=U.concrete(seed,pal["tint"])
    for (w,h,col,dots,x,y,r) in cfg["posters"]:
        p=U.poster(w,h,col,dots); U.paste(bg,U.hard_shadow(p,(8,10),160),x,y,r)
    U.paste(bg,U.spray_blob((1200,820),pal["blob"],seed+7),540,740,-4)
    sgn=1 if side=="right" else -1
    ls=[]
    yr=U.spray_text(cfg["year"],330,(255,255,255),seed=seed); im,x,y=prep(yr,540,270,-4); ls.append(L(im,x,y,0.15,0.5,"slide",(0,-800)))
    ml=U.marker_line(560,pal["acc"],thick=14,seed=seed,wob=9); im,x,y=prep(ml,520,425,-3); ls.append(L(im,x,y,0.75,0.4,"wipe"))
    car=car_sprite(cfg,cfg["carw"]); im,x,y=prep(car,540,cfg["cy"]-0,cfg.get("rot",-3)); ls.append(L(im,x,y,0.35,0.6,"slide",(1500*sgn,0),idle=(7,3,0.8)))
    hz=U.hazard(1300,92,pal["hz1"],(20,20,20)); im,x,y=prep(U.hard_shadow(hz,(6,8)),540,1075,-5); ls.append(L(im,x,y,1.15,0.5,"slide",(-1500,0)))
    lab=U.label(cfg["strip"],64,(255,255,255),(15,15,15)); im,x,y=prep(U.hard_shadow(lab,(8,10)),360,1075,-5); ls.append(L(im,x,y,1.35,0.5,"slide",(-1500,0)))
    ar=U.arrow((255,255,255),seed=seed,L=240); im,x,y=prep(ar,860,1040,-14); ls.append(L(im,x,y,1.7,0.5,"wipe"))
    w1=U.fit(U.spray_text(cfg["w1"],110,pal["acc"],seed=seed+3,drips=True),700); im,x,y=prep(w1,400,1190,3); ls.append(L(im,x,y,1.8,0.5,"slide",(-1200,0)))
    w2=U.fit(U.marker_text(cfg["w2"],86,(255,255,255),seed=seed+5),760); im,x,y=prep(U.hard_shadow(w2,(5,6),200),620,1295,-5); ls.append(L(im,x,y,2.1,0.5,"slide",(1200,0)))
    d1=U.hard_shadow(U.stat_disc(*cfg["s1"],108,pal["d1"],(15,15,15))); im,x,y=prep(d1,235,1455,-8); ls.append(L(im,x,y,2.6,0.5,"pop"))
    d2=U.hard_shadow(U.stat_disc(*cfg["s2"],108,pal["d2"],(255,255,255))); im,x,y=prep(d2,830,1440,8); ls.append(L(im,x,y,2.9,0.5,"pop"))
    ls.append(caption(cfg["c1"],cfg["c2"],3.4,1625))
    return bg,ls

def caption(c1,c2,t0,cy):
    cap=Image.new("RGB",(920,170),(250,248,240)); cd=ImageDraw.Draw(cap)
    cd.text((460,64),c1,font=ImageFont.truetype(MONO,30 if len(c1)<48 else 26),fill=(25,25,25),anchor="mm"); cd.text((460,114),c2,font=ImageFont.truetype(MONO,25 if len(c2)<52 else 22),fill=(25,25,25),anchor="mm")
    cap=P.torn(920,170,cap,edge=(240,236,224),amp=6); cap=U.hard_shadow(cap,(8,10),170)
    tp=Image.new("RGBA",(cap.width+120,cap.height+80),(0,0,0,0)); tp.alpha_composite(cap,(60,40)); tp.alpha_composite(P.tape().rotate(-30,expand=True),(0,10))
    im,x,y=prep(tp,540,cy,-1.2); return L(im,x,y,t0,0.5,"slide",(0,500))

def trio_scene(cfgs,kind):
    seed=77; P.rnd=random.Random(seed)
    bg=U.concrete(seed,(20,10,10))
    for (w,h,col,dots,x,y,r) in [(480,640,(238,196,120),(190,90,40),80,420,-8),(520,460,(255,120,190),(120,40,160),1010,640,7),(560,420,(40,100,255),(20,30,110),980,1150,-6),(420,540,(0,205,190),(10,80,70),70,1200,6)]:
        p=U.poster(w,h,col,dots); U.paste(bg,U.hard_shadow(p,(8,10),160),x,y,r)
    for (c,x,y) in ((cfgs[0],360,760),(cfgs[1],720,1020),(cfgs[2],360,1290)):
        U.paste(bg,U.spray_blob((900,520),c["pal"]["blob"],c["seed"]+3),x,y,0)
    ls=[]; dy=-45 if kind=="cta" else 0
    cars=[(cfgs[0],370,740+dy,-4,-1),(cfgs[1],715,1000+dy,3,1),(cfgs[2],365,1255+dy,-3,-1)]
    if kind=="hook":
        t1=U.spray_text("ONE CAR.",190,(255,255,255),seed=5); im,x,y=prep(t1,540,230,-4); ls.append(L(im,x,y,0.1,0.5,"slide",(0,-700)))
        t2=U.spray_text("THREE ERAS.",150,(255,214,40),seed=6); im,x,y=prep(t2,560,430,-3); ls.append(L(im,x,y,0.5,0.5,"slide",(1300,0)))
        times=[0.9,1.4,1.9]; capt=caption("This little hatchback saved Volkswagen.","Meet the Golf, in three eras.",2.3,1640)
    else:
        t1=U.spray_text("WHICH ERA",170,(255,255,255),seed=8); im,x,y=prep(t1,540,215,-4); ls.append(L(im,x,y,0.1,0.5,"slide",(0,-700)))
        t2=U.spray_text("IS YOUR GOLF?",125,(255,214,40),seed=9); im,x,y=prep(t2,550,400,-3); ls.append(L(im,x,y,0.4,0.5,"slide",(-1300,0)))
        times=[0.7,1.0,1.3]; capt=caption("Over thirty-five million built.","Which era is your Golf? Comment below!",2.2,1640)
    tags=[]
    for i,(c,cx,cy,rot,sg) in enumerate(cars):
        sp=car_sprite(c,720); im,x,y=prep(sp,cx,cy,rot); ls.append(L(im,x,y,times[i],0.55,"slide",(1500*sg*-1,0),idle=(6,3,0.7+i*0.15)))
        tx,ty=[(205,905),(925,1150),(670,1415)][i]; ty+=(-45 if kind=="cta" else 0)
        tg=U.hard_shadow(U.label(c["year"],54,(255,255,255),(15,15,15))); im,x,y=prep(tg,tx,ty,-6*sg); tags.append(L(im,x,y,times[i]+0.25,0.4,"pop"))
    ls+=tags
    if kind=="cta":
        em=Image.open("/home/claude/vid/assets/emblem.png").convert("RGBA").resize((150,150),Image.LANCZOS); em=U.hard_shadow(P.sticker(em,10))
        im,x,y=prep(em,400,1490,0); ls.append(L(im,x,y,1.9,0.5,"pop"))
        wm=U.label("CarEra",58,(255,255,255),(15,15,15)); im,x,y=prep(U.hard_shadow(wm),690,1490,4); ls.append(L(im,x,y,2.0,0.5,"pop"))
    ls.append(capt); return bg,ls

def render_scene(name,bg,ls,dur,style,seed,preview=None):
    rng_seed=seed; n=int(dur*FPS); frames=[]
    cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","medium","-crf","24","-pix_fmt","yuv420p","-movflags","+faststart",OUT+"scenes/tmp_"+name+".mp4"]
    pr=None if preview else subprocess.Popen(cmd,stdin=subprocess.PIPE)
    last=None
    for f in range(n):
        if preview is not None and f not in preview: continue
        if f%POSE==0 or last is None:
            t=f/FPS; rng=random.Random(rng_seed*1000+f)
            base=bg.copy()
            for l in ls: l.draw(base,t,rng)
            a=np.asarray(base.convert("RGB")).astype(np.float32)*VIG
            a+=np.random.default_rng(rng_seed*7+f).normal(0,3.5 if style!="24" else 1.6,(H,W))[...,None]
            if style=="90":
                sh=int(random.Random(f//5).choice([-2,0,2])); a[...,0]=np.roll(a[...,0],sh,axis=1); a[...,2]=np.roll(a[...,2],-sh,axis=1)
                if random.Random(f//3).random()<0.04: y0=rng.randrange(200,1700); a[y0:y0+40]=np.roll(a[y0:y0+40],rng.randrange(-14,14),axis=1)
            if style=="70": a=a*np.array([1.03,1.0,0.94])
            pass
            last=np.clip(a,0,255).astype(np.uint8)
        if preview is not None: Image.fromarray(last).save(OUT+f"prev/{name}_{f:03d}.png")
        else: pr.stdin.write(last.tobytes())
    if pr:
        pr.stdin.close(); pr.wait(); os.rename(OUT+"scenes/tmp_"+name+".mp4",OUT+"scenes/"+name+".mp4")

SCENES=["hook","e74","e97","e24","cta"]; DURS={"hook":4,"e74":6,"e97":7,"e24":7,"cta":6}
def build_scene(name):
    C=U.CFG
    if name=="hook": return trio_scene(C,"hook")+(DURS[name],"90",1)
    if name=="cta": return trio_scene(C,"cta")+(DURS[name],"24",2)
    i={"e74":0,"e97":1,"e24":2}[name]; side=["left","right","left"][i]
    bg,ls=era_scene(C[i],side); return bg,ls,DURS[name],["70","90","24"][i],10+i
if __name__=="__main__":
    mode=sys.argv[1]; names=sys.argv[2:] or SCENES
    for n in names:
        bg,ls,d,st,sd=build_scene(n)
        if mode=="preview": render_scene(n,bg,ls,d,st,sd,preview={10,16,26,40,70,100,150})
        else: render_scene(n,bg,ls,d,st,sd); print("done",n,flush=True)
