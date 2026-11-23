extends "res://main.gd"
# Fase 1 de ESPEC-TRONO.md: el trono de palio cabezón (blender/trono.py) parado en la calle de noche, con la luz de
# su candelería y de las tulipas de los arbotantes, y un tramo de nazarenos cabezones delante para ver la escala.
# Saca cinco capturas (captura_trono_*.png) y se cierra.

var luces = []   # [OmniLight3D, energía base, fase] para el parpadeo de las velas

func _ready() -> void:
	rng.seed = 11
	montar_calle()
	var trono: Node3D = load("res://modelos/trono_palio.glb").instantiate()
	add_child(trono)
	for n in trono.find_children("luz_*", "", true, false):
		var vela = n.name.begins_with("luz_vela")
		var l = omni(n.global_position + Vector3(0, 0.05, 0), Color(1.0, 0.66, 0.32), 0.55 if vela else 0.35, 2.6 if vela else 2.0, false)
		l.light_volumetric_fog_energy = 0.4
		luces.append([l, l.light_energy, rng.randf() * TAU])
	# luz suave de la candelería sobre la cara de la imagen, y una general cálida desde el frente
	omni(Vector3(0, 2.75, 0.25), Color(1.0, 0.75, 0.5), 0.22, 1.2, false)
	omni(Vector3(0, 2.0, 2.2), Color(1.0, 0.7, 0.4), 1.0, 5.0, true)
	# tramo de nazarenos delante del trono (el cirio por dentro)
	for i in range(5):
		for sx in [-1, 1]:
			var n: Node3D = load("res://modelos/nazareno_cabezon" + ("_espejo" if sx > 0 else "") + ".glb").instantiate()
			n.position = Vector3(sx * 1.1, 0, 5.5 + i * 1.5)
			add_child(n)
			var ap: AnimationPlayer = n.find_child("AnimationPlayer", true, false)
			if ap: ap.play("parado"); ap.seek(rng.randf() * 3.0, true)
	cam = Camera3D.new(); cam.fov = 45; add_child(cam)
	await get_tree().process_frame
	var tomas = [
		["trono_frente", Vector3(3.3, 1.5, 6.2), Vector3(0, 1.7, 0)],
		["trono_lado", Vector3(6.2, 2.0, 0.6), Vector3(0, 1.6, 0.2)],
		["trono_cenital", Vector3(0.5, 9.5, 4.5), Vector3(0, 0.5, 0.2)],
		["trono_virgen", Vector3(0.35, 2.62, 0.95), Vector3(0, 2.62, -0.5)],
		["trono_calle", Vector3(-2.6, 1.9, 15.5), Vector3(0.3, 1.5, 2.0)],
	]
	for t in tomas:
		cam.position = t[1]; cam.look_at(t[2])
		for i in range(45):
			await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png("res://captura_" + t[0] + ".png")
		print("captura ", t[0])
	get_tree().quit()

func _process(_dt: float) -> void:
	var t = Time.get_ticks_msec() / 1000.0
	for e in luces:
		e[0].light_energy = e[1] * (0.88 + 0.12 * sin(t * 9.0 + e[2]) * sin(t * 5.3 + e[2] * 2.0))
