# Prueba en Godot 4.3 con personajes de verdad

La salida de un trono de palio de noche, como en `trono.html`, pero hecha en Godot y con personajes animados en vez de figuras de código:

- **Personajes:** *Mini Characters* de [Kenney](https://kenney.nl) (licencia CC0, `personajes/LICENCIA-Kenney.txt`): 12 muñecos cabezones con esqueleto y 32 animaciones. El público está de pie (`idle`), los nazarenos andan (`walk`) con túnica, antifaz, capirote y cirio, y los hombres de trono sujetan el varal (`holding-both`) con la túnica de la hermandad.
- **La Virgen:** el modelo del juego web (`modelos/virgen.glb`) con la ráfaga recortada de la foto, bajo el palio alto (techo a 5,3 m).
- **El motor:** iluminación global (SDFGI), niebla volumétrica, sombras, resplandor y oclusión ambiental, con farolas, ventanas encendidas y la candelería.

Abre la carpeta con Godot 4.3 (Forward+) y ejecuta: `main.gd` monta la escena, saca tres capturas (`captura_cenital.png`, `captura_calle.png`, `captura_trono.png`) y se cierra.

## Prueba de estilo del nazareno (modelado en Blender)

`blender/nazareno.py` modela el nazareno con Blender 5.2 usado sin pantalla (módulo `bpy` de Python) y lo exporta a
`modelos/nazareno_realista.glb` y `modelos/nazareno_cabezon.glb`: túnica con pliegues, capirote y antifaz de
terciopelo con babero, escudo, cíngulo con borlas, mangas, guantes, zapatos y cirio con chorreones y llama.
`blender/vista.py` hace una vista rápida de comprobación con Cycles.

`nazarenos.tscn` (script `nazarenos.gd`) pone un tramo de cada estilo en la misma calle de noche, cada cirio con su luz,
y saca tres capturas: `captura_naz_pareja.png`, `captura_naz_realista.png` y `captura_naz_cabezon.png`.
Todavía no tienen esqueleto: el vaivén es un balanceo por código. El siguiente paso es el esqueleto y las
animaciones con Mixamo.
