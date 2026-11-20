"""Anime-opening style soundtrack for anime.html, synthesised from scratch (no samples, no third-party audio).

    python anime_music.py out.wav

150 BPM (0.4 s per beat) in G major, "royal road" progression C - D - Bm - Em. Intro, driving verse,
impact break, hero build, full chorus with a lead hook, bridge, PASS fanfare and outro. SFX on every cut.
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = 40.0
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


# --- arrangement ---
arp(0.0, 3.2, 0.04)
place(riser(2.0), 1.2, 0.8)
pad(3.2, 11.2)
drums(3.2, 11.2, full=False)
guitar(3.2, 11.2, 0.07)
bass(3.2, 11.2)
# break 11.2-13.6: taiko + menacing rumble ("gogogo")
t = ts(2.4)
place(np.sin(2 * np.pi * 41 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * env(len(t), 0.1, 0.4), 11.2, 0.25)
# build 13.6-18.4: hero theme, snare roll into the chorus
pad(13.6, 18.4, 0.04)
arp(13.6, 18.4, 0.05)
bass(13.6, 18.4, 0.18)
for k in range(24):
    place(snare(0.15 + 0.35 * k / 24), 16.0 + k * 0.1)
place(riser(2.4), 16.0, 0.7)
# chorus 18.4-27.2
pad(18.4, 27.2, 0.04)
drums(18.4, 27.2)
guitar(18.4, 27.2, 0.08)
bass(18.4, 27.2)
lead(18.4, 27.2, 0.07)
# bridge 27.2-31.2
pad(27.2, 31.2, 0.05)
arp(27.2, 31.2, 0.05)
for k in range(5):
    place(kick(0.7), 27.2 + k * 2 * B)
place(riser(2.0), 29.2, 0.8)
# PASS fanfare 31.2-33.6
for m in (55, 59, 62, 67, 71, 74):
    sig = saw(hz(m), 2.4, 6) * env(int(2.4 * SR), 0.01, 1.2)
    place(sig, 31.2, 0.05, .3 * np.sin(m))
drums(31.2, 33.6)
# outro 33.6-40: hook again, then a final chord
pad(33.6, 39.0, 0.04)
drums(33.6, 38.4)
guitar(33.6, 38.4, 0.07)
bass(33.6, 38.4)
lead(33.6, 38.4, 0.07)
for m in (43, 55, 59, 62, 67):
    place(saw(hz(m), 2.0, 6) * env(int(2.0 * SR), 0.005, 1.6), 38.4, 0.06)

# --- hits and SFX on the picture ---
for h, g in ((0.8, .7), (2.0, .9), (4.0, 1.0), (11.2, 1.2), (12.0, .8), (12.8, .8), (14.4, 1.0), (26.0, .9), (31.2, 1.0), (33.6, .9), (38.4, 1.0)):
    place(taiko(g), h, 0.9)
for h in (3.2, 3.4, 3.6, 7.2, 8.4, 9.6, 22.4, 23.6, 24.8, 28.0):
    place(slash(), h - 0.05, 1, .4 * np.sin(h * 3))
for h in (9.0, 10.2):
    place(kick(0.9), h)            # stamp thud
for h in (3.2, 18.4, 31.2, 33.6):
    place(crash(), h)
place(buzzer(), 26.0)              # DEPLOY BLOCKED
for k, m in enumerate((88, 91, 95, 100)):
    place(chime(m), 31.2 + k * 0.1)
    place(chime(m, .09), 34.4 + k * 0.12)
for k in range(16):                # power level counting up
    place(hat(0.15), 18.6 + k * 0.1)

st = np.stack([L, R], 1)
st = np.tanh(st * 1.1)
fade = np.ones(N)
fade[:int(.05 * SR)] = np.linspace(0, 1, int(.05 * SR))
fade[-int(1.6 * SR):] = np.linspace(1, 0, int(1.6 * SR))
st *= fade[:, None]
st *= 0.85 / np.abs(st).max()
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("wrote", sys.argv[1], DUR, "s")
