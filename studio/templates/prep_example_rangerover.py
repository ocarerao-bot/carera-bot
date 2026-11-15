import sys; sys.path.insert(0,"/home/claude/vid/src")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open("/home/claude/vid/src/r5prep.py").read().split("# 1972")[0])
D="/home/claude/vid/rr/photos/"
a=largest(Image.open(D+"a2f.png"))
a=fill(a,[(290,850),(576,880),(570,964),(286,930)],(28,28,26),blur=2); a.save(D+"m1.png")
b=largest(Image.open(D+"b2.png")); b.save(D+"m2.png")
c=largest(Image.open(D+"c.png"))
def glass2(im,poly,k=0.6,r=45):
    m=Image.new("L",im.size,0); ImageDraw.Draw(m).polygon(poly,fill=255); m=m.filter(ImageFilter.GaussianBlur(3))
    bl=im.convert("RGB").filter(ImageFilter.GaussianBlur(r)); bl=Image.eval(bl,lambda v:int(v*k))
    out=im.copy(); rgb=out.convert("RGB"); rgb.paste(bl,(0,0),m); return Image.merge("RGBA",(*rgb.split(),im.split()[3]))
c=glass2(c,[(600,135),(1190,125),(1410,390),(680,420)])
c=fill(c,[(1440,700),(1645,693),(1652,780),(1450,795)],(36,44,42),blur=2)
A=np.asarray(c).astype(np.float32); rgb=A[...,:3]
hsv=np.asarray(Image.fromarray(rgb.astype(np.uint8)).convert("HSV")).astype(np.float32); Hh,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
w=np.clip(1-np.abs(Hh-118)/40,0,1)*np.clip((S-6)/14,0,1)
w=np.asarray(Image.fromarray((w*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)/255
lum=(rgb@np.array([0.299,0.587,0.114]))[...,None]
grey=lum*np.array([1.06,1.06,1.10])*1.12
out=rgb*(1-w[...,None])+grey*w[...,None]
Image.fromarray(np.dstack([out.clip(0,255),A[...,3]]).astype(np.uint8)).save(D+"m3.png")
sh=Image.new("RGB",(2400,700),(90,90,90))
for i,f in enumerate(["m1.png","m2.png","m3.png"]):
    t=Image.open(D+f); t.thumbnail((790,690)); sh.paste(t,(i*800,0),t)
sh.save("/tmp/claude-0/-home-claude/ccb9edd0-eac0-5a46-b13a-a78caeec2b25/scratchpad/rrprep.png")
