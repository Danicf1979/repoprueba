# Montaje del reel

Coloca los archivos con estos nombres exactos y vuelve a generar el vídeo:

| Carpeta / archivo | Qué es |
|---|---|
| `voces/dana.mp4` | «Si necesitan más recursos, que los pidan» (2 nov 2024) |
| `voces/cinco.mp4` | «Son las cinco y no he comido» (junio 2025) |
| `voces/jueces.mp4` | «Hay jueces que no cumplen con la ley» (sept 2025) |
| `voces/fiscalia.mp4` | «¿La Fiscalía de quién depende? Pues ya está» (nov 2019) |
| `reacciones/risa1.mp4`, `risa2.mp4` | Sánchez riéndose |
| `reacciones/baile1.mp4`, `baile2.mp4` | Sánchez bailando / de fiesta (vale también una foto .jpg) |
| `imagenes/NN.jpg` o `.mp4` | Fondo de la tarjeta NN (opcional) |
| `cancion.mp3` | La canción |

Recorta cada corte de voz solo a la frase (2–5 s). Si un archivo no está, el vídeo se genera igual.

```
python3 hacer_reel.py --audio cancion.mp3 --inicio-cancion 0
```
