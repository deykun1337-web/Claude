"""Sound design for motion reels (synthesized, no samples): every on-screen event gets a sound.

    import sfx; sfx.track([("hit", 0.4), ("whoosh", 2.0), ("strike", 3.1), ("pop", 4.0), ("tick", 5.0), ("boom", 9.0)], total, "build/sfx.wav")
    hit    — soft click when a word lands        strike — swish of a crossing line
    whoosh — scene change                        pop    — chip / card spring
    tick   — UI tick (checkbox, keyframe)        boom   — low hit on the key moment / number
    type   — keyboard typing burst (0.6 s)       riser  — 1 s rise before the reveal
Mix it at about -8 dB under voice+music (ffmpeg amix), like in subagenty/kabanovo.
"""
import wave
import numpy as np

SR = 44100
_r = np.random.default_rng(9)


def _t(d): return np.arange(int(d * SR)) / SR


def hit():
    t = _t(0.06); return (np.sin(2 * np.pi * 2400 * t) * 0.4 + _r.uniform(-1, 1, len(t)) * 0.3) * np.exp(-t * 120)


def whoosh(d=0.45):
    t = _t(d); nz = np.convolve(_r.uniform(-1, 1, len(t)), np.ones(24) / 24, "same"); return nz * np.sin(np.pi * t / d) ** 2 * 1.4


def strike():
    t = _t(0.3); nz = _r.uniform(-1, 1, len(t)); nz -= np.convolve(nz, np.ones(8) / 8, "same"); return nz * np.sin(np.pi * t / 0.3) ** 3 * 0.8


def pop():
    t = _t(0.12); f = 500 + 1100 * t / 0.12; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)


def tick():
    t = _t(0.035); return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 160) * 0.6


def boom():
    t = _t(0.7); f = 40 + 70 * np.exp(-t * 14); return np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5))


def type_():
    out = np.zeros(int(0.6 * SR))
    for k in range(9):
        c = tick() * _r.uniform(0.4, 0.9); i = int((k * 0.065 + _r.uniform(0, 0.02)) * SR); out[i:i + len(c)] += c[: len(out) - i]
    return out


def riser(d=1.0):
    t = _t(d); nz = np.convolve(_r.uniform(-1, 1, len(t)), np.ones(6) / 6, "same"); return nz * (t / d) ** 2 * 0.9


KINDS = {"hit": (hit, 0.35), "whoosh": (whoosh, 0.5), "strike": (strike, 0.45), "pop": (pop, 0.4), "tick": (tick, 0.35),
         "boom": (boom, 0.8), "type": (type_, 0.4), "riser": (riser, 0.4)}


def track(events, total, out):
    n = int((total + 1) * SR); buf = np.zeros(n)
    for kind, t in events:
        fn, g = KINDS[kind]; x = fn() * g; i = int(max(0, t) * SR); buf[i:i + len(x)] += x[: max(0, n - i)]
    st = (np.clip(np.stack([buf, buf], 1), -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
    return out
