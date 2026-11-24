# Montaje del reel

```
python hacer_reel.py                       # sin canción (se añade en TikTok/IG)
python hacer_reel.py --audio cancion.mp3 --inicio-cancion <s>   # con canción, que baja al 15 % con la voz
```

| Carpeta / archivo | Qué es | Fuente |
|---|---|---|
| `voces/dana.mp4` | «Si necesita más recursos, que los pida» (2 nov 2024, Moncloa) | YouTube vhoLEqDQYQs, 3,24 s |
| `voces/cinco.mp4` | «Son las cinco, no he comido» (jun 2025, Ferraz) | YouTube Cl1oq0QoLtA, 0,40 s |
| `voces/jueces.mp4` | «Hay jueces haciendo política y políticos que tratan de hacer justicia» (sept 2025, TVE) | YouTube 8bcgPpIp5Dg, 4,84 s |
| `voces/fiscalia.mp4` | «La Fiscalía, ¿de quién depende? … Pues ya está» (nov 2019, RNE) | YouTube wnD_JxaN-2k, 28,0 s |
| `reacciones/risa1.mp4` | Congreso, nov 2023 | zc2k-dycS5g |
| `reacciones/risa2.mp4` | Rueda de prensa G20, nov 2025 | zx_FWphJGRU |
| `reacciones/baile1.mp4` | Congreso del PES, Madrid, feb 2019 | cE1bdaBmPXE |
| `reacciones/baile2.mp4` | Mitin en Fuenlabrada, oct 2026 | 3MafoIiMghQ |
| `reacciones/vacaciones.mp4` | La Mareta (Lanzarote), 3 ago 2026 | T29GJkvvnhI |
| `imagenes/NN.mp4` | Fondo de archivo de la tarjeta NN | agencias / TV |
| `encuadre.json` | Recorte vertical por clip: `[centro_x, centro_y, zoom]` | |

Notas de verificación (transcripción con faster-whisper):
- DANA: la frase literal es en singular («si necesita… que los pida», refiriéndose a la Generalitat).
- Jueces: la frase «hay jueces que no cumplen con la ley» no aparece literal; se usa la frase íntegra de TVE.
- Ceuta 2026: entrada masiva 30–31 jul; Sánchez visitó Ceuta el 31 jul y estuvo de vacaciones en La Mareta
  del 3 al 23 ago, cuando aún quedaban ~5.000 migrantes en la ciudad (EFE, 14 ago).

Si añades la música en TikTok/IG, bájala en: 21,5–24,5 s · 29,5–32,5 s · 33,5–47,5 s.
