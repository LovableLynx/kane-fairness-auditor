"""Cinematic soundtrack for cinematic.html, synthesised from scratch (no samples, no third-party audio).

    python cine_music.py out.wav

100 BPM in A minor. Tension intro, impacts on Kane's screenshots, a full beat for the stats and verdicts,
a breakdown for the fix, and a big final boom on the title card. Cue times match the cuts in cinematic.html.
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 40.0
N = int(SR * DUR)
BEAT = 0.6
rng = np.random.default_rng(11)
L = np.zeros(N)
R = np.zeros(N)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0:
        return
    n = min(len(sig), N - i)
    L[i:i + n] += gain * (1 - pan) * sig[:n]
    R[i:i + n] += gain * (1 + pan) * sig[:n]


def lowpass(x, cut):
    """One-pole low-pass; cut may be an array (a sweep)."""
    cut = np.broadcast_to(np.asarray(cut, float), x.shape)
    a = np.exp(-2 * np.pi * cut / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def ts(d):
    return np.arange(int(d * SR)) / SR


def saw(f, d, detune=0.0):
    t = ts(d)
    out = np.zeros_like(t)
    for k in range(1, 9):
        out += np.sin(2 * np.pi * f * (1 + detune) * k * t) / k
    return out


def env(n, a, r):
    e = np.ones(n)
    ai, ri = max(1, int(a * SR)), max(1, int(r * SR))
    e[:ai] = np.linspace(0, 1, ai)
    e[-ri:] *= np.linspace(1, 0, ri)
    return e


def kick(g=1.0, f0=150, f1=42, dec=0.28):
    t = ts(0.5)
    f = f1 + (f0 - f1) * np.exp(-t / 0.035)
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec)


def clap():
    t = ts(0.25)
    n = rng.standard_normal(len(t))
    n = n - lowpass(n, 900)
    return n * np.exp(-t / 0.06) * 0.35


def hat(g=0.08):
    t = ts(0.05)
    n = np.diff(rng.standard_normal(len(t) + 1))
    return n * np.exp(-t / 0.01) * g


def impact(g=1.0):
    """Trailer 'braam' hit: sub drop + low brass chord + noise burst, long tail."""
    d = 3.0
    t = ts(d)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.9)
    brass = sum(saw(hz(m), d, dt) for m, dt in ((33, 0), (45, .003), (52, -.003), (40, .002)))
    brass = lowpass(brass, 300 + 1500 * np.exp(-t / 0.35)) * np.exp(-t / 1.1) * 0.18
    noise = lowpass(rng.standard_normal(len(t)), 2500) * np.exp(-t / 0.12) * 0.6
    return g * (sub * 1.1 + brass + noise)


def whoosh(d=0.5, g=0.25):
    t = ts(d)
    n = rng.standard_normal(len(t))
    sweep = 300 + 5000 * (t / d) ** 2
    return lowpass(n, sweep) * np.sin(np.pi * t / d) ** 2 * g


def riser(d, g=0.3):
    t = ts(d)
    n = lowpass(rng.standard_normal(len(t)), 200 + 6000 * (t / d) ** 3)
    tone = np.sin(2 * np.pi * np.cumsum(110 + 660 * (t / d) ** 2) / SR) * 0.3
    return (n + tone) * (t / d) ** 2.5 * g


# --- pad: A minor drone, i - VI - III - VII over the whole piece, filtered dark ---
CH = [[45, 52, 57, 60], [41, 48, 53, 57], [48, 55, 60, 64], [43, 50, 55, 59]]
bar = 4 * BEAT
for b in range(int(DUR / bar) + 1):
    t0 = b * bar
    if t0 >= 32.4:
        break
    chord = CH[b % 4] if t0 >= 2.4 else [33, 45, 52]
    d = bar + 0.5
    for m in chord:
        e = env(int(d * SR), 0.4, 0.6)
        place(lowpass(saw(hz(m), d, -.004), 900) * e, t0, 0.05, -.4)
        place(lowpass(saw(hz(m), d, .004), 900) * e, t0, 0.05, .4)

# heartbeat sub pulse in the intro
for t0 in np.arange(0.0, 8.4, 1.2):
    place(kick(0.6, 80, 38, 0.2), t0)
    place(kick(0.35, 80, 38, 0.2), t0 + 0.25)

# ticking clock tension 2.4 - 17.4
for t0 in np.arange(2.4, 17.4, BEAT / 2):
    place(hat(0.05), t0, 1, .3 if int(t0 / (BEAT / 2)) % 2 else -.3)

# full beat 19.2 - 28.8: kick every beat, clap on 2 and 4, 16th hats, bass on 8ths
for i, t0 in enumerate(np.arange(19.2, 28.8 - 1e-6, BEAT)):
    place(kick(1.0), t0)
    if i % 2 == 1:
        place(clap(), t0)
    for k in range(4):
        place(hat(0.07 if k % 2 else 0.04), t0 + k * BEAT / 4, 1, .25 * (-1) ** k)
    root = [33, 29, 36, 31][int((t0 - 19.2) // bar) % 4]
    for k in range(2):
        bs = lowpass(saw(hz(root), 0.28), 500) * env(int(0.28 * SR), 0.005, 0.1)
        place(bs, t0 + k * BEAT / 2, 0.22)

# breakdown 28.8 - 32.4: half-time kick + riser into the PASS
for t0 in (28.8, 30.0):
    place(kick(0.7), t0)
place(riser(2.4), 28.8)
place(riser(1.8), 0.6, 0.6)          # intro riser into the first line
place(riser(1.8), 17.4, 0.8)         # riser into the beat

# whooshes into every cut
for c in (2.4, 4.8, 8.4, 11.4, 14.4, 17.4, 19.2, 20.4, 21.6, 22.8, 28.8, 30.0):
    place(whoosh(0.45, 0.22), c - 0.4, 1, .5 * np.sin(c))

# impacts
for t0, g in ((8.4, .8), (11.4, 1.0), (15.6, .8), (24.0, .9), (25.2, .9), (26.4, .6), (27.6, 1.0), (31.2, .8)):
    place(impact(g), t0)

# final: big boom and a held, opening chord under the title
place(impact(1.3), 32.4)
d = DUR - 32.4
for m, p in ((45, -.3), (52, .3), (57, -.2), (60, .2), (64, 0)):
    t = ts(d)
    e = env(len(t), 1.2, 3.0)
    place(lowpass(saw(hz(m), d, .002 * p), 400 + 1600 * np.minimum(1, t / 4)) * e, 32.4, 0.06, p)
# soft high bell motif on the title (A - C - E)
for k, m in enumerate((81, 84, 88, 93)):
    t = ts(2.5)
    place(np.sin(2 * np.pi * hz(m) * t) * np.exp(-t / 0.7) * 0.08, 34.2 + k * 0.6, 1, .3 * (-1) ** k)

# --- sound effects, synced to the picture ---
def click(g=0.18):
    t = ts(0.03)
    n = rng.standard_normal(len(t))
    return (n - lowpass(n, 2000)) * np.exp(-t / 0.004) * g


def shutter():
    a = click(0.5)
    b = click(0.35)
    out = np.zeros(int(0.12 * SR))
    out[:len(a)] += a
    out[int(0.07 * SR):int(0.07 * SR) + len(b)] += b
    return out


def zap(g=0.3):
    t = ts(0.35)
    f = 1800 * np.exp(-t / 0.05) + 90
    sq = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    return sq * np.exp(-t / 0.09) * g


def chime(g=0.16):
    t = ts(1.8)
    out = np.zeros_like(t)
    for m, k in ((88, 1), (95, .5), (100, .25)):
        out += k * np.sin(2 * np.pi * hz(m) * t) * np.exp(-t / 0.6)
    return out * g


def scribble(d=0.6, g=0.2):
    t = ts(d)
    n = rng.standard_normal(len(t))
    n = n - lowpass(n, 1500)
    return n * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * np.sin(np.pi * t / d) * g


def beep(f=1320, g=0.08):
    t = ts(0.12)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.05) * g


for start, text in ((5.0, "Geoffrey McCarthy"), (5.9, "Matthew Murray")):  # typing, 16 characters/s
    for i, ch in enumerate(text):
        if ch != " ":
            place(click(0.14 + 0.06 * rng.random()), start + i / 16, 1, rng.uniform(-.3, .3))
for t0 in (8.4, 11.4):
    place(shutter(), t0 + 0.02)          # Kane's screenshot
    place(beep(1320), t0 + 0.32)         # scan starts
    place(scribble(), t0 + 1.0)          # marker circle
place(beep(990, .1), 9.05)
place(beep(660, .1), 12.05)
for t0 in (15.6, 24.0, 25.2, 27.6):
    place(zap(), t0)
for t0 in (26.4, 31.2):
    place(chime(), t0)
for i in range(14):                      # 240 counting up
    place(click(0.12), 20.4 + i * 0.065)

st = np.stack([L, R], 1)
st = np.tanh(st * 1.2)
fade = np.ones(N)
fade[:int(.2 * SR)] = np.linspace(0, 1, int(.2 * SR))
fade[-int(3 * SR):] = np.linspace(1, 0, int(3 * SR))
st *= fade[:, None]
st *= 0.8 / np.abs(st).max()
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("wrote", sys.argv[1], DUR, "s")
