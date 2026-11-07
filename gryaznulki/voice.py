import asyncio, json, os, subprocess, edge_tts
PROXY=os.environ.get("HTTPS_PROXY")
VOICE="ru-RU-DmitryNeural"
LINES=[
 ["Хэй! Я Клод-кабан. Кто такие грязнульки?","Хэй! Я Клод-кабан. Кто такие эти грязнульки?"],
 ["Это чумазики, которые уверены, что они десять из десяти.","Это чумазики, уверенные, что они десять из десяти."],
 ["Зумерам: вайб болота, и дезодорант не спасёт.","Для зумеров: вайб болота, дезодорант не спасёт."],
 ["Скуфам: «иди умойся, грязнуля!» Помните?","Скуфам: иди умойся, грязнуля! Помните?","Для скуфов: иди умойся, грязнуля! Помните?"],
 ["А я кабан. Мне можно. Хрю!","А я кабан, мне можно. Хрю!"],
]
RATES=[20,19,21,24,25,18,22,23,17,26,16,27]
async def gen(i,ts):
  for t in (ts if isinstance(ts,list) else [ts]):
    for r in RATES:
        try:
            print("try",i,r,t[:30],flush=True)
            return await gen1(i,t,f"+{r}%")
        except edge_tts.exceptions.NoAudioReceived:
            pass
  raise SystemExit(f"line {i} failed at all rates")
async def gen1(i,t,rate):
    c=edge_tts.Communicate(t,VOICE,rate=rate,boundary="WordBoundary",proxy=PROXY)
    words=[]
    with open(f"build/l{i}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append({"t":ch["offset"]/1e7,"d":ch["duration"]/1e7,"w":ch["text"]})
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"build/l{i}.mp3"]))
    return {"text":t,"rate":rate,"dur":dur,"words":words}
async def main():
    os.makedirs("build",exist_ok=True)
    out=[await gen(i,t) for i,t in enumerate(LINES)]
    json.dump(out,open("build/voice.json","w"),ensure_ascii=False,indent=1)
    for i,o in enumerate(out): print(i,o["rate"],round(o["dur"],2),len(o["words"]))
    print("total",round(sum(o["dur"] for o in out),2))
asyncio.run(main())
