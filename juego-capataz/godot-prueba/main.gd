extends Node3D
# La misma escena que la versión web (trono de palio en una calle de noche, con público),
# hecha con formas igual de simples, para comparar solo lo que aporta el motor:
# iluminación global, niebla volumétrica, reflejos en pantalla, oclusión ambiental y resplandor.

var rng = RandomNumberGenerator.new()
var cam: Camera3D

func mat(color: Color, metal := 0.0, rough := 0.8, emis := Color(0,0,0), emis_e := 0.0) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = color
	m.metallic = metal
	m.roughness = rough
	if emis_e > 0.0:
		m.emission_enabled = true
		m.emission = emis
		m.emission_energy_multiplier = emis_e
	return m

func add_mesh(mesh: Mesh, m: Material, pos: Vector3, rot := Vector3.ZERO, sc := Vector3.ONE, parent: Node3D = null) -> MeshInstance3D:
	var mi = MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = m
	mi.position = pos
	mi.rotation = rot
	mi.scale = sc
	(parent if parent else self).add_child(mi)
	return mi

func box(size: Vector3, m: Material, pos: Vector3, parent: Node3D = null) -> MeshInstance3D:
	var b = BoxMesh.new(); b.size = size
	return add_mesh(b, m, pos, Vector3.ZERO, Vector3.ONE, parent)

func cyl(r1: float, r2: float, h: float, m: Material, pos: Vector3, parent: Node3D = null, seg := 12) -> MeshInstance3D:
	var c = CylinderMesh.new(); c.top_radius = r1; c.bottom_radius = r2; c.height = h; c.radial_segments = seg
	return add_mesh(c, m, pos, Vector3.ZERO, Vector3.ONE, parent)

func sph(r: float, m: Material, pos: Vector3, sc := Vector3.ONE, parent: Node3D = null) -> MeshInstance3D:
	var s = SphereMesh.new(); s.radius = r; s.height = r * 2.0; s.radial_segments = 12; s.rings = 8
	return add_mesh(s, m, pos, Vector3.ZERO, sc, parent)

func omni(pos: Vector3, color: Color, energy: float, rng_: float, shadow := false, parent: Node3D = null) -> OmniLight3D:
	var l = OmniLight3D.new()
	l.position = pos; l.light_color = color; l.light_energy = energy; l.omni_range = rng_
	l.shadow_enabled = shadow
	l.light_volumetric_fog_energy = 1.5
	(parent if parent else self).add_child(l)
	return l

func _ready() -> void:
	rng.seed = 2027
	# --- Entorno: noche, tonemap ACES, resplandor, SSAO, SSR, SDFGI y niebla volumétrica
	var env = Environment.new()
	var sky = Sky.new(); var psm := ProceduralSkyMaterial.new()
	psm.sky_top_color = Color(0.02, 0.025, 0.07); psm.sky_horizon_color = Color(0.16, 0.11, 0.13)
	psm.ground_bottom_color = Color(0.02, 0.02, 0.03); psm.ground_horizon_color = Color(0.16, 0.11, 0.13)
	psm.sun_angle_max = 0.0
	sky.sky_material = psm
	env.background_mode = Environment.BG_SKY; env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.ambient_light_energy = 0.35
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_ACES; env.tonemap_exposure = 1.0
	env.glow_enabled = true; env.glow_intensity = 0.9; env.glow_bloom = 0.08; env.glow_hdr_threshold = 1.2
	env.ssao_enabled = true; env.ssao_intensity = 2.0
	env.ssr_enabled = true; env.ssr_max_steps = 64
	env.sdfgi_enabled = true; env.sdfgi_use_occlusion = true
	env.volumetric_fog_enabled = true; env.volumetric_fog_density = 0.018; env.volumetric_fog_albedo = Color(0.9, 0.85, 0.8)
	var we = WorldEnvironment.new(); we.environment = env; add_child(we)
	var luna = DirectionalLight3D.new(); luna.light_color = Color(0.55, 0.62, 0.9); luna.light_energy = 0.25
	luna.rotation_degrees = Vector3(-55, 30, 0); luna.shadow_enabled = true; add_child(luna)

	# --- Calle: suelo de granito pulido y fachadas con balcones
	var suelo = PlaneMesh.new(); suelo.size = Vector2(16, 120)
	add_mesh(suelo, mat(Color(0.42, 0.38, 0.34), 0.0, 0.28), Vector3(0, 0, 0))
	var colores = [Color(0.89, 0.79, 0.63), Color(0.92, 0.87, 0.8), Color(0.85, 0.72, 0.56), Color(0.94, 0.9, 0.84)]
	for lado in [-1, 1]:
		for k in range(10):
			var z = -55.0 + k * 11.0
			var h = 12.0 + rng.randf() * 6.0
			box(Vector3(0.5, h, 11.0), mat(colores[k % 4], 0.0, 0.9), Vector3(lado * 7.25, h / 2.0, z))
			box(Vector3(0.8, 0.3, 11.0), mat(Color(0.85, 0.81, 0.74)), Vector3(lado * 7.1, h, z))
			for fl in range(3):
				for w in range(3):
					var wz = z - 3.5 + w * 3.5
					var y = 4.3 + fl * 3.2
					var luz = rng.randf() < 0.35
					box(Vector3(0.1, 1.8, 1.1), mat(Color(0.05, 0.04, 0.06), 0, 0.5, Color(1.0, 0.7, 0.4), 2.5 if luz else 0.0), Vector3(lado * 6.98, y + 0.9, wz))
					if fl < 2 or rng.randf() < 0.5:
						box(Vector3(0.7, 0.1, 1.7), mat(Color(0.6, 0.57, 0.52)), Vector3(lado * 6.65, y - 0.05, wz))
						box(Vector3(0.04, 0.9, 1.7), mat(Color(0.08, 0.08, 0.09), 0.6, 0.4), Vector3(lado * 6.32, y + 0.45, wz))
			# farol de pared
			if k % 2 == 0:
				var fp = Vector3(lado * 6.4, 4.9, z + 2.0)
				cyl(0.2, 0.13, 0.5, mat(Color(0.08, 0.08, 0.09), 0.7, 0.4), fp)
				sph(0.12, mat(Color(1, 0.8, 0.5), 0, 0.5, Color(1.0, 0.75, 0.45), 6.0), fp)
				omni(fp + Vector3(-lado * 0.3, -0.3, 0), Color(1.0, 0.72, 0.45), 2.2, 14.0, k == 4)

	# --- Público a los dos lados (cápsulas con ropa de colores)
	var ropa = [Color(0.12, 0.13, 0.19), Color(0.16, 0.18, 0.27), Color(0.23, 0.16, 0.16), Color(0.29, 0.25, 0.21), Color(0.54, 0.48, 0.4), Color(0.85, 0.8, 0.72), Color(0.35, 0.16, 0.18)]
	var piel = mat(Color(0.82, 0.62, 0.48), 0, 0.6)
	for lado in [-1, 1]:
		for k in range(150):
			var z = -40.0 + rng.randf() * 70.0
			var x = lado * (5.4 + rng.randf() * 1.4)
			var e = 0.9 + rng.randf() * 0.2
			var cap = CapsuleMesh.new(); cap.radius = 0.2; cap.height = 1.45
			add_mesh(cap, mat(ropa[rng.randi() % ropa.size()], 0, 0.85), Vector3(x, 0.72 * e, z), Vector3.ZERO, Vector3(1, e, 0.75))
			sph(0.11, piel, Vector3(x, 1.55 * e, z), Vector3(1, 1.15, 1))

	# --- El trono
	var trono = Node3D.new(); add_child(trono)
	var oro = mat(Color(1.0, 0.76, 0.36), 1.0, 0.24)
	var plata = mat(Color(0.93, 0.93, 0.96), 1.0, 0.18)
	var madera = mat(Color(0.17, 0.1, 0.06), 0, 0.6)
	var tunica = mat(Color(0.23, 0.12, 0.31), 0, 0.95)
	var verde = mat(Color(0.07, 0.2, 0.14), 0.1, 0.65)
	var cera = mat(Color(0.95, 0.9, 0.8), 0, 0.5)
	var llama = mat(Color(1, 0.8, 0.45), 0, 0.5, Color(1.0, 0.72, 0.35), 9.0)
	for i in range(8):
		var x = -2.0 + i * 4.0 / 7.0
		var v = cyl(0.07, 0.07, 13.0, madera, Vector3(x, 1.5, 0), trono); v.rotation_degrees.x = 90
		for zz in [-6.6, 6.6]:
			var c = cyl(0.1, 0.13, 0.3, oro, Vector3(x, 1.5, zz), trono); c.rotation_degrees.x = 90
		# hombres de trono, por fuera de su varal
		var z = -6.2
		while z <= 6.21:
			if abs(x) > 1.9 or abs(z) >= 2.7:
				var hx = x + sign(x) * 0.17
				var cap = CapsuleMesh.new(); cap.radius = 0.24; cap.height = 1.45
				add_mesh(cap, tunica, Vector3(hx, 0.72, z), Vector3.ZERO, Vector3.ONE, trono)
				sph(0.105, piel, Vector3(hx, 1.52, z), Vector3(1, 1.12, 1), trono)
			z += 0.55
	box(Vector3(3.3, 0.35, 5.3), madera, Vector3(0, 1.75, 0), trono)
	box(Vector3(3.2, 0.9, 5.2), oro, Vector3(0, 2.38, 0), trono)
	for y in [1.95, 2.86]:
		box(Vector3(3.36, 0.09, 5.36), oro, Vector3(0, y, 0), trono)
	# candelería
	var filas = [[2.25, 0.35], [1.95, 0.45], [1.65, 0.55], [1.35, 0.64], [1.05, 0.72], [0.75, 0.78]]
	for f in filas:
		for k in range(11):
			var x = -1.15 + k * 0.23
			cyl(0.026, 0.026, f[1], cera, Vector3(x, 2.9 + f[1] / 2.0, f[0]), trono, 6)
			sph(0.03, llama, Vector3(x, 2.96 + f[1], f[0]), Vector3(1, 2, 1), trono)
	omni(Vector3(0, 3.6, 1.6), Color(1.0, 0.75, 0.45), 3.0, 9.0, true, trono)
	# arbotantes: árboles de hojarasca dorada con tulipas
	var cristal = mat(Color(1, 1, 1, 0.3), 0.1, 0.05)
	cristal.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	for sx in [-1, 1]:
		for sz in [-1, 1]:
			var base = Vector3(sx * 1.55, 2.9, sz * 2.55)
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
	# palio: varales de plata, techo y bambalinas
	for sx in [-1.25, 1.25]:
		for i in range(6):
			cyl(0.035, 0.035, 1.65, plata, Vector3(sx, 3.7, -1.85 + i * 0.74), trono)
	box(Vector3(2.6, 0.08, 3.8), verde, Vector3(0, 4.55, 0), trono)
	for b in [[Vector3(2.6, 0.45, 0.02), Vector3(0, 4.3, 1.9)], [Vector3(2.6, 0.45, 0.02), Vector3(0, 4.3, -1.9)], [Vector3(0.02, 0.45, 3.8), Vector3(1.3, 4.3, 0)], [Vector3(0.02, 0.45, 3.8), Vector3(-1.3, 4.3, 0)]]:
		box(b[0], verde, b[1], trono)
		var fleco = box(Vector3(b[0].x + 0.01, 0.08, b[0].z + 0.01), oro, b[1] + Vector3(0, -0.24, 0), trono)
	# la Virgen y el manto largo
	cyl(0.3, 0.38, 0.36, oro, Vector3(0, 3.08, -0.75), trono)
	cyl(0.08, 0.27, 0.78, mat(Color(0.94, 0.89, 0.8), 0.1, 0.6), Vector3(0, 3.65, -0.75), trono)
	sph(0.1, mat(Color(0.91, 0.76, 0.63), 0, 0.42), Vector3(0, 4.12, -0.73), Vector3(0.9, 1.15, 0.92), trono)
	cyl(0.1, 0.08, 0.09, oro, Vector3(0, 4.29, -0.77), trono)
	var rafaga = TorusMesh.new(); rafaga.inner_radius = 0.19; rafaga.outer_radius = 0.21
	add_mesh(rafaga, oro, Vector3(0, 4.17, -0.84), Vector3(PI / 2, 0, 0), Vector3.ONE, trono)
	var manto = box(Vector3(2.2, 0.05, 4.8), verde, Vector3(0, 2.75, -3.4), trono); manto.rotation_degrees.x = -9

	# --- Cámaras y capturas
	cam = Camera3D.new(); cam.fov = 55; add_child(cam)
	await get_tree().process_frame
	var tomas = [
		["frente", Vector3(0.6, 3.0, 6.5 + 20), Vector3(0, 3.6, 20)],
		["detras", Vector3(2.5, 7.0, -16 + 20), Vector3(0, 2.5, 26)],
		["lado", Vector3(5.2, 3.2, 3 + 20), Vector3(0, 3.0, 19)],
	]
	trono.position = Vector3(0, 0, 20)
	for t in tomas:
		cam.position = t[1]
		cam.look_at(t[2])
		for i in range(40):
			await get_tree().process_frame
		var img = get_viewport().get_texture().get_image()
		img.save_png("res://godot_" + t[0] + ".png")
		print("captura ", t[0])
	get_tree().quit()
