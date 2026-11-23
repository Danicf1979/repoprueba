# Vista rápida de comprobación (Cycles en CPU): los GLB que se pasen, en fila, de frente y de tres cuartos.
# Uso: python vista.py salida.png a.glb b.glb ...
import sys, math
import bpy
from mathutils import Vector

salida, glbs = sys.argv[1], sys.argv[2:]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
for i, g in enumerate(glbs):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=g)
    for o in set(bpy.data.objects) - antes:
        if o.parent is None:
            o.rotation_mode = 'XYZ'; o.location.x += i * 0.9; o.rotation_euler.z += float(__import__('os').environ.get('GIRO', '0'))
w = bpy.data.worlds.new('w'); scn.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.05, 0.05, 0.08, 1)
bpy.ops.mesh.primitive_plane_add(size=20)
for nom, pos, e, col in (('k', (2, -3, 4), 700, (1, 0.85, 0.7)), ('f', (-3, -2, 2.5), 250, (0.7, 0.8, 1)),
                         ('b', (0, 3, 3), 400, (1, 0.9, 0.8))):
    l = bpy.data.lights.new(nom, 'AREA'); l.energy = e; l.color = col; l.size = 2
    o = bpy.data.objects.new(nom, l); scn.collection.objects.link(o); o.location = pos
    o.rotation_euler = (Vector((0.45 * (len(glbs) - 1), 0, 1)) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
cam = bpy.data.cameras.new('c'); cam.lens = 50
c = bpy.data.objects.new('c', cam); scn.collection.objects.link(c); scn.camera = c
cx = 0.45 * (len(glbs) - 1)
import os; zz = float(os.environ.get("ZOOM", "1"))
c.location = (cx + 1.2 * zz, -4.2 * zz, 1.5 if zz == 1 else float(os.environ.get('ALTO', '1.25')))
c.rotation_euler = (Vector((cx, 0, 1.0 if zz == 1 else float(os.environ.get('ALTO', '1.25')) - 0.05)) - c.location).to_track_quat('-Z', 'Y').to_euler()
scn.render.engine = 'CYCLES'; scn.cycles.samples = 24; scn.cycles.use_denoising = True
scn.render.resolution_x, scn.render.resolution_y = 900, 900
scn.render.filepath = salida
bpy.ops.render.render(write_still=True)
