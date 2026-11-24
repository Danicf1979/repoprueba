Hola. Vengo de otro chat de Claude Code donde se ha preparado un reel vertical (IG Reels / YouTube Shorts / TikTok). Allí no había acceso a YouTube/TikTok ni a modelos de voz, así que te toca terminarlo a ti. Hazlo todo tú: no me pidas que busque segundos ni recorte nada.

## Dónde está todo
- Repo: `danicf1979/repoprueba`, rama `ccr-657422fe-1qpbqk`, carpeta `montaje/`.
- Lee primero `montaje/LEEME.md` y `montaje/hacer_reel.py` (genera el vídeo con Pillow + ffmpeg; si falta un clip, lo salta o deja la tarjeta sin voz).

## Herramientas
Instala lo que haga falta: `yt-dlp`, `ffmpeg`, Python 3 con `pillow`, `numpy` y `faster-whisper` (modelo `small` o `medium`, idioma `es`, con `word_timestamps=True`).

## Tarea 1 — Cortes de voz (vídeo con sonido, 2–5 s, solo la frase)
Busca cada vídeo (YouTube, TikTok o X), descárgalo con yt-dlp, transcríbelo con faster-whisper, localiza la frase por las marcas de tiempo de las palabras y recorta con ~0,3 s de margen antes y después. Comprueba sacando fotogramas que se ve a Pedro Sánchez hablando y que la frase es la correcta. Guarda como:
- `voces/dana.mp4` — «Si necesitan más recursos, que los pidan» (Sánchez, 2 nov 2024, comparecencia tras la DANA).
- `voces/cinco.mp4` — «Son las cinco y no he comido» (junio 2025, rueda de prensa en Ferraz tras el caso Cerdán; hay vídeos de Onda Cero y ABC).
- `voces/jueces.mp4` — «Hay jueces que no cumplen con la ley» (septiembre 2025, entrevista en TVE).
- `voces/fiscalia.mp4` — «¿La Fiscalía de quién depende? … Pues ya está» (noviembre 2019, entrevista en RNE; si solo existe audio con imagen fija, vale).

## Tarea 2 — Planos de contraste (sin texto propio, 2–4 s)
Clips de Sánchez riéndose o bailando/de fiesta en actos públicos (mítines, Congreso, celebraciones). Verifica viendo fotogramas que sale él y que se le ve bien centrado. Guarda como `reacciones/risa1.mp4`, `reacciones/risa2.mp4`, `reacciones/baile1.mp4`, `reacciones/baile2.mp4`.

## Tarea 3 — Canción
La canción es «Yo sí te voy a votar (Pedro Sánchez)», viral en TikTok/Spotify. Pídeme el archivo (`montaje/cancion.mp3`) si no está ya en la carpeta; no la descargues de fuentes piratas. Pregúntame también desde qué segundo empezar o elige tú el arranque del estribillo.

## Tarea 4 — Generar y revisar
```
python3 hacer_reel.py --audio cancion.mp3 --inicio-cancion <segundo>
```
- Revisa fotogramas de cada tarjeta de voz y de reacción: que la cara no quede cortada por el recorte vertical (si pasa, añade al script un desplazamiento/zoom por clip).
- Comprueba que la música baja mientras habla (volumedetect) y que el vídeo dura ≈60–70 s.
- Envíame el vídeo final y haz commit + push a la misma rama.

## Reglas
- No cambies los datos de los rótulos: están verificados. Mantén «Caso abierto · presunción de inocencia» en los casos judiciales.
- No añadas afirmaciones de fraude electoral («pucherazo», votos de muertos): están desmentidas.
- Usa solo frases reales con su audio original: nada de voces generadas con IA ni montajes que le hagan decir algo que no dijo.
- Fecha límite: el vídeo debe estar listo para publicarlo como tarde el viernes 27 de noviembre (el 28 es jornada de reflexión).
