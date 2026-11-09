"""Make TTS voices sound ALIVE and INSIDE the scene (free, no paid TTS).

1) prosody(text, spk) → (rate, pitch, volume) for edge-tts per line, from the emotion in the text:
     «!» / «?!» / caps → excited: faster, higher, louder · «...» → hesitant: slower, lower · «?» → rising pitch
     use in voice.py: edge_tts.Communicate(text, voice, rate=r, pitch=p, volume=v, ...)
2) place(in.wav, out.wav, scene, distance) → the voice recorded IN the location:
     scene: room | kitchen | street | office | car | studio | phone | hall
     = proximity EQ + early reflections + reverb tail sized to the space + room tone bed under the voice.
   distance: 0 close-up … 1 far (wider shots → more room, less bass).
3) ambience(scene, seconds, out.wav) → continuous background bed for the whole reel (room tone / city / kitchen hum / rain).
CLI: python3 reels/voicefx.py place in.wav out.wav kitchen 0.3 | ambience street 30 out.wav
"""
import re, subprocess, sys

PRESETS = {  # reverberance %, HF damping %, room scale %, pre-delay ms, wet gain dB, low-cut Hz, ambience colour
    "studio":  (12, 60, 20, 4, -12, 70, None),
    "room":    (32, 55, 45, 10, -8, 90, "brown"),
    "kitchen": (45, 30, 50, 8, -6, 100, "pink"),
    "office":  (38, 50, 70, 14, -8, 90, "brown"),
    "hall":    (70, 40, 100, 30, -4, 110, "brown"),
    "street":  (18, 70, 100, 40, -12, 120, "pink"),
    "car":     (15, 80, 15, 3, -10, 110, "brown"),
    "phone":   (5, 90, 10, 0, -20, 400, None),
}


def prosody(text, spk="n"):
    t = text.strip(); rate, pitch, vol = 0, 0, 0
    if re.search(r"!|[А-ЯЁ]{4,}", t): rate += 8; pitch += 12; vol += 10
    if t.endswith("?") and "!" not in t: pitch += 6
    if "..." in t or "…" in t: rate -= 10; pitch -= 6
    if len(t) < 14 and not t.endswith("?"): rate -= 4                     # short punchy lines land slower
    base = {"n": 20, "p": 22, "g": 14}.get(spk, 20)
    return f"{base + rate:+d}%", f"{pitch:+d}Hz", f"{vol:+d}%"


def place(src, out, scene="room", distance=0.3):
    rv, damp, scale, pre, wet, lowcut, _ = PRESETS.get(scene, PRESETS["room"])
    d = max(0.0, min(1.0, float(distance)))
    rv = int(rv * (0.7 + 0.6 * d)); wet = wet + 6 * d
    eq = ["highpass", str(lowcut + int(60 * d)), "equalizer", "200", "1q", f"{2 - 4 * d:.1f}", "equalizer", "3500", "1q", f"{3 - 2 * d:.1f}"]
    if scene == "phone": eq = ["highpass", "400", "lowpass", "3400", "overdrive", "6"]
    subprocess.run(["sox", src, out, "gain", "-6"] + eq + ["compand", "0.02,0.2", "6:-70,-60,-20", "-6", "-90", "0.1",
                    "reverb", str(rv), str(damp), str(scale), "100", str(pre), str(wet), "norm", "-1"], check=True)


def ambience(scene, seconds, out):
    _, _, _, _, _, _, colour = PRESETS.get(scene, PRESETS["room"])
    colour = colour or "brown"
    chain = {"street": ["lowpass", "1800", "tremolo", "0.15", "40"], "kitchen": ["lowpass", "900", "equalizer", "120", "2q", "6"],
             "office": ["lowpass", "700"], "room": ["lowpass", "500"], "hall": ["lowpass", "600", "reverb", "60"], "car": ["lowpass", "300"]}.get(scene, ["lowpass", "500"])
    subprocess.run(["sox", "-n", "-r", "48000", "-c", "1", out, "synth", str(seconds), f"{colour}noise"] + chain + ["gain", "-n", "-34"], check=True)


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "place": place(a[2], a[3], a[4], a[5] if len(a) > 5 else 0.3)
    elif a[1] == "ambience": ambience(a[2], float(a[3]), a[4])
    elif a[1] == "prosody": print(prosody(a[2], a[3] if len(a) > 3 else "n"))
