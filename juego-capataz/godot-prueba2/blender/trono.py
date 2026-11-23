# Trono de palio de Málaga en estilo cabezón (fase 1 de ESPEC-TRONO.md), modelado por script y exportado a GLB.
# Uso: python trono.py <salida.glb>
# Medidas en metros; el frente mira a -Y (en Godot, a +Z). Escala «de juguete»: el varal va a 0,8 m (el hombro del
# hombre de trono cabezón) y lo alto se exagera (techo del palio a 3,3 m).
# Parámetros de gestión arriba (orfebrería, color del terciopelo, flor).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
from kit import *

salida = sys.argv[-1]
ORFEBRERIA = (1.0, 0.76, 0.34)          # oro; plata sería (0.92, 0.93, 0.95)
TERCIOPELO = (0.30, 0.025, 0.06)        # granate
FLOR = (0.98, 0.93, 0.95)               # blanco rosado

scn = escena_vacia()
L2, W2 = 2.3, 1.1                       # media longitud y media anchura de la mesa
Z_VARAL = 0.8                           # parte de arriba del varal
Z_MESA, Z_CUB = 0.93, 1.43              # mesa y cubierta (donde va la candelería)
Z_TECHO = 3.3

oro = material('oro', ORFEBRERIA, 0.28, 1.0)
talla = material('talla', ORFEBRERIA, 0.35, 1.0, tex=textura_talla('talla', ORFEBRERIA), escala_nor=1.0)
tercio = material('terciopelo', TERCIOPELO, 0.7, 0.0, sheen=0.2, tex=textura_bordado('bordado', TERCIOPELO), escala_nor=0.8)
madera = material('madera', (0.12, 0.06, 0.03), 0.45)
hierro = material('hierro', (0.05, 0.05, 0.055), 0.5, 0.6)
cera = material('cera', (0.96, 0.93, 0.84), 0.4)
llama = material('llama', (1.0, 0.7, 0.3), 0.5, emis=(1.0, 0.55, 0.15), emis_f=14.0)
flor_m = material('flor', FLOR, 0.55, sheen=0.4, emis=(1.0, 0.85, 0.8), emis_f=0.15, tex=textura_flores('flores', FLOR), escala_nor=0.6)
hoja = material('hoja', (0.08, 0.22, 0.07), 0.6)
cristal = material('tulipa', (1.0, 0.8, 0.55), 0.1, alpha=0.4, emis=(1.0, 0.65, 0.3), emis_f=1.5)
flecos = material('flecos', ORFEBRERIA, 0.35, 1.0, tex=textura_flecos('flecos', ORFEBRERIA), recorte=True)
pintura = material('pintura', (0.55, 0.68, 0.85), 0.6)

# ---------------------------------------------------------------- mesa, patas y varales
objeto('mesa', caja((-W2, -L2, Z_VARAL + 0.01), (W2, L2, Z_MESA)), madera)
objeto('cubierta', caja((-W2 - 0.06, -L2 - 0.06, Z_CUB - 0.02), (W2 + 0.06, L2 + 0.06, Z_CUB)), madera)
for x in (-0.55, 0.55):
    for y in (-1.9, 0.0, 1.9):
        objeto('pata', tubo([(x, y, 0.0), (x, y, 0.06), (x, y, Z_VARAL - 0.12)], [0.07, 0.045, 0.045], segs=10), hierro)
for x in (-1.38, -0.55, 0.55, 1.38):                       # 4 varales: los de fuera a la vista, los de dentro bajo el faldón
    objeto('varal', caja((x - 0.05, -3.75, Z_VARAL - 0.13), (x + 0.05, 3.75, Z_VARAL)), madera)
    for s in (-1, 1):                                       # cabezas de varal
        y0 = s * 3.75
        cv = objeto('cabeza_varal', torno([(0.075, 0), (0.075, 0.22), (0.09, 0.24), (0.09, 0.27), (0.0, 0.29)], 20), talla)
        cv.matrix_world = Matrix.Translation((x, y0 - s * 0.27, Z_VARAL - 0.065)) @ Matrix.Rotation(-s * math.pi / 2, 4, 'X')
        objeto('remate', elipsoide((0.05, 0.05, 0.05), (x, y0 + s * 0.04, Z_VARAL - 0.065)), oro)

# ---------------------------------------------------------------- cajillo tallado (perfil barrido alrededor de la mesa)
def recorrido(ox, oy, ch):
    """Rectángulo con esquinas achaflanadas, en sentido antihorario, empezando en el centro del frente."""
    return [(0, -oy), (ox - ch, -oy), (ox, -oy + ch), (ox, oy - ch), (ox - ch, oy), (-ox + ch, oy), (-ox, oy - ch),
            (-ox, -oy + ch), (-ox + ch, -oy)]

def barrido(nombre, ruta, perfil, mat, tile=0.5):
    bm = bmesh.new(); n = len(ruta); anillos = []
    pts = [Vector((x, y, 0)) for x, y in ruta]
    normales = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        n1 = Vector((b.y - a.y, -(b.x - a.x), 0)).normalized(); n2 = Vector((c.y - b.y, -(c.x - b.x), 0)).normalized()
        m = (n1 + n2).normalized(); normales.append(m / max(m.dot(n1), 0.5))
    for (off, z) in perfil:
        anillos.append([bm.verts.new(pts[i] + normales[i] * off + Vector((0, 0, z))) for i in range(n)])
    largo = [0.0]
    for i in range(n): largo.append(largo[-1] + (pts[(i + 1) % n] - pts[i]).length)
    capa = bm.loops.layers.uv.verify()
    for k in range(len(perfil) - 1):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((anillos[k][i], anillos[k][j], anillos[k + 1][j], anillos[k + 1][i]))
            u0, u1 = largo[i] / tile, largo[i + 1] / tile
            v0, v1 = (perfil[k][1] - perfil[0][1]) / tile, (perfil[k + 1][1] - perfil[0][1]) / tile
            for lp, uv in zip(f.loops, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]): lp[capa].uv = uv
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return objeto(nombre, bm, mat, suave=False)

ruta = recorrido(W2, L2, 0.3)
perfil = [(-0.02, Z_MESA - 0.01), (0.06, Z_MESA + 0.01), (0.06, Z_MESA + 0.05), (0.03, Z_MESA + 0.07), (0.02, Z_MESA + 0.09),
          (0.02, Z_CUB - 0.13), (0.04, Z_CUB - 0.11), (0.1, Z_CUB - 0.06), (0.1, Z_CUB - 0.03), (0.0, Z_CUB - 0.02)]
barrido('cajillo', ruta, perfil, talla)
zc = (Z_MESA + Z_CUB) / 2 - 0.01
cart_borde = objeto('cartela_marco', tubo([(math.sin(a) * 0.1, 0, math.cos(a) * 0.13) for a in [2 * math.pi * i / 28 for i in range(29)]],
                                          0.014, segs=8, tapas=False), oro)
cart_fondo = objeto('cartela_fondo', elipsoide((0.095, 0.02, 0.125)), pintura)
cartelas = [((W2 + 0.025, y), math.pi / 2) for y in (-1.5, -0.75, 0, 0.75, 1.5)] + \
           [((-W2 - 0.025, y), -math.pi / 2) for y in (-1.5, -0.75, 0, 0.75, 1.5)] + \
           [((x, -L2 - 0.025), 0) for x in (-0.45, 0, 0.45)] + [((x, L2 + 0.025), math.pi) for x in (-0.45, 0, 0.45)]
for (x, y), rz in cartelas:
    duplicar(cart_borde, 'cartela_marco', (x, y, zc), (0, 0, rz))
    duplicar(cart_fondo, 'cartela_fondo', (x, y, zc), (0, 0, rz))
bpy.data.objects.remove(cart_borde); bpy.data.objects.remove(cart_fondo)
for sx in (-1, 1):                                          # cantoneras en los chaflanes
    for sy in (-1, 1):
        ob = objeto('cantonera', torno([(0.07, Z_MESA), (0.09, Z_MESA + 0.06), (0.06, Z_MESA + 0.12), (0.08, zc), (0.06, Z_CUB - 0.1),
                                        (0.1, Z_CUB - 0.04), (0.06, Z_CUB + 0.02), (0.035, Z_CUB + 0.12), (0.0, Z_CUB + 0.2)], 16), talla)
        ob.location = (sx * (W2 - 0.07), sy * (L2 - 0.07), 0)

# ---------------------------------------------------------------- faldones con flecos
def lado(nombre, ancho, pos, rz, alto, mat, nx=60, nz=8, f=None, rep=(1, 1)):
    o = objeto(nombre, rejilla(ancho, alto, nx, nz, f, rep), mat); o.location = pos; o.rotation_euler = (0, 0, rz)
    return o
ondas = lambda x, z, i, j: (0, 0.012 * math.sin(x * 9) * (-z / 0.7), 0)
alto_f = Z_MESA - 0.24
for nombre, ancho, pos, rz in (('faldon_frente', 2 * W2, (0, -L2 - 0.03, Z_MESA), 0), ('faldon_detras', 2 * W2, (0, L2 + 0.03, Z_MESA), math.pi),
                               ('faldon_dcha', 2 * L2, (W2 + 0.03, 0, Z_MESA), math.pi / 2), ('faldon_izda', 2 * L2, (-W2 - 0.03, 0, Z_MESA), -math.pi / 2)):
    lado(nombre, ancho, pos, rz, alto_f, tercio, f=ondas, rep=(ancho / 0.55, alto_f / 0.55))
    fl = lado('flecos', ancho, (pos[0], pos[1], Z_MESA - alto_f), rz, 0.07, flecos, nx=20, nz=1, rep=(ancho / 0.3, 1))

# ---------------------------------------------------------------- candelería en tandas (arcos que suben hacia la imagen)
Y_IMG = 0.5
def candelero(k, h):
    pie = objeto('candelero_%d' % k, torno([(0.035, 0), (0.035, 0.015), (0.014, 0.03), (0.012, h * 0.3), (0.022, h * 0.33), (0.012, h * 0.37),
                                         (0.012, h * 0.65), (0.02, h * 0.68), (0.012, h * 0.71), (0.012, h - 0.02), (0.042, h - 0.005),
                                         (0.042, h), (0.0, h)], 12), oro)
    cir = objeto('cirio_%d' % k, torno([(0.017, h), (0.017, h + 0.2), (0.013, h + 0.21), (0.0, h + 0.212)], 10), cera)
    ll = objeto('llama_%d' % k, torno([(0.0, h + 0.215), (0.008, h + 0.225), (0.009, h + 0.24), (0.004, h + 0.26), (0.0, h + 0.275)], 8), llama)
    return [pie, cir, ll]
VELAS = []
for k in range(7):
    R = 1.75 - 0.2 * k; h = 0.14 + 0.1 * k
    piezas = candelero(k, h)
    amax = min(math.asin(min(0.85 / R, 1)), 1.15)
    n = max(3, int(2 * amax * R / 0.155) + 1)
    for i in range(n):
        a = -amax + 2 * amax * i / (n - 1)
        x, y = R * math.sin(a), Y_IMG - 0.35 - R * math.cos(a)
        if y < -L2 + 0.1: continue
        for p in piezas: duplicar(p, p.name.split('.')[0], (x, y, Z_CUB))
        VELAS.append((x, y, Z_CUB + h + 0.24))
    for p in piezas: bpy.data.objects.remove(p)

# ---------------------------------------------------------------- jarras con flores
def jarra(nombre, pos, esc=1.0):
    x, y, z = pos
    j = objeto(nombre, torno([(0.07 * esc, 0), (0.09 * esc, 0.02 * esc), (0.04 * esc, 0.06 * esc), (0.05 * esc, 0.12 * esc), (0.11 * esc, 0.22 * esc),
                              (0.1 * esc, 0.3 * esc), (0.07 * esc, 0.34 * esc), (0.1 * esc, 0.38 * esc), (0.0, 0.38 * esc)], 20), talla)
    j.location = (x, y, z)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.24 * esc, calc_uvs=True)
    for v in bm.verts:
        d = v.co.normalized()
        v.co *= 1 + 0.12 * abs(math.sin(d.x * 17) * math.sin(d.y * 19) * math.sin(d.z * 23)) ** 0.5
        v.co.z *= 0.85
    f = objeto(nombre + '_flor', bm, flor_m); f.location = (x, y, z + 0.38 * esc + 0.17 * esc)
for sx in (-1, 1):
    jarra('jarra', (sx * 0.98, -1.35, Z_CUB), 1.0)
    jarra('jarra', (sx * 0.62, Y_IMG - 0.62, Z_CUB), 0.8)

# ---------------------------------------------------------------- arbotantes (como los de la Virgen de la Paloma)
# Cuatro árboles de hojarasca que nacen en las esquinas del cajillo y se abren en diagonal hacia fuera: tronco con
# nudos, ramas en cuatro pisos (más largas hacia fuera, cortas hacia el palio) con voluta, hojas de acanto y una
# tulipa en la punta de cada rama y otra en la cima. Es la misma construcción del trono web, a escala (0,72).
import random
rr = random.Random(1945)
hoja_m = material('acanto', ORFEBRERIA, 0.3, 1.0, tex=textura_acanto('acanto', ORFEBRERIA), escala_nor=1.0, recorte=True)
vidrio = material('tulipa', (1.0, 0.92, 0.8), 0.04, alpha=0.32, emis=(0.42, 0.27, 0.1), emis_f=1.0)
vela_arb = material('vela_arb', (0.95, 0.9, 0.78), 0.4, emis=(0.16, 0.12, 0.06), emis_f=1.0)
def catmull(pts, n=6):
    P = [Vector(p) for p in pts]; P = [P[0]] + P + [P[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return out
def en(curva, t):
    f = t * (len(curva) - 1); i = min(int(f), len(curva) - 2); return curva[i].lerp(curva[i + 1], f - i)
def tangente(curva, t):
    f = t * (len(curva) - 1); i = min(int(f), len(curva) - 2); return (curva[i + 1] - curva[i]).normalized()
def hoja_en(bm, capa, p, d, esc, giro, inclina):
    # hoja de acanto curvada (punta hacia fuera, bordes hacia dentro), 0,11 x 0,22 m
    Y = (d + Vector((0, 0, 0.35))).normalized()
    X = Y.cross(Vector((0, 0, 1)) if abs(Y.z) < 0.95 else Vector((1, 0, 0))).normalized()
    X = X * math.cos(giro) + Y.cross(X) * math.sin(giro); Z = X.cross(Y)
    ca, sa = math.cos(inclina), math.sin(inclina)
    vs = []
    for j in range(9):
        k = j / 8; fila = []
        for i in range(5):
            u = (i / 4 - 0.5)
            x = u * 0.108 * (1 - 0.15 * k); y = k * 0.216; z = -0.094 * k * k + 1.6 * x * x - 0.03 * math.sin(k * math.pi)
            y, z = y * ca - z * sa, y * sa + z * ca
            fila.append(bm.verts.new(p + (X * x + Y * y + Z * z) * esc))
        vs.append(fila)
    for j in range(8):
        for i in range(4):
            f = bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
            for lp, uv in zip(f.loops, [(i / 4, j / 8), ((i + 1) / 4, j / 8), ((i + 1) / 4, (j + 1) / 8), (i / 4, (j + 1) / 8)]):
                lp[capa].uv = uv
TULIPAS = []
K = 0.72
NIV = [(0.42, 0.7, 8), (0.78, 0.78, 8), (1.12, 0.62, 7), (1.42, 0.4, 5)]
for sx in (-1, 1):
    for sy in (-1, 1):
        nom = 'arbotante_%s_%s' % ('del' if sy < 0 else 'tras', 'dcha' if sx > 0 else 'izda')
        c = Vector((sx * (W2 - 0.04), sy * (L2 - 0.04), Z_CUB))
        d = Vector((sx, sy * 0.75, 0)).normalized(); q = Vector((-d.y, d.x, 0))
        P = lambda u, z, v: c + d * (u * K) + q * (v * K) + Vector((0, 0, z * K))
        tronco = catmull([P(0, 0, 0), P(0.06, 0.6, 0), P(0.14, 1.2, 0), P(0.2, 1.72, 0)], 8)
        objeto(nom + '_tronco', tubo(tronco, 0.06 * K, segs=10), oro)
        for t, rad in ((0.08, 0.16), (0.45, 0.1), (0.75, 0.09)):
            pp = en(tronco, t); objeto(nom + '_nudo', elipsoide((rad * K, rad * K, rad * K * 0.6), pp), talla)
        bm_r = bmesh.new(); hojas = []; puntas = []
        for nv, (hh, r, nb) in enumerate(NIV):
            eje = en(tronco, hh / 1.72)
            for k in range(nb):
                th = -math.pi + 2 * math.pi * (k + 0.5) / nb + nv * 0.25
                R = (r * (0.55 + 0.45 * math.cos(th)) + 0.12) * K
                cu, cv = math.cos(th), math.sin(th)
                pt = lambda f, z, rizo: eje + d * (cu * R * f + rizo * cu) + q * (cv * R * f + rizo * cv) + Vector((0, 0, z * K))
                curva = catmull([pt(0, 0, 0), pt(0.35, -0.08, 0), pt(0.7, 0.02, 0), pt(1, 0.16, 0), pt(0.92, 0.24, -0.03 * K)], 4)
                b = tubo(curva, 0.022 * K, segs=6); me = bpy.data.meshes.new('tmp'); b.to_mesh(me); b.free(); bm_r.from_mesh(me); bpy.data.meshes.remove(me)
                vp = en(curva, 0.3); rad_v = 0.05 * K                                    # voluta
                espiral = [vp + Vector((0, 0, -rad_v)) + (d * cu + q * cv) * (rad_v * (1 - 0.25 * a / (1.5 * math.pi)) * math.sin(a)) +
                           Vector((0, 0, rad_v * (1 - 0.25 * a / (1.5 * math.pi)) * math.cos(a))) for a in [1.5 * math.pi * i / 10 for i in range(11)]]
                b = tubo(espiral, 0.012 * K, segs=6); me = bpy.data.meshes.new('tmp'); b.to_mesh(me); b.free(); bm_r.from_mesh(me); bpy.data.meshes.remove(me)
                for t in (0.1, 0.22, 0.34, 0.46, 0.58, 0.7, 0.82, 0.93):
                    hojas.append((en(curva, t), tangente(curva, t), 0.8 + rr.random() * 0.5))
                puntas.append(curva[-1] + Vector((0, 0, 0.03 * K)))
        for i in range(13):
            pp = en(tronco, 0.05 + i * 0.07)
            for _ in range(3):
                a = rr.random() * 2 * math.pi; hojas.append((pp, Vector((math.cos(a) * 0.8, math.sin(a) * 0.8, 0.6)).normalized(), 0.9 + rr.random() * 0.5))
        puntas.append(en(tronco, 1.0) + Vector((0, 0, 0.05 * K)))
        me = bpy.data.meshes.new(nom + '_ramas'); bm_r.to_mesh(me); bm_r.free()
        o = bpy.data.objects.new(nom + '_ramas', me); scn.collection.objects.link(o); me.materials.append(oro)
        for p_ in me.polygons: p_.use_smooth = True
        bm_h = bmesh.new(); capa = bm_h.loops.layers.uv.verify()
        for (p, tg, e) in hojas:
            hoja_en(bm_h, capa, p, tg, e * K, (rr.random() - 0.5) * 1.6, -0.35 - rr.random() * 0.4)
        objeto(nom + '_hojas', bm_h, hoja_m)
        # cazoletas, velas, tulipas de cristal y llamas (una malla de cada, por arbotante)
        partes = {'cazoletas': (bmesh.new(), oro), 'velas': (bmesh.new(), vela_arb), 'tulipas': (bmesh.new(), vidrio), 'llamas': (bmesh.new(), llama)}
        for p in puntas:
            for nombre_p, b in (('cazoletas', torno([(0.03 * K, 0), (0.05 * K, 0.04 * K), (0.0, 0.04 * K)], 10)),
                                ('velas', torno([(0.02 * K, 0.04 * K), (0.02 * K, 0.18 * K), (0.0, 0.18 * K)], 8)),
                                ('tulipas', torno([(0.045 * K, 0.02 * K), (0.06 * K, 0.12 * K), (0.055 * K, 0.28 * K)], 12, tapa=False)),
                                ('llamas', elipsoide((0.02 * K, 0.02 * K, 0.04 * K), (0, 0, 0.21 * K), 8, 6))):
                bmesh.ops.translate(b, verts=b.verts, vec=p)
                me = bpy.data.meshes.new('tmp'); b.to_mesh(me); b.free(); partes[nombre_p][0].from_mesh(me); bpy.data.meshes.remove(me)
            TULIPAS.append((p.x, p.y, p.z + 0.21 * K))
        for nombre_p, (b, m) in partes.items():
            objeto(nom + '_' + nombre_p, b, m)

# ---------------------------------------------------------------- campana
objeto('campana_soporte', tubo([(0, -L2 - 0.1, Z_CUB - 0.05), (0, -L2 - 0.2, Z_CUB + 0.02), (0, -L2 - 0.26, Z_CUB - 0.02)], 0.012, segs=8), oro)
objeto('campana', torno([(0.07, -0.13), (0.065, -0.11), (0.045, -0.06), (0.04, -0.02), (0.02, 0.0), (0.0, 0.01)], 20), oro).location = (0, -L2 - 0.26, Z_CUB - 0.03)
objeto('campana_mazo', tubo([(0, -L2 - 0.26, Z_CUB - 0.05), (0, -L2 - 0.26, Z_CUB - 0.2)], [0.005, 0.005], segs=6), oro)
objeto('campana_bola', elipsoide((0.015, 0.015, 0.015), (0, -L2 - 0.26, Z_CUB - 0.2)), oro)

# ---------------------------------------------------------------- peana
objeto('peana', torno([(0.5, Z_CUB), (0.5, Z_CUB + 0.06), (0.44, Z_CUB + 0.09), (0.36, Z_CUB + 0.2), (0.41, Z_CUB + 0.24), (0.33, Z_CUB + 0.3),
                       (0.31, Z_CUB + 0.37), (0.0, Z_CUB + 0.37)], 40, rep_u=6, rep_v=0.8), talla).location = (0, Y_IMG, 0)
Z_IMG = Z_CUB + 0.37

# ---------------------------------------------------------------- palio: varales, techo y bambalinas
Y0, Y1 = -L2 + 0.1, L2 - 0.1                 # el palio cubre el cajillo entero
for sx in (-1, 1):
    for k in range(6):
        y = Y0 + 0.04 + k * (Y1 - Y0 - 0.08) / 5
        h = Z_TECHO - Z_CUB
        prof = [(0.05, 0), (0.05, 0.04), (0.022, 0.08)]
        for nz in (0.35, 0.62, 0.86):
            zz = h * nz; prof += [(0.022, zz - 0.05), (0.045, zz - 0.02), (0.05, zz), (0.045, zz + 0.02), (0.022, zz + 0.05)]
        prof += [(0.022, h - 0.06), (0.04, h - 0.02), (0.04, h), (0.0, h)]
        objeto('varal_palio', torno(prof, 12), oro).location = (sx * (W2 - 0.12), y, Z_CUB)
objeto('techo', caja((-W2 + 0.02, Y0, Z_TECHO), (W2 - 0.02, Y1, Z_TECHO + 0.06), rep=(3, 3)), tercio)
objeto('cresteria', tubo([(-W2, Y0, Z_TECHO + 0.07), (W2, Y0, Z_TECHO + 0.07), (W2, Y1, Z_TECHO + 0.07), (-W2, Y1, Z_TECHO + 0.07), (-W2, Y0, Z_TECHO + 0.07)],
                         0.02, segs=8, tapas=False), oro)
ALTO_B = 0.42
def festones(x, z, i, j, ancho):
    # el bajo de la bambalina en ondas (festones)
    if j == 8:
        return (0, 0, 0.05 * abs(math.sin(math.pi * (x + ancho / 2) / 0.3)))
    return (0, 0, 0)
for nombre, ancho, pos, rz in (('bambalina_frente', 2 * W2 - 0.04, (0, Y0 - 0.005, Z_TECHO + 0.06), 0),
                               ('bambalina_detras', 2 * W2 - 0.04, (0, Y1 + 0.005, Z_TECHO + 0.06), math.pi),
                               ('bambalina_dcha', Y1 - Y0, (W2 - 0.015, (Y0 + Y1) / 2, Z_TECHO + 0.06), math.pi / 2),
                               ('bambalina_izda', Y1 - Y0, (-W2 + 0.015, (Y0 + Y1) / 2, Z_TECHO + 0.06), -math.pi / 2)):
    b = lado(nombre, ancho, pos, rz, ALTO_B, tercio, nx=48, nz=8, f=lambda x, z, i, j, a=ancho: festones(x, z, i, j, a),
             rep=(ancho / 0.45, ALTO_B / 0.45))
    fl = objeto(nombre + '_flecos', rejilla(ancho, 0.07, 48, 1, lambda x, z, i, j, a=ancho: (0, 0, 0.05 * abs(math.sin(math.pi * (x + a / 2) / 0.3))),
                                              rep=(ancho / 0.3, 1)), flecos)
    fl.parent = b; fl.location = (0, 0.002, -ALTO_B)
    g = objeto(nombre + '_galon', tubo([(-ancho / 2, -0.006, -0.03), (ancho / 2, -0.006, -0.03)], 0.012, segs=6), oro); g.parent = b

# ---------------------------------------------------------------- la imagen estilizada (Dolorosa)
# Serena, con la mirada baja; proporciones algo suaves (la cabeza un poco mayor de lo real) pero sin caricatura.
piel = material('piel', (0.93, 0.76, 0.66), 0.5, sheen=0.2)
encaje = material('encaje', (0.97, 0.96, 0.93), 0.6, tex=textura_bordado('encaje', (0.95, 0.94, 0.9), (1.0, 1.0, 0.98), N=256, grosor=0.8))
saya = material('saya', (0.95, 0.9, 0.78), 0.6, tex=textura_bordado('saya', (0.93, 0.88, 0.76)), escala_nor=0.8)
manto_m = material('manto', TERCIOPELO, 0.65, sheen=0.25, tex=textura_bordado('manto', TERCIOPELO, grosor=1.2), escala_nor=0.8)
rasgo = material('rasgo', (0.2, 0.11, 0.08), 0.6)
labio = material('labio', (0.72, 0.36, 0.36), 0.5)
rubor = material('rubor', (0.95, 0.55, 0.55), 0.6, alpha=0.35)
lagrima = material('lagrima', (0.9, 0.95, 1.0), 0.05, alpha=0.5)

X, Y, Z = 0.0, Y_IMG, Z_IMG
def T(v): return Vector((X + v[0], Y + v[1], Z + v[2]))
sy = objeto('saya', torno([(0.34, 0), (0.33, 0.08), (0.28, 0.3), (0.21, 0.5), (0.15, 0.62), (0.11, 0.72), (0.0, 0.74)], 36, rep_u=3, rep_v=1.5), saya)
sy.location = T((0, 0, 0))
ab = 0.62                                                 # medio ancho de la abertura del manto (rad)
mt = objeto('manto', torno([(0.43, 0.0), (0.41, 0.1), (0.36, 0.32), (0.27, 0.52), (0.2, 0.66), (0.165, 0.76), (0.155, 0.84), (0.158, 0.93),
                            (0.14, 1.01), (0.09, 1.07), (0.0, 1.09)], 40, rep_u=4, rep_v=2, tapa=False, arco=(ab, 2 * math.pi - ab)), manto_m)
mt.location = T((0, 0, 0)); s = mt.modifiers.new('grosor', 'SOLIDIFY'); s.thickness = 0.012
# cola del manto: baja por la espalda de la imagen, se apoya en la cubierta, sale por la trasera del cajillo y se
# extiende casi hasta el final de los varales traseros (como en el trono web), abriéndose y bajando muy poco para
# pasar por encima de las cabezas de los hombres de trono.
ruta_c = [(0.3, 0.62), (0.42, 0.42), (0.55, 0.1), (0.7, -0.2), (0.9, -0.33), (1.2, -0.355), (1.6, -0.355), (1.8, -0.35),
          (2.1, -0.36), (2.5, -0.38), (2.9, -0.4), (3.15, -0.42), (3.22, -0.47)]
anchos = [0.22, 0.4, 0.55, 0.68, 0.78, 0.82, 0.84, 0.85, 0.9, 0.95, 0.99, 1.0, 1.0]
bm = bmesh.new(); vs = []; nx = 16
for j, (dy, dz) in enumerate(ruta_c):
    w = anchos[j]
    vs.append([bm.verts.new(T((-w + 2 * w * i / nx, dy, dz + 0.006 * math.sin(i * 1.3) * (j > 7)))) for i in range(nx + 1)])
capa = bm.loops.layers.uv.verify()
for j in range(len(vs) - 1):
    for i in range(nx):
        f = bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
        for lp, uv in zip(f.loops, [(i / nx * 4, j * 0.6), ((i + 1) / nx * 4, j * 0.6), ((i + 1) / nx * 4, (j + 1) * 0.6), (i / nx * 4, (j + 1) * 0.6)]):
            lp[capa].uv = uv
borde = [v.co.copy() for v in [f[0] for f in vs]][::-1] + [v.co.copy() for v in vs[-1]] + [f[-1].co.copy() for f in vs]
cola = objeto('manto_cola', bm, manto_m, subdiv=1)
cola.modifiers.new('grosor', 'SOLIDIFY').thickness = 0.012
objeto('cola_galon', tubo([p + Vector((0, 0, 0.008)) for p in borde], 0.014, segs=6, tapas=False), oro)
objeto('manto_galon', tubo([T((math.sin(a) * 0.43, -math.cos(a) * 0.43, 0.005)) for a in [ab + (2 * math.pi - 2 * ab) * i / 40 for i in range(41)]],
                           0.012, segs=6, tapas=False), oro)

# cabeza, toca y rostrillo
HC = Vector((0, -0.015, 0.9)); HR = (0.098, 0.092, 0.115)
objeto('cabeza', elipsoide(HR, T(HC), 28, 18), piel)
objeto('toca', elipsoide((0.118, 0.1, 0.13), T(HC + Vector((0, 0.03, 0.005)))), encaje)
ros = [T(HC + Vector((math.sin(a) * 0.1, -0.06 + 0.02 * math.cos(a) ** 2, math.cos(a) * 0.125))) for a in [2 * math.pi * i / 40 for i in range(41)]]
objeto('rostrillo', tubo(ros, 0.02, segs=10, tapas=False), encaje)

def sup(x, z, sale=0.003):
    """Punto de la cara (delante de la cabeza) a la altura x, z relativas al centro de la cabeza."""
    k = 1 - (x / HR[0]) ** 2 - (z / HR[2]) ** 2
    return T(HC + Vector((x, -HR[1] * math.sqrt(max(k, 0.0)) - sale, z)))
for s_ in (-1, 1):
    # ojos entreabiertos mirando abajo: párpado que cae hacia fuera y la pupila asomando por debajo
    objeto('parpado', tubo([sup(s_ * (0.018 + 0.032 * t), 0.012 - 0.007 * t + 0.003 * math.sin(math.pi * t)) for t in [i / 8 for i in range(9)]],
                           0.0032, segs=6), rasgo)
    objeto('pupila', elipsoide((0.0115, 0.003, 0.0075), sup(s_ * 0.034, 0.004, 0.0)), rasgo)
    # cejas algo levantadas por dentro (dolor)
    objeto('ceja', tubo([sup(s_ * (0.016 + 0.034 * t), 0.045 - 0.012 * t - 0.004 * math.sin(math.pi * t)) for t in [i / 8 for i in range(9)]],
                        0.0025, segs=6), rasgo)
    objeto('rubor', elipsoide((0.017, 0.004, 0.011), sup(s_ * 0.048, -0.025, 0.0)), rubor)
    objeto('lagrima', elipsoide((0.005, 0.004, 0.007), sup(s_ * 0.034, -0.012 - 0.02 * (s_ > 0), 0.004)), lagrima)
objeto('boca', tubo([sup(-0.009 + 0.018 * t, -0.056 + 0.0025 * math.sin(math.pi * t)) for t in [i / 6 for i in range(7)]], 0.0028, segs=6), labio)

# manos juntas sobre el pecho con el pañuelo
for s_ in (-1, 1):
    objeto('mano', elipsoide((0.026, 0.02, 0.048), T((s_ * 0.017, -0.215, 0.6))), piel).rotation_euler = (0.3, s_ * 0.25, 0)
objeto('panuelo', elipsoide((0.026, 0.012, 0.03), T((0.012, -0.228, 0.55))), encaje)

# corona y ráfaga
cc = T(HC + Vector((0, 0.01, 0.168)))
objeto('corona', torno([(0.075, 0), (0.08, 0.012), (0.072, 0.04), (0.092, 0.075), (0.088, 0.08)], 32, tapa=False), oro).location = cc
for a in (0, math.pi / 2):
    arco_c = [cc + Vector((math.cos(a) * 0.085 * math.cos(t), math.sin(a) * 0.085 * math.cos(t), 0.075 + 0.07 * math.sin(t)))
              for t in [math.pi * i / 16 for i in range(17)]]
    objeto('corona_imperial', tubo(arco_c, 0.007, segs=6), oro)
objeto('corona_cruz', tubo([cc + Vector((0, 0, 0.145)), cc + Vector((0, 0, 0.2))], 0.006, segs=6), oro)
objeto('corona_cruz2', tubo([cc + Vector((-0.018, 0, 0.18)), cc + Vector((0.018, 0, 0.18))], 0.005, segs=6), oro)
rc = T(HC + Vector((0, 0.13, 0.04)))                       # centro de la ráfaga, detrás de la cabeza
objeto('rafaga_aro', tubo([rc + Vector((math.cos(t) * 0.22, 0, math.sin(t) * 0.22)) for t in [-0.45 + (math.pi + 0.9) * i / 40 for i in range(41)]],
                          0.012, segs=6, tapas=False), oro)
for i in range(31):
    t = -0.6 + (math.pi + 1.2) * i / 30
    lg = 0.42 if i % 2 == 0 else 0.33
    d = Vector((math.cos(t), 0, math.sin(t)))
    objeto('rayo', tubo([rc + d * 0.2, rc + d * (lg * 0.7), rc + d * lg], [0.016, 0.01, 0.0], segs=4), oro)
for i in range(12):
    t = -0.3 + (math.pi + 0.6) * i / 11
    c = rc + Vector((math.cos(t), 0, math.sin(t))) * 0.47
    estrella = [c + Vector((math.cos(a) * (0.028 if k % 2 == 0 else 0.012), -0.003, math.sin(a) * (0.028 if k % 2 == 0 else 0.012)))
                for k, a in enumerate([math.pi / 2 + math.pi * k / 5 for k in range(11)])]
    objeto('estrella', tubo(estrella, 0.004, segs=4, tapas=False), oro)

# ---------------------------------------------------------------- puntos de luz para Godot (nodos vacíos)
for nombre, pts in (('luz_vela', VELAS[::9]), ('luz_tulipa', TULIPAS[::11])):
    for p in pts:
        e = bpy.data.objects.new(nombre, None); scn.collection.objects.link(e); e.location = p
raiz = bpy.data.objects.new('trono_palio', None); scn.collection.objects.link(raiz)
for o in list(scn.collection.objects):
    if o is not raiz and o.parent is None: o.parent = raiz
bpy.ops.export_scene.gltf(filepath=salida, export_format='GLB', export_apply=True)
print('ok', salida, len(VELAS), 'velas')
