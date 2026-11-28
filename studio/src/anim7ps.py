import sys; sys.path.insert(0,"/home/claude/vid/src")
import json, os
from PIL import Image
import anim7p as F, anim as A, subs
from anim import put
T=json.load(open("/home/claude/vid/p205/sub/timing.json"))
class Sub:
    def __init__(s,img,cx,cy,t0,t1): s.img,s.cx,s.cy,s.t0,s.t1=img,cx,cy,t0,t1
    def draw(s,base,t,rng):
        if t<s.t0 or t>=s.t1: return
        u=min(1,(t-s.t0)/0.1); sc=0.82+0.18*F.ease_out(u)
        im=s.img
        if sc<0.999: im=im.resize((max(2,int(im.width*sc)),max(2,int(im.height*sc))),Image.BILINEAR)
        put(base,im,s.cx-im.width/2,s.cy-im.height/2)
import urban as U, math
class Pulse:
    def __init__(s,img,cx,cy,t0,t1): s.img,s.cx,s.cy,s.t0,s.t1=img.rotate(6,resample=Image.BICUBIC,expand=True),cx,cy,t0,t1
    def draw(s,base,t,rng):
        if t<s.t0 or t>=s.t1: return
        u=min(1,(t-s.t0)/0.25); sc=(0.3+0.7*F.ease_out(u))*(1+0.07*math.sin((t-s.t0)*10))
        im=s.img.resize((max(2,int(s.img.width*sc)),max(2,int(s.img.height*sc))),Image.BILINEAR)
        put(base,im,s.cx-im.width/2,s.cy-im.height/2)
def build(name):
    bg,ls,d,st,sd=F.build(name)
    ls=[l for l in ls if not isinstance(l,A.L) or l is not ls[-1]] if False else ls[:-1]   # drop torn caption (last layer)
    if name=="hook": ls.append(ls.pop(2))      # "PICK 1, 2 OR 3" label on top of the cars
    if name in ("e74","e97","e24"):
        ls[7].x,ls[7].y=ls[7].x-60,560-ls[7].img.height/2
        ls[8].x,ls[8].y=ls[8].x+40,600-ls[8].img.height/2
    if name=="cta":   # swap the CarEra label for a pulsing FOLLOW sticker
        ls=ls[:-2]   # drop emblem + CarEra label (last two before the caption)
        fl=U.hard_shadow(U.label("FOLLOW +",58,(255,255,255),(230,40,90)))
        ls.append(Pulse(fl,860,1468,1.0,4.0))
    cy=1400 if name!="cta" else 1640
    for c in T.get(name,[]):
        im=subs.render(c["lines"],"C",hl=tuple(c["hl"]))
        ls.append(Sub(im,520,cy,c["t0"],c["t1"]))
    return bg,ls,d,st,sd
if __name__=="__main__":
    A.OUT="/home/claude/vid/p205/out/"; os.makedirs(A.OUT+"prev",exist_ok=True)
    mode=sys.argv[1]; names=sys.argv[2:] or ["hook","e74","e97","e24","cta"]
    for n in names:
        bg,ls,d,st,sd=build(n)
        if mode=="preview": A.render_scene(n,bg,ls,d,st,sd,preview={0,30,60,90,110})
        else: A.render_scene(n,bg,ls,d,st,sd); print("done",n,flush=True)
