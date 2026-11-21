# Prueba en Godot 4.3 con personajes de verdad

La salida de un trono de palio de noche, como en `trono.html`, pero hecha en Godot y con personajes animados en vez de figuras de código:

- **Personajes:** *Mini Characters* de [Kenney](https://kenney.nl) (licencia CC0, `personajes/LICENCIA-Kenney.txt`): 12 muñecos cabezones con esqueleto y 32 animaciones. El público está de pie (`idle`), los nazarenos andan (`walk`) con túnica, antifaz, capirote y cirio, y los hombres de trono sujetan el varal (`holding-both`) con la túnica de la hermandad.
- **La Virgen:** el modelo del juego web (`modelos/virgen.glb`) con la ráfaga recortada de la foto, bajo el palio alto (techo a 5,3 m).
- **El motor:** iluminación global (SDFGI), niebla volumétrica, sombras, resplandor y oclusión ambiental, con farolas, ventanas encendidas y la candelería.

Abre la carpeta con Godot 4.3 (Forward+) y ejecuta: `main.gd` monta la escena, saca tres capturas (`captura_cenital.png`, `captura_calle.png`, `captura_trono.png`) y se cierra.
