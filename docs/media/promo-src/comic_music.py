"""Comic-explainer soundtrack for comic.html, synthesised from scratch (no samples, no third-party audio).

    python comic_music.py out.wav

Same 150 BPM palette as the anime edit, arranged lighter so viewers can read: quiet under the story,
full chorus on the results and the PASS. Page flips, bubble pops, stamps, buzzer and chimes on the picture.
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 70.0
N = int(SR * DUR)
B = 0.4
rng = np.random.default_rng(5)
L = np.zeros(N)
R = np.zeros(N)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def ts(d):
    return np.arange(int(d * SR)) / SR


def place(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    n = min(len(sig), N - i)
    L[i:i + n] += g * (1 - pan) * sig[:n]
    R[i:i + n] += g * (1 + pan) * sig[:n]


def env(n, a, r):
    e = np.ones(n)
    ai, ri = max(1, int(a * SR)), max(1, int(r * SR))
    e[:ai] = np.linspace(0, 1, ai)
    e[-ri:] *= np.linspace(1, 0, ri)
    return e


def saw(f, d, h=10):
    t = ts(d)
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, h + 1))


def square(f, d):
    t = ts(d)
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 12, 2))


def smooth(x, k=6):
    return np.convolve(x, np.ones(k) / k, mode="same")


def kick(g=1.0):
    t = ts(0.35)
    f = 45 + 120 * np.exp(-t / 0.03)
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)


def snare(g=0.5):
    t = ts(0.25)
    n = rng.standard_normal(len(t))
    n = n - smooth(n, 8)
    return g * (n * np.exp(-t / 0.07) * 0.7 + np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05))


def hat(g=0.07):
    t = ts(0.05)
    n = np.diff(rng.standard_normal(len(t) + 1))
    return n * np.exp(-t / 0.012) * g


def crash(g=0.25):
    t = ts(1.6)
    n = np.diff(rng.standard_normal(len(t) + 1))
    return n * np.exp(-t / 0.5) * g


def taiko(g=1.0):
    t = ts(1.2)
    f = 55 + 70 * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    skin = smooth(rng.standard_normal(len(t)), 20) * np.exp(-t / 0.04) * 2
    return g * (body + skin)


def slash(g=0.35):
    d = 0.32
    t = ts(d)
    n = rng.standard_normal(len(t))
    hi = n - smooth(n, 4)
    return g * hi * np.sin(np.pi * t / d) ** 3 * (0.3 + t / d)


def chime(m=93, g=0.12):
    t = ts(1.2)
    return g * sum(k * np.sin(2 * np.pi * hz(m + iv) * t) for iv, k in ((0, 1), (7, .5), (12, .3))) * np.exp(-t / 0.4)


def riser(d, g=0.25):
    t = ts(d)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 1400 * (t / d) ** 2) / SR)
    n = rng.standard_normal(len(t)) * (t / d) ** 2
    return g * (tone * 0.5 + n * 0.4) * (t / d) ** 2


def buzzer(g=0.18):
    t = ts(0.45)
    return g * np.sign(np.sin(2 * np.pi * 110 * t)) * np.exp(-t / 0.2)


# chords: C D Bm Em (one per bar of 4 beats)
CH = [[48, 55, 60, 64], [50, 57, 62, 66], [47, 54, 59, 62], [52, 59, 64, 67]]
ROOT = [36, 38, 35, 40]
BAR = 4 * B


def bar_of(t):
    return int(t // BAR) % 4


def guitar(a, b, g=0.09):
    """Distorted power chords (root + fifth + octave), 8th-note chugs, double-tracked left/right."""
    t = a
    while t < b - 1e-6:
        r = ROOT[bar_of(t)] + 12
        d = B / 2
        sig = sum(saw(hz(m), d, 8) for m in (r, r + 7, r + 12))
        sig = np.tanh(sig * 2.2) * env(len(sig), 0.003, 0.03)
        place(sig, t, g, -.35)
        place(sig, t + 0.012, g * .9, .35)
        t += d


def bass(a, b, g=0.22):
    t = a
    while t < b - 1e-6:
        r = ROOT[bar_of(t)]
        sig = smooth(saw(hz(r), B / 2, 6), 3) * env(int(B / 2 * SR), 0.003, 0.05)
        place(sig, t, g)
        t += B / 2


def pad(a, b, g=0.035):
    t = a
    while t < b - 1e-6:
        for m in CH[bar_of(t)]:
            sig = saw(hz(m + 12), BAR + .2, 5) * env(int((BAR + .2) * SR), 0.2, 0.3)
            place(sig, t, g, .4 * np.sin(m))
        t += BAR


def drums(a, b, full=True):
    t, i = a, 0
    while t < b - 1e-6:
        if i % 2 == 0 or full:
            place(kick(1.0), t)
        if i % 2 == 1:
            place(snare(), t)
        place(hat(0.08), t)
        place(hat(0.05), t + B / 2)
        if full and i % 4 == 3:
            place(kick(0.6), t + B / 2)
        t += B
        i += 1


def arp(a, b, g=0.05):
    t = a
    while t < b - 1e-6:
        ch = CH[bar_of(t)]
        for k in range(8):
            m = ch[[0, 1, 2, 3, 2, 1, 2, 3][k]] + 24
            sig = square(hz(m), B / 2) * env(int(B / 2 * SR), 0.002, 0.12)
            place(sig, t + k * B / 2, g, .3 * (-1) ** k)
        t += BAR


# lead hook (G major pentatonic), 2 bars, repeated
HOOK = [(79, 1), (81, 1), (83, 2), (81, 1), (79, 1), (76, 2),
        (74, 1), (76, 1), (79, 2), (81, 1), (83, .5), (86, 1.5), (83, 2)]


def lead(a, b, g=0.06):
    t = a
    while t < b - 1e-6:
        for m, beats in HOOK:
            if t >= b - 1e-6:
                break
            d = beats * B
            tt = ts(d)
            vib = np.sin(2 * np.pi * 5.5 * tt) * 0.004 * np.minimum(1, tt / 0.2)
            sig = np.sin(2 * np.pi * np.cumsum(hz(m) * (1 + vib)) / SR)
            sig = sig + 0.4 * np.sin(2 * np.pi * np.cumsum(2 * hz(m) * (1 + vib)) / SR) + 0.2 * square(hz(m), d)
            place(sig * env(len(sig), 0.01, 0.06), t, g)
            t += d




def pop_sfx(g=0.22):
    t = ts(0.12)
    return g * np.sin(2 * np.pi * np.cumsum(500 + 900 * t / 0.12) / SR) * np.exp(-t / 0.03)


def flip(g=0.3):
    t = ts(0.3)
    n = rng.standard_normal(len(t))
    n = n - smooth(n, 3)
    return g * n * np.sin(np.pi * t / 0.3) ** 2 * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * t))


def boing(g=0.2):
    t = ts(0.6)
    f = 220 + 160 * np.sin(2 * np.pi * 7 * t) * np.exp(-t / 0.25)
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.25)


# --- arrangement (slow version: pages last 8-12 s so viewers can read) ---
OLDT = [0, 9.2, 16, 23.2, 31.2, 38, 44, 50]
NEWT = [0, 12, 21.2, 31.2, 42, 54, 62, 70]


def M(t):
    """Map a moment on the original 50 s timeline to the slowed-down 70 s one (same as comic.html)."""
    for i in range(7):
        if t < OLDT[i + 1] or i == 6:
            return NEWT[i] + (t - OLDT[i]) * (NEWT[i + 1] - NEWT[i]) / (OLDT[i + 1] - OLDT[i])


pad(0.0, 21.2, 0.035)
arp(0.0, 21.2, 0.03)
bass(4.0, 21.2, 0.14)
for i, t0 in enumerate(np.arange(4.0, 21.2, B)):
    if i % 2 == 0:
        place(kick(0.55), t0)
    place(hat(0.045), t0 + B / 2)
# Kane: hero build
pad(21.2, 31.2, 0.04)
arp(21.2, 31.2, 0.04)
bass(21.2, 31.2, 0.15)
for k in range(16):
    place(snare(0.12 + 0.3 * k / 16), 29.6 + k * 0.1)
place(riser(1.6), 29.6, 0.6)
# results + scoreboard: the band comes in, still gentle enough to read over
pad(31.2, 54.0, 0.04)
drums(31.2, 54.0)
guitar(31.2, 54.0, 0.045)
bass(31.2, 54.0)
lead(31.2, 42.0, 0.045)
# the fix: build into PASS
P = M(39.6)
pad(54.0, P, 0.05)
place(riser(P - 54.0), 54.0, 0.8)
for m in (55, 59, 62, 67, 71, 74):
    place(saw(hz(m), 2.4, 6) * env(int(2.4 * SR), 0.01, 1.2), P, 0.05, .3 * np.sin(m))
pad(P, 68.4, 0.04)
drums(P, 68.0)
guitar(P, 68.0, 0.05)
bass(P, 68.0)
lead(P, 68.0, 0.055)
for m in (43, 55, 59, 62, 67):
    place(saw(hz(m), 2.0, 6) * env(int(2.0 * SR), 0.005, 1.6), 68.0, 0.06)

# --- SFX on the picture (original cue times, mapped) ---
for h in OLDT[1:-1]:
    place(flip(), M(h) - 0.05)
for h in (1.2, 11.2, 17.8, 28.0, 28.4, 41.2, 46.6):
    place(pop_sfx(), M(h))
for h in (2.2, 2.6, 3.0):
    place(chime(96, .05), M(h))
place(boing(), M(5.0))
place(taiko(0.8), M(4.8), 0.9)
place(taiko(0.9), M(17.0), 0.9)
for h in (10.0, 10.6, 24.0, 24.6, 32.4, 33.2, 34.0):
    place(slash(0.25), M(h) - 0.05, 1, .4 * np.sin(h * 3))
place(kick(1.0), M(26.4))
place(chime(91, .1), M(26.4) + 0.05)
place(kick(1.0), M(27.2))
place(buzzer(0.14), M(27.2))
place(buzzer(0.1), M(32.6))
place(buzzer(0.1), M(33.4))
place(chime(93, .1), M(34.2))
place(taiko(1.0), P, 0.9)
place(crash(), P)
for k, m in enumerate((88, 91, 95, 100)):
    place(chime(m), P + k * 0.1)
    place(chime(m, .08), M(44.4) + k * 0.12)

st = np.stack([L, R], 1)
st = np.tanh(st * 1.1)
fade = np.ones(N)
fade[:int(.05 * SR)] = np.linspace(0, 1, int(.05 * SR))
fade[-int(1.8 * SR):] = np.linspace(1, 0, int(1.8 * SR))
st *= fade[:, None]
st *= 0.85 / np.abs(st).max()
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("wrote", sys.argv[1], DUR, "s")
