import asyncio, json, os, subprocess, edge_tts
PROXY=os.environ.get("HTTPS_PROXY")
VOICE="ru-RU-DmitryNeural"
LINES=[
 ['[p]Братья! Через минуту откроют двери!', '[p]Братья! Через минуту двери откроют!', '[p]Братья, через минуту откроют двери!'],
 ['Цель — кофемашина. Минус семьдесят процентов.', 'Цель: кофемашина. Минус семьдесят процентов.', 'Наша цель — кофемашина. Минус семьдесят.'],
 ['[p]За скидки!', '[p]За скидки, братья!', '[p]Вперёд! За скидки!'],
 ['[p]Пусто?!', '[p]Пусто... Где всё?!', '[p]Что? Пусто?!'],
 ['Я же нейросеть. Я её ещё ночью онлайн заказал.', 'Я же нейросеть. Заказал её онлайн ещё ночью.', 'Я нейросеть. Ночью онлайн заказал.'],
 ['[p]А нас тогда зачем позвал?!', '[p]Тогда нас зачем позвал?!', '[p]А нас-то зачем позвал?!'],
 ['Для атмосферы.', 'Ну... для атмосферы.', 'Для атмосферы, Руслан.'],
]
RATES=[20,19,21,24,25,18,22,23]
async def gen(i,ts):
  ts = ts if isinstance(ts,list) else [ts]
  cp=f"build/l{i}.json"
  if os.path.exists(cp):
    c=json.load(open(cp))
    if c["text"] in [x.replace("[p]", "").replace("[g]", "") for x in ts]: return c
  for t in ts:
    spk = "p" if t.startswith("[p]") else ("g" if t.startswith("[g]") else "n"); t = t.replace("[p]", "").replace("[g]", "")
    girl = spk != "n"
    for r in ({"p": [24, 22, 26, 20, 28, 18], "g": [14, 12, 16, 10, 18, 8]}.get(spk, RATES)):
        try:
            print("try",i,r,t[:30],flush=True)
            return await gen1(i,t,f"{r:+d}%","ru-RU-SvetlanaNeural" if spk == "g" else VOICE, spk)
        except edge_tts.exceptions.NoAudioReceived:
            pass
  raise SystemExit(f"line {i} failed at all rates")
async def gen1(i,t,rate,voice=None,spk="n"):
    c=edge_tts.Communicate(t,voice or VOICE,rate=rate,boundary="WordBoundary",proxy=PROXY)
    words=[]
    with open(f"build/l{i}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append({"t":ch["offset"]/1e7,"d":ch["duration"]/1e7,"w":ch["text"]})
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"build/l{i}.mp3"]))
    res={"text":t,"rate":rate,"dur":dur,"words":words,"spk":spk}
    json.dump(res,open(f"build/l{i}.json","w"),ensure_ascii=False)
    return res
async def main():
    os.makedirs("build",exist_ok=True)
    out=[await gen(i,t) for i,t in enumerate(LINES)]
    json.dump(out,open("build/voice.json","w"),ensure_ascii=False,indent=1)
    for i,o in enumerate(out): print(i,o["rate"],round(o["dur"],2),len(o["words"]))
    print("total",round(sum(o["dur"] for o in out),2))
asyncio.run(main())
