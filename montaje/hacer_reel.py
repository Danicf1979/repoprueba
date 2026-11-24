#!/usr/bin/env python3
"""Genera un reel vertical 1080x1920 (IG Reels / YouTube Shorts / TikTok).

Uso:
  python3 hacer_reel.py                      # vídeo sin música (la canción se añade en la app)
  python3 hacer_reel.py --audio cancion.mp3  # con audio propio

Imágenes opcionales: montaje/imagenes/NN.jpg (o .png / .mp4 no) donde NN es el número
de tarjeta (00 = intro). Si no existe, se usa un fondo de color.
"""
import argparse, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# (año, titular, subtítulo, ¿caso judicial abierto?, duración s)
TARJETAS = [
    ("", "2018 – 2025", "Lo que ha pasado con Sánchez en el Gobierno", False, 2.5),
    ("2020", "COVID: más de 100.000 muertos", "Los dos estados de alarma, declarados inconstitucionales por el TC", False, 2.2),
    ("2020", "Ábalos y Delcy Rodríguez en Barajas", "Tenía prohibida la entrada en la UE", False, 2.0),
    ("2021", "53 millones para rescatar Plus Ultra", "Una aerolínea pequeña, con fondos de la SEPI", False, 2.0),
    ("2021", "Ceuta: unas 10.000 entradas en 48 h", "Crisis migratoria con Marruecos", False, 2.0),
    ("2021", "Volcán de La Palma", "Quejas por el retraso de las ayudas", False, 2.0),
    ("2022", "Ley del «solo sí es sí»", "Más de 1.000 agresores sexuales con la pena rebajada", False, 2.2),
    ("2024", "Caso Koldo: mascarillas y comisiones", "", True, 2.0),
    ("2024", "Ley de Amnistía", "A cambio de los votos de Junts", False, 2.0),
    ("2024", "Su mujer, Begoña Gómez, investigada", "Cátedra en la Complutense", True, 2.2),
    ("2024", "DANA: 229 muertos", "«Si necesitan ayuda, que la pidan»", False, 2.5),
    ("2025", "Apagón: España entera sin luz", "28 de abril", False, 2.0),
    ("2025", "Su nº 3, Santos Cerdán, a prisión provisional", "", True, 2.2),
    ("2025", "Su hermano, enviado a juicio", "Por su puesto en la Diputación de Badajoz", True, 2.0),
    ("2025", "Su fiscal general, condenado por el Supremo", "Revelación de secretos", False, 2.2),
    ("2025", "Ábalos y Koldo, a prisión provisional", "", True, 2.2),
    ("", "Y aun así…", "¿Tú le vas a votar?", False, 3.0),
]

PALETA = [((120, 10, 20), (15, 5, 10)), ((20, 20, 30), (90, 0, 15))]


def fit(draw, texto, fuente_path, max_w, tam):
    """Parte el texto en líneas y reduce el tamaño hasta que quepa en max_w (máx. 4 líneas)."""
    while tam > 30:
        f = ImageFont.truetype(fuente_path, tam)
        palabras, lineas, act = texto.split(), [], ""
        for p in palabras:
            prueba = (act + " " + p).strip()
            if draw.textlength(prueba, font=f) <= max_w:
                act = prueba
            else:
                lineas.append(act); act = p
        lineas.append(act)
        if len(lineas) <= 4 and all(draw.textlength(l, font=f) <= max_w for l in lineas):
            return f, lineas
        tam -= 6
    return ImageFont.truetype(fuente_path, tam), [texto]


def fondo(i, anio):
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = os.path.join(AQUI, "imagenes", f"{i:02d}.{ext}")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            esc = max(W * 1.1 / im.width, H * 1.1 / im.height)
            im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
            x, y = (im.width - int(W * 1.1)) // 2, (im.height - int(H * 1.1)) // 2
            im = im.crop((x, y, x + int(W * 1.1), y + int(H * 1.1)))
            oscuro = Image.new("RGB", im.size, (0, 0, 0))
            return Image.blend(im, oscuro, 0.45)
    a, b = PALETA[i % 2]
    im = Image.new("RGB", (int(W * 1.1), int(H * 1.1)))
    d = ImageDraw.Draw(im)
    for y in range(im.height):
        t = y / im.height
        d.line([(0, y), (im.width, y)], fill=tuple(int(a[k] * (1 - t) + b[k] * t) for k in range(3)))
    if anio:  # año gigante de marca de agua
        f = ImageFont.truetype(BOLD, 520)
        capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        w = dc.textlength(anio, font=f)
        dc.text(((im.width - w) / 2, im.height * 0.62), anio, font=f, fill=(255, 255, 255, 28))
        im = Image.alpha_composite(im.convert("RGBA"), capa).convert("RGB")
    return im


def texto_png(i, anio, titular, sub, judicial, ruta):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    margen = 90
    y = 700 if anio else 760
    if anio:
        f = ImageFont.truetype(BOLD, 64)
        w = d.textlength(anio, font=f)
        d.rounded_rectangle(((W - w) / 2 - 30, y - 15, (W + w) / 2 + 30, y + 85), 18, fill=(220, 20, 40, 255))
        d.text(((W - w) / 2, y), anio, font=f, fill="white")
        y += 140
    f, lineas = fit(d, titular, BOLD, W - 2 * margen, 96)
    for l in lineas:
        w = d.textlength(l, font=f)
        d.text(((W - w) / 2, y), l, font=f, fill="white", stroke_width=6, stroke_fill="black")
        y += int(f.size * 1.18)
    if sub:
        y += 25
        fs, ls = fit(d, sub, REG, W - 2 * margen, 54)
        for l in ls:
            w = d.textlength(l, font=fs)
            d.text(((W - w) / 2, y), l, font=fs, fill=(255, 225, 120), stroke_width=4, stroke_fill="black")
            y += int(fs.size * 1.25)
    if judicial:
        fj = ImageFont.truetype(REG, 34)
        t = "Caso abierto · presunción de inocencia"
        w = d.textlength(t, font=fj)
        d.text(((W - w) / 2, y + 30), t, font=fj, fill=(230, 230, 230), stroke_width=2, stroke_fill="black")
    capa.save(ruta)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio")
    ap.add_argument("--salida", default=os.path.join(AQUI, "reel_sanchez.mp4"))
    args = ap.parse_args()
    tmp = tempfile.mkdtemp()
    clips = []
    for i, (anio, tit, sub, jud, dur) in enumerate(TARJETAS):
        bg, tx, clip = (os.path.join(tmp, f"{n}{i:02d}.png") for n in ("bg", "tx", "c"))
        clip = clip[:-4] + ".mp4"
        fondo(i, anio).save(bg)
        texto_png(i, anio, tit, sub, jud, tx)
        n = int(dur * FPS)
        vf = (f"[0:v]scale={int(W*1.1)}:{int(H*1.1)},zoompan=z='1+0.08*on/{n}':d={n}"
              f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}[b];"
              f"[1:v]fade=t=in:st=0:d=0.15:alpha=1[t];[b][t]overlay=0:0,format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", bg, "-loop", "1", "-i", tx,
                        "-filter_complex", vf, "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium",
                        "-crf", "18", clip], check=True)
        clips.append(clip)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as fh:
        fh.writelines(f"file '{c}'\n" for c in clips)
    total = sum(t[4] for t in TARJETAS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista]
    if args.audio:
        cmd += ["-i", args.audio, "-map", "0:v", "-map", "1:a", "-af", f"afade=t=out:st={total-1.5}:d=1.5"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a"]
    cmd += ["-t", str(total), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-b:a", "192k", "-movflags", "+faststart", args.salida]
    subprocess.run(cmd, check=True)
    print("OK:", args.salida, f"({total:.1f} s)")


if __name__ == "__main__":
    main()
