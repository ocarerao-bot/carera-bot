import sys; sys.path.insert(0,"/home/claude/vid/src")
from PIL import Image,ImageDraw,ImageFont,ImageFilter
FD="/home/claude/vid/fonts/"
def font(style,size):
    if style=="A":
        f=ImageFont.truetype(FD+"Montserrat[wght].ttf",size)
        try: f.set_variation_by_name("Black")
        except Exception: f.set_variation_by_axes([900])
        return f
    if style=="B": return ImageFont.truetype(FD+"Anton-Regular.ttf",size)
    return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf",size)
SIZE={"A":84,"B":124,"C":96}
def render(lines,style="A",hl=(),maxw=880,yel=(255,222,40)):
    """lines: list of str; hl: words to highlight. returns RGBA image"""
    size=SIZE[style]
    while True:
        f=font(style,size); ws=[f.getlength(l) for l in lines]
        if max(ws)<=maxw or size<40: break
        size-=4
    lh=int(size*(1.12 if style!="B" else 1.05)); pad=26
    W=int(max(ws))+2*pad+40; H=lh*len(lines)+2*pad+20
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    for i,l in enumerate(lines):
        y=pad+i*lh; x0=(W-f.getlength(l))/2
        if style=="C":
            bg=(15,15,15,255) if i%2==0 else yel+(255,); fg=(255,255,255) if i%2==0 else (15,15,15)
            bb=d.textbbox((x0,y),l,font=f); d.rectangle([bb[0]-18,bb[1]-12,bb[2]+18,bb[3]+14],fill=bg)
            d.text((x0,y),l,font=f,fill=fg); continue
        x=x0
        for j,wd in enumerate(l.split(" ")):
            t=wd+(" " if j<len(l.split(" "))-1 else "")
            col=yel if wd.strip(".,!?").upper() in {h.strip(".,!?").upper() for h in hl} else (255,255,255)
            sw=max(6,size//9)
            if style=="B":
                d.text((x+6,y+7),t,font=f,fill=(0,0,0,170),stroke_width=sw,stroke_fill=(0,0,0,170))
            d.text((x,y),t,font=f,fill=col,stroke_width=sw,stroke_fill=(10,10,10))
            x+=f.getlength(t)
    return im
