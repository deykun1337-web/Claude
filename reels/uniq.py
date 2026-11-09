"""Fast uniqualization of a finished reel for an Instagram trial reel (one ffmpeg pass, ~1 min).
Changes the visual/audio fingerprint without hurting quality: 3% zoom-crop, 3% speed-up (pitch kept),
small colour/brightness/hue shift, fresh film grain, slight audio EQ, stripped metadata, new encode.
Usage: python3 reels/uniq.py <in.mp4> <out.mp4>"""
import random, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
r = random.Random(src)
z = 1.03 + r.uniform(0, 0.015); sp = 1.03 + r.uniform(0, 0.01)
vf = (f"scale=iw*{z:.4f}:ih*{z:.4f},crop=1080:1920,setpts=PTS/{sp:.4f},"
      f"eq=brightness={r.uniform(0.01, 0.025):.3f}:saturation={r.uniform(1.04, 1.08):.3f}:contrast={r.uniform(1.01, 1.04):.3f},"
      f"hue=h={r.uniform(-4, 4):.1f},noise=alls={r.randint(3, 5)}:allf=t,format=yuv420p")
af = f"atempo={sp:.4f},equalizer=f={r.randint(2500, 4000)}:t=q:w=1:g={r.uniform(1.0, 2.0):.1f},loudnorm=I=-14:TP=-1.5:LRA=11"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf, "-af", af, "-map_metadata", "-1", "-c:v", "libx264", "-preset", "medium",
                "-crf", "20", "-maxrate", "9M", "-bufsize", "18M", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
print("uniq", out)
