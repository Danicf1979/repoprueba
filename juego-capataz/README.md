# Capataz · La mudanza (fase 1)

Prototipo jugable en el navegador. Eres el capataz de una cuadrilla y tienes que llevar un paso de misterio desde el almacén de la hermandad hasta la parroquia de San Roque, sin golpearlo, y dejarlo a tierra dentro del templo.

Es la fase 1 del plan: comprobar si la mecánica de mandar el paso es divertida antes de invertir en arte, música o gestión.

## Cómo jugar

Abre `index.html` en un navegador (necesita conexión para cargar Three.js y las fuentes).

| Tecla | Orden |
|---|---|
| Espacio | «¡A esta es!»: levantar el paso |
| W / S | De frente / atrás |
| A / D (mantener) | Girar. Parado gira sobre sí mismo; andando, en curva |
| Q / E (mantener) | Costero a costero: desplazarse de lado |
| C | Agachaditos (baja el paso 35 cm) / volver arriba |
| X | Paramos. Si ya está parado, a tierra |
| V · rueda del ratón | Cambiar de cámara · acercar o alejar |
| M · N · H · R | Banda · voz del capataz · ayuda · reiniciar |

En móvil hay botones en pantalla con las mismas órdenes.

## Cómo funciona

- **Órdenes con retardo.** Cada orden tarda 0,45 s en cumplirse y la cuadrilla se mueve a golpe de bombo (88 por minuto, 60 cm por paso). Hay que anticiparse en las esquinas.
- **El paso son tres cuerpos apilados**: faldón y canastilla (hasta 1,50 m), candelería (hasta 2,60 m) y misterio (hasta 3,35 m). Un obstáculo solo cuenta si coincide en planta y en altura con alguno de ellos.
- **Colisiones** por separación de ejes (SAT) en planta: el paso es un rectángulo orientado; paredes, cables, balcones y macetas son segmentos, polígonos o círculos con su franja de altura.
- **Recorrido**: almacén → calle Alfarería (cable a 3,10 m, naranjos) → calle Feria (bolardos, balcones, cable a 3,05 m) → callejón del Agua (farol bajo y maceta) → plaza de San Roque → puerta del templo (3,00 m de ancho y 3,20 m de alto).
- **Nota sobre 10**: un punto menos por golpe y medio punto por cada 15 s por encima de 3:50.

Todo el código está en `index.html` (Three.js r128 desde cdnjs, sonido sintetizado con Web Audio y voz con la síntesis de voz del navegador).

## Siguientes fases

2. Más obstáculos y calles, y puntuación de lucimiento.
3. Compás real: importar una marcha en MP3 y detectar el bombo.
4. Editor de paso con piezas modulares.
5. Procesión completa con cortejo, banda y público.
6. Gestión de la hermandad a lo largo del año.
