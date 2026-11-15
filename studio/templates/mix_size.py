import sys,numpy as np,librosa
from scipy import signal
from scipy.io import wavfile
from kokoro_onnx import Kokoro
SR=44100;DUR=20;N=SR*DUR;vn=sys.argv[1]
rng=np.random.default_rng(7)
def lp(x,fc,o=2):
    b,a=signal.butter(o,fc/(SR/2));return signal.lfilter(b,a,x)
def bp(x,lo,hi):
    b,a=signal.butter(2,[lo/(SR/2),hi/(SR/2)],"band");return signal.lfilter(b,a,x)
def rev(T,f0,f1,punch=1.0):
    t=np.arange(int(T*SR))/SR;u=t/T
    f=f0+(f1-f0)*u**1.6
    ph=2*np.pi*np.cumsum(f)/SR
    x=sum(np.sin(h*ph+h)/h**0.75 for h in range(1,9))
    x*=0.65+0.35*np.sin(ph*0.5)**2                 # firing pulses
    x=np.tanh(x*2.2)
    # opening filter
    out=np.zeros_like(x);seg=int(0.05*SR)
    for i in range(0,len(x),seg):
        fc=500+3500*u[min(i,len(u)-1)]
        out[i:i+seg]=lp(x[i:i+seg+0],fc,1) if False else x[i:i+seg]
    x=lp(x,1800,2)*0.7+lp(x,6000,1)*0.3*u
    x+=0.08*bp(rng.standard_normal(len(x)),800,5000)*u
    env=np.minimum(1,t/0.03)*np.minimum(1,(T-t)/0.06)
    return x*env*punch
def horn(T=0.25):
    t=np.arange(int(T*SR))/SR
    x=sum(np.sign(np.sin(2*np.pi*f*t))*a for f,a in((415,1),(520,0.8),(830,0.2)))
    x=bp(x,300,3000)
    return x*np.minimum(1,t/0.006)*np.minimum(1,(T-t)/0.03)*0.5
def whoosh(T,up=True):
    n=rng.standard_normal(int(T*SR));out=np.zeros_like(n);seg=2048
    u=np.linspace(0,1,len(n)) if up else np.linspace(1,0,len(n))
    for i in range(0,len(n)-seg,seg//2):
        fc=300+7000*u[i]**2
        out[i:i+seg]+=bp(n[i:i+seg],max(200,fc*0.6),min(16000,fc*1.4))*np.hanning(seg)
    t=np.arange(len(n))/SR
    env=np.sin(np.pi*np.arange(len(n))/len(n))**1.5
    return out*env*0.9
def chirp_d(T=0.35):
    t=np.arange(int(T*SR))/SR;f=600+2400*(t/T)**2
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*0.5+0.2*np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))
    return x*np.minimum(1,t/0.01)*np.minimum(1,(T-t)/0.05)*0.5
def blip(T=0.35):  # gas blip
    return rev(T,75,190,1.0)
sfx=np.zeros(N,np.float32)
def put(x,t,g=1.0):
    i=int(t*SR);j=min(N,i+len(x))
    if i<0: x=x[-i:];i=0
    sfx[i:j]+=x[:j-i]*g
put(rev(0.9,70,260),0.0,0.55)                 # frame-0 gas rev
put(whoosh(0.8),3.2,0.35); put(horn(0.28),4.0,0.55)    # -> 1974 vintage honk
put(blip(0.4),6.8,0.45); put(rev(1.0,80,300),7.0,0.6); put(whoosh(0.5),7.5,0.2)  # -> 1997 rev
put(whoosh(0.8),11.2,0.35); put(chirp_d(0.35),11.65,0.5); put(chirp_d(0.2),12.0,0.4)  # -> modern
put(rev(1.0,80,320),15.0,0.6)                 # -> CTA rev
put(horn(0.16),16.0,0.55); put(horn(0.2),16.22,0.55)   # double honk
put(whoosh(0.9,up=False),19.1,0.35)           # loop-back
k=Kokoro("/home/claude/vid/voice/kokoro-v1.0.onnx","/home/claude/vid/voice/voices-v1.0.bin")
LINES={"hook":("The Mini... how much bigger did it get?",0.15,3.8),
"e74":("Fifty-nine. Just three metres... it had to fit in a ten-foot box.",4.1,3.85),
"e97":("Two thousand one. Half a metre longer... almost twice as heavy.",8.1,3.85),
"e24":("And today? Nearly four metres. Twenty-six percent longer.",12.1,3.85),
"cta":("So be honest... is it still a Mini?",16.15,3.8)}
CHUNKS={"e74":[("Fifty-nine.",["1959."],[]),("Just three metres...",["JUST 3 METRES..."],["3 METRES..."]),("it had to fit in a ten-foot box.",["FITS IN A","10-FOOT BOX"],["BOX"])],
"e97":[("Two thousand one.",["2001."],[]),("Half a metre longer...",["HALF A METRE","LONGER..."],["LONGER..."]),("almost twice as heavy.",["ALMOST 2×","AS HEAVY"],["HEAVY"])],
"e24":[("And today?",["AND TODAY?"],[]),("Nearly four metres.",["NEARLY","4 METRES"],["4 METRES"]),("Twenty-six percent longer.",["26%","LONGER"],["26%"])],
"cta":[("So be honest...",None,[]),("is it still a Mini?",["STILL A","MINI? ↓"],["MINI?"])]}
SPEED={}
voice=np.zeros(N,np.float32)
for name,(txt,t,mx) in LINES.items():
    sp=0.97
    while True:
        a,s=k.create(txt,voice=vn,speed=sp,lang="en-us");d=len(a)/s
        if d<=mx or sp>1.45:break
        sp+=0.03
    print(name,"speed %.2f dur %.2f"%(sp,d)); SPEED[name]=(sp,d,t)
    x=librosa.resample(a.astype(np.float32),orig_sr=s,target_sr=SR)
    x=signal.lfilter(*signal.butter(2,90/(SR/2),"high"),x)
    x=np.tanh(x*1.6)/np.tanh(1.6)*0.9;i=int(t*SR);voice[i:i+len(x)]+=x[:N-i]
act=np.abs(voice)>0.02;voice*=0.17/np.sqrt((voice[act]**2).mean())
sr,m=wavfile.read("/home/claude/vid/assets/music_v7_voicebed.wav");m=m.astype(np.float32)/32768
env=np.abs(voice);env=np.clip(lp(env,6,1)/0.15,0,1)
st=lambda v:np.stack([v,v],1)
sf=sfx*(1-0.35*env)
mix=m*0.52*(1-0.5*env[:,None])+st(voice)+st(sf)*0.2
mix=np.tanh(mix*1.1)/np.tanh(1.1);mix=mix/np.abs(mix).max()*0.85
wavfile.write(f"/home/claude/vid/minisize/mix10_{vn}.wav",SR,(mix*32767).astype(np.int16))
sr,m2=wavfile.read("/home/claude/vid/assets/music_v7.wav");m2=m2.astype(np.float32)/32768
mm=m2*0.75+st(sfx)*0.5;mm=np.tanh(mm*1.1)/np.tanh(1.1);mm=mm/np.abs(mm).max()*0.85
wavfile.write("/home/claude/vid/minisize/music_sfx.wav",SR,(mm*32767).astype(np.int16))
wavfile.write("/home/claude/vid/minisize/sfx_only.wav",SR,(np.tanh(sfx*1.2)/np.abs(np.tanh(sfx*1.2)).max()*0.8*32767).astype(np.int16))

vo=st(voice)+st(sfx*(1-0.5*env))*0.2; vo=vo/np.abs(vo).max()*0.85
wavfile.write("/home/claude/vid/minisize/voice_sfx_nomusic.wav",SR,(vo*32767).astype(np.int16))

import json
order=["hook","e74","e97","e24","cta"]; out={}
for sc,ch in CHUNKS.items():
    sp,tot,t0=SPEED[sc]; ds=[len(k.create(tx,voice=vn,speed=sp,lang="en-us")[0])/24000 for tx,_,_ in ch]
    f=tot/sum(ds); t=t0-4*order.index(sc); r=[]
    for (tx,disp,hl),d in zip(ch,ds):
        if disp: r.append(dict(t0=round(t,3),t1=round(t+d*f,3),lines=disp,hl=hl))
        t+=d*f
    r[-1]["t1"]=min(4.0,r[-1]["t1"]+0.35)
    for x,y in zip(r,r[1:]): x["t1"]=y["t0"]
    out[sc]=r
json.dump(out,open("/home/claude/vid/minisize/sub/timing.json","w"),indent=1)
