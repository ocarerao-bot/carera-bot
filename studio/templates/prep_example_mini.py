import sys; sys.path.insert(0,"/home/claude/vid/src")
import numpy as np
from PIL import Image, ImageDraw, ImageOps
exec(open("/home/claude/vid/src/r5prep.py").read().split("# 1972")[0])
def thr(im,t=170):
    a=np.asarray(im).copy(); al=a[...,3]; a[...,3]=np.where(al<t,0,np.where(al>230,255,al)); return Image.fromarray(a)
def kill(im,box):
    a=np.asarray(im).copy(); x0,y0,x1,y1=box; a[y0:y1,x0:x1,3]=0; return Image.fromarray(a)
s1=largest(thr(Image.open("s1.png")))
s2=Image.open("s2.png"); print(s2.size)
s2=largest(thr(s2)); s2=ImageOps.mirror(s2)
s3=Image.open("s3.png"); s3=kill(s3,(1450,0,2000,int(36*2000/790*0.0+90))); s3=largest(thr(s3))
for n,im in [("t1",s1),("t2",s2),("t3",s3)]: im.crop(im.getbbox()).save(n+".png")
sh=Image.new("RGB",(2400,600),(90,90,90))
for i,n in enumerate(["t1","t2","t3"]):
    t=Image.open(n+".png"); t.thumbnail((790,590)); sh.paste(t,(i*800,0),t)
sh.save("/tmp/claude-0/-home-claude/ccb9edd0-eac0-5a46-b13a-a78caeec2b25/scratchpad/tcut.png")
