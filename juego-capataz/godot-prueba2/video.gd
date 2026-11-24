extends "res://main.gd"
# Vídeo de prueba del movimiento: un tramo de nazarenos cabezones con esqueleto (blender/nazareno.py) andando por la
# calle de noche. A los 5 s para la cabeza del tramo y la parada corre hacia atrás pareja a pareja; a los 9,5 s
# arrancan igual. Se graba con el «movie maker» de Godot:
#   godot --path . --write-movie salida.avi --fixed-fps 30 --quit-after 450 res://video.tscn

const V = 0.24             # m/s andando (paso de procesión del cabezón)
const PARA = 5.0
const ARRANCA = 9.5
const RETRASO = 0.45       # s entre pareja y pareja
var filas = []             # [nodo, AnimationPlayer, pareja, velocidad actual, andando]
var t := 0.0

func nazareno(pos: Vector3, espejo: bool, pareja: int) -> void:
	var n: Node3D = load("res://modelos/nazareno_cabezon" + ("_espejo" if espejo else "") + ".glb").instantiate()
	n.position = pos; n.rotation.y = rng.randf_range(-0.04, 0.04)
	add_child(n)
	var ap: AnimationPlayer = n.find_child("AnimationPlayer", true, false)
	for a in ["andar", "parado"]:
		ap.get_animation(a).loop_mode = Animation.LOOP_LINEAR
	ap.play("andar"); ap.seek(rng.randf() * 1.6, true); ap.speed_scale = 0.95 + rng.randf() * 0.1
	# luz del cirio, en la llama (punta del cirio del modelo: x 0,27, alto 1,17, delante 0,27)
	var l = omni(Vector3(0.27 * (-1.0 if espejo else 1.0), 1.2, 0.27), Color(1.0, 0.68, 0.35), 0.45, 3.0, false, n)
	l.light_volumetric_fog_energy = 0.6
	filas.append([n, ap, pareja, V, true])

func _ready() -> void:
	rng.seed = 7
	montar_calle()
	for i in range(12):
		for sx in [-1, 1]:
			nazareno(Vector3(sx * 1.1, 0, -i * 1.5), sx > 0, i)
	cam = Camera3D.new(); cam.fov = 42; add_child(cam)

func _process(dt: float) -> void:
	t += dt
	for f in filas:
		var n: Node3D = f[0]; var ap: AnimationPlayer = f[1]; var p: int = f[2]
		var debe = not (t > PARA + p * RETRASO and t < ARRANCA + p * RETRASO)
		if debe != f[4]:
			f[4] = debe
			ap.play("andar" if debe else "parado", 0.35)
		f[3] = move_toward(f[3], V if debe else 0.0, dt * 0.9)
		n.position.z += f[3] * dt
	# cámara: sigue a la cabeza del tramo, delante y a un lado, a la altura de la gente, girando despacio
	var zc = filas[0][0].position.z
	var a = -0.75 + t * 0.045
	cam.position = Vector3(sin(a) * 3.0, 1.05, zc + 0.6 + cos(a) * 3.0)
	cam.look_at(Vector3(0.0, 0.55, zc - 1.2))
