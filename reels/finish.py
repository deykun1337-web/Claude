"""Final «pro» pass for a finished reel (one ffmpeg run, ~1 min): picture + sound mastering.
  picture: gentle S-curve contrast, warm highlights / cool shadows split-tone, +5% vibrance, 1 px chromatic edge,
           fine film grain, subtle vignette, unsharp for 1080 output
  sound  : voice-forward EQ (cut mud 250 Hz, presence +3 dB 3.5 kHz, air +2 dB 10 kHz), glue compressor,
           tiny room reverb, limiter, −14 LUFS
Usage: python3 reels/finish.py <in.mp4> <out.mp4>   (run before promo.py cover / uniq.py)"""
import subprocess, sys
src, out = sys.argv[1], sys.argv[2]
vf = ("scale=1080:1920:flags=lanczos,"
      "curves=all='0/0.02 0.25/0.22 0.5/0.5 0.75/0.79 1/0.98',"
      "colorbalance=rs=-0.03:bs=0.04:rh=0.04:bh=-0.03,"
      "vibrance=intensity=0.08,"
      "rgbashift=rh=1:bh=-1,"
      "noise=alls=3:allf=t,vignette=PI/6.5,unsharp=5:5:0.45,format=yuv420p")
af = ("highpass=f=60,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1:g=3,equalizer=f=10000:t=q:w=1:g=2,"
      "acompressor=threshold=-18dB:ratio=2.5:attack=15:release=180:makeup=2,"
      "aecho=0.8:0.6:28:0.07,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                "-maxrate", "10M", "-bufsize", "20M", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
print("finished", out)
