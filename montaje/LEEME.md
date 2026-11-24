# Montaje del reel

```
python hacer_reel.py                       # sin canción (se añade en TikTok/IG)
python hacer_reel.py --audio cancion.mp3 --inicio-cancion <s>   # con canción, que baja al 15 % con la voz
```

| Carpeta / archivo | Qué es | Fuente |
|---|---|---|
| `voces/dana.mp4` | «Si necesita más recursos, que los pida» (2 nov 2024, Moncloa) | YouTube vhoLEqDQYQs, 3,24 s |
| `voces/cinco.mp4` | «Son las cinco, no he comido» (jun 2025, rueda de prensa en Ferraz) | YouTube Cl1oq0QoLtA, 0,40 s |
| `voces/jueces.mp4` | «Hay jueces haciendo política y políticos que tratan de hacer justicia» (sept 2025, TVE) | YouTube 8bcgPpIp5Dg, 4,84 s |
| `voces/fiscalia.mp4` | «La Fiscalía, ¿de quién depende? … Pues ya está» (nov 2019, RNE) | YouTube wnD_JxaN-2k, 28,0 s |
| `reacciones/risa1.mp4` | Congreso, nov 2023 | zc2k-dycS5g |
| `reacciones/risa2.mp4` | Rueda de prensa G20, nov 2025 | zx_FWphJGRU |
| `reacciones/baile1.mp4` | Congreso del PES, Madrid, feb 2019 | cE1bdaBmPXE |
| `reacciones/baile2.mp4` | Mitin en Fuenlabrada, oct 2026 | 3MafoIiMghQ |
| `reacciones/vacaciones.mp4` | La Mareta (Lanzarote), 3 ago 2026 | T29GJkvvnhI |
| `reacciones/baile_iceta.mp4` | Iceta e Isabel Rodríguez bailan en Ferraz, noche del 23-J 2023 | eJdcqhv56YU (El Plural), 13,5 s |
| `reacciones/risa_montero26.mp4` | Montero se ríe en la sesión de control, 18 mar 2026 | 8P5jAynXsiU (El Debate), 10,8 s |
| `reacciones/montero_mitin_may.mp4` | Montero en un mitin de la campaña andaluza, may 2026 | YOt7ZKKVriA, 14,0 s |
| `reacciones/montero_mitin_oct.mp4` | Montero en el acto de Fuenlabrada, 17 oct 2026 | JexNWAQ9Umc, 62,1 s |
| `reacciones/baile_sevilla.mp4` | Sánchez y Begoña Gómez bailan en el mitin de Sevilla, 12 nov 2026 | jqcT5BTXpH4, 1,0 s |
| `imagenes/NN.mp4` | Fondo de archivo de la tarjeta NN | agencias / TV |
| `encuadre.json` | Recorte vertical por clip: `[centro_x, centro_y, zoom]` | |

Notas de verificación (transcripción con faster-whisper):
- DANA: la frase literal es en singular («si necesita… que los pida», refiriéndose a la Generalitat).
- Jueces: la frase «hay jueces que no cumplen con la ley» no aparece literal; se usa la frase íntegra de TVE.
- Ceuta 2026: entrada masiva 30–31 jul; Sánchez visitó Ceuta el 31 jul y estuvo de vacaciones en La Mareta
  del 3 al 23 ago, cuando aún quedaban ~5.000 migrantes en la ciudad (EFE, 14 ago).

Fondos: `imagenes/<nombre>.mp4`, con el nombre que indica `img=` en cada tarjeta de `hacer_reel.py`.

Fuentes de las tarjetas añadidas (nov. 2026):
- Indultos del procés: Consejo de Ministros, 22 jun 2021 (BOE 23 jun 2021).
- Sedición y malversación: Ley Orgánica 14/2022, de 22 dic.
- «Tito Berni»: auto de apertura de juicio oral del caso Mediador, 24 sept 2026 (cohecho y otros); pendiente de juicio.
- ERE: Audiencia de Sevilla, sentencia 490/2019 (680 M€), confirmada por el Supremo (jul 2022);
  el Constitucional anuló las condenas de Chaves y Griñán (jul 2024).
- Expareja de Ábalos: admitió ante el Supremo el 27 feb 2025 que no fue a trabajar; la sentencia del caso
  mascarillas recoge 34.450 € de Ineco y 9.500 € de Tragsatec.
- Paco Salazar: dimitió en jul 2025 tras denuncias internas de acoso; nota del PSOE (5 dic 2025)
  admitiendo «no haber estado a la altura». No hay causa judicial (la querella de Hazte Oír fue inadmitida).
- Leire Díez: imputada por cohecho y tráfico de influencias (jul 2025); en instrucción.
- Presupuestos: tercera prórroga de los PGE de 2023 (Consejo de Ministros, 23 dic 2025).
- Zapatero: imputado en el caso Plus Ultra (Audiencia Nacional, 19 may 2026).
- Ábalos: condenado por el Supremo a 24 años; Koldo, a 19 (22 jun 2026).
- David Sánchez: 9 años de inhabilitación por prevaricación (Audiencia de Badajoz, 14 jul 2026); recurrida.
- Begoña Gómez: apertura de juicio oral con jurado por tráfico de influencias y malversación (21 sept 2026).
- Impuestos: Impuestómetro 2026 del Instituto Juan de Mariana (63 explícitas + 46 por no deflactar
  + 32 catastrales = 141). Hacienda discute el recuento total.

Los planos de bailes y risas solo llevan la fecha (sin nombres ni comentarios), para que no se confundan con el momento de la tarjeta anterior.

Cortes de voz en el vídeo (120 s): 35–37,5 s · 45,5–47,5 s · 57–70,5 s. Si añades la música en TikTok/IG,
bájala ahí. En TikTok web las canciones de la biblioteca duran 60 s y no se pueden dividir: volumen único
(-10 dB) y fundido de salida.

Portada: `D:\POLÍTICA\perfil\portada_tiktok.png` (Sánchez riendo en el Congreso, nov 2023).
