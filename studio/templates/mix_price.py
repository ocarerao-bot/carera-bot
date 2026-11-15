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

def tick(f=2400):
    t=np.arange(int(0.025*SR))/SR; return np.sin(2*np.pi*f*t)*np.exp(-t/0.004)*0.6
def ching():
    t=np.arange(int(1.2*SR))/SR
    x=sum(np.sin(2*np.pi*f*t)*a*np.exp(-t/d) for f,a,d in ((2093,1,0.5),(2637,.7,0.4),(3136,.5,0.35),(4186,.3,0.25)))
    x+=bp(rng.standard_normal(len(t)),3000,9000)*np.exp(-t/0.03)*0.8
    return x*0.55
put(ching(),0.4,0.8)
for sc in (4.0,8.0,12.0):
    for k in range(20):
        u=k/20; put(tick(1800+1600*u),sc+0.55+1.3*(1-(1-u)**0.5)*0.98,0.35)
    put(ching(),sc+1.85,0.8)
k=Kokoro("/home/claude/vid/voice/kokoro-v1.0.onnx","/home/claude/vid/voice/voices-v1.0.bin")
LINES={"hook":("Guess what a Range Rover cost in nineteen seventy.",0.15,3.8),
"e74":("Today? One hundred forty-two thousand, one hundred sixty dollars.",4.15,3.8),
"e97":("Ninety-four? Forty-eight thousand, nine hundred forty dollars.",8.15,3.8),
"e24":("And in seventy? Four thousand, seven hundred ninety-five dollars.",12.15,3.8),
"cta":("Twenty-nine old ones, for one new one. Which would you take?",16.1,3.85)}
voice=np.zeros(N,np.float32)
for name,(txt,t,mx) in LINES.items():
    sp=0.97
    while True:
        a,s=k.create(txt,voice=vn,speed=sp,lang="en-us");d=len(a)/s
        if d<=mx or sp>1.45:break
        sp+=0.03
    print(name,"speed %.2f dur %.2f"%(sp,d))
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
wavfile.write(f"/home/claude/vid/rr/mix10_{vn}.wav",SR,(mix*32767).astype(np.int16))
sr,m2=wavfile.read("/home/claude/vid/assets/music_v7.wav");m2=m2.astype(np.float32)/32768
mm=m2*0.75+st(sfx)*0.5;mm=np.tanh(mm*1.1)/np.tanh(1.1);mm=mm/np.abs(mm).max()*0.85
wavfile.write("/home/claude/vid/rr/music_sfx.wav",SR,(mm*32767).astype(np.int16))
wavfile.write("/home/claude/vid/rr/sfx_only.wav",SR,(np.tanh(sfx*1.2)/np.abs(np.tanh(sfx*1.2)).max()*0.8*32767).astype(np.int16))

vo=st(voice)+st(sfx*(1-0.5*env))*0.2; vo=vo/np.abs(vo).max()*0.85
wavfile.write("/home/claude/vid/rr/voice_sfx_nomusic.wav",SR,(vo*32767).astype(np.int16))
