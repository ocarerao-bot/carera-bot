import sys; sys.path.insert(0,"/home/claude/vid/src")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
exec(open("/home/claude/vid/src/r5prep.py").read().split("# 1972")[0])
D="/home/claude/vid/lr/photos/"
# Series I: tint glass (people behind), plate off, keep original bronze green
a=largest(Image.open(D+"a4.png"))
for p in [[(652,298),(1003,238),(1006,468),(658,482)],[(1010,232),(1458,198),(1452,448),(1014,466)],[(1497,212),(1625,218),(1615,452),(1500,442)]]: a=glass(a,p)
a=fill(a,[(148,930),(325,915),(330,1090),(158,1105)],(24,27,20),blur=2)
a.save(D+"l1.png")
# Defender classic: plate off
b=largest(Image.open(D+"b14.png"))
b=fill(b,[(1446,918),(1628,906),(1634,980),(1450,990)],(30,34,28),blur=2)
b.save(D+"l2.png")
# New Defender 90, Tasman Blue: plate off
c=largest(Image.open(D+"c5.png"))
col=np.median(np.asarray(c)[825:860,1590:1630,:3].reshape(-1,3),0).astype(int)
c=fill(c,[(1656,803),(1866,788),(1866,858),(1658,875)],col,shade=0.15,blur=2)
c.save(D+"l3.png")
sh=Image.new("RGB",(2400,700),(70,70,70))
for i,f in enumerate(["l1.png","l2.png","l3.png"]):
    t=Image.open(D+f); t.thumbnail((790,690)); sh.paste(t,(i*800,0),t)
sh.save("/tmp/claude-0/-home-claude/ccb9edd0-eac0-5a46-b13a-a78caeec2b25/scratchpad/lrprep.png")
