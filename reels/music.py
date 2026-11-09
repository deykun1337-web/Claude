"""Own background music, synthesized from scratch (numpy) — no samples, no copyrighted tracks, unique per seed.

    python3 reels/music.py make <genre> <seconds> out.wav [--seed N] [--bpm N]
    python3 reels/music.py mix voice.wav music.wav out.wav [--bed -17]   # ducks music under the voice (sidechain)
    python3 reels/music.py pick <topic words…>                           # suggests a genre for the topic
    python3 reels/music.py demo                                          # 12 s of every genre → reels/state/music_demo/

Genres (what is trending in RU reels right now, re-made as originals):
  phonk     — drift phonk: cowbell melody, distorted 808 with glides, hard kick, 130–150 bpm
  rap       — RU-rap / trap beat: dark minor piano-bell loop, 808, rolling hats, 140 bpm half-time
  lofi      — lo-fi: jazzy 7th chords, dusty kick/snare, vinyl crackle, 80–90 bpm (calm explainers)
  hyperpop  — bright supersaw chords, fast arps, punchy drums, 160 bpm (energetic lists / news)
  cinematic — pads, low booms, ticking pulse (myths, reveals, «как это работает»)
  funk      — brazilian funk / «бразильский фонк»: tamborzão-like pattern, cowbell, 808, 128 bpm
Each run picks key, progression, melody, groove and sound details from the seed, so two reels never share a track.
"""
import os, subprocess, sys, wave
import numpy as np

SR = 44100
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}


def hz(midi): return 440.0 * 2 ** ((midi - 69) / 12)


def env(n, a=0.005, d=0.1, s=0.6, r=0.05, hold=None):
    hold = n if hold is None else min(n, hold); e = np.zeros(n)
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    k = np.arange(n)
    e = np.where(k < A, k / max(A, 1), np.where(k < A + D, 1 - (1 - s) * (k - A) / max(D, 1), s))
    rel = k >= hold
    e[rel] = e[hold - 1 if hold > 0 else 0] * np.clip(1 - (k[rel] - hold) / max(R, 1), 0, 1)
    return e


def saw(f, n, cutoff=6000, phase=0.0):
    """band-limited saw: harmonics only up to the cutoff (built-in low-pass, no aliasing)"""
    t = np.arange(n) / SR; out = np.zeros(n); kmax = int(max(1, min(cutoff, SR / 2 - 500) // max(f, 1)))
    for k in range(1, min(kmax, 60) + 1): out += np.sin(2 * np.pi * k * f * t + phase * k) / k
    return out * 0.55


def square(f, n, cutoff=5000):
    t = np.arange(n) / SR; out = np.zeros(n); kmax = int(max(1, cutoff // max(f, 1)))
    for k in range(1, min(kmax, 40) + 1, 2): out += np.sin(2 * np.pi * k * f * t) / k
    return out * 0.7


def sine(f, n, ph=0.0): return np.sin(2 * np.pi * f * np.arange(n) / SR + ph)


def lp(x, a=0.15):
    """cheap 1-pole low-pass via cumulative trick (vectorized enough for short buffers)"""
    y = np.empty_like(x); acc = 0.0
    for i in range(0, len(x), 256):
        seg = x[i:i + 256]; o = np.empty_like(seg)
        for j, v in enumerate(seg): acc += a * (v - acc); o[j] = acc
        y[i:i + 256] = o
    return y


def noise(n, rng): return rng.uniform(-1, 1, n)


# ---------------------------------------------------------------- drums
def kick(rng, punch=1.0, n=None):
    n = n or int(0.35 * SR); t = np.arange(n) / SR
    f = 45 + 120 * np.exp(-t * 28) * punch; ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 7) + 0.25 * noise(n, rng) * np.exp(-t * 300)
    return np.tanh(x * 1.6)


def snare(rng, tone=190, n=None):
    n = n or int(0.25 * SR); t = np.arange(n) / SR
    body = sine(tone, n) * np.exp(-t * 25); nz = noise(n, rng); nz = nz - lp(nz, 0.25)
    return np.tanh((0.5 * body + 0.8 * nz * np.exp(-t * 16)) * 1.3)


def clap(rng):
    n = int(0.22 * SR); t = np.arange(n) / SR; nz = noise(n, rng); nz = nz - lp(nz, 0.3); e = np.zeros(n)
    for o in (0, 0.011, 0.022): e += np.exp(-np.clip(t - o, 0, None) * 60) * (t >= o)
    return nz * (e * 0.5 + np.exp(-t * 14) * 0.5)


def hat(rng, open_=False):
    n = int((0.18 if open_ else 0.05) * SR); t = np.arange(n) / SR; nz = noise(n, rng); nz = nz - lp(nz, 0.6)
    return nz * np.exp(-t * (14 if open_ else 70)) * 0.5


def cowbell(f, n):
    t = np.arange(n) / SR; x = square(f, n, 4000) + square(f * 1.48, n, 4000)
    return np.tanh(x * np.exp(-t * 9) * 1.2) * 0.45


def bass808(f0, n, glide_to=None, drive=2.2):
    t = np.arange(n) / SR
    f = np.full(n, f0) if glide_to is None else f0 + (glide_to - f0) * np.clip(t / 0.09, 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 1.6) * np.clip(t / 0.004, 0, 1)
    return np.tanh(x * drive) / np.tanh(drive)


def tamb(rng):
    n = int(0.09 * SR); t = np.arange(n) / SR; nz = noise(n, rng); nz = nz - lp(nz, 0.7)
    return nz * np.exp(-t * 35) * 0.4


# ---------------------------------------------------------------- harmony
PROGS_MINOR = [[0, 8, 3, 10], [0, 5, 8, 7], [0, 3, 8, 7], [0, 10, 8, 7], [0, 8, 10, 0], [0, 5, 3, 7]]
SCALE_MINOR = [0, 2, 3, 5, 7, 8, 10]
PHRYG = [0, 1, 3, 5, 7, 8, 10]


def chord(root, kind="m", sev=False):
    c = [root, root + (3 if kind == "m" else 4), root + 7]
    if sev: c.append(root + (10 if kind == "m" else 11))
    return c


def quality_for(deg):   # natural minor diatonic triads
    return {0: "m", 2: "dim", 3: "M", 5: "m", 7: "m", 8: "M", 10: "M"}.get(deg % 12, "m")


class Track:
    def __init__(self, seconds, bpm, rng):
        self.n = int(seconds * SR); self.L = np.zeros(self.n); self.R = np.zeros(self.n); self.bpm = bpm; self.rng = rng
        self.beat = 60 / bpm

    def add(self, x, t, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.n or i < 0: return
        x = x[: self.n - i] * gain
        self.L[i:i + len(x)] += x * (1 - max(0, pan)); self.R[i:i + len(x)] += x * (1 + min(0, pan))

    def steps(self, div=4):   # yields (step_index, time) over the whole track in 1/div beat steps
        k = 0
        while k * self.beat / div < self.n / SR:
            yield k, k * self.beat / div; k += 1

    def render(self):
        st = np.stack([self.L, self.R], 1)
        pk = np.max(np.abs(st)) or 1; st = np.tanh(st / pk * 1.4) * 0.9   # glue / soft clip
        fade = int(0.8 * SR); st[-fade:] *= np.linspace(1, 0, fade)[:, None]; st[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
        return st


def pad(freqs, n, rng, cutoff=2500, det=0.12):
    out = np.zeros(n)
    for f in freqs:
        for d in (-det, 0, det): out += saw(f * 2 ** (d / 12), n, cutoff, rng.uniform(0, 6))
    return out / (len(freqs) * 3) * env(n, 0.25, 0.4, 0.8, 0.4, n - int(0.4 * SR))


def bell(f, n, bright=1.0):
    t = np.arange(n) / SR
    x = sine(f, n) + 0.5 * bright * sine(f * 2.76, n) * np.exp(-t * 6) + 0.25 * bright * sine(f * 5.4, n) * np.exp(-t * 10)
    return x * np.exp(-t * 3.2) * np.clip(t / 0.002, 0, 1) * 0.5


def piano(f, n):
    t = np.arange(n) / SR; x = np.zeros(n)
    for k, a in enumerate((1, 0.45, 0.25, 0.12, 0.06), 1): x += a * sine(f * k * (1 + 0.0004 * k * k), n) * np.exp(-t * (2.2 + k * 0.9))
    return x * np.clip(t / 0.003, 0, 1) * 0.45


# ---------------------------------------------------------------- genres
def g_phonk(T, key, rng):
    prog = PROGS_MINOR[rng.integers(len(PROGS_MINOR))]; bar = 4 * T.beat
    mel = [rng.choice([0, 3, 5, 7, 10, 12, 8, 7]) for _ in range(16)]
    k_pat = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0] if rng.random() < 0.5 else [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    for k, t in T.steps(4):
        s = k % 16; b = int(t // bar)
        root = key + prog[b % 4]
        if k_pat[s]: T.add(kick(T.rng, 1.2), t, 0.9)
        if s in (4, 12): T.add(snare(T.rng, 200), t, 0.55); T.add(clap(T.rng), t, 0.35)
        T.add(hat(T.rng), t, 0.16 + 0.06 * (s % 2 == 0), pan=0.2)
        if b >= 1 and (s % 2 == 0 or rng.random() < 0.25):     # cowbell melody enters after the intro bar
            T.add(cowbell(hz(root + 60 + mel[s]), int(0.22 * SR)), t, 0.32, pan=-0.15)
        if k_pat[s]:
            gl = hz(root + 24 + 12) if rng.random() < 0.2 else None
            T.add(bass808(hz(root + 24), int(T.beat * 1.6 * SR), gl, 3.0), t, 0.75)


def g_rap(T, key, rng):
    prog = PROGS_MINOR[rng.integers(len(PROGS_MINOR))]; bar = 4 * T.beat
    arp = [rng.choice([0, 3, 7, 12, 10, 15]) for _ in range(8)]
    for k, t in T.steps(4):
        s = k % 32; b = int(t // bar); root = key + prog[b % 4]
        if s in (0, 10, 19, 22): T.add(kick(T.rng), t, 0.9); T.add(bass808(hz(root + 24), int(T.beat * 2 * SR), hz(root + 24 + (rng.choice([0, 0, 12, -2]))), 2.0), t, 0.7)
        if s in (8, 24): T.add(snare(T.rng, 180), t, 0.5); T.add(clap(T.rng), t, 0.45)
        roll = (s // 4) in (3, 7) and rng.random() < 0.6
        if roll:
            for r in range(3): T.add(hat(T.rng), t + r * T.beat / 12, 0.14, pan=0.25)
        elif s % 2 == 0: T.add(hat(T.rng), t, 0.17, pan=0.25)
        if s % 4 == 0: T.add(bell(hz(root + 72 + arp[(k // 4) % 8]), int(1.2 * SR), 0.8), t, 0.28, pan=-0.2)
        if s % 16 == 0: T.add(pad([hz(x + 48) for x in chord(root)], int(bar * SR), rng, 1400), t, 0.22)


def g_lofi(T, key, rng):
    prog = [[0, 7], [5, 0], [8, 10], [3, 7]][rng.integers(4)]
    progs = [0, 5, 10, 3] if rng.random() < 0.5 else [0, 8, 5, 7]; bar = 4 * T.beat
    for k, t in T.steps(4):
        s = k % 16; b = int(t // bar); root = key + progs[b % 4]; sw = (T.beat / 4) * 0.18 * (s % 2)
        if s in (0, 7, 10): T.add(lp(kick(T.rng, 0.7), 0.3), t + sw, 0.7)
        if s in (4, 12): T.add(lp(snare(T.rng, 170), 0.35), t + sw, 0.38)
        if s % 2 == 0: T.add(lp(hat(T.rng), 0.5), t + sw, 0.12)
        if s == 0:
            for j, f in enumerate(chord(root, quality_for(progs[b % 4]) if quality_for(progs[b % 4]) != "dim" else "m", True)):
                T.add(piano(hz(f + 60), int(bar * SR)), t + j * 0.012, 0.32)
            T.add(sine(hz(root + 36), int(bar * 0.9 * SR)) * env(int(bar * 0.9 * SR), 0.01, 0.3, 0.5, 0.2), t, 0.35)
        if s in (6, 14) and rng.random() < 0.5: T.add(piano(hz(root + 72 + rng.choice([3, 7, 10, 14])), int(0.8 * SR)), t + sw, 0.18)
    crackle = np.zeros(T.n); idx = T.rng.integers(0, T.n, T.n // 2500); crackle[idx] = T.rng.uniform(-0.5, 0.5, len(idx))
    T.L += crackle * 0.25 + noise(T.n, T.rng) * 0.002; T.R += np.roll(crackle, 37) * 0.25 + noise(T.n, T.rng) * 0.002


def g_hyperpop(T, key, rng):
    prog = PROGS_MINOR[rng.integers(len(PROGS_MINOR))]; bar = 4 * T.beat; key += 12 if rng.random() < 0.5 else 0
    for k, t in T.steps(4):
        s = k % 16; b = int(t // bar); deg = prog[b % 4]; root = key + deg; q = "m" if quality_for(deg) != "M" else "M"
        if s in (0, 6, 8, 11): T.add(kick(T.rng, 1.3), t, 0.85)
        if s in (4, 12): T.add(snare(T.rng, 230), t, 0.5); T.add(clap(T.rng), t, 0.4)
        T.add(hat(T.rng, s % 4 == 2), t, 0.15, pan=0.3 if s % 2 else -0.3)
        if s % 2 == 0:
            c = chord(root, q) + [root + 12]
            T.add(saw(hz(c[(k // 2) % 4] + 72), int(T.beat / 2 * SR), 7000) * env(int(T.beat / 2 * SR), 0.003, 0.08, 0.3, 0.03), t, 0.22, pan=0.4 * (-1) ** (k // 2))
        if s == 0: T.add(pad([hz(x + 60) for x in chord(root, q)], int(bar * SR), rng, 5000, 0.2), t, 0.3)
        if s % 4 == 0: T.add(bass808(hz(root + 36), int(T.beat * SR), None, 1.5), t, 0.5)


def g_cinematic(T, key, rng):
    prog = [0, 8, 3, 10] if rng.random() < 0.5 else [0, 5, 8, 7]; bar = 4 * T.beat
    for k, t in T.steps(4):
        s = k % 16; b = int(t // bar); root = key + prog[b % 4]
        if s == 0:
            T.add(pad([hz(x + 48) for x in chord(root, quality_for(prog[b % 4]) if quality_for(prog[b % 4]) != "dim" else "m")] + [hz(root + 36)], int(bar * 1.1 * SR), rng, 1800, 0.18), t, 0.5)
            if b % 2 == 0: T.add(kick(T.rng, 0.5, int(1.5 * SR)) * 1.0, t, 0.8)
        if s % 2 == 0: T.add(lp(hat(T.rng), 0.4), t, 0.07 + 0.05 * (b >= 2), pan=-0.3)
        if b >= 2 and s in (4, 12): T.add(lp(snare(T.rng, 120), 0.2), t, 0.35)
        if s % 4 == 0 and b >= 1: T.add(bell(hz(root + 72 + [0, 7, 3, 10][(k // 4) % 4]), int(1.5 * SR), 0.5), t, 0.15, pan=0.3)


def g_funk(T, key, rng):
    bar = 4 * T.beat; prog = PROGS_MINOR[rng.integers(len(PROGS_MINOR))]
    tam = [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0]
    mel = [rng.choice([0, 3, 7, 10, 12]) for _ in range(8)]
    for k, t in T.steps(4):
        s = k % 16; b = int(t // bar); root = key + prog[b % 4]
        if tam[s]: T.add(kick(T.rng, 1.1), t, 0.85); T.add(bass808(hz(root + 24), int(T.beat * SR), None, 3.5), t, 0.6)
        if s in (4, 12): T.add(clap(T.rng), t, 0.55)
        if s % 2 == 1: T.add(tamb(T.rng), t, 0.3, pan=0.3)
        if b >= 1 and s % 4 in (0, 3): T.add(cowbell(hz(root + 60 + mel[(k // 2) % 8]), int(0.18 * SR)), t, 0.3, pan=-0.2)


GENRES = {"phonk": (g_phonk, (130, 150)), "rap": (g_rap, (136, 146)), "lofi": (g_lofi, (78, 90)),
          "hyperpop": (g_hyperpop, (155, 165)), "cinematic": (g_cinematic, (90, 110)), "funk": (g_funk, (124, 132))}


def make(genre, seconds, out, seed=None, bpm=None):
    rng = np.random.default_rng(seed)
    fn, (lo, hi) = GENRES[genre]; bpm = bpm or int(rng.integers(lo, hi + 1))
    key = 33 + int(rng.integers(0, 12))       # A1..G#2 root region (+offsets in genres)
    T = Track(seconds + 1.0, bpm, rng); fn(T, key, rng); st = T.render()
    raw = out + ".raw.wav"; _wav(raw, st)
    # master: gentle EQ, stereo width, loudness for a background bed (-16 LUFS, voice will sit on top)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-t", f"{seconds:.2f}", "-af",
                    "highpass=f=30,equalizer=f=320:t=q:w=1:g=-2,equalizer=f=9000:t=q:w=1:g=1.5,acompressor=threshold=-14dB:ratio=2.5:attack=15:release=180,"
                    "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=44100", out], check=True)
    os.remove(raw); return {"genre": genre, "bpm": bpm, "key": key, "seed": seed, "out": out}


def _wav(path, st):
    d = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())


def mix(voice, music, out, bed=-17):
    """Music under the voice: level `bed` dB + sidechain ducking (music dips while someone speaks, swells in pauses)."""
    fc = (f"[1:a]volume={bed}dB,aformat=channel_layouts=stereo[m];[0:a]aformat=channel_layouts=stereo,asplit[v][sc];"
          "[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=420:makeup=1[d];"
          "[v][d]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-i", music, "-filter_complex", fc, out], check=True)


PICK = [("phonk", "машин авто тачк дрифт скорост танк воен лимит взлом хак жестк миллион деньг заработ"),
        ("rap", "систем комбайн агент автомат бизнес клиент продаж конкурент рилс вирал"),
        ("lofi", "учеба памятк скилл установ гайд инструкц спокойн утро дом бэкап код"),
        ("hyperpop", "топ список новост быстро тренд фишк лайфхак дизайн"),
        ("cinematic", "миф правд как работа истори секрет будущ замен страх"),
        ("funk", "смешн мем пятниц шутк вечерин кот")]


def pick(text):
    t = text.lower(); best = max(PICK, key=lambda p: sum(w in t for w in p[1].split()))
    return best[0] if any(w in t for w in best[1].split()) else "rap"


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k, d=None: (a[a.index(k) + 1] if k in a else d)
    if a[0] == "make":
        print(make(a[1], float(a[2]), a[3], int(opt("--seed")) if opt("--seed") else None, int(opt("--bpm")) if opt("--bpm") else None))
    elif a[0] == "mix":
        mix(a[1], a[2], a[3], float(opt("--bed", -17)))
    elif a[0] == "pick":
        print(pick(" ".join(a[1:])))
    elif a[0] == "demo":
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "music_demo"); os.makedirs(d, exist_ok=True)
        for g in GENRES: print(make(g, 12, os.path.join(d, g + ".wav"), seed=7))
