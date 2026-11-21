# Capataz

Prototipo jugable en el navegador de un juego de Semana Santa en el que mandas un paso o un trono. El documento de diseño completo está en Claude Docs.

- `index.html` — **Portada**: elegir entre tronos (Málaga) y pasos (Sevilla).
- `mudanza.html` — **La mudanza** (etapa 1, primer prototipo): paso de costaleros.
- `trono.html` — **El trono** (etapa 2): trono de Málaga mandado con la campana, por un barrio de calles anchas.
- `paso.html` — **La procesión** (etapa 3): paso de misterio mandado con el llamador, con relevos de costaleros, por un barrio de calles estrechas.

## Niveles, permisos y calles (común a tronos y pasos)

- `ciudad.js` — motor de calles común: cada calle es una línea con curvas, un ancho que puede cambiar (calles que se estrechan) y la altura de sus cruces (cuestas). De ahí salen el suelo, las fachadas, las colisiones (con la altura del suelo bajo cada parte del trono o del paso), las zonas y la evaluación de permisos.
- `niveles.js` — los cuatro niveles, comunes a tronos y pasos (los pasos usan el mismo trazado a menor escala):
  1. **Ensayo en el polígono**: cuadrícula ancha, de noche y sin público.
  2. **Ensayo en las afueras**: curvas y contracurvas, y una calle que se estrecha en mitad de la curva.
  3. **Ensayo de esquinas y cuestas**: cruces que no son de 90°, esquina viva, una calle que se queda en 7,6 m y alguna cuesta.
  4. **La salida procesional**: la calle de la casa hermandad sube, se estrecha y gira; después, tres itinerarios hasta el recorrido oficial (o la carrera oficial).
- **Permisos:** para ensayar, el Ayuntamiento solo autoriza calles de las afueras o del polígono, sin obras ni avenidas con tráfico, y el ensayo tiene que volver a la nave. Para la procesión, el Ayuntamiento (sin obras y con anchura suficiente) y la Agrupación de Cofradías o el Consejo de Hermandades (que acabe en el recorrido oficial, que no use una calle reservada para otra cofradía y que se llegue a la hora). Sin permiso no se puede salir.
- **Cuestas por ciudad:** en Málaga casi no hay (alguna calle puntual), en Sevilla alguna más; Granada (Realejo, Albaicín) tendrá muchas y fuertes.
- **Ensayos con adversidades:** camiones, furgonetas y coches mal aparcados, contenedores, señales, ramas bajas, bolardos y vecinos curioseando; y durante el ensayo, imprevistos: un coche que se salta el corte y se queda atravesado, o curiosos que se meten delante.
- **Avance rápido (T o ⏩):** en los tramos sin nada cerca el tiempo va ×3; se corta solo si hay algo delante, cerca de un cruce o tras un golpe.
- **Banda:** síntesis de banda de música (tronos: metales con vibrato, acordes, tuba, bombo, caja, platillos) o de cornetas y tambores (pasos), con eco de calle; 5 marchas inventadas.
- **Progreso:** todos los niveles están abiertos; se recomienda empezar por el primero. La partida se guarda en los puntos de guardado, al terminar ciertas calles.

## El trono (etapa 2)

Eres el mayordomo de trono y llevas un trono de palio desde la nave de la casa hermandad hasta la entrada del recorrido oficial, antes de las 21:30, por un barrio de cuatro filas de calles (itinerarios de 600 a 800 m). Antes de salir eliges el itinerario en un plano.

| Tecla | Orden |
|---|---|
| Espacio ×7 | Exactamente 7 toques suaves y seguidos: los hombres de trono se colocan (con 6 u 8 la levantá sale peor; con menos o más, desigual) |
| F | Toque fuerte: meten el hombro |
| G | Toque grande: ¡arriba! La calidad de la levantá depende de los 7 toques, el ritmo y el tiempo entre el toque fuerte y el toque grande |
| Espacio | En marcha: parar. Parado: bajar a la mesa |
| W / S | Adelante / atrás (con inercia: tarda en arrancar y en frenar). En marcha, W otra vez da más paso (0,75 y 1 m/s, cansa mucho más) y S lo afloja |
| A / D (mantener) | Derecha adelante, izquierda atrás (y al revés): girar |
| Q / E (mantener) | De lado |
| Z | Mecida: lucimiento, pero el trono ocupa más y cansa más |
| P | A pulso: sube 45 cm; luce mucho ante la tribuna |
| B | ¡Música!: pedir una marcha a la banda |
| V · M · N · H · R | Cámara · sonido de la banda · voz · ayuda · reiniciar |

- **Cuerpos del trono:** varales y hombres de trono (4,4 × 13 m, hasta 1,9 m), mesa y candelería (hasta 3,1 m), palio (hasta 5,35 m; las barras se balancean mucho con la mecida y poco al andar) y cuatro arbotantes de hojarasca (dorados o de plata) que se abren en diagonal desde las esquinas del cajillo (5,1 m de ancho entre 3,15 y 4,75 m de alto). Si un arbotante choca, se rompen y se apagan tulipas, que quedan apuntadas como desperfectos.
- **Ensayos:** no sale el trono completo, solo la estructura: varales y mesa cargada con sacos de arena, sin cajillo, imagen, candelería, palio ni arbotantes (y sus colisiones llegan a 2,45 m). Para que los ensayos sigan teniendo dificultad, los obstáculos bajan a esa altura: toldos de comercios y marquesinas de parada que salen de la fachada (a 2,15 m en tronos y 1,35 m en pasos), ramas bajas a 2,1 m (1,3 m) y señales a 2,05 m (1,3 m). En los pasos sale solo la parihuela de hierro con sus trabajaderas y sacos, y se ven los costaleros enteros.
- **Cansancio sin relevos:** solo baja con el trono en el suelo. Si se descansa más de 35 s, la cuadrilla se enfría y la levantá sale peor.
- **Retardo:** las voces tardan 0,7 s en cumplirse (los capataces de las esquinas las repiten); la campana es inmediata.
- **Itinerario:** el barrio tiene tres calles que suben hacia el recorrido oficial (Carretería, la de los Balcones y Granada) y tres que las cruzan (del Ángel/Compañía, Álamos y Císter), con la plaza de la Tribuna. Se elige tocando los cruces en el plano o con uno de los tres itinerarios propuestos. Las calles del itinerario las corta la policía y se llenan de público; las demás tienen coches aparcados, y salirse del itinerario resta un punto («la Agrupación lo apuntará»).
- **Cada calle tiene su dificultad:** ficus alternos en Carretería, balcones a 4,4 m que dejan unos centímetros a los arbotantes en la de los Balcones, naranjos en Granada, un andamio en Álamos, semáforos con el brazo metido, guirnaldas y cables a los que no se puede subir a pulso. Los cruces tienen chaflanes para poder girar el trono sobre sí mismo.
- **Momentos:** parado delante de la iglesia de Santiago, alguien canta una saeta; delante del convento de las Clarisas, en silencio, cantan las monjas. La tribuna de la plaza y la peña de calle Císter dan lucimiento a la mecida y a la levantá a pulso.
- **Puntos de guardado:** la partida se guarda al llegar a ciertos cruces, al terminar cada calle larga (marcados con un aro en el plano); en la pantalla de inicio aparece «Continuar la partida».
- **Gráficos:** reflejos de entorno para que el oro y la plata parezcan metal, resplandor (bloom) de velas, tulipas y farolas, sombras, Virgen con rostro pintado, rostrillo, corona imperial y ráfaga, público con cuerpo, brazos y piernas. El botón «Gráficos» baja la calidad en móviles lentos (altos: todo; medios: sin sombras; bajos: sin resplandor).
- **Cortejo y banda según la hermandad:** en la salida procesional, delante del trono va el cortejo por el itinerario elegido (cruz de guía y faroles, tramos de nazarenos con cirio abiertos por sus insignias, presidencia, acólitos con ciriales e incensarios) y detrás la banda, en filas y con su uniforme. Todo sale de la ficha de la hermandad (`HERMANDADES` en `trono.html`): número de nazarenos, colores de túnica y capirote, insignias, acólitos, banda (propia o contratada, músicos, nivel, uniforme) y prestigio, que también decide cuánto público llena las aceras. Hay dos fichas de prueba hasta que exista el modo historia: `trono.html?hermandad=veterana` (por defecto, 360 nazarenos y banda propia de 72 músicos) y `?hermandad=nueva` (46 nazarenos y una banda contratada de 26). En los ensayos solo sale el trono.
- **Calle vestida y público vivo:** en la salida, los balcones del itinerario cuelgan colgaduras (damasco rojo, rojo y gualda o el color de la hermandad), hay banderines de lado a lado a 7,5 m (por encima del palio y de los arbotantes) y cera y pétalos en el suelo. Cuanto más prestigio, más se vuelca el barrio. El público se balancea y cambia el peso de pie, y se agita en las levantás y cuando suena la banda. La cámara «Desde arriba» (V) es ahora cenital inclinada, como en los juegos de móvil.
- **Virgen en 3D:** `modelos/virgen.glb` (1,1 MB) se generó con TRELLIS (Space `trellis-community/TRELLIS`) a partir de la foto de frente de `referencias/` y se optimizó con gltf-transform (textura JPEG de 1024 px). Se carga con GLTFLoader bajo el palio, de la peana (2,9 m) a la cruz de la ráfaga (4,42 m), sin tocar el techo de palio (4,51 m). La ráfaga del modelo (un aro tosco) se quita y se pone la de la foto, recortada con transparencia (`modelos/rafaga.png`), como un plano detrás de la corona. El manto se genera al cargar: nace en la cabeza, se ciñe a la espalda de la imagen siguiendo su forma real y se abre en cola por la trasera del trono. Si el modelo no carga (sin conexión o abierto como `file://`), queda la Virgen procedural con su manto. Para verla hay que servir la carpeta por HTTP (p. ej. `python3 -m http.server`).

## La procesión (etapa 3)

Eres el capataz de un paso de misterio y lo llevas desde el templo hasta la entrada en la carrera oficial, antes de las 19:45, por un barrio de calles estrechas y encaladas (itinerarios de 530 a 600 m). Usa el mismo motor y la misma base de ciudad que el trono (`CIU` describe la cuadrícula de calles de cada ciudad y lo demás se genera).

| Tecla | Orden |
|---|---|
| Espacio | Llamador. En tierra: un golpe, «¡Atención, preparados!»; otro al poco, «¡A esta es!» y el paso sube. En marcha: ¡paramos! Parado: ¡ahí quedó!, a tierra |
| W / S | ¡De frente! / atrás; en marcha, más paso o menos |
| A / D | Izquierda alante, derecha atrás (y al revés) |
| Q / E | Costero a costero |
| C | ¡Agachaditos!: el paso baja 35 cm para pasar bajo cables (3,05–3,1 m) y balcones |
| X | Relevo, con el paso en tierra: entra otra cuadrilla y el cansancio vuelve a cero, a cambio de tiempo |
| Z · P · B | Mecida · a pulso · ¡música! |

- **Calles:** balcones a 2,6 m (calle Feria), naranjos y cables bajos (Alfarería, Castellar, Cuna, Cabeza), el callejón del Agua (4,4 m, con faroles de forja y macetas, sin sitio para el público), la saeta de Santiago, las monjas del convento y la peña.
- **Itinerario y guardado:** igual que el trono: se elige en el plano y se guarda en los puntos de guardado.

## La mudanza (etapa 1)

Prototipo jugable en el navegador. Eres el capataz de una cuadrilla y tienes que llevar un paso de misterio desde el almacén de la hermandad hasta la parroquia de San Roque, sin golpearlo, y dejarlo a tierra dentro del templo.

Es la fase 1 del plan: comprobar si la mecánica de mandar el paso es divertida antes de invertir en arte, música o gestión.

## Cómo jugar

Abre `mudanza.html` en un navegador (necesita conexión para cargar Three.js y las fuentes).

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

Gráficos: los mismos que el trono (reflejos de metal, resplandor de velas y faroles, sombras, botón «Gráficos»), canastilla tallada en oro, faldón de terciopelo bordado, guardabrisas de cristal en los candelabros, figuras del misterio con rostro pintado y vecinos esperando en la plaza de San Roque y en los balcones de calle Feria.

Todo el código está en `index.html` (Three.js r128 desde cdnjs, sonido sintetizado con Web Audio y voz con la síntesis de voz del navegador).

## Siguientes fases

2. Más obstáculos y calles, y puntuación de lucimiento.
3. Compás real: importar una marcha en MP3 y detectar el bombo.
4. Editor de paso con piezas modulares.
5. Procesión completa con cortejo, banda y público.
6. Gestión de la hermandad a lo largo del año.
