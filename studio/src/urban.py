import sys; sys.path.insert(0,"/home/claude/vid/src")
import math, random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import panels as P
FD=P.FD; W,H=1080,1920
PH="/home/claude/vid/photos/"; O="/home/claude/vid/mock/"
MONO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def F(name,size): return ImageFont.truetype(FD+name,size)

def noise(w,h,scale,seed,amp):
    r=np.random.default_rng(seed)
    n=r.normal(0,1,(max(2,h//scale),max(2,w//scale))).astype(np.float32)
    return np.asarray(Image.fromarray(n).resize((w,h),Image.BICUBIC))*amp

def concrete(seed, tint):
    r=np.random.default_rng(seed)
    base=np.zeros((H,W,3),np.float32)+np.array([146,144,140],np.float32)
    base+=(noise(W,H,180,seed,14)+noise(W,H,40,seed+1,7)+noise(W,H,4,seed+2,5))[...,None]
    base+=np.array(tint,np.float32)*0.25
    for _ in range(14):  # stains
        x,y,rr=r.integers(0,W),r.integers(0,H),r.integers(80,260)
        yy,xx=np.ogrid[:H,:W]; m=np.exp(-(((xx-x)**2+(yy-y)**2)/(2*(rr/2)**2)))
        base-=(m*r.uniform(8,22))[...,None]
    # horizontal panel seams
    for y in (470,1130,1730): base[y:y+3]-=26; base[y+3:y+5]+=14
    return Image.fromarray(np.clip(base,0,255).astype(np.uint8)).convert("RGBA")

def halftone(w,h,col,cell=16,seed=0):
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    a=math.radians(30); u=(xx*math.cos(a)+yy*math.sin(a))/cell; v=(-xx*math.sin(a)+yy*math.cos(a))/cell
    d=np.sqrt((u-np.round(u))**2+(v-np.round(v))**2)
    size=np.clip(0.1+0.4*(yy/h),0,0.5)
    m=(d<size)
    out=np.zeros((h,w,4),np.uint8); out[m]=list(col)+[255]
    return Image.fromarray(out)

def poster(w,h,col,dots,cell=16):
    base=Image.new("RGBA",(w,h),col+(255,))
    ht=halftone(w,h,dots,cell); base.alpha_composite(ht)
    return P.torn(w,h,base.convert("RGB"),amp=7)

def spray_blob(size,col,seed):
    r=np.random.default_rng(seed)
    w,h=size; m=np.zeros((h,w),np.float32)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    for _ in range(9):
        cx=w/2+r.normal(0,w*0.18); cy=h/2+r.normal(0,h*0.14); rr=r.uniform(0.22,0.4)*min(w,h)
        m=np.maximum(m,np.exp(-(((xx-cx)**2+(yy-cy)**2)/(2*(rr*0.6)**2))))
    soft=np.clip((m-0.35)*3.0,0,1)
    speck=(r.random((h,w))<(m**2*0.18)).astype(np.float32)  # overspray dots
    speck=np.asarray(Image.fromarray((speck*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)))/255.
    a=np.clip(soft+speck*0.8,0,1)*0.95
    img=np.zeros((h,w,4),np.uint8); img[...,:3]=col; img[...,3]=(a*255).astype(np.uint8)
    im=Image.fromarray(img)
    # drips
    d=ImageDraw.Draw(im)
    for _ in range(6):
        x=int(r.uniform(w*0.25,w*0.75)); ys=np.where(a[:,x]>0.5)[0]
        if len(ys)==0: continue
        y0=ys.max(); L=int(r.uniform(40,130)); wd=int(r.uniform(5,9))
        d.rectangle([x-wd//2,y0-4,x+wd//2,y0+L],fill=tuple(col)+(240,)); d.ellipse([x-wd,y0+L-wd,x+wd,y0+L+wd],fill=tuple(col)+(240,))
    return im

def text_mask(txt,font,pad=40):
    d0=ImageDraw.Draw(Image.new("L",(8,8))); bb=d0.textbbox((0,0),txt,font=font)
    w,h=bb[2]-bb[0]+2*pad,bb[3]-bb[1]+2*pad
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).text((pad-bb[0],pad-bb[1]),txt,font=font,fill=255); return m

def spray_text(txt,size,col,outline=(15,15,15),seed=1,drips=True,italic=True):
    f=F("Inter-BlackItalic.otf" if italic else "Inter-Black.otf",size); m=text_mask(txt,f,50)
    w,h=m.size; r=np.random.default_rng(seed)
    # rough edge
    arr=np.asarray(m).astype(np.float32)/255
    arr=np.asarray(Image.fromarray((arr*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)))/255.+noise(w,h,3,seed,0.10)
    core=(arr>0.5).astype(np.float32)
    halo=np.asarray(m.filter(ImageFilter.GaussianBlur(size*0.07))).astype(np.float32)/255
    speck=((r.random((h,w))<halo*0.22)*(1-core)).astype(np.float32)
    out=np.zeros((h,w,4),np.float32)
    # dark outline/shadow: offset blob
    sh=np.asarray(Image.fromarray((core*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(11)).transform((w,h),Image.AFFINE,(1,0,-8,0,1,-10)))/255.
    out[...,:3]=outline; out[...,3]=np.maximum(sh,0)*255
    c=np.zeros((h,w,4),np.float32); c[...,:3]=col; c[...,3]=np.maximum(core,speck*0.9)*255
    res=Image.fromarray(out.astype(np.uint8)); res.alpha_composite(Image.fromarray(c.astype(np.uint8)))
    if drips:
        d=ImageDraw.Draw(res)
        ys,xs=np.where(core>0.5)
        for _ in range(4):
            i=r.integers(0,len(xs)); x=xs[i]; col_ys=np.where(core[:,x]>0.5)[0]; y0=col_ys.max()
            L=int(r.uniform(30,95)); wd=max(4,size//28)
            d.rectangle([x-wd//2,y0-3,x+wd//2,y0+L],fill=tuple(col)+(255,)); d.ellipse([x-wd*0.8,y0+L-wd*0.8,x+wd*0.8,y0+L+wd*0.8],fill=tuple(col)+(255,))
    return res

def fit(im,maxw):
    return im if im.width<=maxw else im.resize((maxw,int(im.height*maxw/im.width)),Image.LANCZOS)

def marker_text(txt,size,col,seed=2,italic=True,bold="ExtraBold"):
    f=F(f"Inter-{bold}{'Italic' if italic else ''}.otf",size); m=text_mask(txt,f,20); w,h=m.size
    arr=np.asarray(m).astype(np.float32)/255
    dx=noise(w,h,22,seed,3.0); dy=noise(w,h,22,seed+9,3.0)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    xi=np.clip(xx+dx,0,w-1).astype(int); yi=np.clip(yy+dy,0,h-1).astype(int)
    a=arr[yi,xi]; a=(a>0.5).astype(np.float32)
    out=np.zeros((h,w,4),np.uint8); out[...,:3]=col; out[...,3]=(np.clip(a,0,1)*255).astype(np.uint8)
    return Image.fromarray(out)

def marker_line(w,col,thick=10,seed=3,wob=7,pts=24):
    r=random.Random(seed); im=Image.new("RGBA",(w+40,thick*3+wob*2+20),(0,0,0,0)); d=ImageDraw.Draw(im)
    pp=[(20+i*w/pts,im.height/2+r.uniform(-wob,wob)) for i in range(pts+1)]
    d.line(pp,fill=col+(255,),width=thick,joint="curve")
    for p in pp: d.ellipse([p[0]-thick/2,p[1]-thick/2,p[0]+thick/2,p[1]+thick/2],fill=col+(255,))
    return im

def arrow(col,seed=4,L=260,thick=10):
    r=random.Random(seed); im=Image.new("RGBA",(L+60,170),(0,0,0,0)); d=ImageDraw.Draw(im)
    pp=[(20+t*L,110-80*math.sin(t*math.pi*0.9)+r.uniform(-3,3)) for t in [i/20 for i in range(21)]]
    d.line(pp,fill=col+(255,),width=thick,joint="curve")
    x,y=pp[-1]; d.line([x,y,x-34,y-16],fill=col+(255,),width=thick); d.line([x,y,x-12,y+34],fill=col+(255,),width=thick)
    return im

def scribble_circle(R,col,seed=5,thick=9):
    r=random.Random(seed); im=Image.new("RGBA",(2*R+60,2*R+60),(0,0,0,0)); d=ImageDraw.Draw(im)
    pts=[]
    for i in range(0,430,6):
        a=math.radians(i-10); rr=R*(1+0.05*math.sin(i/40))+r.uniform(-4,4)+i*0.03
        pts.append((R+30+rr*math.cos(a),R+30+rr*math.sin(a)*0.9))
    d.line(pts,fill=col+(255,),width=thick,joint="curve"); return im

def label(txt,size,fg,bg,font="Inter-Black.otf",padx=26,pady=12,mono=False):
    f=ImageFont.truetype(MONO,size) if mono else F(font,size)
    d0=ImageDraw.Draw(Image.new("L",(8,8))); bb=d0.textbbox((0,0),txt,font=f)
    w,h=bb[2]-bb[0]+2*padx,bb[3]-bb[1]+2*pady
    im=Image.new("RGBA",(w,h),bg+(255,)); ImageDraw.Draw(im).text((padx-bb[0],pady-bb[1]),txt,font=f,fill=fg); return im

def hazard(w,h,c1,c2):
    im=Image.new("RGBA",(w,h),c1+(255,)); d=ImageDraw.Draw(im)
    for x in range(-h,w+h,64): d.polygon([(x,h),(x+32,h),(x+32+h,0),(x+h,0)],fill=c2+(255,))
    return im

def stat_disc(txt1,txt2,R,fill,fg):
    im=Image.new("RGBA",(2*R+30,2*R+30),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([15,15,2*R+15,2*R+15],fill=(15,15,15,255)); d.ellipse([15+8,15+8,2*R+7,2*R+7],fill=fill+(255,))
    f1=F("Inter-Black.otf",int(R*0.52)); f2=F("Inter-ExtraBold.otf",int(R*0.26))
    d.text((R+15,R+15-R*0.12),txt1,font=f1,fill=fg,anchor="mm"); d.text((R+15,R+15+R*0.36),txt2,font=f2,fill=fg,anchor="mm"); return im

def recolor(car,hue,silver=False,vscale=1.0,sscale=1.0,tint=(1,1,1),rim=(0,0,0)):
    a=np.asarray(car.convert("RGBA")).astype(np.float32)
    hsv=np.asarray(Image.fromarray(a[...,:3].astype(np.uint8)).convert("HSV")).astype(np.float32)
    Hh,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
    if silver:
        w=np.clip((V-100)/40,0,1)*np.clip((34-S)/16,0,1)
        S2=S*(1-w)+np.clip(150+V*0.25,0,255)*w*sscale
    else:
        dh=np.minimum(Hh,255-Hh); w=np.clip(1-(dh-14)/24,0,1)*np.clip((S-22)/45,0,1)
        S2=S*(1-w)+np.clip(S*0.95*sscale,0,255)*w
    H2=Hh*(1-w)+hue*w; V2=V*(1-w)+np.clip(V*vscale,0,255)*w
    rgb=np.asarray(Image.fromarray(np.stack([H2,S2,V2],-1).astype(np.uint8),"HSV").convert("RGB")).astype(np.float32)
    lum=rgb.mean(-1,keepdims=True); spec=np.clip((lum-205)/45,0,1)
    rgb=rgb*(1-0.4*spec)+255*0.4*spec
    yy,xx=np.mgrid[0:car.height,0:car.width].astype(np.float32); g=(xx/car.width)[...,None]
    rgb=rgb*(np.array(tint)*(0.88+0.24*g))+np.array(rim)*(g**2)
    return Image.fromarray(np.dstack([np.clip(rgb,0,255),a[...,3]]).astype(np.uint8),"RGBA")

def hard_shadow(img,off=(14,16),alpha=235):
    a=img.getchannel("A").point(lambda v:alpha if v>20 else 0)
    sh=Image.new("RGBA",img.size,(10,10,10,0)); sh.putalpha(a)
    out=Image.new("RGBA",(img.width+60,img.height+60),(0,0,0,0)); out.alpha_composite(sh,(30+off[0],30+off[1])); out.alpha_composite(img,(30,30)); return out

def paste(base,img,cx,cy,rot=0):
    im=img.rotate(rot,resample=Image.BICUBIC,expand=True); base.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))

def build(cfg):
    P.rnd=random.Random(cfg["seed"]); seed=cfg["seed"]
    pal=cfg["pal"]
    bg=concrete(seed,pal["tint"])
    # poster scraps at edges (back layer)
    for (w,h,col,dots,x,y,r) in cfg["posters"]:
        p=poster(w,h,col,dots); paste(bg,hard_shadow(p,(8,10,),160),x,y,r)
    # big spray splash behind the car
    blob=spray_blob((1200,820),pal["blob"],seed+7); paste(bg,blob,540,740,-4)
    # car
    car=Image.open(cfg["car"]).convert("RGBA")
    if cfg.get("plate"): P.patch(car,cfg["plate"])
    car=car.crop(car.getbbox()); cw=cfg["carw"]; car=car.resize((cw,int(cw*car.height/car.width)),Image.LANCZOS)
    if cfg.get("wisp"):
        arr=np.array(car); hs=np.asarray(Image.fromarray(arr[...,:3]).convert("HSV")); box=np.zeros(arr.shape[:2],bool); box[:int(arr.shape[0]*0.115),:int(arr.shape[1]*0.24)]=True
        arr[...,3]=np.where(box&(hs[...,1]<110),0,arr[...,3]); car=Image.fromarray(arr)
    car=recolor(car,**cfg["rc"])
    spr=P.sticker(car,14); spr=hard_shadow(spr)
    paste(bg,spr,540+cfg.get("dx",0),cfg.get("cy",760),cfg.get("rot",-3))
    # year (spray) top
    yr=spray_text(cfg["year"],330,(255,255,255),seed=seed,drips=True); paste(bg,yr,540,270,-4)
    # accent spray over year edge
    paste(bg,marker_line(560,pal["acc"],thick=14,seed=seed,wob=9),520,425,-3)
    # era strip (hazard + black label sliding)
    hz=hazard(1300,92,pal["hz1"],(20,20,20)); paste(bg,hard_shadow(hz,(6,8)),540,1080,-5)
    lab=label(cfg["strip"],64,(255,255,255),(15,15,15)); paste(bg,hard_shadow(lab,(8,10)),360,1080,-5)
    # urban words
    w1=fit(spray_text(cfg["w1"],110,pal["acc"],seed=seed+3,drips=True),700); paste(bg,w1,400,1235,3)
    w2=fit(marker_text(cfg["w2"],86,(255,255,255),seed=seed+5),760); paste(bg,hard_shadow(w2,(5,6),200),620,1345,-5)
    paste(bg,arrow((255,255,255),seed=seed,L=240),860,1060,-14)
    # stat discs
    paste(bg,hard_shadow(stat_disc(*cfg["s1"],118,pal["d1"],(15,15,15))),230,1520,-8)
    paste(bg,hard_shadow(stat_disc(*cfg["s2"],118,pal["d2"],(255,255,255))),830,1500,8)
    # caption clipping
    cap=Image.new("RGBA",(920,170),(250,248,240,255)); cd=ImageDraw.Draw(cap)
    cd.text((460,64),cfg["c1"],font=ImageFont.truetype(MONO,30),fill=(25,25,25),anchor="mm"); cd.text((460,114),cfg["c2"],font=ImageFont.truetype(MONO,25),fill=(25,25,25),anchor="mm")
    cap=P.torn(920,170,cap.convert("RGB"),edge=(240,236,224),amp=6); paste(bg,hard_shadow(cap,(8,10),170),540,1715,-1.2)
    paste(bg,P.tape(),120,1640,-30); paste(bg,P.tape(),960,1790,32)
    # grain + vignette
    a=np.asarray(bg.convert("RGB")).astype(np.float32)
    a+=np.random.default_rng(seed).normal(0,cfg.get("grain",5),(H,W))[...,None]
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); dd=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/1.42
    a*=(1-0.32*dd**2)[...,None]
    Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(cfg["out"])

CFG=[
 dict(seed=11,year="1974",car=PH+"golf_mk1_np2.png",carw=980,cy=800,rot=-3,out=O+"urban_1974.png",
  rc=dict(hue=124,vscale=1.05,sscale=1.0,tint=(1.06,1.0,0.9),rim=(34,16,-6)),
  pal=dict(tint=(40,20,0),blob=(255,128,30),acc=(255,214,40),hz1=(255,200,0),d1=(255,214,40),d2=(220,60,40)),
  posters=[(460,600,(238,196,120),(190,90,40),90,330,-8),(520,420,(196,70,40),(255,170,120),1010,520,7),(560,380,(120,70,50),(220,150,90),980,1000,-6),(420,520,(240,220,170),(200,120,60),70,1010,6)],
  strip="THE SEVENTIES",w1="BELL-BOTTOMS",w2="cassette tapes",s1=("≈ 50","HP"),s2=("< 800","KG"),
  c1="1974. Bell-bottoms, cassette tapes.",c2="A boxy, light Golf with just fifty horsepower.",circle=True),
 dict(seed=21,year="1997",car=PH+"golf_mk4_np.png",carw=1000,cy=805,rot=-2,out=O+"urban_1997.png",
  rc=dict(hue=232,vscale=1.1,sscale=1.0,tint=(1.0,0.98,1.06),rim=(10,0,30)),
  pal=dict(tint=(10,0,30),blob=(0,205,190),acc=(255,226,60),hz1=(255,90,170),d1=(255,226,60),d2=(130,60,220)),
  posters=[(470,590,(110,50,170),(255,120,200),85,340,7),(520,420,(255,120,190),(120,40,160),1000,540,-8),(560,380,(40,190,200),(20,70,110),990,1010,6),(420,520,(250,230,90),(230,110,40),70,1020,-7)],
  strip="THE NINETIES",w1="CD • TAMAGOTCHI",w2="airbags & turbo diesel",s1=("AIR","BAGS"),s2=("TURBO","DIESEL"),
  c1="1997. CDs and Tamagotchis.",c2="Now premium: airbags, galvanized body, turbo diesels.",circle=True),
 dict(seed=31,year="2024",car=PH+"golf_mk8_np.png",carw=1010,cy=815,rot=-2,out=O+"urban_2024.png",
  grain=3,
  rc=dict(hue=44,silver=True,vscale=1.15,sscale=1.0,tint=(1.0,1.02,0.98),rim=(10,16,30)),
  pal=dict(tint=(0,10,40),blob=(40,100,255),acc=(0,235,170),hz1=(0,235,170),d1=(255,255,255),d2=(40,100,255)),
  posters=[(470,590,(30,40,90),(80,140,255),85,340,-7),(520,420,(235,240,250),(90,120,200),1000,540,8),(560,380,(20,20,24),(0,235,170),990,1010,-6),(420,520,(0,235,170),(10,80,70),70,1020,7)],
  strip="TODAY",w1="MILD-HYBRID",w2="digital cockpit",s1=("MILD","HYBRID"),s2=("DIGI","COCKPIT"),
  c1="Today: digital cockpit, mild-hybrid power,",c2="and it can help steer on the highway.",circle=True),
]
if __name__=="__main__":
    import sys
    for c in CFG: build(c)
    ims=[Image.open(c["out"]).resize((540,960)) for c in CFG]
    s=Image.new("RGB",(1620,960)); [s.paste(im,(i*540,0)) for i,im in enumerate(ims)]; s.save(O+"urban_overview.png"); print("ok")
