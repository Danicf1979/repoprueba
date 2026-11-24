/* Motor de calles de Capataz, común a tronos y pasos.
 * Cada nivel describe su barrio como datos: cruces (nodos) con su altura y calles con su trazado (puntos de control,
 * curvas), su ancho (que puede cambiar a lo largo de la calle) y sus marcas (zona, obras, tráfico).
 * Con eso se «estampa» el suelo transitable en una rejilla fina, y de ahí salen las fachadas, las colisiones,
 * las alturas del suelo (cuestas), las zonas para los objetivos y la evaluación de los permisos.
 * No depende de Three.js: solo calcula. */
(function () {
  'use strict';
  const lerp = (a, b, k) => a + (b - a) * k;
  function catmull(p0, p1, p2, p3, t) {
    const t2 = t * t, t3 = t2 * t;
    return [0, 1].map((i) => 0.5 * (2 * p1[i] + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2 + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3));
  }
  function anchoEn(w, k) {
    if (typeof w === 'number') return w;
    for (let i = 0; i + 1 < w.length; i++) if (k <= w[i + 1][0]) return lerp(w[i][1], w[i + 1][1], (k - w[i][0]) / Math.max(1e-6, w[i + 1][0] - w[i][0]));
    return w[w.length - 1][1];
  }
  function dentroDe(pts, x, z) {
    let d = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const [xi, zi] = pts[i], [xj, zj] = pts[j];
      if ((zi > z) !== (zj > z) && x < ((xj - xi) * (z - zi)) / (zj - zi) + xi) d = !d;
    }
    return d;
  }
  function simplificar(pts, tol) {   // Douglas-Peucker sobre una polilínea abierta
    if (pts.length < 3) return pts;
    const [ax, az] = pts[0], [bx, bz] = pts[pts.length - 1];
    let dmax = 0, idx = 0; const L = Math.hypot(bx - ax, bz - az) || 1e-9;
    for (let i = 1; i < pts.length - 1; i++) { const d = Math.abs((bx - ax) * (az - pts[i][1]) - (ax - pts[i][0]) * (bz - az)) / L; if (d > dmax) { dmax = d; idx = i; } }
    if (dmax <= tol) return [pts[0], pts[pts.length - 1]];
    const a = simplificar(pts.slice(0, idx + 1), tol), b = simplificar(pts.slice(idx), tol);
    return a.slice(0, -1).concat(b);
  }

  function crear(CIU) {
    const NODOS = {};
    for (const [id, n] of Object.entries(CIU.nodos)) NODOS[id] = { id, x: n[0], z: n[1], y: n[2] || 0, ...(n[3] || {}) };
    const TRAMOS = CIU.calles.map((c) => ({ ...c }));
    const TR = Object.fromEntries(TRAMOS.map((t) => [t.id, t]));
    const incid = (id) => TRAMOS.filter((t) => t.a === id || t.b === id);
    // ---- trazado de cada calle: muestras cada 0,5 m con tangente, normal, ancho y altura
    for (const t of TRAMOS) {
      const A = NODOS[t.a], B = NODOS[t.b];
      const ctrl = [[A.x, A.z], ...(t.via || []), [B.x, B.z]];
      const denso = [];
      for (let i = 0; i + 1 < ctrl.length; i++) {
        const p0 = ctrl[Math.max(0, i - 1)], p1 = ctrl[i], p2 = ctrl[i + 1], p3 = ctrl[Math.min(ctrl.length - 1, i + 2)];
        const n = Math.max(4, Math.ceil(Math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 0.25));
        for (let k = 0; k < n; k++) denso.push(t.recta ? [lerp(p1[0], p2[0], k / n), lerp(p1[1], p2[1], k / n)] : catmull(p0, p1, p2, p3, k / n));
      }
      denso.push([B.x, B.z]);
      let L = 0; const acum = [0];
      for (let i = 1; i < denso.length; i++) { L += Math.hypot(denso[i][0] - denso[i - 1][0], denso[i][1] - denso[i - 1][1]); acum.push(L); }
      t.largo = L;
      const pts = []; let j = 0;
      for (let s = 0; s <= L + 1e-6; s += 0.5) {
        while (j + 1 < acum.length - 1 && acum[j + 1] < s) j++;
        const k = (s - acum[j]) / Math.max(1e-9, acum[j + 1] - acum[j]);
        const x = lerp(denso[j][0], denso[j + 1][0], k), z = lerp(denso[j][1], denso[j + 1][1], k);
        pts.push({ x, z, s });
      }
      if (pts[pts.length - 1].s < L - 0.01) pts.push({ x: B.x, z: B.z, s: L });
      pts.forEach((p, i) => {
        const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
        let tx = b.x - a.x, tz = b.z - a.z; const l = Math.hypot(tx, tz) || 1; tx /= l; tz /= l;
        p.tx = tx; p.tz = tz; p.nx = tz; p.nz = -tx;   // normal: a la izquierda según avanza la calle
        p.w = anchoEn(t.w, p.s / L); p.y = lerp(A.y, B.y, p.s / L);
      });
      t.pts = pts; t.anchoMin = Math.min(...pts.map((p) => p.w)); t.anchoMax = Math.max(...pts.map((p) => p.w));
      t.pendiente = (B.y - A.y) / L;
    }
    // radio libre de cada cruce: la mitad del mayor ancho de las calles que llegan
    for (const [id, n] of Object.entries(NODOS)) {
      let r = 0; for (const t of incid(id)) { const p = t.a === id ? t.pts[0] : t.pts[t.pts.length - 1]; r = Math.max(r, p.w / 2); }
      n.rLibre = n.plaza ? Math.max(n.plaza.hx, n.plaza.hz) : r;
    }
    // tramo útil de cada calle (fuera de los cruces)
    for (const t of TRAMOS) {
      const ra = NODOS[t.a].plaza ? 0 : NODOS[t.a].rLibre + 1, rb = NODOS[t.b].plaza ? 0 : NODOS[t.b].rLibre + 1;
      const enPl = (n, p) => n.plaza && Math.abs(p.x - n.x) < n.plaza.hx && Math.abs(p.z - n.z) < n.plaza.hz;
      let s0 = ra, s1 = t.largo - rb;
      if (NODOS[t.a].plaza) { const p = t.pts.find((q) => !enPl(NODOS[t.a], q)); s0 = p ? p.s + 0.5 : 0; }
      if (NODOS[t.b].plaza) { const p = [...t.pts].reverse().find((q) => !enPl(NODOS[t.b], q)); s1 = p ? p.s - 0.5 : t.largo; }
      if (t.b === CIU.meta?.nodo) s1 = t.largo;
      t.s0 = Math.min(s0, t.largo / 2); t.s1 = Math.max(s1, t.largo / 2);
    }
    function muestra(t, s) {
      const ps = t.pts; s = Math.max(0, Math.min(t.largo, s));
      const i = Math.min(ps.length - 2, Math.floor(s / 0.5)); const a = ps[i], b = ps[i + 1]; const k = Math.max(0, Math.min(1, (s - a.s) / Math.max(1e-9, b.s - a.s)));
      return { x: lerp(a.x, b.x, k), z: lerp(a.z, b.z, k), y: lerp(a.y, b.y, k), w: lerp(a.w, b.w, k), tx: a.tx, tz: a.tz, nx: a.nx, nz: a.nz };
    }
    // Punto de una calle: u metros desde el principio del tramo útil (extremo «a»), desplazado off (positivo = izquierda)
    const Fr = (t, u) => muestra(t, t.s0 + u);
    const P = (t, u, off = 0) => { const m = Fr(t, u); return [m.x + m.nx * off, m.z + m.nz * off]; };
    const L_UTIL = (t) => t.s1 - t.s0;

    // ---- rejilla del suelo transitable y de alturas
    const C = CIU.celda || 0.4;
    let x0 = Infinity, z0 = Infinity, x1 = -Infinity, z1 = -Infinity;
    const crece = (x, z, r) => { x0 = Math.min(x0, x - r); z0 = Math.min(z0, z - r); x1 = Math.max(x1, x + r); z1 = Math.max(z1, z + r); };
    for (const t of TRAMOS) for (const p of t.pts) crece(p.x, p.z, p.w + 2);
    for (const n of Object.values(NODOS)) crece(n.x, n.z, n.rLibre + (n.plaza ? 4 : 2));
    const nv = CIU.nave; if (nv) crece(nv.x, nv.z, nv.fondo + nv.ancho);
    const M = 30; x0 -= M; z0 -= M; x1 += M; z1 += M;
    const NX = Math.ceil((x1 - x0) / C), NZ = Math.ceil((z1 - z0) / C);
    const mask = new Uint8Array(NX * NZ), alt = new Float32Array(NX * NZ).fill(NaN);
    const cel = (x, z) => [Math.floor((x - x0) / C), Math.floor((z - z0) / C)];
    function estampaPoli(pts, y, valor = 1) {
      let a = Infinity, b = Infinity, c = -Infinity, d = -Infinity;
      for (const [x, z] of pts) { a = Math.min(a, x); b = Math.min(b, z); c = Math.max(c, x); d = Math.max(d, z); }
      const [i0, j0] = cel(a, b), [i1, j1] = cel(c, d);
      for (let j = Math.max(0, j0); j <= Math.min(NZ - 1, j1); j++) for (let i = Math.max(0, i0); i <= Math.min(NX - 1, i1); i++) {
        const x = x0 + (i + 0.5) * C, z = z0 + (j + 0.5) * C;
        if (dentroDe(pts, x, z)) { const k = j * NX + i; mask[k] = valor; if (valor) alt[k] = typeof y === 'function' ? y(x, z) : y; }
      }
    }
    function estampaDisco(x, z, r, y) {
      const [i0, j0] = cel(x - r, z - r), [i1, j1] = cel(x + r, z + r);
      for (let j = Math.max(0, j0); j <= Math.min(NZ - 1, j1); j++) for (let i = Math.max(0, i0); i <= Math.min(NX - 1, i1); i++) {
        const cx = x0 + (i + 0.5) * C, cz = z0 + (j + 0.5) * C;
        if ((cx - x) ** 2 + (cz - z) ** 2 <= r * r) { const k = j * NX + i; mask[k] = 1; alt[k] = y; }
      }
    }
    // calles: cuadriláteros entre muestras, con discos en las curvas para no dejar cuñas, y prolongadas en los cruces
    for (const t of TRAMOS) {
      const ps = t.pts;
      for (let i = 0; i + 1 < ps.length; i++) {
        const a = ps[i], b = ps[i + 1];
        estampaPoli([[a.x + a.nx * a.w / 2, a.z + a.nz * a.w / 2], [b.x + b.nx * b.w / 2, b.z + b.nz * b.w / 2], [b.x - b.nx * b.w / 2, b.z - b.nz * b.w / 2], [a.x - a.nx * a.w / 2, a.z - a.nz * a.w / 2]], (a.y + b.y) / 2);
        if (i > 0 && !t.recta) estampaDisco(a.x, a.z, a.w / 2, a.y);
      }
      for (const [id, p, sg] of [[t.a, ps[0], -1], [t.b, ps[ps.length - 1], 1]]) {
        const n = NODOS[id]; if (n.plaza || n.sinProlongar) continue;
        let e = 0; for (const o of incid(id)) if (o !== t) { const q = o.a === id ? o.pts[0] : o.pts[o.pts.length - 1]; e = Math.max(e, q.w / 2); }
        if (!e) continue;
        const qx = p.x + p.tx * sg * e, qz = p.z + p.tz * sg * e;
        estampaPoli([[p.x + p.nx * p.w / 2, p.z + p.nz * p.w / 2], [qx + p.nx * p.w / 2, qz + p.nz * p.w / 2], [qx - p.nx * p.w / 2, qz - p.nz * p.w / 2], [p.x - p.nx * p.w / 2, p.z - p.nz * p.w / 2]], n.y);
      }
    }
    for (const n of Object.values(NODOS)) {
      if (n.plaza) estampaPoli([[n.x - n.plaza.hx, n.z - n.plaza.hz], [n.x + n.plaza.hx, n.z - n.plaza.hz], [n.x + n.plaza.hx, n.z + n.plaza.hz], [n.x - n.plaza.hx, n.z + n.plaza.hz]], n.y);
      if (n.redondeo) estampaDisco(n.x, n.z, n.redondeo, n.y);
    }
    // la nave (o el almacén): interior y puerta
    let NAVE = null;
    if (nv) {
      const ca = Math.cos(nv.a), sa = Math.sin(nv.a);   // nv.a: hacia dónde mira la puerta (0 = +z)
      const loc = (lx, lz) => [nv.x + lx * ca + lz * sa, nv.z - lx * sa + lz * ca];
      const S = NODOS.S;
      NAVE = [loc(-nv.ancho / 2, -nv.fondo), loc(nv.ancho / 2, -nv.fondo), loc(nv.ancho / 2, -0.4), loc(-nv.ancho / 2, -0.4)];
      estampaPoli(NAVE, S.y);
      estampaPoli([loc(-nv.puerta / 2, -0.6), loc(nv.puerta / 2, -0.6), loc(nv.puerta / 2, 0.8), loc(-nv.puerta / 2, 0.8)], S.y);
      nv.loc = loc;
    }
    // alturas de lo no transitable: la del vecino transitable más cercano (para fachadas y suelo)
    { const cola = []; for (let k = 0; k < mask.length; k++) if (mask[k]) cola.push(k);
      for (let h = 0; h < cola.length; h++) { const k = cola[h], i = k % NX, j = (k - i) / NX;
        for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const ii = i + di, jj = j + dj; if (ii < 0 || jj < 0 || ii >= NX || jj >= NZ) continue; const q = jj * NX + ii; if (Number.isNaN(alt[q])) { alt[q] = alt[k]; cola.push(q); } } } }
    const libre = (x, z) => { const i = Math.floor((x - x0) / C), j = Math.floor((z - z0) / C); return i >= 0 && j >= 0 && i < NX && j < NZ && mask[j * NX + i] === 1; };
    function H(x, z) {
      const fi = (x - x0) / C - 0.5, fj = (z - z0) / C - 0.5;
      const i = Math.max(0, Math.min(NX - 2, Math.floor(fi))), j = Math.max(0, Math.min(NZ - 2, Math.floor(fj)));
      const a = Math.max(0, Math.min(1, fi - i)), b = Math.max(0, Math.min(1, fj - j));
      const g = (ii, jj) => alt[jj * NX + ii] || 0;
      return lerp(lerp(g(i, j), g(i + 1, j), a), lerp(g(i, j + 1), g(i + 1, j + 1), a), b);
    }
    // ---- contornos (marching squares) → fachadas y paredes
    const CONTORNOS = [];
    { const v = (i, j) => (i < 0 || j < 0 || i >= NX || j >= NZ ? 0 : mask[j * NX + i]);
      const segs = new Map(), key = (p) => `${p[0].toFixed(2)},${p[1].toFixed(2)}`;
      const P2 = (i, j) => [x0 + (i + 0.5) * C, z0 + (j + 0.5) * C];
      const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
      for (let j = -1; j < NZ; j++) for (let i = -1; i < NX; i++) {
        const a = v(i, j), b = v(i + 1, j), c = v(i + 1, j + 1), d = v(i, j + 1), caso = a | (b << 1) | (c << 2) | (d << 3);
        if (caso === 0 || caso === 15) continue;
        const pa = P2(i, j), pb = P2(i + 1, j), pc = P2(i + 1, j + 1), pd = P2(i, j + 1);
        const e = { ab: mid(pa, pb), bc: mid(pb, pc), cd: mid(pc, pd), da: mid(pd, pa) };
        const L = { 1: [['da', 'ab']], 2: [['ab', 'bc']], 3: [['da', 'bc']], 4: [['bc', 'cd']], 5: [['da', 'ab'], ['bc', 'cd']], 6: [['ab', 'cd']], 7: [['da', 'cd']], 8: [['cd', 'da']], 9: [['cd', 'ab']], 10: [['ab', 'bc'], ['cd', 'da']], 11: [['cd', 'bc']], 12: [['bc', 'da']], 13: [['bc', 'ab']], 14: [['ab', 'da']] }[caso];
        for (const [p, q] of L) { const A = e[p], B = e[q]; segs.set(key(A), (segs.get(key(A)) || []).concat([B])); }
      }
      const usados = new Set();
      for (const [k0, outs] of segs) {
        for (const b0 of outs) {
          const id0 = k0 + '>' + key(b0); if (usados.has(id0)) continue;
          const loop = [k0.split(',').map(Number)]; let cur = b0, prevK = k0; usados.add(id0);
          for (let guard = 0; guard < 200000; guard++) {
            loop.push(cur); const kc = key(cur); if (kc === k0) break;
            const sig = (segs.get(kc) || []).find((nb) => !usados.has(kc + '>' + key(nb)));
            if (!sig) break; usados.add(kc + '>' + key(sig)); prevK = kc; cur = sig;
          }
          if (loop.length < 4) continue;
          // simplificar el anillo partiéndolo en dos
          const h = Math.floor(loop.length / 2);
          const s1 = simplificar(loop.slice(0, h + 1), CIU.tolerancia || 0.22), s2 = simplificar(loop.slice(h), CIU.tolerancia || 0.22);
          const pts = s1.slice(0, -1).concat(s2.slice(0, -1));
          if (pts.length < 3) continue;
          // ¿encierra una manzana (no transitable dentro) o es el borde exterior?
          let area = 0; pts.forEach((a, i) => { const b = pts[(i + 1) % pts.length]; area += a[0] * b[1] - b[0] * a[1]; });
          const [ax, az] = pts[0], [bx, bz] = pts[1], mx = (ax + bx) / 2, mz = (az + bz) / 2, l = Math.hypot(bx - ax, bz - az) || 1;
          const nx = (bz - az) / l, nz = -(bx - ax) / l;
          const ladoLibre = libre(mx + nx * 0.5, mz + nz * 0.5) ? 1 : -1;
          const dentroLado = dentroDe(pts, mx + nx * 0.3, mz + nz * 0.3) ? 1 : -1;
          CONTORNOS.push({ pts, bloque: ladoLibre !== dentroLado, area: Math.abs(area) / 2 });
        }
      }
    }
    // ---- zonas: nave, plazas, cruces y calles
    const PLAZAS = Object.values(NODOS).filter((n) => n.plaza).map((n) => ({ id: n.id, x0: n.x - n.plaza.hx, x1: n.x + n.plaza.hx, z0: n.z - n.plaza.hz, z1: n.z + n.plaza.hz, nombre: n.nombre }));
    const enPlaza = (x, z) => PLAZAS.some((p) => x > p.x0 && x < p.x1 && z > p.z0 && z < p.z1);
    const enCruce = (x, z) => { for (const n of Object.values(NODOS)) { if (n.plaza || n.id === 'S' || n.id === CIU.meta?.nodo) continue; if (Math.hypot(x - n.x, z - n.z) < n.rLibre + 0.5 && incid(n.id).length > 1) return n.id; } return null; };
    const HASH = new Map(), hk = (x, z) => `${Math.floor(x / 6)},${Math.floor(z / 6)}`;
    for (const t of TRAMOS) for (const p of t.pts) { const k = hk(p.x, p.z); if (!HASH.has(k)) HASH.set(k, []); HASH.get(k).push([t, p]); }
    function calleEn(x, z) {
      let mejor = null, dm = Infinity;
      for (let di = -1; di <= 1; di++) for (let dj = -1; dj <= 1; dj++) for (const [t, p] of HASH.get(`${Math.floor(x / 6) + di},${Math.floor(z / 6) + dj}`) || []) { const d = Math.hypot(x - p.x, z - p.z); if (d < p.w / 2 + 0.4 && d < dm) { dm = d; mejor = { t, p }; } }
      return mejor;
    }
    function zonaEn(x, z) {
      if (NAVE && dentroDe(NAVE, x, z)) return { tipo: 'nave' };
      for (const p of PLAZAS) if (x > p.x0 && x < p.x1 && z > p.z0 && z < p.z1) return { tipo: 'nodo', id: p.id };
      const c = enCruce(x, z); if (c) return { tipo: 'nodo', id: c };
      const k = calleEn(x, z); if (k) return { tipo: 'tramo', id: k.t.id, s: k.p.s };
      return null;
    }
    const tramoEntre = (a, b) => TRAMOS.find((t) => (t.a === a && t.b === b) || (t.a === b && t.b === a));
    const vecinos = (id) => incid(id).map((t) => (t.a === id ? t.b : t.a));
    const largoRuta = (nodos) => { let L = 0; for (let i = 0; i + 1 < nodos.length; i++) { const t = tramoEntre(nodos[i], nodos[i + 1]); if (t) L += t.id === CIU.meta?.calle ? CIU.meta.u : t.largo; } return L; };
    // ---- permisos
    function evaluarPermisos(nodos, op) {
      const ayto = { ok: true, motivos: [], condiciones: [] }, fed = { ok: true, motivos: [], condiciones: [] };
      const ts = []; for (let i = 0; i + 1 < nodos.length; i++) ts.push(tramoEntre(nodos[i], nodos[i + 1]));
      const L = largoRuta(nodos);
      const no = (q, m) => { q.ok = false; if (!q.motivos.includes(m)) q.motivos.push(m); };
      for (const t of ts) {
        if (t.obras) no(ayto, `${t.nombre} está en obras.`);
        if (t.anchoMin < op.anchoMinimo) no(ayto, `En ${t.nombre} no cabe: tiene ${t.anchoMin.toFixed(1).replace('.', ',')} m en lo más estrecho y hacen falta ${op.anchoMinimo.toFixed(1).replace('.', ',')} m.`);
        if (CIU.modo === 'ensayo') {
          if (t.zona === 'centro') no(ayto, `${t.nombre} es del centro: para ensayar solo se dan permisos en las afueras y en el polígono.`);
          if (t.trafico) no(ayto, `${t.nombre} es una avenida con tráfico: no se corta para un ensayo.`);
        } else {
          if (t.trafico) ayto.condiciones.push(`Corte de tráfico en ${t.nombre} durante el paso.`);
          if (t.reservada) no(fed, `${t.nombre} está reservada a esa hora para ${t.reservada}.`);
        }
      }
      if (CIU.modo === 'ensayo') {
        if (nodos[nodos.length - 1] !== 'S' || nodos.length < 3) no(ayto, 'El ensayo tiene que volver a la nave.');
        if (op.largoMax && L > op.largoMax) no(ayto, `El ensayo es demasiado largo (${Math.round(L)} m; como mucho ${op.largoMax} m).`);
        if (ayto.ok) ayto.condiciones.push(op.horarioEnsayo || 'Ensayo autorizado de 22:00 a 0:30, con la calle cortada por la Policía Local.');
        fed.ok = true; fed.noAplica = true;
      } else {
        if (nodos[nodos.length - 1] !== CIU.meta.nodo) no(fed, `El itinerario tiene que acabar en ${NODOS[CIU.meta.nodo].nombre}.`);
        const minutos = L / op.velocidad / 60 * op.escalaReloj + op.margenMin;
        if (minutos > op.minutosDisponibles) no(fed, `Con ese itinerario (${Math.round(L)} m) no llegas a tu hora: harían falta unos ${Math.round(minutos)} min y tienes ${op.minutosDisponibles}.`);
        if (ayto.ok) ayto.condiciones.unshift('Calles cortadas al tráfico y retirada de veladores durante el paso.');
        if (fed.ok) fed.condiciones.push(op.horaEntrada);
      }
      return { ayto, fed, largo: L };
    }
    const meta = CIU.meta ? (() => { const t = TR[CIU.meta.calle], m = muestra(t, CIU.meta.u); return { x: m.x, z: m.z, y: m.y, tx: m.tx, tz: m.tz, w: m.w, t }; })() : null;
    let SALIDA = null;
    if (nv) { const [x, z] = nv.loc(0, -nv.fondo / 2 - 0.5); SALIDA = { x, z, a: nv.a }; }
    return { NODOS, TRAMOS, TR, P, Fr, muestra, L_UTIL, libre, H, CONTORNOS, PLAZAS, enPlaza, enCruce, zonaEn, calleEn, tramoEntre, vecinos, largoRuta, evaluarPermisos, MARCO: { x0, z0, x1, z1 }, NAVE, SALIDA, META: meta, dentroDe, celda: C };
  }
  window.MotorCiudad = { crear };
})();
