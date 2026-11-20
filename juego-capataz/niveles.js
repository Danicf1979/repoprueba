/* Niveles de Capataz, comunes a tronos y pasos (los pasos usan el mismo trazado a menor escala y con calles más
 * estrechas). Van de menos a más: ensayos en el polígono y en las afueras, con permiso del Ayuntamiento, y la salida
 * procesional por el centro, con permiso del Ayuntamiento y de la Agrupación (o el Consejo).
 * nodos: [x, z, altura, opciones]. calles: w puede ser un número o [[fracción, ancho], ...] (calles que se estrechan);
 * via: puntos de control para curvas. cosas: lo que hay en cada calle (u = fracción del tramo útil, lado: 1 izquierda,
 * -1 derecha según se va de a a b). */
(function () {
  'use strict';
  const NIVELES = [
    {
      id: 'poligono', titulo: 'Ensayo en el polígono', modo: 'ensayo', estilo: 'industrial',
      resumen: 'Calles anchas y en cuadrícula, de noche y sin público. Para aprender a levantar, andar y girar. El Ayuntamiento solo da permiso en calles del polígono o de las afueras, y el ensayo tiene que volver a la nave.',
      horaInicio: 22 * 60, horaLimite: 24 * 60 + 30, largoMax: 900,
      nave: { x: 0, z: 0, a: 0, ancho: 12, fondo: 18, puerta: 6.4, nombre: 'la nave del polígono' },
      nodos: {
        S: [0, 0, 0], A: [0, 60, 0, { redondeo: 9 }], B: [80, 60, 0, { redondeo: 9 }], C: [80, 170, 0, { redondeo: 9 }],
        D: [0, 170, 0, { redondeo: 9 }], E: [-80, 170, 0, { redondeo: 9 }], F: [-80, 60, 0, { redondeo: 9 }], G: [0, 260, 0, { redondeo: 12 }], H: [80, 260, 0, { redondeo: 9 }],
      },
      calles: [
        { id: 'torneros', a: 'S', b: 'A', nombre: 'calle Torneros', w: 16, zona: 'poligono', recta: true },
        { id: 'fundidores', a: 'A', b: 'B', nombre: 'calle Fundidores', w: 15, zona: 'poligono', recta: true, cosas: [{ tipo: 'camion', u: 0.45, lado: 1 }] },
        { id: 'herreros', a: 'B', b: 'C', nombre: 'calle Herreros', w: 15, zona: 'poligono', recta: true, cosas: [{ tipo: 'camion', u: 0.6, lado: -1 }, { tipo: 'arboles', cada: 30 }] },
        { id: 'carpinteros', a: 'C', b: 'D', nombre: 'calle Carpinteros', w: 14, zona: 'poligono', recta: true },
        { id: 'ebanistas', a: 'D', b: 'A', nombre: 'calle Ebanistas', w: 14, zona: 'poligono', recta: true, cosas: [{ tipo: 'cable', u: 0.5 }] },
        { id: 'tintoreros', a: 'D', b: 'E', nombre: 'calle Tintoreros', w: 14, zona: 'poligono', recta: true },
        { id: 'curtidores', a: 'E', b: 'F', nombre: 'calle Curtidores', w: 14, zona: 'poligono', recta: true, cosas: [{ tipo: 'arboles', cada: 28 }] },
        { id: 'alfareros', a: 'F', b: 'A', nombre: 'calle Alfareros', w: 14, zona: 'poligono', recta: true, cosas: [{ tipo: 'camion', u: 0.5, lado: -1 }] },
        { id: 'velazquez', a: 'D', b: 'G', nombre: 'avenida de Velázquez', w: 22, zona: 'afueras', trafico: true, recta: true },
        { id: 'fresadores', a: 'C', b: 'H', nombre: 'calle Fresadores', w: 14, zona: 'poligono', obras: true, recta: true, cosas: [{ tipo: 'vallas', u: 0.5 }] },
        { id: 'torneros2', a: 'H', b: 'G', nombre: 'calle Matriceros', w: 14, zona: 'poligono', recta: true },
      ],
      rutas: { este: { nombre: 'Vuelta por Herreros', nodos: ['S', 'A', 'B', 'C', 'D', 'A', 'S'] }, oeste: { nombre: 'Vuelta por Curtidores', nodos: ['S', 'A', 'F', 'E', 'D', 'A', 'S'] } },
      puntos: ['B', 'C', 'D', 'E', 'F'],
    },
    {
      id: 'afueras', titulo: 'Ensayo en las afueras', modo: 'ensayo', estilo: 'afueras',
      resumen: 'Curvas y contracurvas, y una calle que se estrecha en mitad de la curva. Hay que ir corrigiendo de lado sin parar. La avenida tiene tráfico y una calle está en obras: el Ayuntamiento no las autoriza.',
      horaInicio: 22 * 60, horaLimite: 24 * 60 + 40, largoMax: 1000,
      nave: { x: 0, z: 0, a: 0, ancho: 12, fondo: 18, puerta: 6.4, nombre: 'la nave de las afueras' },
      nodos: { S: [0, 0, 0], A: [0, 50, 0, { redondeo: 9 }], B: [40, 175, 0, { redondeo: 9 }], C: [0, 275, 0, { redondeo: 9 }], D: [-60, 190, 0, { redondeo: 9 }], E: [115, 60, 0, { redondeo: 12 }] },
      calles: [
        { id: 'jacarandas', a: 'S', b: 'A', nombre: 'calle Jacarandas', w: 14, zona: 'afueras', recta: true },
        { id: 'ermita', a: 'A', b: 'B', nombre: 'camino de la Ermita', w: [[0, 12], [0.4, 8.6], [0.62, 8.6], [1, 11]], via: [[32, 88], [8, 130]], zona: 'afueras', cosas: [{ tipo: 'arbol', u: 0.15, lado: -1 }, { tipo: 'arbol', u: 0.85, lado: 1 }] },
        { id: 'arroyo', a: 'B', b: 'C', nombre: 'calle del Arroyo', w: 10.5, via: [[58, 218], [14, 240]], zona: 'afueras', cosas: [{ tipo: 'cable', u: 0.5 }] },
        { id: 'olmos', a: 'C', b: 'D', nombre: 'calle Olmos', w: 11, via: [[-35, 250]], zona: 'afueras', cosas: [{ tipo: 'arboles', cada: 26 }] },
        { id: 'retamas', a: 'D', b: 'A', nombre: 'calle Retamas', w: 11, via: [[-62, 120], [-28, 75]], zona: 'afueras', cosas: [{ tipo: 'farolas' }] },
        { id: 'andalucia', a: 'A', b: 'E', nombre: 'avenida de Andalucía', w: 22, zona: 'afueras', trafico: true, recta: true },
        { id: 'molinos', a: 'B', b: 'E', nombre: 'calle Molinos', w: 12, zona: 'afueras', obras: true, cosas: [{ tipo: 'vallas', u: 0.5 }] },
      ],
      rutas: { ermita: { nombre: 'Por la Ermita', nodos: ['S', 'A', 'B', 'C', 'D', 'A', 'S'] }, reves: { nombre: 'Al revés, por Retamas', nodos: ['S', 'A', 'D', 'C', 'B', 'A', 'S'] } },
      puntos: ['B', 'C', 'D'],
    },
    {
      id: 'cuestas', titulo: 'Ensayo de esquinas y cuestas', modo: 'ensayo', estilo: 'afueras',
      resumen: 'Cruces que no son de 90 grados, una esquina viva sin chaflán, una calle que se queda en nada y alguna cuesta. En Málaga y en Sevilla las cuestas son pocas y suaves; en Granada (el Realejo, el Albaicín) serán muchas y fuertes.',
      horaInicio: 22 * 60, horaLimite: 24 * 60 + 50, largoMax: 1100,
      nave: { x: 0, z: 0, a: 0, ancho: 12, fondo: 18, puerta: 6.4, nombre: 'la nave' },
      nodos: { S: [0, 0, 0], A: [0, 45, 0, { redondeo: 9 }], B: [0, 140, 7, { redondeo: 9 }], C: [58, 200, 8.5, { redondeo: 7.5 }], D: [58, 268, 8.5], E: [-40, 268, 4.5, { redondeo: 9 }], F: [-50, 145, 2, { redondeo: 9 }] },
      calles: [
        { id: 'lagar', a: 'S', b: 'A', nombre: 'calle Lagar', w: 14, zona: 'afueras', recta: true },
        { id: 'vid', a: 'A', b: 'B', nombre: 'cuesta de la Vid', w: 12, zona: 'afueras', recta: true, cosas: [{ tipo: 'farolas' }] },
        { id: 'sesgada', a: 'B', b: 'C', nombre: 'calle Sesgada', w: 11.5, zona: 'afueras', recta: true },
        { id: 'escuadra', a: 'C', b: 'D', nombre: 'calle Escuadra', w: 13, zona: 'afueras', recta: true },
        { id: 'angosta', a: 'D', b: 'E', nombre: 'calle Angosta', w: [[0, 13], [0.45, 7.6], [0.6, 7.6], [1, 12]], zona: 'afueras', recta: true, cosas: [{ tipo: 'balcones', lado: 1, cada: 14 }] },
        { id: 'bajada', a: 'E', b: 'F', nombre: 'calle de la Bajada', w: 11, via: [[-58, 210]], zona: 'afueras' },
        { id: 'diagonal', a: 'F', b: 'A', nombre: 'calle Diagonal', w: 12, zona: 'afueras', recta: true, cosas: [{ tipo: 'arboles', cada: 30 }] },
        { id: 'atajo', a: 'B', b: 'F', nombre: 'calle del Atajo', w: 9, zona: 'afueras', obras: true, recta: true, cosas: [{ tipo: 'vallas', u: 0.5 }] },
      ],
      rutas: { vuelta: { nombre: 'La vuelta de las cuestas', nodos: ['S', 'A', 'B', 'C', 'D', 'E', 'F', 'A', 'S'] } },
      puntos: ['B', 'C', 'D', 'E', 'F'],
    },
    {
      id: 'salida', titulo: 'La salida procesional', modo: 'procesion', estilo: 'centro',
      resumen: 'El día grande, por el centro. La salida es lo más difícil: la calle de la casa hermandad sube, se estrecha y gira, y acaba en una esquina viva. Después eliges itinerario hasta la entrada en el recorrido oficial, y tienen que aprobarlo el Ayuntamiento y la Agrupación (o el Consejo).',
      horaInicio: 18 * 60 + 30, horaLimite: 21 * 60 + 15,
      nave: { x: 0, z: 0, a: 0, ancho: 12, fondo: 18, puerta: 6.6, nombre: 'la casa hermandad' },
      nodos: {
        S: [0, 0, 3], A: [12, 78, 6], B: [72, 112, 6, { plaza: { hx: 16, hz: 16 }, nombre: 'la plaza de la Tribuna' }], C: [72, 225, 4, { redondeo: 8.5 }], D: [72, 335, 3, { redondeo: 9 }], M: [72, 420, 3],
        E: [155, 205, 6, { redondeo: 9 }], F: [155, 315, 4, { redondeo: 9 }], G: [-20, 190, 8, { redondeo: 9 }], H: [-10, 300, 5, { redondeo: 9 }],
      },
      calles: [
        { id: 'cofradia', a: 'S', b: 'A', nombre: 'calle Cofradía', w: [[0, 10.5], [0.45, 7.8], [0.7, 7.8], [1, 9.5]], via: [[9, 32], [2, 55]], zona: 'centro', cosas: [{ tipo: 'balcones', lado: -1, cada: 12 }] },
        { id: 'postigo', a: 'A', b: 'B', nombre: 'calle Postigo', w: 10.5, zona: 'centro', recta: true, cosas: [{ tipo: 'farol', u: 0.4, lado: 1 }] },
        { id: 'granada', a: 'B', b: 'C', nombre: 'calle Granada', w: 10, zona: 'centro', recta: true, cosas: [{ tipo: 'balcones', lado: 1, cada: 12 }, { tipo: 'guirnalda', u: 0.6 }] },
        { id: 'nueva', a: 'C', b: 'D', nombre: 'calle Nueva', w: 11, zona: 'centro', recta: true, cosas: [{ tipo: 'terraza', u: 0.3, lado: -1 }, { tipo: 'quiosco', u: 0.7, lado: 1 }] },
        { id: 'larga', a: 'D', b: 'M', nombre: 'calle Larga', w: 14, zona: 'centro', recta: true },
        { id: 'carreteria', a: 'B', b: 'E', nombre: 'calle Carretería', w: 12, via: [[125, 128]], zona: 'centro', cosas: [{ tipo: 'iglesia', u: 0.55, lado: 1 }] },
        { id: 'alamos', a: 'E', b: 'F', nombre: 'calle Álamos', w: 12, zona: 'centro', recta: true, cosas: [{ tipo: 'pena', u: 0.5, lado: -1 }, { tipo: 'arboles', cada: 30 }] },
        { id: 'cister', a: 'F', b: 'D', nombre: 'calle Císter', w: 12, zona: 'centro', recta: true, cosas: [{ tipo: 'semaforo', u: 0.5, lado: 1 }] },
        { id: 'compania', a: 'C', b: 'E', nombre: 'calle Compañía', w: 11, zona: 'centro', recta: true, reservada: 'la Cofradía del Rocío' },
        { id: 'alcazabilla', a: 'B', b: 'G', nombre: 'calle Alcazabilla', w: 11, zona: 'centro', recta: true, cosas: [{ tipo: 'farolas' }] },
        { id: 'santamaria', a: 'G', b: 'H', nombre: 'calle Santa María', w: 10, via: [[-32, 248]], zona: 'centro', cosas: [{ tipo: 'convento', u: 0.5, lado: -1 }] },
        { id: 'angel', a: 'H', b: 'D', nombre: 'calle del Ángel', w: 11, zona: 'centro', recta: true, cosas: [{ tipo: 'guirnalda', u: 0.5 }] },
        { id: 'mosquera', a: 'G', b: 'C', nombre: 'calle Mosquera', w: 9, zona: 'centro', obras: true, recta: true, cosas: [{ tipo: 'vallas', u: 0.5 }] },
      ],
      meta: { calle: 'larga', nodo: 'M', u: 42 },
      rutas: { granada: { nombre: 'Por calle Granada', nodos: ['S', 'A', 'B', 'C', 'D', 'M'] }, carreteria: { nombre: 'Por Carretería', nodos: ['S', 'A', 'B', 'E', 'F', 'D', 'M'] }, santamaria: { nombre: 'Por Santa María', nodos: ['S', 'A', 'B', 'G', 'H', 'D', 'M'] } },
      puntos: ['B', 'C', 'E', 'G', 'F', 'H', 'D'],
    },
  ];
  // Versión para pasos: mismo trazado, más pequeño y con calles más estrechas
  function adaptar(n, k, kw, kh) {
    const o = JSON.parse(JSON.stringify(n));
    for (const [id, v] of Object.entries(o.nodos)) { v[0] *= k; v[1] *= k; v[2] = (v[2] || 0) * kh; if (v[3]) { if (v[3].redondeo) v[3].redondeo *= kw * 1.1; if (v[3].plaza) { v[3].plaza.hx *= k; v[3].plaza.hz *= k; } } }
    for (const c of o.calles) { c.w = typeof c.w === 'number' ? c.w * kw : c.w.map(([f, w]) => [f, w * kw]); if (c.via) c.via = c.via.map(([x, z]) => [x * k, z * k]); }
    o.nave = { ...o.nave, ancho: 6, fondo: 9, puerta: 3.6 };
    if (o.meta) o.meta.u *= k;
    if (o.largoMax) o.largoMax *= k;
    return o;
  }
  // Las cuestas dependen de la ciudad: en Málaga casi no hay (alguna calle puntual), en Sevilla alguna más
  // y en Granada (Realejo, Albaicín) muchas y fuertes. Los trazados guardan la altura «de Granada» y cada ciudad la rebaja.
  const CUESTAS = { malaga: 0.3, sevilla: 0.5, granada: 1.4 };
  const conCuestas = (n, f) => { const o = JSON.parse(JSON.stringify(n)); for (const v of Object.values(o.nodos)) v[2] = (v[2] || 0) * f; return o; };
  window.NIVELES = { trono: NIVELES.map((n) => conCuestas(n, CUESTAS.malaga)), paso: NIVELES.map((n) => conCuestas(adaptar(n, 0.62, 0.46, 0.62), CUESTAS.sevilla)), CUESTAS };
})();
