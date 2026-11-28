import sys; sys.path.insert(0,"/home/claude/vid/src")
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import helpers as R
D="/home/claude/vid/p205/photos/"
def harden(im):
    a=np.asarray(im).copy(); al=a[...,3].astype(np.float32); a[...,3]=np.clip((al-60)*2.2,0,255).astype(np.uint8); return Image.fromarray(a)
def cut(im,polys):
    m=Image.new("L",im.size,0); d=ImageDraw.Draw(m); [d.polygon(p,fill=255) for p in polys]
    a=np.asarray(im).copy(); a[...,3][np.asarray(m)>0]=0; return Image.fromarray(a)
def tint(im,polys,col=(24,26,34),k=0.75):
    m=Image.new("L",im.size,0); d=ImageDraw.Draw(m); [d.polygon(p,fill=255) for p in polys]; m=m.filter(ImageFilter.GaussianBlur(3))
    bl=im.filter(ImageFilter.GaussianBlur(10)); bl=Image.blend(bl,Image.new("RGBA",im.size,col+(255,)),k); bl.putalpha(im.getchannel("A")); return Image.composite(bl,im,m)
def recolor(im,col,inc=None,exc=(),ell=(),vmin=55,gain=1.0,base=0.25,spec0=0.55):
    a=np.asarray(im).astype(np.float32); rgb=a[...,:3]; W,H=im.size
    hsv=np.asarray(im.convert("RGB").convert("HSV")).astype(np.float32); S,V=hsv[...,1],hsv[...,2]
    m=Image.new("L",im.size,0); d=ImageDraw.Draw(m)
    if inc: [d.polygon(p,fill=255) for p in inc]
    else: d.rectangle([0,0,W,H],fill=255)
    for e in exc: d.polygon(e,fill=0)
    for e in ell: d.ellipse(e,fill=0)
    m=np.asarray(m.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)/255
    w=m*np.clip((V-vmin)/30,0,1)*np.clip((150-S)/50,0,1)*(a[...,3]>0)
    L=V/255.0; c=np.array(col,np.float32)
    paint=c[None,None,:]*np.clip(base+1.5*L*gain,0,1.7)[...,None]
    spec=np.clip((L-spec0)/0.4,0,1)[...,None]; paint=paint*(1-spec)+np.maximum(rgb,paint)*spec
    out=rgb*(1-w[...,None])+paint*w[...,None]
    return Image.fromarray(np.dstack([np.clip(out,0,255),a[...,3]]).astype(np.uint8),"RGBA")
which=sys.argv[1:]
if "205red" in which:
    im=harden(Image.open(D+"205red_raw.png").convert("RGBA"))
    im=R.fill(im,[(1612,742),(1828,675),(1832,772),(1618,838)],(38,38,40),blur=2)
    im.save(D+"205_red.png")
if "205blue" in which:
    im=harden(Image.open(D+"205brown_raw.png").convert("RGBA"))
    im=cut(im,[[(250,0),(1330,0),(1300,92),(800,108),(700,128),(480,134),(340,150),(250,160)]])
    im=R.fill(im,[(1288,782),(1515,690),(1522,762),(1298,852)],(40,40,42),blur=2)
    GL=[[(205,400),(330,175),(470,165),(700,168),(728,470),(400,432)],[(805,140),(1290,112),(1530,350),(1000,470),(945,372)]]
    im=tint(im,GL)
    EXC=GL+[[(955,640),(1130,630),(1135,770),(960,770)],[(1595,455),(1645,450),(1650,565),(1600,570)],[(1530,655),(1600,640),(1600,700),(1530,715)],
            [(1195,800),(1285,780),(1290,860),(1200,870)],[(1130,642),(1615,547),(1625,640),(1135,745)],
            [(830,755),(960,768),(1130,745),(1650,575),(1662,640),(1520,700),(1295,860),(1000,848),(870,835)],[(1285,690),(1525,680),(1525,770),(1295,860)],
            [(140,345),(205,345),(205,420),(140,420)],[(1100,880),(1180,880),(1180,980),(1100,980)]]
    ELL=[(60,540,200,765),(655,712,972,1095)]
    im=recolor(im,(28,88,200),exc=EXC,ell=ELL,vmin=28,gain=1.05,base=0.15)
    im.save(D+"205_blue.png")
if "208blue" in which:
    im=harden(Image.open(D+"208blue_raw.png").convert("RGBA"))
    im=R.fill(im,[(1543,572),(1797,570),(1797,652),(1545,655)],(30,30,34),blur=2)
    GL=[[(225,210),(295,95),(520,55),(790,45),(1100,40),(1340,110),(1520,262),(1000,265),(880,290),(840,300),(640,300),(300,245)]]
    im=tint(im,GL,k=0.55)
    from lrcfg import recolor2
    im=recolor2(im,src=165,width=22,soft=12,hue=160,smin=15,sfloor=165,sscale=1.3,vscale=1.85)
    im.save(D+"208_blue.png")
if "208red" in which:
    im=harden(Image.open(D+"208silver_raw.png").convert("RGBA"))
    im=R.fill(im,[(1578,532),(1800,530),(1800,600),(1580,602)],(30,30,32),blur=2)
    GL=[[(232,212),(300,85),(560,45),(1120,35),(1400,115),(1545,248),(1020,255),(935,300),(640,296),(255,245)]]
    im=tint(im,GL,k=0.6)
    EXC=GL+[[(650,222),(812,228),(818,285),(670,292)],[(1098,322),(1200,368),(1300,410),(1445,478),(1300,472),(1200,447),(1128,392)],
            [(1805,365),(1842,390),(1868,472),(1810,468)],[(1450,485),(1840,490),(1848,640),(1812,668),(1540,668),(1500,600)],[(1290,645),(1350,645),(1350,700),(1290,700)],
            [(65,260),(105,270),(100,340),(70,350)]]
    ELL=[(60,490,272,782),(900,505,1135,860)]
    im=recolor(im,(168,18,30),exc=EXC,ell=ELL,vmin=45,gain=0.85,base=0.12,spec0=0.75)
    im.save(D+"208_red.png")
if "2082yel" in which:
    im=harden(Image.open(D+"2082yel_raw.png").convert("RGBA"))
    im=cut(im,[[(0,470),(70,470),(75,640),(0,640)]])
    im=R.fill(im,[(140,595),(395,622),(392,718),(140,697)],(30,30,30),blur=2)
    im.save(D+"2082_yel.png")
if "2082yelB" in which:
    im=harden(Image.open(D+"2082yelB_raw.png").convert("RGBA"))
    im=R.fill(im,[(1663,560),(1882,541),(1885,618),(1666,636)],(30,30,30),blur=2)
    im.save(D+"2082_yelB.png")
