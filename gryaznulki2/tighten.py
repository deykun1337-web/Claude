# Shorten long pauses inside each voice line, remap word timings, then speed up slightly.
import json, subprocess, numpy as np, wave
SR=48000; MAXGAP=0.22; TEMPO=1.0; THR=0.012
def load(p):
    raw=subprocess.check_output(["ffmpeg","-v","error","-i",p,"-f","s16le","-ac","1","-ar",str(SR),"-"])
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
def save(p,a):
    with wave.open(p,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a,-1,1)*32767).astype(np.int16).tobytes())
data=json.load(open("build/voice.json"))
for i,o in enumerate(data):
    a=load(f"build/l{i}.mp3")
    win=int(SR*0.01); n=len(a)//win
    loud=np.sqrt((a[:n*win].reshape(n,win)**2).mean(1))>THR
    idx=np.where(loud)[0]; s0,s1=idx[0],idx[-1]+1
    keep=[]; tmap=[]  # (orig_time, new_time)
    t_new=0; k=s0
    while k<s1:
        j=k
        if not loud[k]:
            while j<s1 and not loud[j]: j+=1
            run=j-k; use=min(run,int(MAXGAP*100))
            keep.append(a[k*win:(k+use)*win]); tmap.append((k/100,t_new)); t_new+=use/100; k=j
        else:
            while j<s1 and loud[j]: j+=1
            keep.append(a[k*win:j*win]); tmap.append((k/100,t_new)); t_new+=(j-k)/100; k=j
    tmap.append((s1/100,t_new))
    out=np.concatenate(keep)
    # fade edges
    f=int(SR*0.01); out[:f]*=np.linspace(0,1,f); out[-f:]*=np.linspace(1,0,f)
    save(f"build/t{i}_raw.wav",out)
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"build/t{i}_raw.wav","-af",f"atempo={TEMPO}",f"build/t{i}.wav"],check=True)
    ot=np.array([x[0] for x in tmap]); nt=np.array([x[1] for x in tmap])
    def m(t): return float(np.interp(t,ot,nt))/TEMPO
    for w in o["words"]:
        st=m(w["t"]); en=m(w["t"]+w["d"]); w["t"]=round(st,3); w["d"]=round(max(en-st,0.08),3)
    o["dur"]=round(t_new/TEMPO,3)
    print(i,o["dur"],o["text"])
json.dump(data,open("build/voice_tight.json","w"),ensure_ascii=False,indent=1)
print("total",round(sum(o["dur"] for o in data),2))
