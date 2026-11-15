"""CarEra theme: harder tech-house, 120 BPM, with a repeatable 2-bar melodic hook (sonic logo). 30 s, cuts at 4/10/17/24 s."""
import numpy as np
from scipy import signal
from scipy.io import wavfile
SR=44100; DUR=20.0; BPM=120; BEAT=60/BPM; S16=BEAT/4; N=int(SR*DUR)
rng=np.random.default_rng(23)
BUSES=("kick","bass","perc","hat","lead","pad","fx")
BUS={k:np.zeros((N,2),np.float32) for k in BUSES}
def tt(d): return np.arange(int(SR*d))/SR
def add(bus,sig,t0,g=1.0,pan=0.0):
    i=int(round(t0*SR))
    if i>=N or i<0: return
    j=min(N,i+len(sig)); seg=sig[:j-i]*g
    BUS[bus][i:j,0]+=seg*(1-max(0,pan)); BUS[bus][i:j,1]+=seg*(1+min(0,pan))
def flt(x,f,kind,o=2):
    f=np.atleast_1d(f)/(SR/2); b,a=signal.butter(o,f if len(f)>1 else f[0],kind); return signal.lfilter(b,a,x)
hz=lambda m:440*2**((m-69)/12)
def kick():
    t=tt(0.5); f=44+150*np.exp(-t*42); ph=2*np.pi*np.cumsum(f)/SR
    s=np.tanh(2.4*np.sin(ph))*np.exp(-t*8.5); s+=flt(rng.normal(0,1,len(t)),3000,"high")*np.exp(-t*220)*0.25
    return (s*0.85).astype(np.float32)
def snare(d=0.2,g=1.0):
    t=tt(d); n=flt(rng.normal(0,1,len(t)),1800,"high")*np.exp(-t*30)*0.6+np.sin(2*np.pi*(190+60*np.exp(-t*40))*t)*np.exp(-t*34)*0.5
    return (n*g).astype(np.float32)
def clap():
    t=tt(0.25); n=flt(rng.normal(0,1,len(t)),[1000,4200],"band")
    env=np.exp(-t*24)+0.8*np.exp(-np.clip(t-0.011,0,None)*32)*(t>0.011)+0.6*np.exp(-np.clip(t-0.022,0,None)*32)*(t>0.022)
    return (n*env*0.65).astype(np.float32)
def hat(op=False,acc=1.0):
    t=tt(0.22 if op else 0.05); n=flt(rng.normal(0,1,len(t)),8000,"high",3); return (n*np.exp(-t*(15 if op else 120))*acc).astype(np.float32)
def bassn(m,d,drive=1.0):
    f=hz(m); t=tt(d); s=0.8*np.sin(2*np.pi*f*t)+0.5*signal.sawtooth(2*np.pi*f*t)
    s=flt(s,260+700*drive*np.exp(-t*30),"low") if False else flt(s,520,"low")
    s=np.tanh(1.8*s)*np.minimum(1,t/0.003)*np.minimum(1,(d-t)/0.02)*np.exp(-t*4.0); return s.astype(np.float32)
def lead(m,d,bright=1.0,octv=0):
    f=hz(m+12*octv); t=tt(d); s=0
    for dt in (-0.0035,0,0.0035): s=s+signal.sawtooth(2*np.pi*f*(1+dt)*t)
    s=s/3+0.35*np.sin(2*np.pi*f*0.5*t); s=flt(s,2200+2600*bright,"low")
    env=(0.25+0.75*np.exp(-t*7))*np.minimum(1,t/0.004)*np.minimum(1,(d-t)/0.04); return (s*env).astype(np.float32)
def chord_saw(ms,d):
    t=tt(d); s=0
    for m in ms:
        for dt in (-0.004,0.004): s=s+signal.sawtooth(2*np.pi*hz(m)*(1+dt)*t)
    s=flt(s/(2*len(ms)),2400,"low"); env=np.minimum(1,t/0.05)*np.minimum(1,(d-t)/0.06); return (s*env).astype(np.float32)
def riser(d,g=1.0):
    t=tt(d); n=rng.normal(0,1,len(t)); out=np.zeros_like(n); k=16
    for i in range(k):
        a,b=int(i*len(t)/k),int((i+1)*len(t)/k); fc=250+10000*((i+1)/k)**2.0
        out[a:b]=flt(n,[max(80,fc*0.5),min(19000,fc*1.5)],"band")[a:b]
    pitch=np.sin(2*np.pi*np.cumsum(200+1400*(t/d)**2)/SR)*0.25
    return ((out*0.9+pitch)*(t/d)**2.2*g).astype(np.float32)
def rev_crash(d=1.0):
    t=tt(d); n=flt(rng.normal(0,1,len(t)),4500,"high"); return (n*(t/d)**3).astype(np.float32)
def boom():
    t=tt(1.4); return (np.sin(2*np.pi*(36+34*np.exp(-t*7))*t)*np.exp(-t*3.0)).astype(np.float32)
def crash():
    t=tt(1.6); n=flt(rng.normal(0,1,len(t)),5500,"high"); return (n*np.exp(-t*3.2)).astype(np.float32)
# --- musical material ---
CH=[(38,[62,65,69,72]),(34,[58,62,65,69]),(41,[60,65,69,72]),(36,[60,64,67,72])]   # Dm | Bb | F | C
HOOK=[(0,74,2),(3,74,1),(6,77,2),(10,74,1),(12,81,3),(16,79,2),(19,77,1),(22,74,2),(26,72,1),(28,74,4)]  # 2 bars, D-minor pentatonic
BAR=4*BEAT
def hook(t0,g=1.0,octv=0,bright=1.0,pan=0.0):
    for (p,m,l) in HOOK: add("lead",lead(m,l*S16*1.05,bright,octv),t0+p*S16,0.34*g,pan)
# --- arrangement ---
# 0-3.5 hook teaser (bright pluck, delayed) over pad + riser, 3.5-4 dropout (silence) then DROP at 4.0
add("fx",boom(),0.0,0.6); add("fx",crash(),0.0,0.2)
SEG=[(0.0,4.0),(4.0,8.0),(8.0,12.0),(12.0,16.0),(16.0,20.0)]
def sec(t):
    for i,(a,b) in enumerate(SEG):
        if a<=t<b: return i
    return 4
nbeats=int(DUR/BEAT)
for k in range(nbeats):
    tb=k*BEAT
    if tb>=DUR-0.01: continue
    s=sec(tb); bar=int(tb//BAR); ch=CH[bar%4]
    add("kick",kick(),tb,1.0)
    if k%2==1: add("perc",clap(),tb,0.7); add("perc",snare(0.18,0.35),tb,0.6)
    add("hat",hat(True),tb+BEAT/2,0.30,0.15)
    for q in (1,3): add("hat",hat(False,0.8 if q==3 else 0.5),tb+q*S16,0.16,-0.2)
    if s>=1:
        add("hat",hat(False,0.9),tb,0.12,-0.1); add("hat",hat(False,0.7),tb+2*S16,0.12,0.1)
    # rumble tail after kick (tech-house low swell)
    # rolling 16th bass
    pat=[1,0,1,1, 1,0,1,0, 1,1,0,1, 1,0,1,1] if s>=1 else [1,0,0,1, 0,1,0,0, 1,0,0,1, 0,1,0,1]
    for q in range(4):
        if pat[(k%4)*4+q]:
            note=ch[0]+(12 if (q==3 and k%4==3) else 0)+(7 if (s>=2 and q==2 and k%4==1) else 0)
            add("bass",bassn(note,S16*1.7),tb+q*S16,0.9)
    # chords/pad
    if k%4==0:
        add("pad",chord_saw([m-12 if s<2 else m for m in ch[1]],BAR+0.1),tb,0.20 if s<2 else 0.28)
# hook phrases
for bar2 in range(0,int(DUR//(2*BAR))+1):
    t0=bar2*2*BAR
    if t0>=DUR-2.0: break
    s=sec(t0)
    if s==0: hook(t0,1.05,0,1.2,0.0)                     # frame-0 hook: full melody immediately
    elif s==1: hook(t0,0.55,-1,0.6,-0.2)                 # 1974: lower/softer -> room for voice
    elif s==2: hook(t0,1.0,0,1.0,0.1)
    elif s==3: hook(t0,1.0,0,1.2,-0.1); hook(t0,0.5,1,1.3,0.3)
    else: hook(t0,1.05,0,1.2,0.0); hook(t0,0.45,1,1.3,0.25)
# fills: short accelerating snare roll + riser into each cut, boom on the cut
for tc in (4.0,8.0,12.0,16.0):
    for dt in [-1.0,-0.75,-0.5,-0.375]+[-0.25+i*0.0625 for i in range(4)]:
        add("perc",snare(0.09,0.75*(1+dt/1.5)),tc+dt,1.0)
    add("fx",riser(1.2,0.30),tc-1.2,1.0); add("fx",rev_crash(0.6),tc-0.6,0.16)
    add("fx",boom(),tc,0.8); add("fx",crash(),tc,0.2)
add("fx",boom(),18.0,0.6); add("fx",crash(),18.0,0.18)
# --- mix ---
side=np.ones(N,np.float32)
for k in range(nbeats+1):
    i=int(k*BEAT*SR)
    if i<N and k*BEAT>=0.0:
        m=min(N-i,int(0.30*SR)); tm=np.arange(m)/SR; side[i:i+m]=np.minimum(side[i:i+m],1-0.88*np.exp(-tm/0.085))
dly=int(BEAT*0.75*SR)
def echo(x,fb=0.42,n=3):
    out=x.copy()
    for r in range(1,n+1):
        sh=dly*r; seg=np.zeros_like(x); seg[sh:]=x[:-sh]*(fb**r); out+=seg[:,::-1] if r%2 else seg
    return out
LEAD=echo(BUS["lead"]); PAD=BUS["pad"]
def master(lead_g,pad_g):
    mix=BUS["kick"]*1.0+BUS["perc"]*0.9+BUS["hat"]*0.85+BUS["fx"]*1.0
    mix+=BUS["bass"]*1.0*side[:,None]+PAD*pad_g*side[:,None]*(1)+LEAD*lead_g*(0.55+0.45*side[:,None])
    b,a=signal.butter(2,30/(SR/2),"high"); mix=signal.lfilter(b,a,mix,axis=0)
    b,a=signal.butter(2,16000/(SR/2),"low"); mix=signal.lfilter(b,a,mix,axis=0)
    fi=np.minimum(1,np.arange(N)/(0.01*SR))[:,None]; fo=np.minimum(1,(N-np.arange(N))/(0.12*SR))[:,None]
    mix=np.tanh(mix*1.05)/np.tanh(1.05)*fi*fo
    return mix/(np.max(np.abs(mix))+1e-9)*0.52
for name,lg,pg in (("music_v7",1.0,1.0),("music_v7_voicebed",0.35,0.45)):
    m=master(lg,pg); wavfile.write(f"/home/claude/vid/assets/{name}.wav",SR,(m*32767).astype(np.int16))
    print(name,"rms %.3f peak %.2f"%(np.sqrt((m**2).mean()),np.abs(m).max()))
