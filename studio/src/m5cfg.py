import sys; sys.path.insert(0,"/home/claude/vid/src")
import copy, numpy as np
from PIL import Image, ImageFilter
import urban as U, panels as P
from lrcfg import recolor2
def sticker_pad(img,border=14):
    # pad first, so the white outline is never clipped at the image edge (roof/wheels)
    pad=border+6; big=Image.new("RGBA",(img.width+2*pad,img.height+2*pad),(0,0,0,0)); big.alpha_composite(img,(pad,pad))
    a=big.getchannel("A").point(lambda v:255 if v>110 else 0)
    ring=a.filter(ImageFilter.MaxFilter(border*2+1)).filter(ImageFilter.GaussianBlur(2)).point(lambda v:255 if v>80 else 0)
    out=Image.new("RGBA",big.size,(0,0,0,0)); out.paste(Image.new("RGBA",big.size,(255,255,255,255)),(0,0),ring); out.alpha_composite(big)
    return out
def car_sprite(cfg,cw):
    car=Image.open(cfg["car"]).convert("RGBA"); car=car.crop(car.getbbox()); car=car.resize((cw,int(cw*car.height/car.width)),Image.LANCZOS)
    car=recolor2(car,**cfg["rc2"])
    return U.hard_shadow(sticker_pad(car,14))
MP="/home/claude/vid/m5/photos/"
NO=dict(src=0,width=0,soft=1,hue=0,smin=300)
def make():
    C=copy.deepcopy(U.CFG)
    C[0].update(year="1985",car=MP+"e28_red.png",carw=1000,cy=790,trw=560,rc2=NO,
      strip="THE EIGHTIES",w1="M1 HEART",w2="a supercar engine",s1=("286","HP"),s2=("152","MPH"),c1="",c2="")
    C[1].update(year="1998",car=MP+"e39_np.png",carw=1000,cy=790,trw=580,rc2=NO,
      strip="THE NINETIES",w1="V8!",w2="the first V8 M5",s1=("400","HP"),s2=("V8","4.9L"),c1="",c2="")
    C[2].update(year="2024",car=MP+"g90_np.png",carw=1000,cy=790,trw=580,rc2=NO,
      strip="TODAY",w1="PLUG-IN",w2="the first hybrid M5",s1=("727","HP"),s2=("2.4T","HEAVY"),c1="",c2="")
    return C
