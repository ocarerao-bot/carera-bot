import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
def harden(a):
    al=np.clip((a[...,3].astype(np.float32)-90)*3,0,255)
    lab,n=ndimage.label(al>0)
    if n>1:
        sz=ndimage.sum(np.ones_like(al),lab,range(1,n+1)); al[lab!=np.argmax(sz)+1]=0
    a[...,3]=al.astype(np.uint8); return a
# E39
im=Image.open("e39.png").convert("RGBA"); a=harden(np.asarray(im).copy())
m=Image.new("L",im.size,0); ImageDraw.Draw(m).polygon([(1240,728),(1462,698),(1468,800),(1240,820)],fill=255)
mk=np.asarray(m.filter(ImageFilter.MaxFilter(15)))
bgr=cv2.inpaint(cv2.cvtColor(a[...,:3],cv2.COLOR_RGB2BGR),mk,15,cv2.INPAINT_TELEA)
a[...,:3]=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB); Image.fromarray(a).save("e39_np.png")
# G90
im=Image.open("g90.png").convert("RGBA"); a=harden(np.asarray(im).copy())
m=Image.new("L",im.size,0); ImageDraw.Draw(m).polygon([(2738,1710),(3348,1686),(3348,1862),(3210,1880),(3210,1915),(2738,1918)],fill=255)
mf=np.asarray(m.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(4))).astype(np.float32)[...,None]/255
rng=np.random.default_rng(1); flat=np.full(a[...,:3].shape,(27,27,29),np.float32)+rng.normal(0,3,a[...,:3].shape)
a[...,:3]=(a[...,:3]*(1-mf)+flat*mf).astype(np.uint8); Image.fromarray(a).save("g90_np.png")
print(Image.open("g90_np.png").getbbox(),Image.open("e39_np.png").getbbox())
