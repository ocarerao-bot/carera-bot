"""CarEra logo as a countdown timer: the tick ring empties, the clock hand sweeps, seconds in the face."""
import math
from PIL import Image, ImageDraw, ImageFont
import urban as U, panels as P
from anim import put, ease_out_back
INTER="/usr/share/fonts/opentype/inter/Inter-Black.otf"
NAVY=(16,26,46); RIM=(86,96,112); DIM=(48,60,80); ORANGE=(255,120,30); YEL=(255,214,40); RED=(235,50,80)
def face(rem,total,S=600,label=True):
    n=math.ceil(rem); col=RED if n<=3 else YEL
    im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im); c=S/2; R=S/2-4
    d.ellipse([c-R,c-R,c+R,c+R],fill=RIM); r0=R*0.93; d.ellipse([c-r0,c-r0,c+r0,c+r0],fill=NAVY)
    act=rem/total
    for k in range(60):
        a=-math.pi/2+2*math.pi*k/60; on=k/60>=1-act-1e-6
        r1,r2=R*0.80,R*0.89; w=S*0.022
        p=[(c+math.cos(a)*r1,c+math.sin(a)*r1),(c+math.cos(a)*r2,c+math.sin(a)*r2)]
        d.line(p,fill=col if on else DIM,width=max(2,int(w)))
    ro=R*0.71; d.ellipse([c-ro,c-ro,c+ro,c+ro],outline=ORANGE,width=max(3,int(S*0.03)))
    ang=-math.pi/2+2*math.pi*(1-act)        # sweeping hand
    d.line([(c+math.cos(ang)*R*0.56,c+math.sin(ang)*R*0.56),(c+math.cos(ang)*R*0.76,c+math.sin(ang)*R*0.76)],fill=ORANGE,width=max(4,int(S*0.04)))
    hx,hy=c+math.cos(ang)*R*0.71,c+math.sin(ang)*R*0.71; rr=S*0.035; d.ellipse([hx-rr,hy-rr,hx+rr,hy+rr],fill=(255,255,255),outline=ORANGE,width=max(2,int(S*0.01)))
    f=ImageFont.truetype(INTER,int(S*(0.36 if n<10 else 0.30)))
    d.text((c,c+S*0.03),str(n),font=f,fill=(255,255,255),anchor="mm",stroke_width=max(2,int(S*0.012)),stroke_fill=NAVY)
    if label:
        fs=ImageFont.truetype(INTER,int(S*0.07)); d.text((c,c+S*0.25),"SEC",font=fs,fill=ORANGE,anchor="mm")
    return U.hard_shadow(P.sticker(im,max(6,int(S*0.025))),(8,10))
class Timer:
    """off = global start time of this scene; reveal = global time the answer comes"""
    def __init__(s,off,reveal,cx,cy,S,t_in=0.0,grow=None,style='A'):
        s.off,s.rev,s.cx,s.cy,s.S,s.t_in,s.grow,s.style=off,reveal,cx,cy,S,t_in,grow,style; s.cache={}
    def f(s,rem,S): return faceA(rem,s.rev,S) if s.style=='A' else face(rem,s.rev,S)
    def draw(s,base,t,rng):
        if t<s.t_in: return
        g=s.off+t; rem=max(0.001,s.rev-g); n=math.ceil(rem)
        S=s.S; cx,cy=s.cx,s.cy
        if s.grow:                                   # (dur, from_cx, from_cy, from_S)
            u=min(1,t/s.grow[0]); e=1-(1-u)**3
            cx=s.grow[1]+(cx-s.grow[1])*e; cy=s.grow[2]+(cy-s.grow[2])*e; S=int(s.grow[3]+(S-s.grow[3])*e)
        key=(n,int(rem/s.rev*60),int((1-rem/s.rev)*90),S)
        if key not in s.cache: s.cache={key:s.f(rem,S)} if len(s.cache)>40 else {**s.cache,key:s.f(rem,S)}
        im=s.cache[key]
        ph=n-rem                                     # pop on each new second
        sc=1+0.12*max(0,1-ph/0.25) if ph<0.25 else 1
        if t-s.t_in<0.3: sc*=ease_out_back(min(1,(t-s.t_in)/0.3),2.0)
        if sc!=1: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BILINEAR)
        put(base,im,cx-im.width/2,cy-im.height/2)

QUAD=[((255,150,40),(190,70,20)),((255,90,170),(120,40,160)),((0,205,190),(10,80,70)),((40,100,255),(20,30,110))]
_Q={}
def faceA(rem,total,S=600):
    import random
    n=math.ceil(rem); act=rem/total; c=S/2; M=int(S*0.08)
    im=Image.new("RGBA",(S+2*M,S+2*M),(0,0,0,0)); C=c+M
    if S not in _Q:
        q=Image.new("RGBA",(S,S))
        for i,(col,dots) in enumerate(QUAD): q.paste(U.poster(S//2,S//2,col,dots,cell=max(8,S//38)),((i%2)*S//2,(i//2)*S//2))
        m=Image.new("L",(S,S),0); ImageDraw.Draw(m).ellipse([0,0,S-1,S-1],fill=255); _Q[S]=(q,m)
    q,m=_Q[S]; im.paste(q,(M,M),m)
    d=ImageDraw.Draw(im)
    r=S*0.33; d.ellipse([C-r,C-r,C+r,C+r],fill=(15,15,15))
    col=RED if n<=3 else (255,255,255)
    for k in range(30):
        a=-math.pi/2+2*math.pi*k/30
        if k/30<1-act-1e-6: continue
        r1,r2=S*0.355,S*0.465
        d.line([(C+math.cos(a)*r1,C+math.sin(a)*r1),(C+math.cos(a)*r2,C+math.sin(a)*r2)],fill=(15,15,15),width=max(5,int(S*0.06)))
        d.line([(C+math.cos(a)*r1,C+math.sin(a)*r1),(C+math.cos(a)*r2,C+math.sin(a)*r2)],fill=col,width=max(3,int(S*0.04)))
    d.ellipse([M+3,M+3,M+S-3,M+S-3],outline=YEL,width=max(4,int(S*0.045)))
    for x in (0.40,0.60):
        xx=M+S*x; yy=M+S*(0.5+math.sqrt(0.25-(x-0.5)**2))-2; L=S*random.Random(int(x*100)).uniform(0.05,0.08)
        d.line([(xx,yy),(xx,yy+L)],fill=YEL,width=max(3,int(S*0.03))); rr=S*0.022; d.ellipse([xx-rr,yy+L-rr,xx+rr,yy+L+rr],fill=YEL)
    f=ImageFont.truetype(INTER,int(S*(0.36 if n<10 else 0.30)))
    d.text((C,C),str(n),font=f,fill=(255,255,255),anchor="mm",stroke_width=max(2,int(S*0.015)),stroke_fill=(15,15,15))
    return U.hard_shadow(im,(8,10))
