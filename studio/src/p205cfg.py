import sys; sys.path.insert(0,"/home/claude/vid/src")
import copy
import urban as U
from lrcfg import recolor2
from m5cfg import sticker_pad
def car_sprite(cfg,cw):
    car=__import__("PIL.Image",fromlist=["Image"]).open(cfg["car"]).convert("RGBA"); car=car.crop(car.getbbox())
    from PIL import Image
    car=car.resize((cw,int(cw*car.height/car.width)),Image.LANCZOS)
    return U.hard_shadow(sticker_pad(car,14))
MP="/home/claude/vid/p205/photos/"
def make():
    C=copy.deepcopy(U.CFG)
    C[0].update(year="1983",car=MP+"205_red.png",carw=1000,cy=790,trw=560,
      strip="THE EIGHTIES",w1="RALLY KING",w2="world champion twice",s1=("2x","WRC"),s2=("2x","DAKAR"),c1="",c2="")
    C[1].update(year="2012",car=MP+"208_blue.png",carw=1030,cy=790,trw=580,
      strip="NOW: THE 208",w1="8:13!",w2="smashed Pikes Peak",s1=("875","HP"),s2=("-90","SEC"),c1="",c2="")
    C[2].update(year="2024",car=MP+"2082_yel.png",carw=1030,cy=790,trw=580,
      strip="TODAY",w1="No.1",w2="beat the VW Golf",s1=("#1","2022"),s2=("100%","EV"),c1="",c2="")
    return C
