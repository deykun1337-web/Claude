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
