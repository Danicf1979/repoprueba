# Especificación: trono y pasos en Godot (estilo cabezón)

Noviembre de 2026. Propuesta para revisar antes de implementar. Sigue el camino del nazareno cabezón: modelos hechos
en Blender por script, esqueleto y animaciones dentro del GLB, y escena en Godot.

## 1. Qué se hace primero

1. **Trono de palio de Málaga**, porque es el que ya tiene toda la mecánica en `trono.html` (varales, campana,
   mecida, palio con inercia, arbotantes con tulipas que se rompen, cansancio, levantá).
2. **Paso de palio de Sevilla** después, reutilizando casi todo: cambian la parihuela, los costaleros (ocultos bajo
   los faldones), el llamador y las reglas.
3. **Pasos de misterio** al final (figuras secundarias y Cristo), porque necesitan más modelos de personas.

## 2. Escala: un mundo «de juguete»

Los muñecos miden poco más de 1 m sin capirote y casi todo es cabeza. Si el trono va a tamaño real, la gente
parece niños debajo; si se encoge todo por igual, el trono pierde grandeza. Propuesta:

- **El varal va al hombro del hombre de trono cabezón** (alrededor de 0,8 m). Los hombres de trono son algo más altos
  que los nazarenos cabezones para que se vean bajo el varal.
- **Lo alto se exagera**: palio, candelería, imagen y arbotantes van más altos de lo que tocaría a esa escala, para
  que el trono siga imponiendo (orientativo: palio a unos 3 m, el triple de la altura del varal).
- **Las calles y obstáculos** (balcones, cables, ramas, toldos) se escalan con el mismo factor, para que la mecánica
  de alturas de `trono.html` siga funcionando: todas sus medidas se multiplican por un factor común `ESC`.

## 3. El trono como juego de piezas (Blender por script)

Cada pieza se modela una vez y se repite. El trono se monta con parámetros que vienen de la **gestión de la
hermandad**.

| Pieza | Cómo | Parámetros de gestión |
|---|---|---|
| Mesa y estructura | Cajón con patas; en los ensayos sale solo la estructura con los sacos (como ahora) | Tamaño: nº de varales y largo |
| Varales | Torneados, con cabezas de varal y remates delanteros | Nº de varales (4–6), metal |
| Cajillo / canastilla | Molduras, cartelas y cantoneras repetidas, relieve en la textura (mapa de normales) | Oro / plata, nivel de talla |
| Faldones | Terciopelo liso con galón en paños y flecos (sin bordar: el bordado y el respiradero son de los pasos) | Color del terciopelo |
| Candelería | Un candelero y un cirio repetidos cientos de veces (MultiMesh), llama animada en el shader | Nº de tandas, cera blanca / tiniebla |
| Jarras y flores | Una jarra y un ramo repetidos | Tipo y color de flor |
| Arbotantes y faroles | Con tulipas que se rompen al chocar (ya existe en la web) | Nº de arbotantes |
| Varales de palio | 12, torneados con nudos | Metal |
| Techo y bambalinas | Terciopelo bordado; bambalinas con huesos que se mecen (más en la mecida, menos al andar, como ahora) | Color, bordado |
| Peana, imagen y manto | Ver punto 4 | — |
| Campana | En el frente, con su mazo | — |

**Catálogo para la gestión** (cada trono cambia; según las fotos de tronos de Málaga):

- **Manto de cola**: nace en punta detrás de la corona, baja en rampa abombada, cada vez más ancho, y acaba
  redondeado sobre los varales traseros, con los bordes caídos. Varía el color del terciopelo (granate, morado, azul,
  negro, blanco, rojo) y el bordado: un gran dibujo simétrico con motivo central (escudo, paloma, anagrama) y cenefa.
- **Bordado** (palio —techo y bambalinas— y manto, por separado; los faldones del trono van lisos con galón): cinco niveles, del más barato al más caro, con su plazo de
  taller orientativo: liso (solo galón, una temporada), sencillo (motivos sueltos, un año), medio (dos años),
  cargado (roleos gruesos y filigrana, tres o cuatro años) y riquísimo (casi todo oro, a realce, cinco años o más).
  Cuanto más cargado, más prestigio al estrenarlo.
- **Cabezas de varal**: tallas doradas de hojarasca, madera tallada, plata cincelada.
- **Varales**: forrados de plata o metal, o de madera.
- **Arbotantes**: árboles de hojarasca dorada (como la Paloma) o de plata con brazos en voluta; nº de tulipas;
  **cuatro (en las esquinas) o solo los dos de atrás**.
- **Cajillo**: plata cincelada con capillas e imágenes, madera dorada con figuras, madera tallada en su color.
- **Candelería**: candeleros bajos y cirios altos de color hueso en tandas que suben hasta el pecho de la imagen.
- **Flores**: jarras con ramos altos por los costados y friso por el borde delantero; tipo y color.
- **Palio**: color y bordado del terciopelo; bambalinas altas en ondas con fleco de bellotas; crestería o corona en
  la bambalina delantera.

La luz del trono la dan las velas: emisión y resplandor siempre, y solo unas pocas luces reales (unas 4–6), para
que vaya en móvil.

## 4. La imagen (decisión pendiente)

La Virgen es lo más delicado. Opciones:

- **A. Imagen realista** (el modelo de TRELLIS que ya tenemos, con manto y ráfaga): respetuosa, pero contrasta con
  los muñecos.
- **B. Imagen estilizada en Blender**: rostro sereno y sencillo, proporciones algo más suaves, sin caricatura. Encaja
  con el estilo; hay que cuidarla mucho para no resultar irrespetuosa.
- **C. Mezcla**: rostro y manos de la imagen realista, todo lo demás (manto, saya, corona, ráfaga) modelado.

Recomendación: **B**, hecha con mimo y enseñada antes de seguir.

## 5. La gente del trono

- **Hombres de trono (Málaga)**: van a los dos lados de cada varal, con la mano en el varal. **Cómo visten lo
  decide la hermandad en el modo gestión, y por separado para cada trono** (en el Sepulcro de Málaga, los del Cristo
  van de traje y los de la Virgen con túnica sin faraona):
  1. **Traje** (chaqueta oscura, corbata), cara descubierta.
  2. **Túnica sin faraona**, cara descubierta.
  3. **Túnica con faraona**, cara descubierta.
  4. **Túnica con faraona y la cara tapada.**

  Es un mismo cuerpo con piezas de ropa intercambiables (traje, túnica, faraona abierta, faraona cerrada), con los
  colores de la hermandad. Para las opciones 1–3 hace falta una cara sencilla: ojos y boca pintados en la textura,
  con varias expresiones (normal, esfuerzo, cansancio, emoción).
- **Mayordomo y capataz** en la campana, **hombres de campana y de varal** delante.
- **Costaleros (Sevilla)**: bajo los faldones; se ven los pies, y en los relevos salen con el costal y la faja.

Animaciones (esqueleto propio en Blender; Mixamo solo si hace falta algo que no salga bien a mano):

| Animación | Quién | Qué hace |
|---|---|---|
| Andar a compás | Hombres de trono, costaleros | Paso corto; su ritmo lo marca la velocidad del trono para que no patinen |
| Mecida | Todos los de debajo | Balanceo del cuerpo a la vez, de lado a lado |
| Levantá | Todos | Agacharse un poco y empujar hacia arriba al toque |
| Arriar | Todos | Bajar el trono despacio |
| Parado | Todos | Respirar, recolocarse la túnica |
| Cansancio | Todos | Cabeza baja, paso pesado (ligado al cansancio del juego) |
| Relevo | Costaleros / hombres de trono | Salir y entrar |

Las manos se quedan pegadas al varal aunque el cuerpo se mueva (IK de Godot).

## 6. Movimiento del trono

Se pasa a GDScript la lógica que ya funciona en `trono.html`, con los mismos números:

- Inercia al arrancar y parar, curvas y giros, cuestas.
- Mecida con su amplitud, palio con inercia y bambalinas.
- Levantá y arriada a toques de campana.
- Choques: arbotantes, tulipas, balcones, cables, ramas, toldos de los ensayos.
- Cansancio de la cuadrilla, que se nota en el paso y en las caras.

El cuerpo del trono no es un objeto de física: lo mueve nuestro código, como en la web. Los hombres de trono leen
ese movimiento para animarse.

## 7. Rendimiento (objetivo: móvil de gama media a 30 fps)

- Hasta ahora las capturas usan efectos de ordenador (luz global SDFGI, niebla volumétrica) que el modo móvil de
  Godot no tiene. Se diseñará la luz para el **modo Mobile** desde el principio y se compararán las dos versiones.
- Velas, flores, candeleros y cartelas como MultiMesh (miles de copias por el coste de una).
- Hombres de trono: los de los varales de fuera con animación completa; los de dentro, más sencillos o sin piernas
  (no se ven). Nivel de detalle por distancia.
- Presupuesto orientativo del trono completo: 250–300 mil triángulos.

## 8. Fases y lo que se entrega en cada una

| Fase | Contenido | Entrega para revisar |
|---|---|---|
| 1 | Trono de palio cabezón **quieto**: juego de piezas, materiales, luz de velas, imagen (opción elegida) | Capturas de frente, lateral, cenital y de noche en la calle |
| 2 | Hombres de trono con cara, esqueleto y animaciones; trono que anda, se mece, para, levanta y arría con la lógica de la web | Vídeo |
| 3 | Escena jugable mínima: trono + cortejo de nazarenos + calle con obstáculos, con los controles del juego web | Vídeo y versión para probar en el ordenador |
| 4 | Paso de palio sevillano con costaleros, llamador y relevos | Capturas y vídeo |
| 5 | Variantes de gestión (oro/plata, colores, flores, tamaño) y pasos de misterio | Capturas |

## 9. Decisiones que necesito antes de empezar

1. ¿Escala «de juguete» del punto 2?
2. ¿Imagen A, B o C?
3. ¿Empezamos por el trono de palio de Málaga?

## Para más adelante: nazarenos con vida propia

Cuando esté todo el cortejo: que los nazarenos se desordenen un poco por su cuenta (se paran, se giran a hablar entre
ellos, se separan de la fila, se adelantan), y que el jugador tenga que **llamarles la atención** (diputados de
tramo, celadores) para que el cortejo vuelva a ir ordenado. Afecta a la puntuación y a la imagen de la hermandad
ante la prensa y el Consejo o la Agrupación.
