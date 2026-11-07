import asyncio, json, os, subprocess, edge_tts
PROXY=os.environ.get("HTTPS_PROXY")
VOICE="ru-RU-DmitryNeural"
LINES=[
 ["Здарова! Я Клод-кабан. Никита Скуф Скуфыч.","Здарова! Я Клод-кабан, Никита Скуф Скуфыч.","Привет! Я Клод-кабан. Никита Скуф Скуфыч."],
 ["Грязнульки — это альтушки: подводка, цепи, хаос в глазах.","Грязнульки, это альтушки: подводка, цепи и хаос в глазах.","Грязнульки — это альтушки. Подводка, цепи, хаос в глазах."],
 ["И вот прикол: скуфы всё чаще выбирают грязнульку вместо жены.","И знаете что? Скуфы всё чаще выбирают грязнульку вместо жены.","А скуфы всё чаще выбирают грязнульку вместо жены.","Скуфы всё чаще берут грязнульку вместо жены.","И вот прикол. Скуфы всё чаще выбирают грязнульку вместо жены.","Прикол в том, что скуфы всё чаще выбирают грязнульку вместо жены."],
 ["Жена: вынеси мусор. Грязнулька: погнали на концерт!","Жена: вынеси мусор. А грязнулька: погнали на концерт!","Жена: иди мусор вынеси. Грязнулька: погнали на концерт!","Жена: мусор вынеси. Грязнулька: го на концерт!","Жена: вынеси мусор! Грязнулька: погнали на концерт!","Жена говорит: вынеси мусор. Грязнулька: погнали на концерт!"],
 ["Я бы выбрал грязнулек за место жинки. А ты?","Я бы выбрал грязнулек за место жинки! А ты?","Я бы выбрал грязнулек вместо жинки. А ты?"],
]
RATES=[20,19,21,24,25,18,22,23]
async def gen(i,ts):
  ts = ts if isinstance(ts,list) else [ts]
  cp=f"build/l{i}.json"
  if os.path.exists(cp):
    c=json.load(open(cp))
    if c["text"] in ts: return c
  for t in ts:
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
