import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
im=Image.open("e28.png").convert("RGBA"); W,H=im.size
a=np.asarray(im).copy()
al=a[...,3].astype(np.float32)
# harden alpha, remove smudge above-left of hood
al=np.clip((al-90)*3,0,255)
sm=Image.new('L',(W,H),0); ImageDraw.Draw(sm).polygon([(560,300),(760,300),(740,385),(660,450),(560,470)],fill=255)
al[np.asarray(sm)>0]=0
rgb=cv2.cvtColor(a[...,:3],cv2.COLOR_RGB2BGR)
m=Image.new("L",(W,H),0); d=ImageDraw.Draw(m)
d.polygon([(688,420),(875,420),(880,565),(688,565)],fill=255)          # person reflection on hood
d.polygon([(345,900),(705,992),(700,1102),(340,1008)],fill=255)          # show plate board
mk=np.asarray(m.filter(ImageFilter.MaxFilter(9)))
rgb=cv2.inpaint(rgb,mk,9,cv2.INPAINT_TELEA)
out=np.dstack([cv2.cvtColor(rgb,cv2.COLOR_BGR2RGB),al.astype(np.uint8)])
Image.fromarray(out,"RGBA").save("e28_np.png")

# ---- step 2: tint glass + recolour a BLACK car (body mask = everything minus glass/front band/wheels) ----
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
O=(140,120)
def P(pts): return [(x+O[0],y+O[1]) for x,y in pts]
im=Image.open("e28_np.png").convert("RGBA"); W,H=im.size
GL=[P([(598,274),(785,40),(1392,60),(1370,354),(880,300)]), P([(1402,62),(1562,70),(1640,212),(1600,268),(1410,272)])]
def glass(img):
    m=Image.new("L",img.size,0); [ImageDraw.Draw(m).polygon(g,fill=255) for g in GL]; m=m.filter(ImageFilter.GaussianBlur(4))
    bl=img.filter(ImageFilter.GaussianBlur(10)); flat=Image.new("RGBA",img.size,(22,24,34,255))
    bl=Image.blend(bl,flat,0.72); bl.putalpha(img.getchannel("A")); return Image.composite(bl,img,m)
base=glass(im); base.save("e28_glass.png")
EXC=[P([(40,515),(560,615),(990,700),(1060,795),(1215,835),(1215,1150),(0,1150)]),
     [(1375,800),(1490,765),(1505,1240),(1250,1240),(1290,1000),(1335,880)],
     [(1725,520),(1800,500),(1810,775),(1640,775),(1650,690),(1690,600)]]
def recolor(img,col,gain=1.0):
    a=np.asarray(img).astype(np.float32); rgb=a[...,:3]
    hsv=np.asarray(Image.fromarray(rgb.astype(np.uint8)).convert("HSV")).astype(np.float32)
    S,V=hsv[...,1],hsv[...,2]
    m=Image.new("L",img.size,0); d=ImageDraw.Draw(m)
    d.rectangle([0,0,W,H],fill=255)
    for e in EXC: d.polygon(e,fill=0)
    for g in GL: d.polygon(g,fill=0)
    m=np.asarray(m.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)/255
    w=m*np.clip((130-S)/50,0,1)*(a[...,3]>0)
    L=V/255.0
    c=np.array(col,np.float32)
    paint=c[None,None,:]*np.clip(0.30+2.2*L*gain,0,1.6)[...,None]
    spec=np.clip((L-0.45)/0.4,0,1)[...,None]          # keep bright reflections
    paint=paint*(1-spec)+rgb*spec
    out=rgb*(1-w[...,None])+paint*w[...,None]
    return Image.fromarray(np.dstack([np.clip(out,0,255),a[...,3]]).astype(np.uint8),"RGBA")
for name,col in [("red",(196,40,28)),("blue",(30,78,190))]:
    r=recolor(base,col); r.save(f"e28_{name}.png")
