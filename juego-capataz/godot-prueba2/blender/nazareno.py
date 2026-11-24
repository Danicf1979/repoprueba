# Modela un nazareno en Blender (sin pantalla) y lo exporta a GLB para Godot.
# Uso: python nazareno.py <realista|cabezon> <salida.glb>
# Las piezas se hacen por perfiles torneados y tubos, con pliegues en la túnica y suavizado (subdivisión):
# túnica, capirote con antifaz (babero delante y caída detrás), escudo, cíngulo con borlas, mangas anchas,
# guantes, zapatos y cirio con chorreones y llama. Todo mira hacia -Y de Blender (+Z en Godot).
import sys, math
import bpy, bmesh
from mathutils import Vector

estilo, salida = sys.argv[-2], sys.argv[-1]
espejo = '_espejo' in salida      # versión espejada: el cirio al otro lado, para la otra fila del cortejo

# Proporciones: altura de hombros, cabeza (centro y radio), cintura, anchuras, capirote y cirio
P = {
    'realista': dict(hombro=1.44, cab_z=1.62, cab_r=0.105, cintura=1.04, r_bajo=0.34, r_cin=0.17, r_pecho=0.2,
                     r_hombro=0.21, capi=0.78, babero=0.44, espalda=0.52, capa_r=0.215, pliegues=16, prof=0.035,
                     brazo=0.055, manga=0.085, mano=0.045, cirio_l=1.35, cirio_r=0.03, ojo=(0.026, 0.017), lado=0.12, punta=1.5),
    'cabezon':  dict(hombro=0.66, cab_z=0.9, cab_r=0.22, cintura=0.44, r_bajo=0.27, r_cin=0.2, r_pecho=0.21,
                     r_hombro=0.2, capi=0.5, babero=0.32, espalda=0.26, capa_r=0.235, pliegues=9, prof=0.03,
                     brazo=0.07, manga=0.1, mano=0.07, cirio_l=0.95, cirio_r=0.03, ojo=(0.06, 0.045), lado=0.03, punta=3.0),
}[estilo]

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

def material(nombre, color, rough=0.8, metal=0.0, sheen=0.0, emis=None, emis_f=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
        b.inputs['Sheen Tint'].default_value = (*[min(1, c * 2.5) for c in color], 1)
    if emis:
        b.inputs['Emission Color'].default_value = (*emis, 1); b.inputs['Emission Strength'].default_value = emis_f
    return m

M = dict(
    tunica=material('tunica', (0.78, 0.74, 0.64), 0.85, sheen=0.4),
    antifaz=material('antifaz', (0.055, 0.007, 0.08), 0.6, sheen=0.35),
    cingulo=material('cingulo', (0.85, 0.62, 0.16), 0.45, metal=0.3),
    oro=material('oro', (1.0, 0.75, 0.35), 0.28, metal=1.0),
    escudo=material('escudo', (0.55, 0.05, 0.08), 0.5),
    guante=material('guante', (0.93, 0.92, 0.88), 0.7),
    zapato=material('zapato', (0.03, 0.03, 0.03), 0.35),
    ojo=material('ojo', (0.01, 0.01, 0.01), 0.9),
    cera=material('cera', (0.95, 0.91, 0.8), 0.45),
    llama=material('llama', (1.0, 0.7, 0.3), 0.5, emis=(1.0, 0.55, 0.15), emis_f=12.0),
)

def objeto(nombre, bm, mat, suave=True, subdiv=1):
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nombre, me); scn.collection.objects.link(ob)
    me.materials.append(mat)
    if suave:
        for p in me.polygons: p.use_smooth = True
    if subdiv:
        md = ob.modifiers.new('sub', 'SUBSURF'); md.levels = subdiv; md.render_levels = subdiv
    return ob

def torno(filas, segs=40, tapa_arriba=True, tapa_abajo=False):
    """filas: lista de funciones/valores -> para cada fila (z, f(theta)->radio o radio, opcional dz(theta))."""
    bm = bmesh.new(); anillos = []
    for fila in filas:
        z, r = fila[0], fila[1]
        dz = fila[2] if len(fila) > 2 else None
        sx = fila[3] if len(fila) > 3 else 1.0
        sy = fila[4] if len(fila) > 4 else 1.0
        an = []
        for i in range(segs):
            th = 2 * math.pi * i / segs          # th = 0 mira al frente (-Y)
            rr = r(th) if callable(r) else r
            zz = z + (dz(th) if dz else 0)
            an.append(bm.verts.new((rr * math.sin(th) * sx, -rr * math.cos(th) * sy, zz)))
        anillos.append(an)
    for a, b in zip(anillos, anillos[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if tapa_arriba: bm.faces.new(list(reversed(anillos[0])) if False else anillos[0])
    if tapa_abajo: bm.faces.new(list(reversed(anillos[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def tubo(puntos, radios, segs=14, tapas=True):
    bm = bmesh.new(); anillos = []
    pts = [Vector(p) for p in puntos]
    for k, p in enumerate(pts):
        t = (pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(a).normalized(); v = t.cross(u).normalized()
        r = radios[k]
        anillos.append([bm.verts.new(p + (u * math.cos(2 * math.pi * i / segs) + v * math.sin(2 * math.pi * i / segs)) * r)
                        for i in range(segs)])
    for a, b in zip(anillos, anillos[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if tapas:
        bm.faces.new(list(reversed(anillos[0]))); bm.faces.new(anillos[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def elipsoide(nombre, c, r, mat, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2]))
    ob = objeto(nombre, bm, mat, subdiv=0)
    ob.location = c; ob.rotation_euler = rot
    return ob

def smooth(t): return t * t * (3 - 2 * t)

# ---------------------------------------------------------------- túnica
h, ci = P['hombro'], P['cintura']
n, prof = P['pliegues'], P['prof']
def pliegue(r0, peso, fase=0.0):
    # pliegues verticales que se abren hacia el bajo; delante algo más planos
    return lambda th: r0 * (1 + peso * prof / r0 * (0.6 * math.sin(n * th + fase) + 0.4 * math.sin(2.3 * n * th + 1.7)))
filas = []
cuello = P['cab_r'] * (0.55 if estilo == 'realista' else 0.5)
filas.append((h + 0.05, cuello))
filas.append((h, P['r_hombro']))
filas.append((h - (h - ci) * 0.35, P['r_pecho']))
filas.append((ci + 0.02, P['r_cin']))
pasos = 9
for k in range(pasos + 1):
    t = k / pasos
    z = ci - t * (ci - 0.02)
    r0 = P['r_cin'] + (P['r_bajo'] - P['r_cin']) * smooth(t) ** 0.8
    filas.append((z, pliegue(r0, t ** 0.7)))
filas = [(z, r, None, 1.0, 0.78) for (z, r) in filas]
PERFIL_T = [(z, r if not callable(r) else r(0.0)) for (z, r, *_ ) in filas]
def r_tun(z):
    for (z0, r0), (z1, r1) in zip(PERFIL_T, PERFIL_T[1:]):
        if z1 <= z <= z0: return r0 + (r1 - r0) * (z0 - z) / max(z0 - z1, 1e-6)
    return 0.0
tun = objeto('tunica', torno(filas, segs=64, tapa_arriba=True, tapa_abajo=False), M['tunica'])
tun.modifiers.new('solid', 'SOLIDIFY').thickness = 0.008
tun.modifiers.move(1, 0)

# ---------------------------------------------------------------- capirote y antifaz (una sola tela)
cz, cr = P['cab_z'], P['cab_r']
top = cz + cr + P['capi']
filas = [(top, 0.004)]
for k in range(1, 7):                                       # cono
    t = k / 6
    filas.append((top - t * P['capi'], 0.004 + (cr * 1.02) * t))
for k in range(1, 6):                                       # sobre la cabeza hasta la barbilla
    a = k / 5 * math.pi * 0.5
    filas.append((cz + cr * math.cos(a) * 0.9 - cr * 0.1 * (k / 5), cr * (1.02 + 0.06 * k / 5)))
cuelloz = cz - cr * 0.95
for k in range(1, 8):                                       # caída: babero delante, más larga detrás
    t = k / 7
    zf = cuelloz - (cuelloz - (h + 0.02)) * min(1, t * 1.6) * 0.9
    def r(th, t=t, zf=zf):
        base = cr * 1.08 + (P['capa_r'] - cr * 1.08) * smooth(min(1, t * 1.6)) + 0.01 * math.sin(7 * th) * t
        return max(base, r_tun(zf + dz(th)) + 0.03 + abs(math.sin(th)) ** 2 * P['brazo'] * 0.9)   # ceñido, tapando justo los hombros
    def dz(th, t=t):
        f = math.cos(th)                                     # 1 delante, -1 detrás
        caida = P['babero'] * max(f, 0) ** P['punta'] + P['espalda'] * max(-f, 0) ** (P['punta'] * 0.8) + P['lado'] * (1 - abs(f))
        return -t * caida
    filas.append((cuelloz - (cuelloz - (h + 0.02)) * min(1, t * 1.6) * 0.9, r, dz, 1.0, 0.8))
filas = [f if len(f) > 2 else (f[0], f[1], None, 1.0, 1.0) for f in filas]
capi = objeto('capirote', torno(filas, segs=56, tapa_arriba=False), M['antifaz'])
capi.modifiers.new('solid', 'SOLIDIFY').thickness = 0.006
capi.modifiers.move(1, 0)

# ojos del antifaz (huecos oscuros)
oa, ob_ = P['ojo']
for s in (-1, 1):
    th = 0.36 * s
    rr = cr * 1.03
    e = elipsoide('ojo', (rr * math.sin(th), -rr * math.cos(th), cz + cr * 0.12), (oa, 0.012, ob_), M['ojo'],
                  rot=(0, 0, th))

# escudo sobre el babero
ez = h + 0.02 - P['babero'] * (0.35 if estilo == 'realista' else 0.05)
# el escudo va justo sobre la tela: se busca la superficie del antifaz con un rayo desde delante
dg = bpy.context.evaluated_depsgraph_get()
golpe, punto, *_ = capi.evaluated_get(dg).ray_cast(Vector((0, -2, ez)), Vector((0, 1, 0)))
ey = (punto.y if golpe else -(P['capa_r'] * 0.8)) - 0.02
esc_r = 0.05 if estilo == 'realista' else 0.07
bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=esc_r)
for v in bm.verts: v.co = Vector((v.co.x, 0, v.co.y * 1.25))
bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
o = objeto('escudo', bm, M['escudo'], subdiv=0); o.location = (0, ey, ez); o.rotation_euler = (-0.08, 0, 0)
bm = bmesh.new(); bmesh.ops.create_circle(bm, segments=32, radius=1)
anillo = [Vector((math.sin(a) * esc_r, 0, math.cos(a) * esc_r * 1.25)) for a in [2 * math.pi * i / 32 for i in range(33)]]
o = objeto('escudo_borde', tubo(anillo, [0.006] * 33, segs=8, tapas=False), M['oro'], subdiv=0)
o.location = (0, ey - 0.004, ez); o.rotation_euler = (-0.08, 0, 0)

# ---------------------------------------------------------------- cíngulo y borlas
ry = 0.78
pts = [Vector((math.sin(a) * P['r_cin'] * 1.08, -math.cos(a) * P['r_cin'] * 1.08 * ry, ci + 0.02))
       for a in [2 * math.pi * i / 40 for i in range(41)]]
objeto('cingulo', tubo(pts, [0.012 if estilo == 'realista' else 0.018] * 41, segs=10, tapas=False), M['cingulo'], subdiv=0)
for s, largo in ((-1, 0.42), (-1, 0.36)):
    x0 = 0.07 * s; y0 = -P['r_cin'] * ry * 1.05
    caida = largo * (1 if estilo == 'realista' else 0.55)
    pts = [(x0 + 0.01 * k, y0 - 0.02 * math.sin(k / 6 * math.pi) - 0.005 * k, ci + 0.02 - caida * k / 6) for k in range(7)]
    objeto('cordon', tubo(pts, [0.008] * 7, segs=8), M['cingulo'], subdiv=0)
    x, y, z = pts[-1]
    bm = tubo([(x, y, z + 0.01), (x, y, z - 0.02), (x, y, z - 0.07)], [0.012, 0.022, 0.03], segs=12)
    objeto('borla', bm, M['cingulo'], subdiv=1)

# ---------------------------------------------------------------- brazos, mangas, guantes y cirio (una postura por estilo)
def manga(nom, pts, rad):
    o = objeto(nom, tubo(pts, rad, segs=20, tapas=False), M['tunica'])
    o.modifiers.new('solid', 'SOLIDIFY').thickness = 0.006
    o.modifiers.move(1, 0)

def guante_cirio(mano, codo, k=1.0):
    # guante cerrado sobre el cirio: dorso, dedos alrededor y pulgar
    mn = P['mano'] * k
    u = (codo - mano); u = (u - dirc * u.dot(dirc)).normalized()          # hacia el dorso (lado del codo)
    v = dirc.cross(u).normalized()
    rr = P['cirio_r'] + mn * 0.22
    dorso = mano + u * (P['cirio_r'] + mn * 0.45)
    elipsoide('guante', dorso, (mn * 0.62, mn * 0.62, mn * 0.62), M['guante'])
    anillo = [mano + (u * math.cos(a) + v * math.sin(a)) * rr for a in [math.pi * (-0.75 + 1.5 * i / 10) for i in range(11)]]
    objeto('dedos', tubo(anillo, [mn * 0.36] * 11, segs=10), M['guante'], subdiv=1)
    objeto('pulgar', tubo([dorso + v * mn * 0.5, mano + v * rr * 0.9 + dirc * mn * 0.45], [mn * 0.26, mn * 0.22], segs=10),
           M['guante'], subdiv=1)

if estilo == 'realista':
    # Brazos pegados al cuerpo, codos a la altura de la cintura y antebrazos hacia delante: las dos manos sujetan
    # el cirio apoyado en la cadera, por debajo del babero.
    dirc = Vector((0.18, -0.16, 1)).normalized()                          # eje del cirio
    mano_d = Vector((P['r_cin'] * 0.75, -(r_tun(ci) * 0.78 + P['manga'] * 0.6 + 0.012), ci - 0.07))
    mano_i = mano_d - dirc * P['mano'] * 2.4 + Vector((-0.012, 0, 0))   # la izquierda, más abajo
    for nom, lado, mano in (('brazo_d', 1, mano_d), ('brazo_i', -1, mano_i)):
        # el brazo va por fuera de la túnica: a cada altura, radio del cuerpo más el grosor de la manga
        hombro = Vector((lado * (r_tun(h - 0.05) - P['brazo'] * 0.3), 0.01, h - 0.06))
        cz_ = ci - (0.02 if lado > 0 else 0.08)
        codo = Vector((lado * (r_tun(cz_) + P['brazo'] * 1.1), -0.01, cz_))
        zm = (hombro.z + codo.z) / 2
        medio = Vector((lado * (r_tun(zm) + P['brazo'] * 0.8), 0.0, zm))
        muneca = mano + (codo - mano).normalized() * P['mano'] * 1.1
        pts = [hombro, medio, codo, codo.lerp(muneca, 0.45), codo.lerp(muneca, 0.8), muneca]
        rad = [P['brazo'], P['brazo'] * 1.08, P['brazo'] * 1.2, P['manga'] * 0.72, P['manga'] * 0.68, P['manga'] * 0.6]
        # la manga cuelga: el centro de cada anillo baja según lo ancho que es
        pts = [p + Vector((0, 0, -(r - P['brazo']) * 0.3)) for p, r in zip(pts, rad)]
        manga(nom, pts, rad)
        guante_cirio(mano, codo)
    base = mano_d - dirc * P['mano'] * 4.0                                  # por debajo de la mano de abajo
else:
    # Cabezón: brazos cortos y redondos que salen por debajo de los lados del antifaz. La mano derecha agarra el
    # cirio en el costado, casi vertical; la izquierda cae relajada junto al cuerpo, con la manopla cerrada.
    dirc = Vector((0.1, -0.06, 1)).normalized()
    zh = ci + 0.17                                                         # los dos hombros, justo bajo el borde del antifaz
    mano_d = Vector((r_tun(ci) * 0.95, -(r_tun(ci) * 0.78 + 0.07), ci - 0.05))
    hombro = Vector((r_tun(zh) - 0.02, 0.0, zh))
    codo = Vector((r_tun(ci) + 0.055, -0.03, ci - 0.02))
    muneca = mano_d + (codo - mano_d).normalized() * 0.05
    manga('brazo_d', [hombro, hombro.lerp(codo, 0.5), codo, codo.lerp(muneca, 0.5), muneca], [0.06, 0.064, 0.066, 0.064, 0.068])
    guante_cirio(mano_d, codo, 0.85)
    hombro = Vector((-(r_tun(zh) - 0.02), 0.0, zh))
    codo = Vector((-(r_tun(ci) + 0.055), -0.03, ci - 0.02))                # simétrico al del cirio
    mano = Vector((-r_tun(ci) * 0.97, -(r_tun(ci) * 0.78 + 0.045), ci - 0.06))   # a la altura de la otra mano
    muneca = mano + (codo - mano).normalized() * 0.045
    manga('brazo_i', [hombro, hombro.lerp(codo, 0.5), codo, codo.lerp(muneca, 0.5), muneca], [0.06, 0.064, 0.066, 0.064, 0.068])
    elipsoide('guante', mano, (0.05, 0.048, 0.056), M['guante'])           # manopla
    elipsoide('pulgar', mano + Vector((0.025, -0.03, 0.01)), (0.018, 0.018, 0.024), M['guante'])
    base = mano_d - dirc * 0.16

# cirio apoyado en la cadera: sale de la mano derecha hacia arriba y algo hacia fuera y delante
punta = base + dirc * P['cirio_l']
objeto('cirio', tubo([base, base.lerp(punta, 0.5), punta], [P['cirio_r']] * 3, segs=16), M['cera'], subdiv=0)
for k, t in enumerate((0.9, 0.8, 0.95, 0.72)):                           # chorreones de cera
    p = base.lerp(punta, t); a = k * 1.9
    q = p + Vector((math.cos(a), math.sin(a), 0)) * P['cirio_r']
    objeto('cera', tubo([q, q + Vector((0, 0, -0.05 - 0.03 * k))], [0.006, 0.004], segs=6), M['cera'], subdiv=0)
ll = objeto('llama', tubo([punta + dirc * 0.005, punta + Vector((0, 0, 0.03)), punta + Vector((0, 0, 0.075))],
                          [0.012, 0.016, 0.0], segs=12), M['llama'], subdiv=1)

# ---------------------------------------------------------------- zapatos asomando por el bajo
for s in (-1, 1):
    elipsoide('zapato', (0.08 * s, -P['r_bajo'] * 0.72, 0.035), (0.045, 0.09, 0.035), M['zapato'])

if espejo:
    from mathutils import Matrix
    for o in list(scn.collection.objects):
        if o.type != 'MESH': continue
        o.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.reverse_faces(bm, faces=bm.faces[:]); bm.to_mesh(o.data); bm.free()
        o.location.x = -o.location.x; o.rotation_euler.z = -o.rotation_euler.z; o.rotation_euler.y = -o.rotation_euler.y

# ---------------------------------------------------------------- esqueleto y animaciones
# Se aplican los modificadores, se une todo en una malla y se pesa por zonas a 7 huesos:
#   raiz · cuerpo (túnica de cintura arriba, cíngulo) · cabeza (capirote y antifaz) · pierna_d / pierna_i (bajo de la
#   túnica y zapatos) · brazo_d / brazo_i (mangas y guantes; el del lado del cirio lleva el cirio).
# Animaciones: «andar» (paso de procesión, ciclo de 1,6 s) y «parado» (respiración), en bucle.
import os
from mathutils import Matrix
dg = bpy.context.evaluated_depsgraph_get()
mallas = [o for o in scn.collection.objects if o.type == 'MESH']
for o in mallas:
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    me.transform(o.matrix_world)
    o.modifiers.clear(); o.data = me; o.matrix_world = Matrix.Identity(4)
def centro(o): return sum((v.co for v in o.data.vertices), Vector()) / max(len(o.data.vertices), 1)
cirio_o = next(o for o in mallas if o.name.startswith('cirio'))
lado_cirio = 1 if centro(cirio_o).x > 0 else -1
nom_lado = lambda x: '_d' if x * lado_cirio > 0 else '_i'      # _d = lado del cirio
hombros = {}
for o in mallas:
    if o.name.startswith('brazo'):
        vs = [v.co for v in o.data.vertices]
        hom = max(vs, key=lambda c: c.z)
        hombros[nom_lado(centro(o).x)] = (hom.copy(), max(vs, key=lambda c: (c - hom).length).copy())
zc = ci - 0.08                                                   # cadera
huesos = ['raiz', 'cuerpo', 'cabeza', 'pierna_d', 'pierna_i', 'brazo_d', 'brazo_i']
def peso(o, v):
    n, c = o.name, v.co
    if n.startswith(('capirote', 'ojo', 'escudo')): return {'cabeza': 1}
    if n.startswith('zapato'): return {'pierna' + ('_d' if c.x * lado_cirio > 0 else '_i'): 1}
    if n.startswith(('cirio', 'cera', 'llama')): return {'brazo_d': 1}
    if n.startswith(('guante', 'dedos', 'pulgar')): return {'brazo' + nom_lado(centro(o).x): 1}
    if n.startswith('brazo'):
        b = 'brazo' + nom_lado(centro(o).x); hom = hombros[b[5:]][0]
        w = min(1, (c - hom).length / 0.08)
        return {b: w, 'cuerpo': 1 - w}
    if n.startswith('tunica') and c.z < zc:
        t = (zc - c.z) / zc; wl = 0.85 * t
        sd = min(1, max(0, 0.5 + c.x * lado_cirio / 0.12))
        return {'pierna_d': wl * sd, 'pierna_i': wl * (1 - sd), 'cuerpo': 1 - wl}
    return {'cuerpo': 1}
for o in mallas:
    grupos = {b: o.vertex_groups.new(name=b) for b in huesos}
    for v in o.data.vertices:
        for b, w in peso(o, v).items():
            if w > 0: grupos[b].add([v.index], w, 'REPLACE')
bpy.ops.object.select_all(action='DESELECT')
for o in mallas: o.select_set(True)
bpy.context.view_layer.objects.active = mallas[0]
bpy.ops.object.join()
cuerpo_m = bpy.context.view_layer.objects.active; cuerpo_m.name = 'nazareno'

arm = bpy.data.armatures.new('esqueleto'); rig = bpy.data.objects.new('esqueleto', arm); scn.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
def hueso(n, cab, cola, padre=None):
    b = arm.edit_bones.new(n); b.head = cab; b.tail = cola
    if padre: b.parent = arm.edit_bones[padre]
    return b
hueso('raiz', (0, 0, 0), (0, 0, 0.1))
hueso('cuerpo', (0, 0, zc), (0, 0, h), 'raiz')
hueso('cabeza', (0, 0, h), (0, 0, h + 0.3), 'cuerpo')
for sfx in ('_d', '_i'):
    x = 0.08 * lado_cirio * (1 if sfx == '_d' else -1)
    hueso('pierna' + sfx, (x, 0, zc), (x, 0, 0.02), 'raiz')
    hom, mano = hombros[sfx]
    hueso('brazo' + sfx, tuple(hom), tuple(mano), 'cuerpo')
bpy.ops.object.mode_set(mode='OBJECT')
cuerpo_m.parent = rig
cuerpo_m.modifiers.new('arm', 'ARMATURE').object = rig

# animaciones
fps = 30; scn.render.fps = fps
rig.animation_data_create()
pb = rig.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
amp = dict(pierna=0.32 if estilo == 'cabezon' else 0.22, brazo=0.22 if estilo == 'cabezon' else 0.0,
           bote=0.012 if estilo == 'cabezon' else 0.01, ladeo=0.06 if estilo == 'cabezon' else 0.03)
def accion(nombre, n, f):
    act = bpy.data.actions.new(nombre); rig.animation_data.action = act
    for k in range(0, n + 1, 2):
        t = (k % n) / n
        for b in pb: b.location = (0, 0, 0); b.rotation_euler = (0, 0, 0)
        f(t)
        for b in pb:
            b.keyframe_insert('location', frame=k); b.keyframe_insert('rotation_euler', frame=k)
    tr = rig.animation_data.nla_tracks.new(); tr.name = nombre
    tr.strips.new(nombre, 0, act)
    rig.animation_data.action = None
S = lambda t, fase=0.0: math.sin(2 * math.pi * t + fase)
def andar(t):
    pb['pierna_d'].rotation_euler.x = amp['pierna'] * S(t)
    pb['pierna_i'].rotation_euler.x = -amp['pierna'] * S(t)
    pb['cuerpo'].location.y = amp['bote'] * (0.5 - 0.5 * math.cos(4 * math.pi * t))    # sube en cada paso
    pb['cuerpo'].rotation_euler.z = amp['ladeo'] * S(t, 0.3)                      # se ladea hacia el pie que apoya
    pb['cuerpo'].rotation_euler.y = 0.05 * S(t)                                   # gira un poco la cadera
    pb['cabeza'].rotation_euler.z = -0.5 * amp['ladeo'] * S(t, -0.4)              # el capirote compensa con retraso
    pb['brazo_i'].rotation_euler.x = -amp['brazo'] * S(t)                         # el brazo libre se mece
    pb['brazo_d'].rotation_euler.x = 0.03 * S(t)
def parado(t):
    pb['cuerpo'].location.y = 0.004 * (0.5 - 0.5 * math.cos(2 * math.pi * t))
    pb['cabeza'].rotation_euler.z = 0.015 * S(t, 1.0)
    pb['brazo_i'].rotation_euler.x = 0.03 * S(t, 0.5)
accion('andar', 48, andar)
accion('parado', 90, parado)

raiz = bpy.data.objects.new('nazareno_' + estilo, None); scn.collection.objects.link(raiz)
rig.parent = raiz
bpy.ops.export_scene.gltf(filepath=salida, export_format='GLB', export_apply=False, export_animation_mode='NLA_TRACKS')
print('ok', salida)
