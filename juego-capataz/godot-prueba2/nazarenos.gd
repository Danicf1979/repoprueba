extends "res://main.gd"
# Prueba de estilo de los muñecos: el nazareno modelado en Blender (blender/nazareno.py) en dos proporciones,
# realista (1,75 m más capirote) y cabezón (unas 3 cabezas), en la misma calle de noche de main.gd.
# Cada cirio lleva su luz. Saca tres capturas (captura_naz_*.png) y se cierra.

var NAZ = {}
var tramo = []   # [nodo, fase] para el vaivén al andar

# El cirio va siempre por dentro del cortejo: el modelo lo lleva a su lado +X, así que la fila de la
# derecha (x > 0) se espeja.
func nazareno(estilo: String, pos: Vector3, rot_y := 0.0, espejo := false) -> Node3D:
	var n: Node3D = NAZ[estilo].instantiate()
	n.position = pos; n.rotation.y = rot_y + rng.randf_range(-0.06, 0.06)
	n.scale = Vector3.ONE * (0.96 + rng.randf() * 0.08)
	if espejo: n.scale.x = -n.scale.x
	add_child(n)
	for mi in n.find_children("llama*", "MeshInstance3D", true, false):
		var l = omni(mi.get_aabb().get_center() + Vector3(0, 0.03, 0), Color(1.0, 0.68, 0.35), 0.5, 3.0, false, n)
		l.light_volumetric_fog_energy = 0.6
	tramo.append([n, rng.randf() * TAU, pos])
	return n

func _ready() -> void:
	rng.seed = 2028
	for e in ["realista", "cabezon"]:
		NAZ[e] = load("res://modelos/nazareno_" + e + ".glb")
	montar_calle()
	# tramo realista (detrás) y tramo cabezón (delante), en dos filas por el centro de la calle, andando hacia +Z
	for i in range(12):
		for sx in [-1, 1]:
			nazareno("realista", Vector3(sx * 1.35, 0, -14.0 - i * 2.2), 0.0, sx > 0)
	for i in range(12):
		for sx in [-1, 1]:
			nazareno("cabezon", Vector3(sx * 1.1, 0, 26.0 - i * 1.5), 0.0, sx > 0)
	# la pareja para comparar de cerca
	nazareno("realista", Vector3(-0.55, 0, 2.0), -0.25)
	nazareno("cabezon", Vector3(0.55, 0, 2.0), 0.25, true)

	cam = Camera3D.new(); cam.fov = 45; add_child(cam)
	await get_tree().process_frame
	var tomas = [
		["naz_pareja", Vector3(0.3, 1.25, 5.6), Vector3(0, 1.05, 2.0)],
		["naz_realista", Vector3(-2.4, 2.0, -9.5), Vector3(0.6, 1.4, -24.0)],
		["naz_cabezon", Vector3(-2.0, 1.4, 30.0), Vector3(0.5, 0.75, 16.0)],
	]
	for t in tomas:
		cam.position = t[1]; cam.look_at(t[2])
		for i in range(45):
			await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png("res://captura_" + t[0] + ".png")
		print("captura ", t[0])
	get_tree().quit()

func _process(_dt: float) -> void:
	# vaivén del paso de procesión: leve balanceo lateral y cabeceo
	var t = Time.get_ticks_msec() / 1000.0
	for e in tramo:
		var n: Node3D = e[0]
		n.rotation.z = sin(t * 2.2 + e[1]) * 0.025
		n.position.y = e[2].y + abs(sin(t * 2.2 + e[1])) * 0.015
