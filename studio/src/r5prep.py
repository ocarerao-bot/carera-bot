import sys; sys.path.insert(0,"/home/claude/vid/src")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from price_sl import recolor_silver
D="/home/claude/vid/r5/photos/"
def largest(im):
    a=np.array(im); m=a[...,3]>40; lab,n=ndimage.label(m)
    if n>1:
        sz=ndimage.sum(m,lab,range(1,n+1)); keep=lab==(1+int(np.argmax(sz)))
        keep=ndimage.binary_fill_holes(keep); a[...,3]=np.where(ndimage.binary_dilation(keep,iterations=3),a[...,3],0)
    return Image.fromarray(a)
def fill(im,poly,col,shade=0.0,blur=3):
    lay=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(lay); d.polygon(poly,fill=tuple(col)+(255,))
    a=np.array(lay).astype(np.float32)
    if shade:
        ys=np.arange(im.height)[:,None]; y0=min(p[1] for p in poly); y1=max(p[1] for p in poly)
        f=1-shade*np.clip((ys-y0)/(y1-y0+1),0,1); a[...,:3]*=f[...,None]
    lay=Image.fromarray(a.clip(0,255).astype(np.uint8)); m=lay.split()[3].filter(ImageFilter.GaussianBlur(blur))
    out=im.copy(); base=out.convert("RGB"); base.paste(lay.convert("RGB"),(0,0),m); out=Image.merge("RGBA",(*base.split(),im.split()[3])); return out
def glass(im,poly):
    """replace window area with dark tinted glass + soft reflection (hides people behind the car)"""
    a=np.array(im).astype(np.float32); m=Image.new("L",im.size,0); ImageDraw.Draw(m).polygon(poly,fill=255)
    m=np.asarray(m.filter(ImageFilter.GaussianBlur(2))).astype(np.float32)/255
    bl=np.asarray(im.convert("RGB").filter(ImageFilter.GaussianBlur(28))).astype(np.float32)
    lum=bl.mean(-1,keepdims=True); g=lum*0.22+np.array([18,22,28])
    H,W=m.shape; yy,xx=np.mgrid[0:H,0:W]; streak=np.exp(-((xx*0.55+yy)-(min(p[0] for p in poly)*0.55+min(p[1] for p in poly)+140))**2/(2*45**2))
    g=g+streak[...,None]*55
    a[...,:3]=a[...,:3]*(1-m[...,None])+g*m[...,None]; return Image.fromarray(a.clip(0,255).astype(np.uint8))
# 1972 orange R5 TL – plate off, glass tinted (people behind)
r1=largest(Image.open(D+"r1.png"))
r1=glass(r1,[(592,132),(1043,124),(1178,293),(612,343)])
r1=glass(r1,[(483,152),(568,146),(598,365),(478,330)])
r1=glass(r1,[(402,152),(462,150),(458,305),(398,280)])
a=np.asarray(r1); bump=np.median(a[700:820,1112:1140,:3].reshape(-1,3),0).astype(int); print("bump",bump)
r1=fill(r1,[(1222,756),(1478,676),(1486,748),(1236,842)],bump,shade=0.25)
r1.save(D+"r1_np.png")
# 1984 Super 5 – plate off, silver -> period red
r2=largest(Image.open(D+"r2.png"))
a=np.asarray(r2); bump=np.median(a[820:880,1760:1800,:3].reshape(-1,3),0).astype(int); print("bump2",bump)
r2=fill(r2,[(1490,885),(1748,812),(1754,888),(1500,970)],bump,shade=0.2)
r2.save(D+"r2_np.png")
r2c=recolor_silver(r2,1,215,0.82); r2c.save(D+"r2_rc.png")
r3=largest(Image.open(D+"r3b.png")); r3.save(D+"r3_np.png")
sh=Image.new("RGB",(2000,1500),(0,160,80))
for i,im in enumerate([r1,r2c,r3]):
    t=im.copy(); t.thumbnail((990,740)); sh.paste(t,((i%2)*1000,(i//2)*750),t)
sh.save("/tmp/claude-0/-home-claude/ccb9edd0-eac0-5a46-b13a-a78caeec2b25/scratchpad/prep.png")
