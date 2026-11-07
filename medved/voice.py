import asyncio, json, os, subprocess, edge_tts
PROXY=os.environ.get("HTTPS_PROXY")
VOICE="ru-RU-DmitryNeural"
LINES=[
 ["Ноябрь двадцать шестого наступил. Все ждали медведя.","Наступил ноябрь двадцать шестого. Все ждали медведя.","Ноябрь две тысячи двадцать шестого наступил. Все ждали медведя.","Вот и ноябрь двадцать шестого. Все ждали медведя."],
 ["Три года нас пугали мемом из будущего.","Нас три года пугали мемом из будущего.","Три года нас пугали этим мемом из будущего.","Три года нас пугали мемом."],
 ["[bear]Помни... ноябрь двадцать шестого близко.","[bear]Помни. Ноябрь двадцать шестого близко.","[bear]Помни, ноябрь двадцать шестого уже близко.","[bear]Помни. Ноябрь близко.","[bear]Запомни. Ноябрь двадцать шестого близко.","[bear]Помни... ноябрь близко...","[bear]Ноябрь двадцать шестого близко. Помни."],
 ["Ну пришёл он. И что сделал?","Ну пришёл. И что он сделал?","И вот он пришёл. И что сделал?","Ну пришёл он, и что?"],
 ["Сел на диван, открыл пиво и стал скуфом.","Сел на диван, открыл пиво, и стал скуфом.","Сел на мой диван, открыл пиво и стал скуфом.","Сел на диван, взял пиво и стал скуфом."],
 ["[bear]Медведь Скуфыч.","[bear]Я медведь Скуфыч.","[bear]Зови меня медведь Скуфыч.","[bear]Теперь я медведь Скуфыч."],
 ["Так что запомни:","Так что, запомни:","Короче, запомни:","Запомни:"],
]
RATES=[20,19,21,24,25,18,22,23]
async def gen(i,ts):
  ts = ts if isinstance(ts,list) else [ts]
  cp=f"build/l{i}.json"
  if os.path.exists(cp):
    c=json.load(open(cp))
    if c["text"] in [x.replace("[bear]", "") for x in ts]: return c
  for t in ts:
    bear = t.startswith("[bear]"); t = t.replace("[bear]", "")
    for r in ([-10, -12, -8, -5, 0, 5] if bear else RATES):
        try:
            print("try",i,r,t[:30],flush=True)
            return await gen1(i,t,f"{r:+d}%")
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
    res={"text":t,"rate":rate,"dur":dur,"words":words}
    json.dump(res,open(f"build/l{i}.json","w"),ensure_ascii=False)
    return res
async def main():
    os.makedirs("build",exist_ok=True)
    out=[await gen(i,t) for i,t in enumerate(LINES)]
    json.dump(out,open("build/voice.json","w"),ensure_ascii=False,indent=1)
    for i,o in enumerate(out): print(i,o["rate"],round(o["dur"],2),len(o["words"]))
    print("total",round(sum(o["dur"] for o in out),2))
asyncio.run(main())
