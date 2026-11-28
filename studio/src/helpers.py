import sys; sys.path.insert(0,"/home/claude/vid/src")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
D="/home/claude/vid/r5/photos/"
def largest(im):
    a=np.array(im); m=a[...,3]>40; lab,n=ndimage.label(m)
    if n>1:
        sz=ndimage.sum(m,lab,range(1,n+1)); keep=lab==(1+int(np.argmax(sz)))
        keep=ndimage.binary_fill_holes(keep); a[...,3]=np.where(ndimage.binary_dilation(keep,iterations=3),a[...,3],0)
    return Image.fromarray(a)
def fill(im,poly,col,shade=0.0,blur=3):
    lay=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(lay); d.polygon(poly,fill=tuple(col)+(255,))
    a=np.array(lay).astype(np.float32)
    if shade:
        ys=np.arange(im.height)[:,None]; y0=min(p[1] for p in poly); y1=max(p[1] for p in poly)
        f=1-shade*np.clip((ys-y0)/(y1-y0+1),0,1); a[...,:3]*=f[...,None]
    lay=Image.fromarray(a.clip(0,255).astype(np.uint8)); m=lay.split()[3].filter(ImageFilter.GaussianBlur(blur))
    out=im.copy(); base=out.convert("RGB"); base.paste(lay.convert("RGB"),(0,0),m); out=Image.merge("RGBA",(*base.split(),im.split()[3])); return out
def glass(im,poly):
    """replace window area with dark tinted glass + soft reflection (hides people behind the car)"""
    a=np.array(im).astype(np.float32); m=Image.new("L",im.size,0); ImageDraw.Draw(m).polygon(poly,fill=255)
    m=np.asarray(m.filter(ImageFilter.GaussianBlur(2))).astype(np.float32)/255
    bl=np.asarray(im.convert("RGB").filter(ImageFilter.GaussianBlur(28))).astype(np.float32)
    lum=bl.mean(-1,keepdims=True); g=lum*0.22+np.array([18,22,28])
    H,W=m.shape; yy,xx=np.mgrid[0:H,0:W]; streak=np.exp(-((xx*0.55+yy)-(min(p[0] for p in poly)*0.55+min(p[1] for p in poly)+140))**2/(2*45**2))
    g=g+streak[...,None]*55
    a[...,:3]=a[...,:3]*(1-m[...,None])+g*m[...,None]; return Image.fromarray(a.clip(0,255).astype(np.uint8))
