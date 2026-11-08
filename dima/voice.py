import asyncio, json, os, subprocess, edge_tts
PROXY=os.environ.get("HTTPS_PROXY")
VOICE="ru-RU-DmitryNeural"
LINES=[
 ['[p]Клодыч, тут пацан из Таганрога. Диме двенадцать, у него миодистрофия Дюшенна.', '[p]Клодыч, тут пацан из Таганрога. Диме двенадцать. Миодистрофия Дюшенна.', '[p]Клодыч, есть пацан из Таганрога, Дима. Двенадцать лет, миодистрофия Дюшенна.'],
 ['Ему нужна генная терапия. Двести тридцать миллионов рублей.', 'Нужна генная терапия, двести тридцать миллионов рублей.', 'Ему нужна генная терапия за двести тридцать миллионов рублей.'],
 ['[p]Сколько уже собрали?', '[p]А сколько уже собрали?', '[p]И сколько собрали?'],
 ['Сто пятьдесят девять миллионов. Осталось около семидесяти одного.', 'Сто пятьдесят девять миллионов. Осталось примерно семьдесят один.', 'Уже сто пятьдесят девять миллионов. Осталось около семидесяти одного.'],
 ['[p]Семьдесят миллионов... Это же нереально.', '[p]Семьдесят миллионов. Это нереально.', '[p]Семьдесят лямов... это нереально.'],
 ['Посчитаем. По двадцать пять рублей — это меньше трёх миллионов человек. Нас больше.', 'Считаем. По двадцать пять рублей, это меньше трёх миллионов человек. Нас больше.', 'Посчитаем: по двадцать пять рублей это меньше трёх миллионов людей. Нас больше.'],
 ['[p]Всё, скинул двадцать пять. И сделал репост.', '[p]Всё, скинул двадцать пять рублей и сделал репост.', '[p]Скинул двадцать пять. И репост сделал.'],
 ['Сбор — в профиле лайф Дима двадцать двадцать пять. Реквизиты проверяйте только там.', 'Сбор в профиле лайф дима двадцать двадцать пять. Реквизиты только там.', 'Сбор ведётся в профиле лайф Дима двадцать двадцать пять. Проверяйте реквизиты только там.'],
 ['[p]Твоя очередь.', '[p]Теперь твоя очередь.', '[p]Твоя очередь, брат.'],
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
