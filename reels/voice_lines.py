"""Voice a reel script line by line (edge-tts with retries) → build/timing.json + build/voice_full.wav (scene acoustics).

    python3 reels/voice_lines.py <reel_dir> [--voice ru-RU-DmitryNeural] [--rate +8%] [--scene studio] [--gap 0.25]
<reel_dir>/lines.json = ["реплика 1", ...]. In the text: «Claude» is read as «Клод», *stars* and [TAGS] are stripped.
edge-tts fails randomly on some phrases (NoAudioReceived) — each line is retried up to 15 times.
"""
import json, os, re, subprocess, sys, time

a = sys.argv[1:]; D = a[0]
opt = lambda k, d: a[a.index(k) + 1] if k in a else d
VOICE, RATE, SCENE, GAP = opt("--voice", "ru-RU-DmitryNeural"), opt("--rate", "+8%"), opt("--scene", "studio"), float(opt("--gap", "0.25"))
B = os.path.join(D, "build"); os.makedirs(B, exist_ok=True)
L = json.load(open(os.path.join(D, "lines.json"), encoding="utf-8"))
env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")


def speakable(t):
    t = re.sub(r"\[[^\]]*\]", "", t).replace("*", "").replace("_", " ")
    t = t.replace("Claude Code", "Клод Код").replace("Claude", "Клод").replace(" — ", ", ")
    return t


st, t = [], 0.35
for i, line in enumerate(L):
    mp3 = os.path.join(B, f"v{i}.mp3")
    for k in range(15):
        subprocess.run(["edge-tts", "--proxy", os.environ.get("HTTPS_PROXY", ""), "--voice", VOICE, f"--rate={RATE}",
                        "--text", speakable(line), "--write-media", mp3], env=env, capture_output=True)
        if os.path.exists(mp3) and os.path.getsize(mp3) > 2000: break
        time.sleep(3)
    else:
        sys.exit(f"voice failed on line {i}: {line}")
    wav = os.path.join(B, f"w{i}.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse", "-ar", "44100", "-ac", "1", wav], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]))
    st.append([round(t, 3), round(d, 3)]); t += d + GAP
total = round(t + 2.4, 2)
json.dump({"lines": st, "total": total}, open(os.path.join(B, "timing.json"), "w"))
inputs = sum([["-i", os.path.join(B, f"w{i}.wav")] for i in range(len(L))], [])
fc = "".join(f"[{i}]adelay={int(s * 1000)}[a{i}];" for i, (s, d) in enumerate(st)) + "".join(f"[a{i}]" for i in range(len(L))) + \
     f"amix=inputs={len(L)}:normalize=0,apad=whole_dur={total}"
raw = os.path.join(B, "voice_raw.wav")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-t", str(total), raw], check=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import voicefx
voicefx.place(raw, os.path.join(B, "voice_full.wav"), SCENE, 1.0)
print(json.dumps({"lines": st, "total": total}))
