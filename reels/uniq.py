"""Uniqualization of OUR OWN finished reel before re-posting it as an Instagram trial reel (one ffmpeg pass, ~1 min).
Same set of changes «уникализатор»-bots apply, tuned so quality stays high:
  video: trim first 2–4 frames · 3–5% zoom with a slow drifting crop (Ken Burns) · 0.4–0.8° rotation ·
         fps 24 → 30 · 2–4% speed-up · brightness/contrast/saturation/gamma/hue shift · fresh temporal grain ·
         light vignette · 1–2 px unsharp · different encoder settings (GOP, profile, CRF) → new bitstream/hash
  audio: same speed-up with ±1–2% pitch shift · EQ tilt · −45 dB pink noise floor · new loudness pass
  file : all metadata stripped, new creation_time, new encoder tag
No mirroring (would flip on-screen text). Usage: python3 reels/uniq.py <in.mp4> <out.mp4>"""
import datetime as dt, random, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
r = random.Random(src + str(dt.date.today()))
z = 1.035 + r.uniform(0, 0.02); sp = 1.02 + r.uniform(0, 0.02); rot = r.choice((-1, 1)) * r.uniform(0.4, 0.8)
pitch = 1 + r.choice((-1, 1)) * r.uniform(0.01, 0.02); skip = r.randint(2, 4) / 24
W, H = 1080, 1920
dx, dy = r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6)  # px per frame drift of the crop window
vf = (f"trim=start={skip:.3f},setpts=PTS-STARTPTS,fps=30,"
      f"scale={int(W * z) // 2 * 2}:{int(H * z) // 2 * 2},"
      f"rotate={rot:.3f}*PI/180:fillcolor=black:ow=iw:oh=ih,"
      f"crop={W}:{H}:x='(iw-{W})/2+{dx:.2f}*sin(n/40)*20':y='(ih-{H})/2+{dy:.2f}*cos(n/50)*20',"
      f"setpts=PTS/{sp:.4f},"
      f"eq=brightness={r.uniform(0.01, 0.03):.3f}:contrast={r.uniform(1.02, 1.05):.3f}:saturation={r.uniform(1.03, 1.08):.3f}:gamma={r.uniform(0.97, 1.03):.3f},"
      f"hue=h={r.uniform(-5, 5):.1f},noise=alls={r.randint(3, 6)}:allf=t,vignette=PI/{r.uniform(5.5, 7):.2f},unsharp=3:3:{r.uniform(0.3, 0.6):.2f},format=yuv420p")
af = (f"atrim=start={skip:.3f},asetpts=PTS-STARTPTS,asetrate=48000*{pitch:.4f},aresample=48000,atempo={sp / pitch:.4f},"
      f"equalizer=f={r.randint(2500, 4500)}:t=q:w=1:g={r.uniform(1.0, 2.5):.1f},equalizer=f={r.randint(90, 160)}:t=q:w=1:g={r.uniform(-1.5, 1.0):.1f},"
      f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000")
ct = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=r.randint(5, 600))).strftime("%Y-%m-%dT%H:%M:%SZ")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-f", "lavfi", "-i", "anoisesrc=color=pink:amplitude=0.006:sample_rate=48000",
                "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a0];[1:a]volume=0.12[n];[a0][n]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "[v]", "-map", "[a]", "-map_metadata", "-1", "-metadata", f"creation_time={ct}", "-metadata", "encoder=",
                "-c:v", "libx264", "-preset", "medium", "-profile:v", r.choice(("high", "main")), "-crf", str(r.choice((19, 20, 21))),
                "-g", str(r.choice((48, 60, 90))), "-maxrate", "9M", "-bufsize", "18M",
                "-c:a", "aac", "-b:a", r.choice(("160k", "192k")), "-ar", "48000", "-shortest", "-movflags", "+faststart", out], check=True)
print("uniq", out)
