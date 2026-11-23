# Piezas comunes para modelar en Blender sin pantalla: materiales (con texturas generadas), formas torneadas con UV,
# tubos, elipsoides, rejillas y texturas de bordado y talla dibujadas con numpy.
import math
import numpy as np
import bpy, bmesh
from mathutils import Vector

def escena_vacia():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene

# ---------------------------------------------------------------- texturas
def _desenfoque(a, n=2):
    for _ in range(n):
        a = (a + np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)) / 5
    return a

def _linea(d, w):
    return np.clip(1 - np.abs(d) / w, 0, 1)

def patron(N=512, grosor=1.0, motivo='bordado'):
    """Máscara 0..1 de un dibujo repetible: roseta central, hojas en las diagonales, roleos en las esquinas."""
    y, x = np.mgrid[0:N, 0:N] / N
    m = np.zeros((N, N))
    w = 0.011 * grosor
    dx, dy = x - 0.5, y - 0.5
    r, th = np.hypot(dx, dy), np.arctan2(dy, dx)
    m = np.maximum(m, _linea(r - 0.15 * (0.78 + 0.22 * np.cos(6 * th)), w))      # roseta
    m = np.maximum(m, _linea(r - 0.075, w * 0.9))
    m = np.maximum(m, (r < 0.035).astype(float))
    for k in range(6):                                                         # pétalos
        a = k * math.pi / 3
        px, py = 0.5 + 0.11 * math.cos(a), 0.5 + 0.11 * math.sin(a)
        ex, ey = x - px, y - py
        u = ex * math.cos(a) + ey * math.sin(a); v = -ex * math.sin(a) + ey * math.cos(a)
        m = np.maximum(m, _linea(np.hypot(u / 0.05, v / 0.022) - 1, 0.25 * grosor))
    for cx, cy in ((0, 0), (1, 0), (0, 1), (1, 1)):                            # roleos en las esquinas
        ex, ey = x - cx, y - cy
        rr, tt = np.hypot(ex, ey), np.arctan2(ey, ex) % (2 * math.pi)
        for vuelta in range(2):
            m = np.maximum(m, _linea(rr - (0.05 + 0.04 * (tt + 2 * math.pi * vuelta) / (2 * math.pi)), w) * (rr < 0.2))
    for s in (1, -1):                                                          # tallos y hojas en las diagonales
        d = (y - 0.5) - s * (x - 0.5)
        tallo = _linea(d / 1.414, w * 0.8) * (np.abs(x - 0.5) > 0.2) * (np.abs(x - 0.5) < 0.42)
        m = np.maximum(m, tallo)
        for t in (0.27, 0.37):
            for q in (t, 1 - t):
                hx, hy = q, 0.5 + s * (q - 0.5)
                ex, ey = x - hx, y - hy
                m = np.maximum(m, _linea(np.hypot((ex + ey * s) / 0.045, (ex - ey * s) / 0.02) - 1, 0.3 * grosor))
    if motivo == 'talla':
        m = np.maximum(m, _linea(np.minimum(np.minimum(x, 1 - x), np.minimum(y, 1 - y)), 0.02))
    return np.clip(m, 0, 1)

def _imagen(nombre, rgba):
    h, w = rgba.shape[:2]
    im = bpy.data.images.new(nombre, w, h, alpha=True)
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1], dtype=np.float32).ravel())
    im.file_format = 'PNG'; im.pack()
    return im

def _normal(alto, fuerza):
    gy, gx = np.gradient(alto)
    n = np.dstack([-gx * fuerza, gy * fuerza, np.ones_like(alto)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return np.dstack([n * 0.5 + 0.5, np.ones_like(alto)])

def textura_bordado(nombre, fondo, oro=(1.0, 0.74, 0.3), N=512, grosor=1.0):
    """Terciopelo de color `fondo` bordado en oro: color, metal/rugosidad y relieve."""
    m = _desenfoque(patron(N, grosor), 1)
    rng = np.random.default_rng(3)
    ruido = _desenfoque(rng.random((N, N)), 3)
    base = np.array(fondo)[None, None, :] * (0.85 + 0.3 * ruido[..., None])
    hilo = np.array(oro)[None, None, :] * (0.7 + 0.3 * _desenfoque(m, 2)[..., None])
    col = base * (1 - m[..., None]) + hilo * m[..., None]
    mr = np.dstack([np.zeros_like(m), 0.75 - 0.4 * m, m, np.ones_like(m)])      # G rugosidad, B metal
    return (_imagen(nombre + '_col', np.dstack([col, np.ones_like(m)])), _imagen(nombre + '_mr', mr),
            _imagen(nombre + '_nor', _normal(_desenfoque(m, 2), 6.0)))

def textura_talla(nombre, metal=(1.0, 0.76, 0.34), N=512):
    """Orfebrería o madera dorada tallada: el dibujo en relieve, más oscuro en los fondos."""
    m = _desenfoque(patron(N, 2.2, 'talla'), 2)
    col = np.array(metal)[None, None, :] * (0.45 + 0.55 * m[..., None])
    mr = np.dstack([np.zeros_like(m), 0.42 - 0.2 * m, np.ones_like(m), np.ones_like(m)])
    return (_imagen(nombre + '_col', np.dstack([col, np.ones_like(m)])), _imagen(nombre + '_mr', mr),
            _imagen(nombre + '_nor', _normal(m, 9.0)))

def textura_flecos(nombre, oro=(1.0, 0.75, 0.32), N=256):
    y, x = np.mgrid[0:N, 0:N] / N
    hilo = (np.abs(((x * 48) % 1) - 0.5) < 0.3).astype(float) * (y > 0.12)
    cab = (y < 0.16).astype(float)
    a = np.maximum(hilo, cab) * (1 - 0.6 * (y > 0.92) * ((x * 48 % 1) > 0.5))
    col = np.array(oro)[None, None, :] * (0.7 + 0.3 * np.cos(x * 48 * 2 * math.pi)[..., None] ** 2)
    return _imagen(nombre, np.dstack([col, a]))

def textura_flores(nombre, color, N=512):
    """Ramo visto de cerca: muchas flores pequeñas (círculos con pétalos) con sombra entre ellas."""
    rng = np.random.default_rng(5)
    y, x = np.mgrid[0:N, 0:N] / N
    alto = np.zeros((N, N))
    for _ in range(140):
        cx, cy, r = rng.random(), rng.random(), 0.035 + 0.03 * rng.random()
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                dx, dy = x - cx - ox, y - cy - oy
                d = np.hypot(dx, dy) / r
                pet = 1 - d / (0.75 + 0.25 * np.cos(5 * np.arctan2(dy, dx) + cx * 9))
                alto = np.maximum(alto, np.clip(pet, 0, 1) ** 0.6)
    col = np.array(color)[None, None, :] * (0.62 + 0.38 * alto[..., None])
    col[..., 1] *= 0.97; col = np.clip(col, 0, 1)
    mr = np.dstack([np.zeros_like(alto), 0.7 + 0 * alto, np.zeros_like(alto), np.ones_like(alto)])
    return (_imagen(nombre + '_col', np.dstack([col, np.ones_like(alto)])), _imagen(nombre + '_mr', mr),
            _imagen(nombre + '_nor', _normal(alto, 5.0)))

def textura_acanto(nombre, metal=(1.0, 0.76, 0.34), N=256):
    """Hoja de acanto: silueta lobulada (en el alfa), nervio central y nervios laterales en relieve."""
    v, u = np.mgrid[0:N, 0:N] / N                      # v a lo largo de la hoja (0 = base), u a lo ancho
    ancho = 0.46 * (1 - v) ** 0.35 * (0.72 + 0.28 * np.abs(np.cos(v * 7 * math.pi))) * np.clip(v * 8, 0, 1) ** 0.5
    a = (np.abs(u - 0.5) < ancho).astype(float)
    nerv = np.maximum(_linea(u - 0.5, 0.03), 0)
    for k in range(7):
        y0 = 0.1 + k * 0.12
        nerv = np.maximum(nerv, _linea((v - y0) - 0.8 * np.abs(u - 0.5), 0.018) * (v > y0))
    alto = _desenfoque(nerv, 2) + 0.3 * (1 - np.abs(u - 0.5) * 2)
    col = np.array(metal)[None, None, :] * (0.55 + 0.45 * alto[..., None] / max(alto.max(), 1e-6))
    mr = np.dstack([np.zeros_like(a), 0.3 + 0 * a, np.ones_like(a), np.ones_like(a)])
    return (_imagen(nombre + '_col', np.dstack([col, a])), _imagen(nombre + '_mr', mr), _imagen(nombre + '_nor', _normal(alto, 6.0)))

def textura_manto(nombre, fondo, oro=(1.0, 0.74, 0.3), N=1024):
    """Bordado de un manto de cola, simétrico: medallón central, tallo, grandes roleos a los lados, filigrana de fondo
    y cenefa en el borde. u a lo ancho (0,5 = eje), v a lo largo (0 = la punta junto a la cabeza, 1 = el final)."""
    fila, u = np.mgrid[0:N, 0:N] / N
    v = 1 - fila
    xm = 0.5 + np.abs(u - 0.5)                          # espejo: el dibujo se repite igual a los dos lados
    m = np.zeros((N, N))
    def espiral(cx, cy, a, w, vueltas=1.6):
        dx, dy = xm - cx, (v - cy) * 1.3
        r, th = np.hypot(dx, dy), np.arctan2(dy, dx) % (2 * math.pi)
        out = np.zeros_like(r)
        for k in range(int(vueltas) + 1):
            tt = th + 2 * math.pi * k
            out = np.maximum(out, _linea(r - a * tt / (2 * math.pi), w) * (tt < vueltas * 2 * math.pi))
        return out
    roleos = [(0.72, 0.3, 0.05), (0.8, 0.52, 0.06), (0.7, 0.74, 0.07), (0.84, 0.86, 0.05), (0.62, 0.92, 0.04), (0.88, 0.22, 0.04),
              (0.6, 0.18, 0.035), (0.9, 0.68, 0.045), (0.64, 0.42, 0.04), (0.78, 0.96, 0.035), (0.86, 0.4, 0.035)]
    for cx, cy, a in roleos:
        m = np.maximum(m, espiral(cx, cy, a, 0.011))
        for dxh, dyh in ((0.06, -0.05), (-0.05, 0.06), (0.04, 0.07)):                                # hojas junto al roleo
            m = np.maximum(m, _linea(np.hypot((xm - cx - dxh) / 1.6, (v - cy - dyh) * 1.3) - 0.018, 0.009))
    m = np.maximum(m, _linea(np.hypot((xm - 0.5) / 0.11, (v - 0.55) / 0.09) - 1, 0.07))              # medallón
    m = np.maximum(m, _linea(np.hypot((xm - 0.5) / 0.08, (v - 0.55) / 0.065) - 1, 0.06))
    m = np.maximum(m, ((np.hypot((xm - 0.5) / 0.05, (v - 0.55) / 0.04) < 1)).astype(float) * 0.9)
    tallo = _linea(xm - 0.5, 0.009) * (v > 0.08) * (v < 0.95) * (np.abs(v - 0.55) > 0.09)
    m = np.maximum(m, tallo)
    for k in range(9):                                     # hojas a lo largo del tallo
        cy = 0.12 + k * 0.1
        if abs(cy - 0.55) < 0.1: continue
        m = np.maximum(m, _linea(np.hypot((xm - 0.53) / 0.035, (v - cy - (xm - 0.5) * 0.6) / 0.012) - 1, 0.25))
    fondo_f = np.tile(patron(N // 4, 1.5), (4, 4)) * 0.8                                           # filigrana
    m = np.maximum(m, fondo_f * (np.abs(u - 0.5) < 0.45) * (v < 0.95))
    m = np.maximum(m, (np.abs(u - 0.5) > 0.465).astype(float))                                     # cenefa
    m = np.maximum(m, _linea(np.abs(u - 0.5) - 0.445, 0.004))
    m = np.maximum(m, (v > 0.965).astype(float))
    m = _desenfoque(np.clip(m, 0, 1), 1)
    rng = np.random.default_rng(4)
    ruido = _desenfoque(rng.random((N, N)), 4)
    base = np.array(fondo)[None, None, :] * (0.85 + 0.3 * ruido[..., None])
    hilo = np.array(oro)[None, None, :] * (0.7 + 0.3 * _desenfoque(m, 2)[..., None])
    col = base * (1 - m[..., None]) + hilo * m[..., None]
    mr = np.dstack([np.zeros_like(m), 0.75 - 0.4 * m, m, np.ones_like(m)])
    return (_imagen(nombre + '_col', np.dstack([col, np.ones_like(m)])), _imagen(nombre + '_mr', mr),
            _imagen(nombre + '_nor', _normal(_desenfoque(m, 2), 7.0)))

# ---------------------------------------------------------------- materiales
def material(nombre, color=(0.8, 0.8, 0.8), rough=0.6, metal=0.0, sheen=0.0, emis=None, emis_f=0.0,
             alpha=1.0, tex=None, escala_nor=1.0, recorte=False):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
        b.inputs['Sheen Tint'].default_value = (*[min(1, c * 2.5) for c in color], 1)
    if emis:
        b.inputs['Emission Color'].default_value = (*emis, 1); b.inputs['Emission Strength'].default_value = emis_f
    if alpha < 1.0 or recorte:
        b.inputs['Alpha'].default_value = alpha
        m.surface_render_method = 'BLENDED' if not recorte else 'DITHERED'
    if tex:
        col, mr, nor = (tex + (None, None))[:3] if isinstance(tex, tuple) else (tex, None, None)
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = col
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if recorte: nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
        if mr:
            t2 = nt.nodes.new('ShaderNodeTexImage'); t2.image = mr; mr.colorspace_settings.name = 'Non-Color'
            sep = nt.nodes.new('ShaderNodeSeparateColor')
            nt.links.new(t2.outputs['Color'], sep.inputs['Color'])
            nt.links.new(sep.outputs['Green'], b.inputs['Roughness'])
            nt.links.new(sep.outputs['Blue'], b.inputs['Metallic'])
        if nor:
            t3 = nt.nodes.new('ShaderNodeTexImage'); t3.image = nor; nor.colorspace_settings.name = 'Non-Color'
            nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = escala_nor
            nt.links.new(t3.outputs['Color'], nm.inputs['Color'])
            nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m

# ---------------------------------------------------------------- mallas
def objeto(nombre, bm, mat, suave=True, subdiv=0, coleccion=None):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nombre, me)
    (coleccion or bpy.context.scene.collection).objects.link(ob)
    if isinstance(mat, (list, tuple)):
        for mm in mat: me.materials.append(mm)
    else:
        me.materials.append(mat)
    if suave:
        for p in me.polygons: p.use_smooth = True
    if subdiv:
        md = ob.modifiers.new('sub', 'SUBSURF'); md.levels = subdiv; md.render_levels = subdiv
    return ob

def _uv(bm, caras_uv):
    capa = bm.loops.layers.uv.verify()
    for f, uvs in caras_uv:
        for lp, uv in zip(f.loops, uvs): lp[capa].uv = uv

def torno(perfil, segs=32, rep_u=1.0, rep_v=1.0, tapa=True, arco=(0.0, 2 * math.pi)):
    """Forma de revolución alrededor de Z. perfil: [(radio, z), ...] de abajo arriba. Con UV."""
    bm = bmesh.new(); anillos = []
    a0, a1 = arco; cerrado = abs(a1 - a0 - 2 * math.pi) < 1e-6
    n = segs if cerrado else segs + 1
    largo = [0.0]
    for (r0, z0), (r1, z1) in zip(perfil, perfil[1:]): largo.append(largo[-1] + math.hypot(r1 - r0, z1 - z0))
    for (r, z) in perfil:
        anillos.append([bm.verts.new((r * math.sin(a0 + (a1 - a0) * i / segs), -r * math.cos(a0 + (a1 - a0) * i / segs), z))
                        for i in range(n)])
    cuv = []
    for k, (a, b) in enumerate(zip(anillos, anillos[1:])):
        for i in range(segs):
            j = (i + 1) % n
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            u0, u1 = i / segs * rep_u, (i + 1) / segs * rep_u
            v0, v1 = largo[k] / max(largo[-1], 1e-6) * rep_v, largo[k + 1] / max(largo[-1], 1e-6) * rep_v
            cuv.append((f, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]))
    if tapa and cerrado and perfil[-1][0] > 1e-4:
        bm.faces.new(anillos[-1])
    _uv(bm, cuv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def tubo(puntos, radios, segs=12, tapas=True, rep_u=1.0, rep_v=1.0):
    bm = bmesh.new(); anillos = []
    pts = [Vector(p) for p in puntos]
    if not isinstance(radios, (list, tuple)): radios = [radios] * len(pts)
    largo = [0.0]
    for p, q in zip(pts, pts[1:]): largo.append(largo[-1] + (q - p).length)
    ref = None
    for k, p in enumerate(pts):
        t = (pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]).normalized()
        a = ref if ref is not None else (Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0)))
        u = (a - t * a.dot(t)).normalized(); v = t.cross(u); ref = u
        anillos.append([bm.verts.new(p + (u * math.cos(2 * math.pi * i / segs) + v * math.sin(2 * math.pi * i / segs)) * radios[k])
                        for i in range(segs)])
    cuv = []
    for k, (a, b) in enumerate(zip(anillos, anillos[1:])):
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            cuv.append((f, [(i / segs * rep_u, largo[k] * rep_v), ((i + 1) / segs * rep_u, largo[k] * rep_v),
                            ((i + 1) / segs * rep_u, largo[k + 1] * rep_v), (i / segs * rep_u, largo[k + 1] * rep_v)]))
    if tapas:
        bm.faces.new(list(reversed(anillos[0]))); bm.faces.new(anillos[-1])
    _uv(bm, cuv)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def caja(minimo, maximo, rep=(1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
    c = (Vector(minimo) + Vector(maximo)) / 2; s = Vector(maximo) - Vector(minimo)
    for v in bm.verts: v.co = Vector((c.x + v.co.x * s.x, c.y + v.co.y * s.y, c.z + v.co.z * s.z))
    capa = bm.loops.layers.uv.verify()
    for f in bm.faces:
        for lp in f.loops: lp[capa].uv = (lp[capa].uv[0] * rep[0], lp[capa].uv[1] * rep[1])
    return bm

def elipsoide(r, centro=(0, 0, 0), u=24, v=14):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0, calc_uvs=True)
    for vv in bm.verts: vv.co = Vector((centro[0] + vv.co.x * r[0], centro[1] + vv.co.y * r[1], centro[2] + vv.co.z * r[2]))
    return bm

def rejilla(ancho, alto, nx, nz, f=None, rep=(1, 1)):
    """Lámina vertical en el plano XZ (de x=-ancho/2 a +ancho/2, de z=0 a z=-alto). f(x, z) -> (dx, dy, dz)."""
    bm = bmesh.new(); vs = []
    for j in range(nz + 1):
        fila = []
        for i in range(nx + 1):
            x = -ancho / 2 + ancho * i / nx; z = -alto * j / nz
            d = f(x, z, i, j) if f else (0, 0, 0)
            fila.append(bm.verts.new((x + d[0], d[1], z + d[2])))
        vs.append(fila)
    cuv = []
    for j in range(nz):
        for i in range(nx):
            fc = bm.faces.new((vs[j][i], vs[j + 1][i], vs[j + 1][i + 1], vs[j][i + 1]))
            u0, u1 = i / nx * rep[0], (i + 1) / nx * rep[0]; v0, v1 = 1 - j / nz * rep[1], 1 - (j + 1) / nz * rep[1]
            cuv.append((fc, [(u0, v0), (u0, v1), (u1, v1), (u1, v0)]))
    _uv(bm, cuv)
    return bm

def duplicar(ob, nombre, pos, rot=(0, 0, 0), esc=(1, 1, 1)):
    """Copia enlazada (misma malla): el GLB la guarda una vez."""
    d = bpy.data.objects.new(nombre, ob.data); bpy.context.scene.collection.objects.link(d)
    d.location = pos; d.rotation_euler = rot; d.scale = esc
    return d
