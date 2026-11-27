import re, math, random, sys
src_a=open('/home/claude/vid/src/mockup_zine_photo.py').read().split('bg = paper_bg()')[0]
src_b=open('/home/claude/vid/src/mockup_zine_v2.py').read()
fn=src_b[src_b.index('import numpy as np\ndef recolor_green'):src_b.index('SW,SH=984,1124')]
exec(src_a); exec(fn)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
SW,SH=984,1124
PH="/home/claude/vid/photos/"
def starburst(txt,r,col,fg):
    pts=[]; n=18
    for i in range(n*2):
        rr=r if i%2==0 else r*0.78; a=math.pi*i/n
        pts.append((r+20+rr*math.cos(a),r+20+rr*math.sin(a)))
    img=Image.new("RGBA",(2*r+40,2*r+40),(0,0,0,0)); d=ImageDraw.Draw(img)
    d.polygon(pts,fill=(20,20,20,255))
    d.polygon([(r+20+(p[0]-r-20)*0.93,r+20+(p[1]-r-20)*0.93) for p in pts],fill=col)
    lines=txt.split("\n"); size=int(min(r*0.34,1.45*r/(0.66*max(len(l) for l in lines))))
    f=ImageFont.truetype(FD+"Inter-Black.otf",size)
    for k,l in enumerate(lines):
        d.text((r+20,r+20+(k-(len(lines)-1)/2)*size*1.08),l,font=f,fill=fg,anchor="mm")
    return img


def patch(img, poly):
    d=ImageDraw.Draw(img); d.polygon(poly,fill=(238,238,232,255)); d.line(poly+[poly[0]],fill=(90,90,90,255),width=5)

def scene(style):
    sc=Image.new("RGB",(SW,SH)); d=ImageDraw.Draw(sc)
    if style=="70":
        for y in range(SH):
            t=min(1,y/760); d.line([0,y,SW,y],fill=(int(250-52*t),int(176-62*t),int(70-16*t)))
        d.ellipse([440,190,820,570],fill=(255,226,150))
        for i,(x,w_,h_) in enumerate([(0,120,230),(130,90,330),(230,150,200),(390,80,280),(480,110,170),(600,100,300),(710,130,220),(850,140,260)]):
            d.rectangle([x,760-h_,x+w_,760],fill=(120+i%3*8,70,48))
            for wy in range(760-h_+20,740,38):
                for wx in range(x+14,x+w_-14,30):
                    if (wx*7+wy*3)%5<2: d.rectangle([wx,wy,wx+12,wy+16],fill=(255,214,120))
        d.rectangle([0,760,SW,SH],fill=(66,48,42)); d.rectangle([0,760,SW,772],fill=(180,150,120))
        for x in range(-20,SW,230): d.polygon([(x,1060),(x+150,1060),(x+170,1078),(x+20,1078)],fill=(232,204,150))
    elif style=="90":
        for y in range(SH):
            t=min(1,y/760); d.line([0,y,SW,y],fill=(int(70+170*t),int(40+60*t),int(130-10*t)))
        # memphis shapes
        for (x,y,r,c) in ((120,170,60,(0,200,190)),(820,260,45,(255,226,60)),(660,110,38,(255,90,160)),(250,420,30,(255,226,60))):
            d.ellipse([x-r,y-r,x+r,y+r],fill=c)
        d.polygon([(860,120),(930,240),(790,240)],fill=(0,200,190))
        for k in range(6): d.line([(80+k*30,520),(110+k*30,490),(140+k*30,520)],fill=(255,255,255),width=6)
        # mall
        d.rectangle([0,560,SW,780],fill=(205,196,215)); d.rectangle([0,560,SW,610],fill=(40,30,70))
        d.text((SW//2,585),"M A L L   •   S A L E   •   C D s",font=ImageFont.truetype(FD+"Inter-Black.otf",34),fill=(255,90,160),anchor="mm")
        for x in range(40,SW,150): d.rectangle([x,640,x+100,740],fill=(90,140,170))
        d.rectangle([0,780,SW,SH],fill=(78,76,92))
        for x in range(0,SW,160): d.line([x,800,x-40,SH],fill=(235,235,240),width=8)
    else:
        for y in range(SH):
            t=min(1,y/760); d.line([0,y,SW,y],fill=(int(120+120*t),int(190+50*t),int(240+10*t)))
        for i,(x,w_,h_) in enumerate([(30,150,520),(200,120,400),(340,170,590),(530,120,350),(670,160,480),(850,140,420)]):
            d.rectangle([x,760-h_,x+w_,760],fill=(70+i*9,120+i*7,170+i*5))
            for wy in range(760-h_+16,740,44): d.line([x,wy,x+w_,wy],fill=(200,230,250),width=2)
            d.line([x+w_//2,760-h_,x+w_//2,760],fill=(200,230,250),width=2)
        d.rectangle([0,760,SW,SH],fill=(92,98,108)); d.rectangle([0,760,SW,770],fill=(210,214,220))
        for x in range(-20,SW,230): d.rectangle([x,1060,x+150,1074],fill=(240,240,244))
        # EV charger
        d.rectangle([860,590,905,775],fill=(240,244,248)); d.rectangle([870,610,895,650],fill=(40,200,140))
    return sc

def build(car_path, year, strip_txt, cap1, cap2, b1, b2, style, out, green=False, plate=None, carw=920, grain=7, seed=3):
    global rnd
    rnd=random.Random(seed)
    car=Image.open(car_path).convert("RGBA")
    if plate: patch(car,plate)
    car=car.crop(car.getbbox())
    car=car.resize((carw,int(carw*car.height/car.width)),Image.LANCZOS)
    if green: car=recolor_green(car)
    spr=sticker(car,12)
    sc=scene(style).convert("RGBA")
    cx,bottom=SW//2+10,985
    sh=Image.new("RGBA",(SW,SH),(0,0,0,0))
    ImageDraw.Draw(sh).ellipse([cx-carw//2,bottom-70,cx+carw//2-20,bottom+20],fill=(10,6,4,200))
    sc.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    sc.alpha_composite(spr,(int(cx-spr.width/2),int(bottom-spr.height+30)))
    arr=np.asarray(sc.convert("RGB")).astype(np.float32)
    if grain: arr+=np.random.default_rng(5).normal(0,grain,arr.shape[:2])[...,None]; arr=arr*0.94+12
    if style=="90": arr=np.clip(arr,0,255); arr[...,0]=np.roll(arr[...,0],3,axis=1); arr[...,2]=np.roll(arr[...,2],-3,axis=1)
    st=stamp(1040,1180,Image.fromarray(np.clip(arr,0,255).astype(np.uint8)))
    bg=paper_bg()
    place(bg,st,540,1045,rot=-1.6 if style=="70" else (1.4 if style=="90" else -0.8))
    for (x,y,r) in ((120,470,-38),(960,480,34),(110,1590,30),(965,1600,-32)): place(bg,tape(),x,y,r,shadow=False)
    cols=[((255,255,255),(200,38,38)),((20,20,20),(250,240,200)),((255,220,60),(20,20,20)),((255,255,255),(30,90,170))]
    order={"70":[0,1,2,3],"90":[3,2,0,1],"24":[1,0,3,2]}[style]
    x=105
    for i,ch in enumerate(year):
        fg,bgc=cols[order[i]]
        t=letter_tile(ch,170+rnd.randint(-12,12),fg,bgc,i*2+1)
        place(bg,t,x+t.width/2-20,250+rnd.randint(-18,18),rot=rnd.uniform(-9,9)); x+=t.width-44
    strip=torn(700,110,(28,28,30),amp=6)
    ImageDraw.Draw(strip).text((strip.width/2,strip.height/2),strip_txt,font=ImageFont.truetype(FD+"Inter-ExtraBold.otf",48),fill=(250,240,200),anchor="mm")
    place(bg,strip,400,470,rot=-2.5)
    place(bg,starburst(b1,135,(255,214,60),(20,20,20)),215,1600,rot=-10)
    place(bg,starburst(b2,135,(240,90,60),(255,255,255)),870,1610,rot=9)
    clip=torn(900,170,(252,250,244),edge=(240,236,224),amp=6); cd=ImageDraw.Draw(clip)
    M="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    cd.text((clip.width/2,66),cap1,font=ImageFont.truetype(M,30),fill=(30,30,30),anchor="mm")
    cd.text((clip.width/2,114),cap2,font=ImageFont.truetype(M,25),fill=(30,30,30),anchor="mm")
    place(bg,clip,540,1775,rot=-1.2)
    a=np.asarray(bg.convert("RGB"),dtype=np.float32)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    dd=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/1.42
    a*=(1-0.35*dd**2)[...,None]
    Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(out)

if __name__=="__main__":
    O="/home/claude/vid/mock/"
    build(PH+"golf_mk1_clean2.png","1974","THE SEVENTIES","1974. Bell-bottoms, cassette tapes.","A boxy, light Golf with just fifty horsepower.","≈ 50 HP","< 800 KG","70",O+"panel_1974.png",green=True)
    build(PH+"golf_mk4_cut.png","1997","THE NINETIES","1997. CDs and Tamagotchis.","Now premium: airbags, galvanized body, turbo diesels.","AIRBAGS","TURBO\nDIESEL","90",O+"panel_1997.png",plate=[(344,1074),(716,1106),(716,1206),(350,1180)],carw=980,grain=5,seed=5)
    build(PH+"golf_mk8_cut.png","2024","TODAY","Today: digital cockpit, mild-hybrid power,","and it can help steer on the highway.","MILD-\nHYBRID","DIGITAL\nCOCKPIT","24",O+"panel_2024.png",plate=[(256,860),(576,880),(576,968),(260,948)],carw=990,grain=0,seed=7)
    print("ok")

# --- fix (user, 2026-11-27): pad before drawing the white sticker outline, otherwise it is clipped
# where the car touches the edge of its cropped image (roof, wheels, nose). Applies to every video.
_sticker_orig=sticker
def sticker(img, border=16):
    pad=border+6; big=Image.new("RGBA",(img.width+2*pad,img.height+2*pad),(0,0,0,0)); big.alpha_composite(img.convert("RGBA"),(pad,pad))
    a=big.getchannel("A").point(lambda v:255 if v>110 else 0)
    ring=a.filter(ImageFilter.MaxFilter(border*2+1)).filter(ImageFilter.GaussianBlur(2)).point(lambda v:255 if v>80 else 0)
    out=Image.new("RGBA",big.size,(0,0,0,0)); out.paste(Image.new("RGBA",big.size,(255,255,255,255)),(0,0),ring); out.alpha_composite(big)
    return out
