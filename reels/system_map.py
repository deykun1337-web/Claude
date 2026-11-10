"""КАРТА СИСТЕМЫ «комбайн @deykun1337» — для CodeGraph: `codegraph explore "system_map"` отдаёт всю схему одним запросом.

Держи в актуальном виде: меняешь расписание, скрипт, стиль или правило — поправь здесь и сделай `codegraph sync .`.
Владелец: Руслан, Instagram @deykun1337 (ig_user_id 17841409120122863), Telegram-канал «ДЕЙКУН × Claude» (бот @deykun_kanal_bot).
Цель: быстрый рост Instagram и Telegram. 2 премиум-ролика в день про Claude, у каждого кодовое слово и пробная копия.
"""

# ---------------------------------------------------------------- расписания (MSK) и где они выполняются
SCHEDULE = {
    "утро 09:17": {"trigger": "trig_017T1HmRuDcGkgZzrBhh18eQ", "session": "session_01WpmoiMdpovnbXkewgt5mSw (Opus, воркер роликов, есть push)",
                   "does": "reels/RUN_REEL.md, слот am (UI-стиль) → публикация 12:30"},
    "вечер 18:01": {"trigger": "trig_011XmAVJ6KQ3dsTtQpe4na8h", "session": "session_01WpmoiMdpovnbXkewgt5mSw",
                    "does": "RUN_REEL.md, слот pm (персонажи) или серия «Кабаново» (каждый 2-й день) → публикация 21:30"},
    "каждый час :56": {"trigger": "trig_01E5cwjyBb8xzWxzT1LLgXAr", "session": "session_01WpmoiKBjMrKAFzoyhtbbQE (Haiku, воркер автоответов)",
                       "does": "bash reels/autoreply.sh — кодовые слова, Директ, одобрение заявок TG, push состояния"},
    "пн 11:23": {"trigger": "trig_015Uu8u6jV1qcWzCvtj3w4r4", "session": "новая сессия (Sonnet)", "does": "reels/WEEKLY.md — недельный отчёт"},
    "каждые 5 мин": {"trigger": None, "session": "основная сессия (nohup)", "does": "reels/watch_loop.sh — то же, что autoreply, чаще; гибнет при перезапуске"},
    "ВЫКЛЮЧЕНЫ": ["trig_01Hh4GroitAXAdQ8cbEyJS65", "trig_011K2EVBCer5tAWqLyeBFt2K", "trig_012rt4D8sSRB6AhvDRqCUGQ1", "trig_01Ks1rAsWsC2omau8DSFyAYp"],
}
WHY_WORKERS = ("Новые сессии от расписания не получают push в репозиторий (403), а пробные рилсы публикуются только через "
               "публичный raw.githubusercontent URL после push. Поэтому расписания стреляют в постоянные сессии-воркеры с репозиторием.")

# ---------------------------------------------------------------- конвейер ролика (RUN_REEL.md)
PIPELINE = [
    "0. npx -y @colbymchenry/codegraph init -i . ; git pull ; текстуры/зависимости",
    "0b. идеи: reels/SWIPE.md, reels/IDEAS_INBOX.md, reels/REFERENCES.md, viral.py",
    "1. тема + кодовое слово (не занятое в reels/KEYWORDS.md)",
    "стиль: python3 reels/style_pick.py <am|pm> '<тема>' → reels/STYLES.md (10 стилей)",
    "голос: edge-tts (ru-RU-DmitryNeural/SvetlanaNeural, прокси обязателен) → reels/voicefx.py place (акустика)",
    "музыка: reels/music.py make <жанр> → mix (ducking под голос); звуки: reels/motion/sfx.py",
    "графика: UI-стили reels/motion/mokit.py (3/4/9), reels/motion/hud.py (10, 60 fps); 3D klod3d/*.py (Blender EEVEE); 2D drawn/drawn2d.py",
    "субтитры: klod3d/ui_kit.py phrase_captions (фразами, плавно) или hud.words (UI)",
    "финиш: reels/finish.py → обложки reels/promo.py cover (A/B хуки) → reels/uniq.py (пробная копия)",
    "публикация: reels/ig_post.py post ... --at 12:30|21:30 --comment ; пробная --trial (через push + video_url)",
    "лимит пробных ~11/сутки → reels/state/trial_later.txt (по 1 за запуск), очередь перевыпуска reels/state/retrial_queue.txt",
    "Telegram: reels/tg_bot.py post <гайд> ; video ; вечером «Промпт дня» reels/tg/prompt_<дата>.md",
    "учёт: reels/LOG.md, style_pick.py log, push",
]

# ---------------------------------------------------------------- кодовые слова (бот reels/ig_bot.py читает reels/KEYWORDS.md)
KEYWORDS = {"ДОЛГ": "dolg", "КАБАН": "kakdelayu/spisok", "АГЕНТЫ": "subagenty Dfh-nyLiS5r", "КАБАНОВО": "kabanovo DfiCDvLjv2Y (серия)",
            "ЛИМИТ": "limit DfjlnuDge13", "БЭКАП": "«Клод, я удалил проект» Dfh-n-wjHGS"}
BOT_FLOW = ("коммент со словом → проверка, что мы ещё не отвечали (replies в Instagram) → личный ответ «подпишись и ответь +» + публичный "
            "«Отправил в Директ» → ответ «+» → is_user_follow_business → ссылка TG (заявка одобряется tg_bot.py approve). "
            "КАБАНОВО: участок/дом в следующей серии. Состояние reels/state/ig.json.")

# ---------------------------------------------------------------- стили (reels/STYLES.md, эталоны reels/profile/style_*.jpg)
STYLES = {1: "гладкий 3D (klod3d/chars_smooth.py)", 2: "пластилин (clay3d.py)", 3: "тёмный редакционный (mokit DARK)",
          4: "светлый бумага+точки (mokit LIGHT)", 5: "пиксельный сплит", 6: "рисованный 2D (drawn2d)", 7: "HD пиксель-арт",
          8: "реализм Poly Haven", 9: "гибрид 3D-герой + тёмный UI", 10: "HUD-лайм моушн кодом (hud.py, 60 fps)"}
STYLE_RULE = "в день 1 UI-ролик (3/4/9/10) + 1 с персонажами; не повторять 3 последних стиля; история reels/state/styles_used.txt"

# ---------------------------------------------------------------- серия «Кабаново — деревня подписчиков»
VILLAGE = {"script": "reels/village.py collect|plan|register", "scene": "klod3d/village3d.py", "overlay": "kabanovo/compose.py",
           "state": "reels/village/state.json", "report": "reels/village/REPORT.md", "rules": "RUN_REEL.md раздел 6c",
           "episodes": {1: "DfiCDvLjv2Y (09.11)"}, "cadence": "каждые 2 дня вечером"}

# ---------------------------------------------------------------- герои и правила контента
HEROES = "Клод — ВСЕГДА кабан (лососевый, пятачок, клыки, искорка); Руслан — розовая кепка DEYKUN, белая футболка, золотая цепь, джинсы"
BANS = ["боевая тактика и инструкции к оружию", "чужие сценарии/ролики", "чужие трендовые треки (только reels/music.py)",
        "СВО/политика только факты с источниками", "не трогать посты сбора для Димы", "не выдумывать факты; инструменты проверять (WebSearch)"]

# ---------------------------------------------------------------- доступы и секреты (значений здесь НЕТ)
ACCESS = {"Instagram Graph API": "токен как сетевой секрет среды (graph.facebook.com, rupload.facebook.com); удалять медиа API не даёт",
          "Telegram": "TG_BOT_TOKEN — переменная среды; канал chat_id -1002636410677",
          "репозиторий": "deykun1337-web/Claude ПУБЛИЧНЫЙ — секреты не коммитить",
          "сеть среды": "speech.platform.bing.com, trendsee.io, instagram, cdninstagram, api.telegram.org, polyhaven"}

# ---------------------------------------------------------------- ручные задачи Руслана
OWNER_TODO = ["закреплять первый комментарий под новыми роликами", "удалить дубли из reels/TO_DELETE.md",
              "добавить разрешение instagram_manage_insights", "отозвать засвеченные в чате токены"]
