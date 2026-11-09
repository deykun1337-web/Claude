"""Builds the soundtrack: voice + synthesized music + SFX, and the per-frame mouth envelope."""
import json, os, subprocess, wave
VARIANT = os.environ.get('VARIANT', 'a')
import numpy as np
from timeline import *

SR = 48000
N = int(SR * DUR)
rng = np.random.default_rng(7)


def load_wav(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i] * gain


def tt(d):
    return np.arange(int(SR * d)) / SR


def lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


# ---------- SFX ----------
def thud(f0=150, f1=45, d=0.3):
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)


def pop():
    t = tt(0.08); f = 500 + 900 * t / 0.08
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.8


def whoosh(d=0.4):
    t = tt(d); n = rng.standard_normal(len(t))
    env = np.sin(np.pi * t / d) ** 2
    return lowpass(n, 0.12) * env * 2.2


def splash():
    t = tt(0.8); n = rng.standard_normal(len(t))
    out = lowpass(n, 0.25) * np.exp(-t * 6) * 1.6
    for _ in range(9):
        st = rng.uniform(0.02, 0.5); bt = tt(0.07)
        f = rng.uniform(350, 600) + 900 * bt / 0.07
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-bt * 45) * 0.5
        i = int(st * SR); out[i:i + len(b)] += b
    return out + 0.7 * np.pad(thud(110, 40, 0.3), (0, len(t) - int(0.3 * SR)))


def bling():
    t = tt(0.6)
    return (np.sin(2 * np.pi * 1760 * t) + 0.6 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 7) * 0.35


def slap():
    t = tt(0.12); n = rng.standard_normal(len(t))
    return np.diff(n, prepend=0) * np.exp(-t * 60) * 0.6 + 0.6 * thud(220, 80, 0.12)


def boing():
    t = tt(0.45); f = 220 + 70 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.6


def oink():
    out = np.zeros(int(SR * 0.5))
    for st, f0 in ((0.0, 210), (0.2, 250)):
        t = tt(0.18); f = f0 + 40 * np.sin(2 * np.pi * 9 * t)
        ph = np.cumsum(f) / SR; saw = 2 * (ph % 1) - 1
        g = saw * (1 + 0.7 * np.sin(2 * np.pi * 35 * t)) * np.sin(np.pi * t / 0.18)
        i = int(st * SR); out[i:i + len(g)] += lowpass(g, 0.3) * 0.7
    return out


# ---------- Music (120 BPM bouncy loop) ----------
def music():
    m = np.zeros(N); beat = 60 / (BPM if VARIANT == 'a' else BPM * 0.85)
    kick = thud(160, 48, 0.28)
    t = tt(0.15); clap = lowpass(rng.standard_normal(len(t)), 0.6) * np.exp(-t * 30) * 0.5
    t = tt(0.05); hat = np.diff(rng.standard_normal(len(t)), prepend=0) * np.exp(-t * 90) * 0.18
    roots = [57, 53, 60, 55] if VARIANT == 'a' else [62, 58, 65, 60]  # A F C G / Dm Bb F C
    nb = int(DUR / beat) + 1
    for b in range(nb):
        tb = b * beat
        place(m, kick, tb, 0.9)
        if b % 2 == 1:
            place(m, clap, tb, 1.0)
        place(m, hat, tb + beat / 2, 1.0); place(m, hat, tb, 0.6)
        root = roots[(b // 4) % 4]
        for k, off in enumerate((0, 0.75)):
            f = 440 * 2 ** ((root - 24 - 69 + (12 if k else 0)) / 12)
            tn = tt(beat * 0.45); ph = f * tn; saw = 2 * (ph % 1) - 1
            place(m, lowpass(saw, 0.08) * np.exp(-tn * 5) * 0.9, tb + off * beat)
        if b % 2 == 1:  # off-beat chord stab
            tn = tt(0.16); ch = 0
            for iv in (0, 3 if root == 57 else 4, 7):
                f = 440 * 2 ** ((root + iv - 69) / 12)
                ch = ch + np.sign(np.sin(2 * np.pi * f * tn))
            place(m, lowpass(ch, 0.15) * np.exp(-tn * 18) * 0.12, tb + beat / 2)
    return m


voice = np.zeros(N)
for i in range(len(VOICE_START)):
    place(voice, load_wav(f"build/t{i}.wav"), VOICE_START[i])

sfx = np.zeros(N)


def scratch():
    t = tt(0.45); f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.5 * t))
    n = rng.standard_normal(len(t))
    return lowpass(n, 0.3) * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 1.4


def riser(d=0.6):
    t = tt(d); f = 200 + 1400 * (t / d) ** 2
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + lowpass(rng.standard_normal(len(t)), 0.3) * 0.6) * (t / d) ** 2


def cash():
    t = tt(0.5)
    return (np.sin(2 * np.pi * 2093 * t) + np.sin(2 * np.pi * 3136 * t)) * np.exp(-t * 9) * 0.3




def psst():
    t = tt(0.7); n = np.diff(rng.standard_normal(len(t)), prepend=0)
    return n * np.exp(-t * 5) * 0.35 + lowpass(rng.standard_normal(len(t)), 0.4) * np.exp(-t * 8) * 0.3


def ding(n=1):
    out = np.zeros(int(SR * (0.2 * n + 0.5)))
    for k in range(n):
        t = tt(0.3); c = np.sin(2 * np.pi * (1320 + 220 * k) * t) * np.exp(-t * 14) * 0.5
        i = int(k * 0.07 * SR); out[i:i + len(c)] += c
    return out


def buzz():
    t = tt(0.35); f = 110
    return np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 6) * 0.25




def rip():
    t = tt(0.35); n = rng.standard_normal(len(t))
    return np.diff(n, prepend=0) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 40 * t))) * np.exp(-t * 7) * 0.5


def tick():
    t = tt(0.04)
    return np.sin(2 * np.pi * 2500 * t) * np.exp(-t * 120) * 0.5


def clink():
    t = tt(0.8)
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((2349, 6), (3520, 9), (4699, 12))) * 0.25


def drone(d):
    t = tt(d)
    x = np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 55.7 * t) + 0.3 * np.sin(2 * np.pi * 82.4 * t)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.4)
    return x * env * 0.35


def wind(d):
    t = tt(d); n = lowpass(rng.standard_normal(len(t)), 0.02)
    return n * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t)) * 3.0 * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.3)


S = VOICE_START; E = VOICE_END


def note(f, d, kind="pluck", g=1.0):
    t = tt(d)
    if kind == "pluck":
        x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t); env = np.exp(-t * 9)
    elif kind == "bell":
        x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t); env = np.exp(-t * 4)
    elif kind == "brass":
        ph = f * t; x = lowpass(2 * (ph % 1) - 1, 0.18) + 0.5 * lowpass(2 * ((ph * 1.005) % 1) - 1, 0.18)
        env = np.minimum(1, t / 0.04) * np.minimum(1, (d - t) / 0.25)
    else:
        x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 1.5 * t); env = np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.4)
    return x * env * g


def hz(m): return 440 * 2 ** ((m - 69) / 12)


def chime(level):
    """Gacha reveal chime: more notes and higher for rarer pulls."""
    seq = [[72, 76, 79], [74, 78, 81, 86], [76, 80, 83, 88, 91], [72, 76, 79, 84, 88, 91, 96]][level]
    out = np.zeros(int(SR * 2.2))
    for k, m in enumerate(seq):
        c = note(hz(m), 1.4, "bell", 0.28); i = int(k * 0.06 * SR); out[i:i + len(c)] += c[:len(out) - i]
    return out


def squish():
    t = tt(0.22); f = 260 * np.exp(-t * 9) + 60
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.9 + lowpass(rng.standard_normal(len(t)), 0.2) * np.exp(-t * 30) * 0.5


def rattle(d):
    t = tt(d); g = (np.sin(2 * np.pi * 14 * t) > 0.3).astype(float)
    return np.diff(rng.standard_normal(len(t)), prepend=0) * g * np.minimum(1, t / d) * 0.35


def drumroll(d):
    out = np.zeros(int(SR * d)); k = 0.0
    while k < d - 0.03:
        t = tt(0.06); hit = np.diff(rng.standard_normal(len(t)), prepend=0) * np.exp(-t * 60) * (0.25 + 0.6 * k / d)
        i = int(k * SR); out[i:i + len(hit)] += hit[:len(out) - i]; k += 0.045
    return out


def boom():
    return thud(90, 28, 1.4) * 1.3 + lowpass(rng.standard_normal(int(SR * 1.4)), 0.05) * np.exp(-tt(1.4) * 3) * 1.5



def coin():
    t = tt(0.25); f = rng.uniform(2800, 3600)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.48 * t)) * np.exp(-t * 18) * 0.25


def key():
    t = tt(0.03); return np.diff(rng.standard_normal(len(t)), prepend=0) * np.exp(-t * 200) * 0.35


def paper():
    t = tt(0.18); n = rng.standard_normal(len(t)); return (n - lowpass(n, 0.2)) * np.sin(np.pi * t / 0.18) * 0.25


S = VOICE_START; E = VOICE_END


def send():
    t = tt(0.25); f = 600 + 1800 * t / 0.25
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) * 0.3 + lowpass(rng.standard_normal(len(t)), 0.3) * np.exp(-t * 18) * 0.3


def recv():
    out = np.zeros(int(SR * 0.5))
    for k, f in enumerate((1318, 1760)):
        t = tt(0.3); c = np.sin(2 * np.pi * f * t) * np.exp(-t * 12) * 0.4; i = int(k * 0.09 * SR); out[i:i + len(c)] += c
    return out


def typing(d):
    out = np.zeros(int(SR * d)); k = 0.0
    while k < d - 0.05:
        c = key(); i = int(k * SR); out[i:i + len(c)] += c[:len(out) - i]; k += rng.uniform(0.05, 0.11)
    return out


for i in (1, 3, 5):
    place(sfx, typing(1.2), S[i] + 0.4, 0.8); place(sfx, send(), S[i] + 1.7, 0.8)
place(sfx, scratch(), S[2] - 0.05, 0.7); place(sfx, rip(), S[2] + 0.2, 0.6)
place(sfx, recv(), S[4] + 0.75, 0.9)
place(sfx, recv(), S[6] + 0.55, 0.9); place(sfx, cash(), S[6] + 0.7, 1.0)
for k in range(14): place(sfx, coin(), S[6] + 0.8 + k * 0.07, 0.6)
place(sfx, boing(), S[8] + 0.1, 0.5); place(sfx, bling(), S[9] + 1.2, 0.7)
for i in range(1, 10): place(sfx, whoosh(0.25), S[i] - 0.18, 0.35)

# music: night lo-fi groove 88 BPM; drops out on "Это наезд!" and the reading pause
mus = np.zeros(N); beat = 60 / 88
prog_ = [(62, 65, 69), (58, 62, 65), (55, 58, 62), (57, 61, 64)]
for b in range(int(DUR / beat) + 1):
    tb = b * beat; ch = prog_[(b // 4) % 4]
    if S[2] - 0.1 <= tb < S[3] - 0.2 or E[5] + 0.1 <= tb < S[6] + 0.5: continue
    place(mus, thud(120, 45, 0.28) * 0.8, tb)
    if b % 2: place(mus, lowpass(rng.standard_normal(int(SR * 0.12)), 0.45) * np.exp(-tt(0.12) * 28) * 0.4, tb)
    for h in (0, 0.5): place(mus, np.diff(rng.standard_normal(int(SR * 0.03)), prepend=0) * np.exp(-tt(0.03) * 100) * 0.12, tb + h * beat)
    if b % 4 == 0:
        for m in ch: place(mus, note(hz(m), beat * 4, "pad", 0.12), tb)
    place(mus, note(hz(ch[0] - 24), beat * 0.9, "pluck", 0.4), tb)
    if b % 2 == 0: place(mus, note(hz(ch[(b // 2) % 3] + 12), 0.4, "bell", 0.08), tb + beat * 0.5)

# Duck music under the voice
venv = np.abs(voice); k = int(SR * 0.15)
venv = np.convolve(venv, np.ones(k) / k, mode="same")
duck = 1 - 0.45 * np.clip(venv / 0.05, 0, 1)
fade = np.ones(N)  # no fade: the video loops on the beat
tt_ = np.arange(N) / SR
fade *= np.clip((DUR - tt_) / 1.0, 0, 1)
mix = voice * 1.0 + mus * 0.32 * duck * fade + sfx * 0.45
e = int(SR * 0.01); mix[:e] *= np.linspace(0, 1, e); mix[-e:] *= np.linspace(1, 0, e)
mix /= np.max(np.abs(mix)) / 0.89

with wave.open("build/mix.wav" if VARIANT == "a" else f"build/mix_{VARIANT}.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

# Mouth envelope per video frame (from voice only)
env = []
for f in range(NFRAMES):
    a = int((f / FPS - 0.02) * SR); b = int((f / FPS + 0.045) * SR)
    seg = voice[max(a, 0):max(b, 1)]
    env.append(float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0)
env = np.array(env); ref = np.percentile(env[env > 0.005], 90) if (env > 0.005).any() else 1
mouth = np.clip(env / ref, 0, 1)
json.dump([round(float(x), 3) for x in mouth], open("build/mouth.json", "w"))
print("audio ok", round(float(np.max(np.abs(mix))), 2), "frames", len(mouth))
