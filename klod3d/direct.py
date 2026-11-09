"""Directing helpers for plan_*.py (pure Python): visemes, gaze, gestures, sentence-level cutting with reaction shots.

Usage inside a plan script (project dir is cwd, timeline + base imported):
    import direct
    D = direct.Director(VOICE_START, VOICE_END, SPK, WORDS, base.MOUTH)
    D.face(t, "p")      -> {"vis": 0..4, "b": 0/1, "g": "l|c|r"}   (texture v2r_/v2k_<expr>_<vis>_<b>_<g>)
    D.gesture(t, "p")   -> 0..1 arm/head accent on stressed words (use for arm raise / head nod)
    D.shots(close={"p": "r", "n": "k"}, wide="two", react=True) -> [(t_start, shot_name), ...]
    D.pause_before_punch(i) -> recommended extra silence (s) before the last line (punchline)
"""
import math, re

VOW = {"а": 2, "я": 2, "о": 3, "ё": 3, "у": 3, "ю": 3, "и": 1, "ы": 1, "е": 1, "э": 1}
LIPS = set("мбп")


class Director:
    def __init__(self, S, E, SPK, WORDS, MOUTH, fps_mouth=60):
        self.S, self.E, self.SPK, self.W, self.M, self.fm = S, E, SPK, WORDS, MOUTH, fps_mouth

    def line(self, t):
        return max([k for k in range(len(self.S)) if t >= self.S[k] - 0.05] or [0])

    def speaking(self, t, spk):
        i = self.line(t)
        return self.SPK[i] == spk and self.S[i] <= t <= self.E[i] + 0.05

    def word(self, t):
        for w in self.W:
            if w["t0"] <= t < w["t1"]: return w
        return None

    def viseme(self, t, spk):
        if not self.speaking(t, spk): return 0
        v = self.M[min(int(t * self.fm), len(self.M) - 1)]
        if v < 0.18: return 0
        w = self.word(t)
        if not w: return 2 if v > 0.5 else 1
        letters = re.sub(r"[^а-яё]", "", w["w"].lower())
        if not letters: return 2 if v > 0.5 else 1
        k = min(len(letters) - 1, int((t - w["t0"]) / max(0.05, w["t1"] - w["t0"]) * len(letters)))
        ch = letters[k]
        if ch in LIPS: return 4
        for j in range(k, len(letters)):  # next vowel shapes the mouth
            if letters[j] in VOW: return VOW[letters[j]] if v > 0.3 else 1
        return 2 if v > 0.55 else 1

    def blink(self, t, seed=0.0):
        p = (t + seed * 1.7) % 3.3
        return 1 if p < 0.11 else 0

    def gaze(self, t, spk, partner_side="r"):
        """Speaker looks at the partner, glances away while thinking; listener looks at the speaker."""
        i = self.line(t)
        if self.SPK[i] == spk:
            phase = (t - self.S[i]) % 4.0
            return "c" if phase < 2.6 else partner_side
        return partner_side

    def gesture(self, t, spk):
        """Accent on long/stressed words (≥ 6 letters or with ! ?) while speaking: smooth 0..1 bump."""
        if not self.speaking(t, spk): return 0.0
        w = self.word(t)
        if not w: return 0.0
        txt = w["w"]
        if len(re.sub(r"[^\w]", "", txt)) < 6 and not re.search(r"[!?]", txt): return 0.0
        x = (t - w["t0"]) / max(0.1, w["t1"] - w["t0"])
        return math.sin(math.pi * min(1, max(0, x)))

    def sentences(self, i):
        """Split line i into sentence start times (cut points)."""
        ws = [w for w in self.W if w["line"] == i]
        cuts = [self.S[i]]
        for a, b in zip(ws, ws[1:]):
            if re.search(r"[.!?…:]$", a["w"]) and b["t0"] - cuts[-1] > 1.2: cuts.append(b["t0"])
        return cuts

    def shots(self, close=None, wide="two", react=True, wide_every=4):
        """Cut on every sentence; alternate speaker close-ups; short silent reaction of the listener after punchy lines;
        a wide shot every few lines to re-establish space."""
        close = close or {"p": "r", "n": "k"}
        out = [(0.0, close[self.SPK[0]])]
        for i in range(len(self.S)):
            spk = self.SPK[i]; other = "n" if spk == "p" else "p"
            for k, c in enumerate(self.sentences(i)):
                name = wide if (i and i % wide_every == 0 and k == 0) else close[spk]
                if out and out[-1][1] == name and k: name = name + "_alt"   # same speaker, new sentence → alternate angle
                out.append((max(0.0, c - 0.08), name))
            if react and re.search(r"[!?]", " ".join(w["w"] for w in self.W if w["line"] == i)[-3:]):
                out.append((self.E[i] + 0.02, close[other] + "_react"))
        out.sort()
        dedup = []
        for t, n in out:
            if dedup and abs(dedup[-1][0] - t) < 0.5: dedup[-1] = (dedup[-1][0], n)
            else: dedup.append((t, n))
        return dedup

    @staticmethod
    def pause_before_punch(n_lines):
        return {n_lines - 1: 0.7}
