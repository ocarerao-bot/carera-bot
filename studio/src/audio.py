"""Original 30 s background track (synthesised, so no licensing issues)."""
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
DUR = 30.0
BPM = 108
BEAT = 60.0 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N, np.float32)
R = np.zeros(N, np.float32)


def add(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def stereo(sig, t0, gain=1.0, pan=0.0):
    add(L, sig, t0, gain * (1 - max(0, pan)))
    add(R, sig, t0, gain * (1 + min(0, pan)))


def tt(d):
    return np.arange(int(SR * d)) / SR


def kick():
    t = tt(0.32)
    f = 45 + 100 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 14)).astype(np.float32)


def snare():
    t = tt(0.22)
    n = rng.normal(0, 1, len(t))
    b, a = signal.butter(2, 1500 / (SR / 2), "high")
    n = signal.lfilter(b, a, n)
    return ((n * np.exp(-t * 24) * 0.8 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 28) * 0.5)).astype(np.float32)


def hat(open_=False):
    t = tt(0.12 if open_ else 0.045)
    n = rng.normal(0, 1, len(t))
    b, a = signal.butter(3, 7000 / (SR / 2), "high")
    n = signal.lfilter(b, a, n)
    return (n * np.exp(-t * (28 if open_ else 90))).astype(np.float32)


def pluck(freq, d=0.35, bright=1.0):
    t = tt(d)
    s = np.zeros_like(t)
    for k, amp in ((1, 1.0), (2, 0.5 * bright), (3, 0.28 * bright), (4, 0.12 * bright)):
        s += amp * np.sin(2 * np.pi * freq * k * t)
    return (s * np.exp(-t * 11)).astype(np.float32)


def bass(freq, d=0.5):
    t = tt(d)
    s = signal.sawtooth(2 * np.pi * freq * t) * 0.6 + np.sin(2 * np.pi * freq * t)
    b, a = signal.butter(2, 420 / (SR / 2), "low")
    s = signal.lfilter(b, a, s)
    return (s * np.exp(-t * 6.5)).astype(np.float32)


def pad(freqs, d):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.6)
    return (s * env).astype(np.float32) / len(freqs)


def whoosh(d=0.55):
    t = tt(d)
    n = rng.normal(0, 1, len(t))
    b, a = signal.butter(2, [900 / (SR / 2), 7000 / (SR / 2)], "band")
    n = signal.lfilter(b, a, n)
    env = (t / d) ** 2.2 * np.exp(-((t / d) - 1) ** 2 * 0)
    env[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return (n * env).astype(np.float32)


def hz(note):  # MIDI -> Hz
    return 440.0 * 2 ** ((note - 69) / 12)


# chords per bar: Am, F, C, G  (midi roots, triad)
CH = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]
BAR = 4 * BEAT
nbars = int(DUR / BAR) + 1

for bar in range(nbars):
    t0 = bar * BAR
    root, tri = CH[bar % 4]
    # pad
    for p, sgn in ((pad([hz(n) for n in tri], BAR + 0.4), 0),):
        stereo(p, t0, 0.07)
    full = t0 >= 2.2
    for b in range(4):
        tb = t0 + b * BEAT
        if full:
            stereo(kick(), tb, 0.85)
            if b in (1, 3):
                stereo(snare(), tb, 0.32)
        for e in range(2):
            te = tb + e * BEAT / 2
            if t0 >= 4.0:
                stereo(hat(open_=(e == 1)), te, 0.07 if e == 0 else 0.05, pan=0.2)
    # bass (eighth pattern)
    if t0 >= 4.0:
        pat = [1, 0, 0, 1, 0, 1, 0, 0]
        for i, on in enumerate(pat):
            if on:
                oct_ = 12 if i == 5 else 0
                stereo(bass(hz(root - 12 + oct_)), t0 + i * BEAT / 2, 0.42)
    # arp (16th notes)
    if t0 >= 4.0:
        idx = [0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 1, 2, 0, 1, 2, 1]
        for i, k in enumerate(idx):
            note = tri[k] + 12
            pan = -0.25 if i % 2 == 0 else 0.25
            stereo(pluck(hz(note), 0.3, 1.0), t0 + i * BEAT / 4, 0.10, pan=pan)
    # hook: rising pings
    if t0 < 4.0:
        for i in range(8):
            stereo(pluck(hz(tri[i % 3] + 24), 0.5, 0.6), t0 + i * BEAT / 2, 0.04 + 0.01 * bar, pan=(-1) ** i * 0.3)

# whooshes into each scene cut
for tc in (4.0, 10.0, 17.0, 24.0):
    w = whoosh(0.5)
    stereo(w, tc - 0.48, 0.30)

# simple glue: gentle low-pass, fade in/out, normalise
y = np.stack([L, R], axis=1)
b, a = signal.butter(2, 9500 / (SR / 2), "low")
y = signal.lfilter(b, a, y, axis=0)
fade_in = np.minimum(1, np.arange(N) / (0.15 * SR))[:, None]
fade_out = np.minimum(1, (N - np.arange(N)) / (1.3 * SR))[:, None]
y = y * fade_in * fade_out
y = y / (np.max(np.abs(y)) + 1e-9) * 0.5
wavfile.write("/home/claude/vid/assets/music.wav", SR, (y * 32767).astype(np.int16))
print("music ok", y.shape)
