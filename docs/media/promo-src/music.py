"""Original soundtrack for the promo video, synthesised from scratch (no samples, no third-party audio).

    python music.py music.wav [seconds]

120 BPM in A minor (Am - F - C - G, one chord per bar). Hits land on the video's stamp moments:
verdict stamps at 16.7 / 17.5 / 18.3 s and DEPLOY BLOCKED at 26.0 s.
"""
import sys
import wave

import numpy as np

SR = 44100
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 34.0
N = int(SR * DUR)
T = np.arange(N) / SR
BEAT = 0.5
rng = np.random.default_rng(7)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # one-pole filter; fine for 34 s
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += gain * sig[:n]


def env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r)
    return e


def tone(f, dur, detune=0.0, harmonics=6):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        out += np.sin(2 * np.pi * f * k * (1 + detune) * t) / k ** 2
    return out


def kick(gain=1.0, f0=120, f1=45, decay=0.25):
    t = np.arange(int(0.45 * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.04)
    return gain * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)


def hat():
    n = int(0.06 * SR)
    x = np.diff(rng.standard_normal(n + 1))
    return x * np.exp(-np.arange(n) / SR / 0.012) * 0.12


def hit():
    t = np.arange(int(1.2 * SR)) / SR
    body = kick(1.0, 90, 34, 0.5)
    noise = lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-t / 0.18) * 0.9
    out = noise
    out[:len(body)] += body
    return out


CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
ROOTS = [45, 41, 36, 43]

L = np.zeros(N)
R = np.zeros(N)
drums = np.zeros(N)
bass = np.zeros(N)

# pad: one chord per bar, slightly detuned left/right for width
bars = int(np.ceil(DUR / (4 * BEAT)))
for b in range(bars):
    t0, dur = b * 4 * BEAT, 4 * BEAT + 0.4
    for m in CHORDS[b % 4]:
        e = env(int(dur * SR), 0.35, 0.6)
        place(L, tone(hz(m), dur, -0.0025) * e, t0, 0.11)
        place(R, tone(hz(m), dur, +0.0025) * e, t0, 0.11)
        place(L, tone(hz(m + 12), dur, 0.004, 3) * e, t0, 0.03)
        place(R, tone(hz(m + 12), dur, -0.004, 3) * e, t0, 0.03)


def groove(a, b, kick_gain=0.8, hats=True, with_bass=True):
    t = a
    while t < b - 1e-6:
        beat = round((t - 0) / BEAT)
        place(drums, kick(kick_gain), t)
        if hats:
            place(drums, hat(), t + BEAT / 2)
        if with_bass:
            root = ROOTS[int(t // (4 * BEAT)) % 4]
            n = int(0.42 * SR)
            sig = np.sin(2 * np.pi * hz(root) * np.arange(n) / SR) * np.exp(-np.arange(n) / SR / 0.18)
            place(bass, sig, t, 0.35)
            place(bass, sig, t + BEAT / 2, 0.2)
        t += BEAT


groove(4.0, 15.5)
groove(15.5, 21.0, 0.9)
groove(21.0, 25.0, 0.0, hats=False)          # stat moment: pad + bass only
groove(25.0, 29.0, 0.95)
groove(29.0, 31.0, 0.5, hats=False, with_bass=False)

# riser into the first beat
n = int(1.6 * SR)
riser = lowpass(rng.standard_normal(n), 3000) * np.linspace(0, 1, n) ** 2 * 0.18
place(drums, riser, 2.4)

for t in (16.7, 17.5, 18.3):
    place(drums, hit(), t, 0.55)
place(drums, hit(), 26.0, 0.95)
place(drums, hit(), 29.0, 0.5)

mixL = L + drums + bass
mixR = R + drums + bass
st = np.stack([mixL, mixR], axis=1)
st = np.tanh(st * 1.3)
fade = np.ones(N)
fi, fo = int(0.3 * SR), int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
st *= fade[:, None]
st *= 0.7 / np.abs(st).max()  # leave headroom for AAC

with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("wrote", sys.argv[1], DUR, "s")
