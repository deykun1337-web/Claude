# Мультики

Репозиторий для создания мультиков через Claude Code в облачной среде «Claude — мультики».

## Инструменты (ставит скрипт настройки среды)

- `ffmpeg`, `ffprobe` — сборка видео, звук, конвертация
- `convert` (ImageMagick), `rsvg-convert` — обработка картинок и SVG
- `sox`, `pydub` — монтаж и эффекты звука
- `espeak-ng -v ru` — простая озвучка без сети (роботизированный голос)
- `edge-tts` — нейросетевой русский голос (`ru-RU-SvetlanaNeural`, `ru-RU-DmitryNeural`)
- Python: `moviepy`, `cairosvg`, `pillow`, `numpy` — кадры и анимация
- Шрифты: DejaVu, Noto (кириллица), Noto Color Emoji

## Важно

- `edge-tts` сам не использует прокси среды, его надо указывать явно:

  ```bash
  SSL_CERT_FILE=/root/.ccr/ca-bundle.crt edge-tts --proxy "$HTTPS_PROXY" \
    --voice ru-RU-SvetlanaNeural --text "Привет!" --write-media voice.mp3
  ```

- Простой способ анимации: рисовать каждый кадр как SVG → `cairosvg` в PNG →
  `moviepy.ImageSequenceClip(..., fps=24)` → добавить звук → `write_videofile("out.mp4")`.
- Готовые ролики класть в `output/`, временные кадры — во временную папку, не в репозиторий.

## Экономия токенов: CodeGraph (обязательно)

В репозитории настроен [CodeGraph](https://github.com/colbymchenry/codegraph) — локальный индекс кода (символы, вызовы, файлы).
Перед тем как искать код через Grep/Glob/Read, **сначала спрашивай CodeGraph** — он сразу отдаёт нужные функции с исходником.

- В начале сессии (если нет папки `.codegraph/`): `npx -y @colbymchenry/codegraph init -i .` (≈5 с), иначе `codegraph sync .`
- MCP-сервер `codegraph` подключён в `.mcp.json` — используй его инструменты (`codegraph_explore`, `codegraph_node`, …), если они есть.
- Без MCP — через Bash: `codegraph explore "<что ищешь>" .` · `codegraph node <имя_функции> .` · `codegraph query <символ> .`
- Код, который выдал CodeGraph, повторно через Read не читать. Read — только для markdown/JSON/данных и когда CodeGraph не нашёл.
- Телеметрия выключена (`CODEGRAPH_TELEMETRY=0`). Индекс `.codegraph/` не коммитить.
