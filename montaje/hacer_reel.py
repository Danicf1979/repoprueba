#!/usr/bin/env python3
"""Genera un reel vertical 1080x1920 (IG Reels / YouTube Shorts / TikTok).

Uso:
  python3 hacer_reel.py                      # sin canción (se añade en la app)
  python3 hacer_reel.py --audio cancion.mp3  # con la canción, que baja de volumen cuando habla Sánchez

Imágenes opcionales: imagenes/NN.jpg (NN = número de tarjeta, 00 = intro).
Cortes de voz: voces/<nombre>.mp3 (o .m4a/.wav/.mp4). Si existe, la tarjeta dura lo que el corte
y la música se baja al 15 % mientras suena.
"""
import argparse, json, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OBL = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DUCK = 0.15  # volumen de la canción mientras habla Sánchez

def T(anio, tit, sub="", judicial=False, dur=2.0):
    return dict(tipo="dato", anio=anio, tit=tit, sub=sub, judicial=judicial, dur=dur)

def V(cita, contexto, voz, dur=3.0):
    return dict(tipo="voz", cita=cita, contexto=contexto, voz=voz, dur=dur)

TARJETAS = [
    T("", "2018 – 2026", "Lo que ha pasado con Sánchez en el Gobierno", dur=2.5),
    T("2020", "COVID: más de 100.000 muertos", "Los dos estados de alarma, declarados inconstitucionales por el TC", dur=2.2),
    T("2020", "Ábalos y Delcy Rodríguez en Barajas", "Tenía prohibida la entrada en la UE"),
    T("2021", "53 millones para rescatar Plus Ultra", "Una aerolínea pequeña, con fondos de la SEPI"),
    T("2021", "Ceuta: 10.000 personas entran en dos días", "Mayo de 2021", dur=2.2),
    T("2021", "Volcán de La Palma", "Quejas por el retraso de las ayudas"),
    T("2022", "Ley del «solo sí es sí»", "Más de 1.000 agresores sexuales con la pena rebajada", dur=2.2),
    T("2024", "Caso Koldo: mascarillas y comisiones", judicial=True),
    T("2024", "Ley de Amnistía", "A cambio de los votos de Junts"),
    T("2024", "Su mujer, Begoña Gómez, investigada", "Cátedra en la Complutense", True, 2.2),
    T("2024", "DANA de Valencia: 229 muertos", "Y el presidente dijo…", dur=2.0),
    V("Si necesitan más recursos, que los pidan", "Pedro Sánchez · 2 nov. 2024, tras la DANA", "dana"),
    T("2025", "Apagón: España entera sin luz", "28 de abril"),
    T("2025", "Su nº 3, Santos Cerdán, a prisión provisional", "", True, 2.2),
    V("Son las cinco y no he comido", "Pedro Sánchez · junio 2025, cortando las preguntas sobre Cerdán", "cinco", 2.5),
    T("2025", "Su hermano, enviado a juicio", "Por su puesto en la Diputación de Badajoz", True),
    V("Hay jueces que no cumplen con la ley", "Pedro Sánchez · septiembre 2025", "jueces", 2.5),
    V("¿La Fiscalía de quién depende? … Pues ya está", "Pedro Sánchez · noviembre 2019", "fiscalia", 2.8),
    T("2025", "Su fiscal general, condenado por el Supremo", "Revelación de secretos", dur=2.2),
    T("2025", "Ábalos y Koldo, a prisión provisional", "", True, 2.2),
    T("2026", "Adamuz: 46 muertos", "Descarrilan dos trenes de alta velocidad · enero", dur=2.2),
    T("2026", "Regularización masiva", "1,17 millones de solicitudes · plazo cerrado el 30 de junio", dur=2.2),
    T("2026", "Ceuta otra vez: 72.000 entradas en dos días", "30 y 31 de julio, según Interior. La Ciudad habla de más de 96.000", dur=2.5),
    T("2026", "Ley de nietos: el Supremo frena el voto de miles de nacionalizados", "Por el riesgo de un censo «irregular»", dur=2.5),
    T("2026", "Urda: 69 muertos", "Choque de dos trenes de alta velocidad · octubre", dur=2.2),
    T("", "Él no lo hizo solo.", "El 29-N, tú decides.", dur=3.2),
]

PALETA = [((120, 10, 20), (15, 5, 10)), ((20, 20, 30), (90, 0, 15))]


def fit(draw, texto, fuente_path, max_w, tam, max_lineas=4):
    while tam > 30:
        f = ImageFont.truetype(fuente_path, tam)
        lineas, act = [], ""
        for p in texto.split():
            prueba = (act + " " + p).strip()
            if draw.textlength(prueba, font=f) <= max_w:
                act = prueba
            else:
                lineas.append(act); act = p
        lineas.append(act)
        if len(lineas) <= max_lineas and all(draw.textlength(l, font=f) <= max_w for l in lineas):
            return f, lineas
        tam -= 6
    return ImageFont.truetype(fuente_path, tam), [texto]


def buscar(carpeta, base, exts):
    for ext in exts:
        p = os.path.join(AQUI, carpeta, f"{base}.{ext}")
        if os.path.exists(p):
            return p


def fondo(i, t):
    p = buscar("imagenes", f"{i:02d}", ("jpg", "jpeg", "png", "webp"))
    S = (int(W * 1.1), int(H * 1.1))
    if p:
        im = Image.open(p).convert("RGB")
        esc = max(S[0] / im.width, S[1] / im.height)
        im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
        x, y = (im.width - S[0]) // 2, (im.height - S[1]) // 2
        im = im.crop((x, y, x + S[0], y + S[1]))
        return Image.blend(im, Image.new("RGB", S, (0, 0, 0)), 0.45 if t["tipo"] == "dato" else 0.6)
    if t["tipo"] == "voz":
        return Image.new("RGB", S, (8, 8, 10))
    a, b = PALETA[i % 2]
    im = Image.new("RGB", S)
    d = ImageDraw.Draw(im)
    for y in range(S[1]):
        k = y / S[1]
        d.line([(0, y), (S[0], y)], fill=tuple(int(a[c] * (1 - k) + b[c] * k) for c in range(3)))
    if t["anio"]:
        f = ImageFont.truetype(BOLD, 520)
        capa = Image.new("RGBA", S, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        w = dc.textlength(t["anio"], font=f)
        dc.text(((S[0] - w) / 2, S[1] * 0.62), t["anio"], font=f, fill=(255, 255, 255, 28))
        im = Image.alpha_composite(im.convert("RGBA"), capa).convert("RGB")
    return im


def centrar(d, lineas, f, y, **kw):
    for l in lineas:
        d.text(((W - d.textlength(l, font=f)) / 2, y), l, font=f, **kw)
        y += int(f.size * 1.2)
    return y


def texto_png(t, ruta):
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    mw = W - 180
    if t["tipo"] == "voz":
        fe = ImageFont.truetype(BOLD, 40)
        et = "🔊 EN SUS PALABRAS".replace("🔊 ", "")
        w = d.textlength(et, font=fe)
        d.rounded_rectangle(((W - w) / 2 - 26, 640, (W + w) / 2 + 26, 708), 14, fill=(255, 210, 0, 255))
        d.text(((W - w) / 2, 650), et, font=fe, fill="black")
        f, ls = fit(d, f"«{t['cita']}»", OBL, mw, 92)
        y = centrar(d, ls, f, 780, fill="white", stroke_width=5, stroke_fill="black")
        fc, lc = fit(d, t["contexto"], REG, mw, 40, 3)
        centrar(d, lc, fc, y + 40, fill=(200, 200, 200))
    else:
        y = 700 if t["anio"] else 760
        if t["anio"]:
            f = ImageFont.truetype(BOLD, 64)
            w = d.textlength(t["anio"], font=f)
            d.rounded_rectangle(((W - w) / 2 - 30, y - 15, (W + w) / 2 + 30, y + 85), 18, fill=(220, 20, 40, 255))
            d.text(((W - w) / 2, y), t["anio"], font=f, fill="white")
            y += 140
        f, ls = fit(d, t["tit"], BOLD, mw, 96)
        y = centrar(d, ls, f, y, fill="white", stroke_width=6, stroke_fill="black")
        if t["sub"]:
            fs, ls = fit(d, t["sub"], REG, mw, 54)
            y = centrar(d, ls, fs, y + 25, fill=(255, 225, 120), stroke_width=4, stroke_fill="black")
        if t["judicial"]:
            centrar(d, ["Caso abierto · presunción de inocencia"], ImageFont.truetype(REG, 34), y + 30,
                    fill=(230, 230, 230), stroke_width=2, stroke_fill="black")
    capa.save(ruta)


def duracion(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p],
                       capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def ritmo(audio, inicio):
    """Estima el pulso (BPM) y la fase del primer beat. Devuelve (periodo_s, offset_s)."""
    import numpy as np
    sr, hop = 22050, 512
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(inicio), "-t", "90", "-i", audio,
                          "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    n = len(x) // hop
    e = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1))
    onset = np.maximum(np.diff(np.log1p(100 * e)), 0)
    onset -= onset.mean()
    fps = sr / hop
    ac = np.correlate(onset, onset, "full")[len(onset) - 1:]
    lags = np.arange(int(fps * 60 / 180), int(fps * 60 / 70))
    pesos = np.exp(-0.5 * (np.log2(60 * fps / lags / 120)) ** 2)  # prefiere ~120 BPM
    lag = lags[np.argmax(ac[lags] * pesos)]
    fases = [onset[f::lag].sum() for f in range(lag)]
    return lag / fps, int(np.argmax(fases)) / fps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", help="archivo de la canción")
    ap.add_argument("--inicio-cancion", type=float, default=0, help="segundo de la canción por el que empezar")
    ap.add_argument("--salida", default=os.path.join(AQUI, "reel_sanchez.mp4"))
    args = ap.parse_args()
    tmp = tempfile.mkdtemp()
    durs, fvoz = [], []
    for t in TARJETAS:
        v = buscar("voces", t["voz"], ("mp3", "m4a", "wav", "aac", "ogg", "mp4")) if t["tipo"] == "voz" else None
        if t["tipo"] == "voz" and not v:
            print(f"aviso: falta voces/{t['voz']}.mp3 — tarjeta sin voz")
        fvoz.append(v)
        durs.append(duracion(v) + 0.4 if v else t["dur"])
    if args.audio:  # encajar cada corte en un beat de la canción
        per, off = ritmo(args.audio, args.inicio_cancion)
        print(f"ritmo detectado: {60/per:.1f} BPM, primer beat en {off:.2f} s")
        fin_prev, nuevos = 0.0, []
        for i, d in enumerate(durs):
            fin = fin_prev + d
            k = round((fin - off) / per)
            if fvoz[i]:  # la voz no se corta: siguiente beat
                k = int(-(-(fin - off) // per))
            fin_b = off + k * per
            if fin_b - fin_prev < 2 * per:
                fin_b = fin_prev + 2 * per
            nuevos.append(fin_b - fin_prev); fin_prev = fin_b
        durs = nuevos
    clips, voces, t0 = [], [], 0.0
    for i, t in enumerate(TARJETAS):
        dur = durs[i]
        if fvoz[i]:
            voces.append((fvoz[i], t0 + 0.2, t0, t0 + dur))
        bg, tx = os.path.join(tmp, f"bg{i:02d}.png"), os.path.join(tmp, f"tx{i:02d}.png")
        clip = os.path.join(tmp, f"c{i:02d}.mp4")
        fondo(i, t).save(bg)
        texto_png(t, tx)
        n = round(dur * FPS)
        vf = (f"[0:v]scale={int(W*1.1)}:{int(H*1.1)},zoompan=z='1+0.08*on/{n}':d={n}"
              f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}[b];"
              f"[1:v]fade=t=in:st=0:d=0.15:alpha=1[t];[b][t]overlay=0:0,format=yuv420p")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", bg, "-loop", "1", "-i", tx,
                        "-filter_complex", vf, "-frames:v", str(n), "-c:v", "libx264", "-crf", "18", clip], check=True)
        clips.append(clip)
        t0 += n / FPS
    total = t0
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as fh:
        fh.writelines(f"file '{c}'\n" for c in clips)

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista]
    filtros, mezcla = [], []
    if args.audio:
        cmd += ["-ss", str(args.inicio_cancion), "-i", args.audio]
        cond = "+".join(f"between(t,{a:.2f},{b:.2f})" for _, _, a, b in voces) or "0"
        filtros.append(f"[1:a]volume='if({cond},{DUCK},1)':eval=frame,"
                       f"afade=t=out:st={total-1.5:.2f}:d=1.5[mus]")
        mezcla.append("[mus]")
    base = 2 if args.audio else 1
    for k, (v, ini, _, _) in enumerate(voces):
        cmd += ["-i", v]
        ms = int(ini * 1000)
        filtros.append(f"[{base+k}:a]aresample=44100,volume=1.6,adelay={ms}|{ms}[v{k}]")
        mezcla.append(f"[v{k}]")
    cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    mezcla.append(f"[{base+len(voces)}:a]")
    filtros.append("".join(mezcla) + f"amix=inputs={len(mezcla)}:normalize=0:duration=longest[a]")
    cmd += ["-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", args.salida]
    subprocess.run(cmd, check=True)
    print(f"OK: {args.salida} ({total:.1f} s, {len(voces)} cortes de voz)")


if __name__ == "__main__":
    main()
