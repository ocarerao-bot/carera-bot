import sys; sys.path.insert(0,"/home/claude/vid/src")
import random
from PIL import Image
import urban as U, panels as P, price_r5 as Pr
from brand2 import grain_vig
P.rnd=random.Random(5); bg=U.concrete(5,(20,10,10))
for (w,h,col,dots,x,y,r) in [(560,700,(255,150,40),(190,70,20),110,560,-8),(560,620,(255,90,170),(120,40,160),990,700,7),(560,600,(40,100,255),(20,30,110),980,1500,-6),(520,640,(0,205,190),(10,80,70),90,1520,6)]:
    U.paste(bg,U.hard_shadow(U.poster(w,h,col,dots),(8,10),160),x,y,r)
U.paste(bg,U.spray_blob((1100,760),(255,120,20),9),540,820,-4)
lab=U.hard_shadow(U.label("NEW POST",56,(255,255,255),(230,40,90))); U.paste(bg,lab,300,300,-6)
t1=U.spray_text("1972 RENAULT 5",112,(255,255,255),seed=4); U.paste(bg,U.fit(t1,1000),540,440,-4)
car=Pr.sprite(Pr.ERAS[0],820); U.paste(bg,car,540,800,-3)
q=Pr.tag("$ ?,???",130).rotate(-4,resample=Image.BICUBIC,expand=True); U.paste(bg,q,600,1110,0)
t2=U.spray_text("CHEAPER THAN",120,(255,214,40),seed=7); U.paste(bg,U.fit(t2,960),540,1290,-3)
t3=U.spray_text("A GAMING PC?",120,(255,214,40),seed=8); U.paste(bg,U.fit(t3,960),550,1420,-3)
w=U.hard_shadow(U.label("WRONG ANSWERS ONLY",58,(15,15,15),(0,235,170))); U.paste(bg,w,540,1560,3)
hint=U.hard_shadow(U.label("ANSWER IN THE REEL",40,(255,255,255),(15,15,15))); U.paste(bg,hint,540,1740,-2)
grain_vig(bg,3,4,0.22).save("/home/claude/vid/story/story_renault5_1080x1920.png")
