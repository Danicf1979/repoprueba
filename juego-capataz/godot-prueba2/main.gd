extends Node3D
# Prueba 2 en Godot 4.3: la salida de un trono de palio de noche, con personajes de verdad en vez de formas de código.
# - Personajes: «Mini Characters» de Kenney (CC0), cabezones con esqueleto y animaciones (de pie, andar, sujetar).
#   A los nazarenos se les pone túnica y capirote; a los hombres de trono, túnica de la hermandad.
# - La Virgen es el modelo 3D del juego web (modelos/virgen.glb) con la ráfaga recortada de la foto.
# - Lo que aporta el motor: iluminación global (SDFGI), niebla volumétrica, sombras de cada luz, resplandor y SSAO.
# Al ejecutarlo saca tres capturas (captura_*.png) y se cierra.

var rng = RandomNumberGenerator.new()
var cam: Camera3D
const ESC = 2.3            # los personajes de Kenney miden 0,67 m: así quedan en 1,55 m
const VARAL_Y = 1.05       # en este estilo cabezón el trono va más bajo, al hombro de los muñecos
var PERSONAJES = []

func mat(color: Color, metal := 0.0, rough := 0.8, emis := Color(0,0,0), emis_e := 0.0) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = color; m.metallic = metal; m.roughness = rough
	if emis_e > 0.0:
		m.emission_enabled = true; m.emission = emis; m.emission_energy_multiplier = emis_e
	return m

func add_mesh(mesh: Mesh, m: Material, pos: Vector3, parent: Node3D = null, rot := Vector3.ZERO, sc := Vector3.ONE) -> MeshInstance3D:
	var mi = MeshInstance3D.new(); mi.mesh = mesh; mi.material_override = m
	mi.position = pos; mi.rotation = rot; mi.scale = sc
	(parent if parent else self).add_child(mi)
	return mi

func box(size: Vector3, m: Material, pos: Vector3, parent: Node3D = null) -> MeshInstance3D:
	var b = BoxMesh.new(); b.size = size
	return add_mesh(b, m, pos, parent)

func cyl(r1: float, r2: float, h: float, m: Material, pos: Vector3, parent: Node3D = null, seg := 12) -> MeshInstance3D:
	var c = CylinderMesh.new(); c.top_radius = r1; c.bottom_radius = r2; c.height = h; c.radial_segments = seg
	return add_mesh(c, m, pos, parent)

func sph(r: float, m: Material, pos: Vector3, sc := Vector3.ONE, parent: Node3D = null) -> MeshInstance3D:
	var s = SphereMesh.new(); s.radius = r; s.height = r * 2.0; s.radial_segments = 12; s.rings = 8
	return add_mesh(s, m, pos, parent, Vector3.ZERO, sc)

func omni(pos: Vector3, color: Color, energy: float, rango: float, shadow := false, parent: Node3D = null) -> OmniLight3D:
	var l = OmniLight3D.new(); l.position = pos; l.light_color = color; l.light_energy = energy; l.omni_range = rango
	l.shadow_enabled = shadow; l.light_volumetric_fog_energy = 1.2
	(parent if parent else self).add_child(l)
	return l

# Un personaje de Kenney con una animación, en un punto, mirando hacia «mira»
func persona(pos: Vector3, rot_y: float, anim: String, parent: Node3D = null, cual := -1) -> Node3D:
	var esc: PackedScene = PERSONAJES[cual if cual >= 0 else rng.randi() % PERSONAJES.size()]
	var p: Node3D = esc.instantiate()
	p.position = pos; p.rotation.y = rot_y; p.scale = Vector3.ONE * ESC * (0.94 + rng.randf() * 0.1)
	(parent if parent else self).add_child(p)
	var ap: AnimationPlayer = p.find_child("AnimationPlayer", true, false)
	if ap and ap.has_animation(anim):
		ap.get_animation(anim).loop_mode = Animation.LOOP_LINEAR
		ap.play(anim); ap.seek(rng.randf() * 1.0, true); ap.speed_scale = 0.8 + rng.randf() * 0.4
	return p

func _ready() -> void:
	rng.seed = 2027
	for n in ["male-a", "male-b", "male-c", "male-d", "male-e", "male-f", "female-a", "female-b", "female-c", "female-d", "female-e", "female-f"]:
		PERSONAJES.append(load("res://personajes/character-" + n + ".glb"))
	# --- Entorno de noche
	var env = Environment.new()
	var sky = Sky.new(); var psm := ProceduralSkyMaterial.new()
	psm.sky_top_color = Color(0.03, 0.035, 0.1); psm.sky_horizon_color = Color(0.22, 0.14, 0.2)
	psm.ground_bottom_color = Color(0.02, 0.02, 0.03); psm.ground_horizon_color = Color(0.22, 0.14, 0.2)
	sky.sky_material = psm
	env.background_mode = Environment.BG_SKY; env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_ACES; env.tonemap_exposure = 1.1
	env.glow_enabled = true; env.glow_intensity = 0.8; env.glow_bloom = 0.06; env.glow_hdr_threshold = 1.3
	env.ssao_enabled = true; env.ssao_intensity = 1.5
	env.sdfgi_enabled = true; env.sdfgi_use_occlusion = true
	env.volumetric_fog_enabled = true; env.volumetric_fog_density = 0.012; env.volumetric_fog_albedo = Color(0.9, 0.85, 0.8)
	var we = WorldEnvironment.new(); we.environment = env; add_child(we)
	var luna = DirectionalLight3D.new(); luna.light_color = Color(0.6, 0.66, 0.95); luna.light_energy = 0.3
	luna.rotation_degrees = Vector3(-60, 25, 0); luna.shadow_enabled = true; add_child(luna)

	# --- Calle de adoquín, fachadas encaladas y de albero con balcones, colgaduras y banderines
	var adoq = StandardMaterial3D.new()
	adoq.albedo_texture = load("res://tex/adoq_diff.jpg"); adoq.normal_enabled = true; adoq.normal_texture = load("res://tex/adoq_nor.jpg")
	adoq.uv1_scale = Vector3(6, 45, 1); adoq.roughness = 0.75
	var suelo = PlaneMesh.new(); suelo.size = Vector2(13, 130)
	add_mesh(suelo, adoq, Vector3(0, 0, 0))
	var colores = [Color(0.96, 0.93, 0.86), Color(0.93, 0.78, 0.5), Color(0.96, 0.93, 0.86), Color(0.86, 0.55, 0.42)]
	var colg = [mat(Color(0.5, 0.06, 0.1), 0, 0.8), mat(Color(0.12, 0.32, 0.2), 0, 0.8), mat(Color(0.75, 0.6, 0.15), 0.2, 0.6)]
	var hierro = mat(Color(0.06, 0.06, 0.07), 0.6, 0.4)
	for lado in [-1, 1]:
		for k in range(12):
			var z = -60.0 + k * 10.0
			var h = 11.0 + rng.randf() * 5.0
			box(Vector3(0.5, h, 10.0), mat(colores[(k + (1 if lado > 0 else 0)) % 4], 0.0, 0.92), Vector3(lado * 6.75, h / 2.0, z))
			box(Vector3(0.9, 0.5, 10.0), mat(Color(0.55, 0.42, 0.3)), Vector3(lado * 6.55, 0.25, z))
			box(Vector3(0.8, 0.3, 10.0), mat(Color(0.85, 0.81, 0.74)), Vector3(lado * 6.6, h, z))
			for fl in range(3):
				for w in range(3):
					var wz = z - 3.2 + w * 3.2
					var y = 3.9 + fl * 3.1
					var luz = rng.randf() < 0.45
					box(Vector3(0.1, 1.8, 1.1), mat(Color(0.06, 0.05, 0.07), 0, 0.5, Color(1.0, 0.68, 0.38), 2.2 if luz else 0.0), Vector3(lado * 6.48, y + 0.9, wz))
					box(Vector3(0.7, 0.1, 1.7), mat(Color(0.62, 0.58, 0.52)), Vector3(lado * 6.15, y - 0.05, wz))
					box(Vector3(0.04, 0.9, 1.7), hierro, Vector3(lado * 5.82, y + 0.45, wz))
					if fl == 0 and rng.randf() < 0.6:   # colgadura del balcón
						var c = box(Vector3(0.03, 1.5, 1.5), colg[rng.randi() % 3], Vector3(lado * 5.78, y - 0.3, wz))
						box(Vector3(0.035, 0.08, 1.52), mat(Color(0.9, 0.72, 0.3), 0.6, 0.4), Vector3(lado * 5.77, y - 1.0, wz))
			if k % 2 == 0:   # farol de pared
				var fp = Vector3(lado * 6.0, 4.6, z + 2.0)
				cyl(0.2, 0.13, 0.5, hierro, fp)
				sph(0.12, mat(Color(1, 0.8, 0.5), 0, 0.5, Color(1.0, 0.75, 0.45), 6.0), fp)
				omni(fp + Vector3(-lado * 0.3, -0.3, 0), Color(1.0, 0.72, 0.45), 2.4, 14.0, k == 6)
	# banderines de lado a lado
	var bmats = [mat(Color(0.12, 0.32, 0.2), 0, 0.8), mat(Color(0.95, 0.92, 0.84), 0, 0.8), mat(Color(0.85, 0.68, 0.3), 0, 0.8)]
	for zb in range(-50, 50, 12):
		for i in range(20):
			var t = (i + 0.5) / 20.0
			var x = -5.8 + 11.6 * t
			var y = 7.0 - sin(PI * t) * 0.8
			var tri = PrismMesh.new(); tri.size = Vector3(0.36, 0.42, 0.02)
			add_mesh(tri, bmats[i % 3], Vector3(x, y - 0.21, zb), null, Vector3(PI, 0, 0))

	# --- Público: personajes de pie a los dos lados, mirando a la calle
	for lado in [-1, 1]:
		for fila in range(3):
			var z = -45.0
			while z < 45.0:
				var x = lado * (4.35 + fila * 0.55 + rng.randf() * 0.15)
				persona(Vector3(x, 0, z + rng.randf() * 0.3), (-PI / 2.0 if lado > 0 else PI / 2.0) + rng.randf_range(-0.4, 0.4), "idle")
				z += 0.75 + rng.randf() * 0.35

	# --- Cortejo: nazarenos con túnica y capirote, en dos filas, delante del trono
	var tunica_n = mat(Color(0.96, 0.95, 0.91), 0, 0.85)
	var capirote_n = mat(Color(0.11, 0.33, 0.22), 0, 0.8)
	var cera = mat(Color(0.95, 0.9, 0.8), 0, 0.5)
	var llama = mat(Color(1, 0.8, 0.45), 0, 0.5, Color(1.0, 0.72, 0.35), 9.0)
	var zt = 20.0
	for i in range(16):
		for sx in [-1, 1]:
			var pos = Vector3(sx * 1.4, 0, zt + 9.0 + i * 1.6)
			var n = persona(pos, 0.0, "walk")
			# túnica (cono hasta los pies) y capirote, colgados del personaje (en sus unidades)
			var tun = CylinderMesh.new(); tun.top_radius = 0.12; tun.bottom_radius = 0.2; tun.height = 0.34; tun.radial_segments = 14
			add_mesh(tun, tunica_n, Vector3(0, 0.17, 0), n)
			var cap = CylinderMesh.new(); cap.top_radius = 0.0; cap.bottom_radius = 0.17; cap.height = 0.55; cap.radial_segments = 14
			add_mesh(cap, capirote_n, Vector3(0, 0.62, -0.01), n)
			var ant = CylinderMesh.new(); ant.top_radius = 0.17; ant.bottom_radius = 0.2; ant.height = 0.08; ant.radial_segments = 14
			add_mesh(ant, capirote_n, Vector3(0, 0.33, 0), n)
			cyl(0.012, 0.012, 0.45, cera, Vector3(0.14, 0.28, 0.1), n, 6)
			sph(0.014, llama, Vector3(0.14, 0.52, 0.1), Vector3(1, 2, 1), n)
			if i % 4 == 0:
				omni(pos + Vector3(0, 1.3, 0.3), Color(1.0, 0.72, 0.4), 0.5, 3.0)

	# --- El trono, con hombres de trono, palio alto y la Virgen
	var trono = Node3D.new(); add_child(trono); trono.position = Vector3(0, 0, zt)
	var oro = mat(Color(1.0, 0.76, 0.36), 1.0, 0.24)
	var plata = mat(Color(0.93, 0.93, 0.96), 1.0, 0.18)
	var madera = mat(Color(0.17, 0.1, 0.06), 0, 0.6)
	var morado = mat(Color(0.3, 0.14, 0.42), 0, 0.9)
	var verde = mat(Color(0.07, 0.22, 0.15), 0.1, 0.65)
	var dy = VARAL_Y - 1.5
	for i in range(8):
		var x = -2.0 + i * 4.0 / 7.0
		var v = cyl(0.07, 0.07, 13.0, madera, Vector3(x, VARAL_Y, 0), trono); v.rotation_degrees.x = 90
		for zz in [-6.6, 6.6]:
			var c = cyl(0.1, 0.13, 0.3, oro, Vector3(x, VARAL_Y, zz), trono); c.rotation_degrees.x = 90
		var z = -6.2
		while z <= 6.21:
			if abs(x) > 1.9 or abs(z) >= 2.7:
				var h = persona(Vector3(x + sign(x) * 0.2, 0, z), 0.0, "holding-both", trono)
				var tun = CylinderMesh.new(); tun.top_radius = 0.13; tun.bottom_radius = 0.2; tun.height = 0.36; tun.radial_segments = 14
				add_mesh(tun, morado, Vector3(0, 0.18, 0), h)
			z += 0.6
	box(Vector3(3.3, 0.35, 5.3), madera, Vector3(0, 1.75 + dy, 0), trono)
	box(Vector3(3.2, 0.9, 5.2), oro, Vector3(0, 2.38 + dy, 0), trono)
	for y in [1.95, 2.86]:
		box(Vector3(3.36, 0.09, 5.36), oro, Vector3(0, y + dy, 0), trono)
	var filas = [[2.25, 0.35], [1.95, 0.45], [1.65, 0.55], [1.35, 0.64], [1.05, 0.72], [0.75, 0.78]]
	for f in filas:
		for k in range(11):
			var x = -1.15 + k * 0.23
			cyl(0.026, 0.026, f[1], cera, Vector3(x, 2.9 + dy + f[1] / 2.0, f[0]), trono, 6)
			sph(0.03, llama, Vector3(x, 2.96 + dy + f[1], f[0]), Vector3(1, 2, 1), trono)
	omni(Vector3(0, 3.4 + dy, 1.6), Color(1.0, 0.75, 0.45), 3.5, 9.0, true, trono)
	var cristal = mat(Color(1, 1, 1, 0.3), 0.1, 0.05); cristal.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	for sx in [-1, 1]:
		for sz in [-1, 1]:
			var base = Vector3(sx * 1.55, 2.9 + dy, sz * 2.55)
			for n in range(26):
				var t = n / 26.0
				var a = rng.randf() * TAU
				var r = 0.15 + t * 0.7
				var p = base + Vector3(sx * r * 0.9 + cos(a) * 0.25, 0.25 + t * 1.6, sz * r * 0.6 + sin(a) * 0.25)
				var hoja = sph(0.09, oro, p, Vector3(1, 0.35, 2.0), trono); hoja.rotation = Vector3(rng.randf(), rng.randf() * TAU, rng.randf())
				if n % 3 == 0:
					cyl(0.055, 0.045, 0.26, cristal, p + Vector3(0, 0.18, 0), trono)
					sph(0.022, llama, p + Vector3(0, 0.22, 0), Vector3(1, 2, 1), trono)
			omni(base + Vector3(sx * 0.6, 1.2, sz * 0.4), Color(1.0, 0.74, 0.42), 1.2, 5.0, false, trono)
	# palio alto: techo a 5,3 m (contado desde los varales a 1,5 m, como en el juego web)
	var techo_y = 5.3 + dy
	for sx in [-1.25, 1.25]:
		for i in range(6):
			cyl(0.035, 0.035, techo_y - (2.9 + dy), plata, Vector3(sx, (techo_y + 2.9 + dy) / 2.0, -1.85 + i * 0.74), trono)
	box(Vector3(2.6, 0.08, 3.8), verde, Vector3(0, techo_y, 0), trono)
	for b in [[Vector3(2.6, 0.45, 0.02), Vector3(0, techo_y - 0.25, 1.9)], [Vector3(2.6, 0.45, 0.02), Vector3(0, techo_y - 0.25, -1.9)], [Vector3(0.02, 0.45, 3.8), Vector3(1.3, techo_y - 0.25, 0)], [Vector3(0.02, 0.45, 3.8), Vector3(-1.3, techo_y - 0.25, 0)]]:
		box(b[0], verde, b[1], trono)
		box(Vector3(b[0].x + 0.01, 0.08, b[0].z + 0.01), oro, b[1] + Vector3(0, -0.24, 0), trono)
	# la Virgen: el modelo del juego web, de la peana (2,9 m) a la cruz de la ráfaga (4,42 m)
	var virgen: Node3D = load("res://modelos/virgen.glb").instantiate()
	trono.add_child(virgen)
	var aabb := AABB(); var primero = true
	for mi in virgen.find_children("*", "MeshInstance3D", true, false):
		var bb = mi.get_aabb(); bb = mi.transform * bb
		aabb = bb if primero else aabb.merge(bb); primero = false
	var k_v = (4.42 - 2.9) / aabb.size.y
	virgen.scale = Vector3.ONE * k_v
	virgen.position = Vector3(-aabb.get_center().x * k_v, 2.9 + dy - aabb.position.y * k_v, -0.75 - aabb.get_center().z * k_v)
	var raf = QuadMesh.new(); raf.size = Vector2(0.42, 0.42)
	var mraf = StandardMaterial3D.new(); mraf.albedo_texture = load("res://modelos/rafaga.png"); mraf.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	mraf.alpha_scissor_threshold = 0.45; mraf.metallic = 0.4; mraf.roughness = 0.35; mraf.cull_mode = BaseMaterial3D.CULL_DISABLED
	mraf.emission_enabled = true; mraf.emission = Color(0.42, 0.29, 0.11); mraf.emission_energy_multiplier = 0.6
	add_mesh(raf, mraf, Vector3(0, 4.225 + dy, -0.78), trono)
	omni(Vector3(0, 4.0 + dy, 0.3), Color(1.0, 0.82, 0.6), 1.2, 3.0, false, trono)
	var manto = box(Vector3(2.0, 0.05, 4.6), verde, Vector3(0, 2.85 + dy, -3.4), trono); manto.rotation_degrees.x = -9

	# --- Cámaras y capturas
	cam = Camera3D.new(); cam.fov = 50; add_child(cam)
	await get_tree().process_frame
	var tomas = [
		["cenital", Vector3(0, 22, zt - 6), Vector3(0, 0, zt + 8)],
		["calle", Vector3(-2.6, 2.4, zt + 22), Vector3(0.6, 2.2, zt + 4)],
		["trono", Vector3(3.6, 3.4, zt + 7.5), Vector3(0, 2.4, zt)],
	]
	for t in tomas:
		cam.position = t[1]; cam.look_at(t[2])
		for i in range(45):
			await get_tree().process_frame
		var img = get_viewport().get_texture().get_image()
		img.save_png("res://captura_" + t[0] + ".png")
		print("captura ", t[0])
	get_tree().quit()
