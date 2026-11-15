"""Original deep/tech-house bed, 120 BPM, 30 s. Leaves room in the mids for a voice-over."""
import numpy as np
from scipy import signal
from scipy.io import wavfile
SR=44100; DUR=30.0; BPM=120; BEAT=60/BPM; N=int(SR*DUR)
rng=np.random.default_rng(11)
L=np.zeros(N,np.float32); R=np.zeros(N,np.float32)
BUS={k:np.zeros((N,2),np.float32) for k in ("kick","bass","pad","stab","hat","perc","fx")}
def tt(d): return np.arange(int(SR*d))/SR
def add(bus,sig,t0,g=1.0,pan=0.0):
    i=int(t0*SR)
    if i>=N or i<0: return
    j=min(N,i+len(sig)); seg=sig[:j-i]*g
    BUS[bus][i:j,0]+=seg*(1-max(0,pan)); BUS[bus][i:j,1]+=seg*(1+min(0,pan))
def lp(x,f,o=2): b,a=signal.butter(o,f/(SR/2),"low"); return signal.lfilter(b,a,x)
def hp(x,f,o=2): b,a=signal.butter(o,f/(SR/2),"high"); return signal.lfilter(b,a,x)
def bp(x,f1,f2,o=2): b,a=signal.butter(o,[f1/(SR/2),f2/(SR/2)],"band"); return signal.lfilter(b,a,x)
def kick():
    t=tt(0.42); f=48+110*np.exp(-t*38); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t*9.5); click=hp(rng.normal(0,1,len(t)),2500)*np.exp(-t*160)*0.15
    return (s+click).astype(np.float32)
def clap():
    t=tt(0.22); n=bp(rng.normal(0,1,len(t)),900,3500)
    env=np.exp(-t*26)+0.7*np.exp(-np.clip(t-0.012,0,None)*30)*(t>0.012)+0.5*np.exp(-np.clip(t-0.024,0,None)*30)*(t>0.024)
    return (n*env*0.5).astype(np.float32)
def hat(op=False):
    t=tt(0.20 if op else 0.05); n=hp(rng.normal(0,1,len(t)),7500,3); return (n*np.exp(-t*(16 if op else 110))).astype(np.float32)
def shaker():
    t=tt(0.09); n=bp(rng.normal(0,1,len(t)),5500,11000); return (n*np.exp(-t*50)).astype(np.float32)
def bassn(f,d):
    t=tt(d); s=np.sin(2*np.pi*f*t)+0.35*signal.sawtooth(2*np.pi*f*t)
    s=lp(s,320)*np.minimum(1,t/0.004)*np.exp(-t*3.2)*np.minimum(1,(d-t)/0.03)
    return s.astype(np.float32)
def stab(freqs,d=0.42):
    t=tt(d); s=0
    for f in freqs:
        s=s+np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*f*2.005*t)+0.25*np.sin(2*np.pi*f*3.01*t)
    s=lp(s/len(freqs),2600)*np.exp(-t*9)*np.minimum(1,t/0.003); return s.astype(np.float32)
def pad(freqs,d):
    t=tt(d); s=sum(np.sin(2*np.pi*f*t)+np.sin(2*np.pi*f*1.004*t) for f in freqs)/ (2*len(freqs))
    env=np.minimum(1,t/1.0)*np.minimum(1,(d-t)/0.8); return (lp(s,1400)*env).astype(np.float32)
def riser(d):
    t=tt(d); n=rng.normal(0,1,len(t)); out=np.zeros_like(n); k=12
    for i in range(k):
        a,b=int(i*len(t)/k),int((i+1)*len(t)/k); fc=300+9000*((i+1)/k)**2.2
        out[a:b]=bp(n,max(100,fc*0.5),min(18000,fc*1.5))[a:b]
    return (out*(t/d)**2.4*0.9).astype(np.float32)
def boom(): 
    t=tt(1.2); return (np.sin(2*np.pi*(38+30*np.exp(-t*6))*t)*np.exp(-t*3.4)).astype(np.float32)
hz=lambda m:440*2**((m-69)/12)
# Dm9-ish loop, 4 bars @120 = 8 s : Dm9 | Bbmaj7 | Fmaj7 | Am7
CH=[(38,[62,65,69,72,76]),(34,[58,62,65,69,72]),(41,[60,65,69,72,76]),(33,[57,60,64,67,72])]
BAR=4*BEAT
# arrangement by time: intro(0-4) groove(4-10) +stabs(10-17) +perc(17-24) outro(24-30)
nb=int(DUR/BAR)+1
for bar in range(nb):
    t0=bar*BAR; root,ch=CH[bar%4]
    if t0<DUR: add("pad",pad([hz(m-12) for m in ch[:4]],BAR+0.9),t0,0.55 if t0<4 else 0.42)
    drop=t0>=4.0
    for b in range(4):
        tb=t0+b*BEAT
        if drop: add("kick",kick(),tb,1.0)
        elif t0>=2.0: add("kick",kick(),tb,0.55)      # filtered-ish pre-drop pulse
        if drop and b in (1,3): add("perc",clap(),tb,0.55)
        for e in range(2):
            te=tb+e*BEAT/2
            if t0>=2.0 and e==1: add("hat",hat(op=True),te,0.22,0.15)
            elif drop and e==0: add("hat",hat(),te+BEAT/4,0.11,-0.2)
        if t0>=17.0:
            for q in range(4): add("perc",shaker(),tb+q*BEAT/4,0.05+0.02*(q%2),0.3*(-1)**q)
    if drop:
        # rolling off-beat bass (house): hits on the "&" and 16ths
        for i,on in enumerate([0,0,1,0, 0,1,1,0, 0,0,1,0, 0,1,0,1]):
            if on: add("bass",bassn(hz(root+(12 if i==15 else 0)),BEAT/4*1.6),t0+i*BEAT/4,0.9)
    if t0>=10.0 and t0<DUR-1.5:
        st=stab([hz(m) for m in ch[:4]],0.45)
        for pos in ([1.5,2.5,3.25] if bar%2==0 else [0.75,1.5,2.5]): add("stab",st,t0+pos*BEAT,0.32,0.25)
# risers + impacts into each cut
for tc in (4.0,10.0,17.0,24.0):
    add("fx",riser(1.9),tc-1.9,0.17); add("fx",boom(),tc,0.55)
    add("fx",hp(rng.normal(0,1,int(SR*0.5)),5000)*np.exp(-tt(0.5)*8)*0.07,tc,1.0)
# mix: sidechain pump on bass/pad/stab/fx-lite keyed to every beat
side=np.ones(N,np.float32)
for k in range(int(DUR/BEAT)+1):
    i=int(k*BEAT*SR)
    if i<N and k*BEAT>=4.0:
        m=min(N-i,int(0.30*SR)); tm=np.arange(m)/SR; side[i:i+m]=np.minimum(side[i:i+m],1-0.78*np.exp(-tm/0.10))
mix=np.zeros((N,2),np.float32)
mix+=BUS["kick"]*1.0+BUS["perc"]*0.8+BUS["hat"]*0.8
mix+=BUS["bass"]*0.95*side[:,None]+BUS["pad"]*0.9*side[:,None]+BUS["stab"]*side[:,None]*0.9+BUS["fx"]
# stab echo (dotted 8th)
d=int(BEAT*0.75*SR); e=np.zeros_like(mix); e[d:]=BUS["stab"][:-d]*0.35; e[2*d:]+=BUS["stab"][:-2*d]*0.18; mix+=e[:,::-1]*0.8
# keep 1–3 kHz clear for speech on the melodic bus is handled by low levels; gentle master LP/HP
mix=hp(mix,28,2,) if False else mix
b,a=signal.butter(2,28/(SR/2),"high"); mix=signal.lfilter(b,a,mix,axis=0)
b,a=signal.butter(2,15000/(SR/2),"low"); mix=signal.lfilter(b,a,mix,axis=0)
fi=np.minimum(1,np.arange(N)/(0.2*SR))[:,None]; fo=np.minimum(1,(N-np.arange(N))/(1.6*SR))[:,None]
mix=mix*fi*fo
mix=np.tanh(mix*1.15)/np.tanh(1.15); mix=mix/(np.max(np.abs(mix))+1e-9)*0.62
wavfile.write("/home/claude/vid/assets/music_house.wav",SR,(mix*32767).astype(np.int16))
rms=np.sqrt((mix**2).mean()); print("ok rms %.3f peak %.2f"%(rms,np.abs(mix).max()))
