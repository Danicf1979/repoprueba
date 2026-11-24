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
def _fuente(*cands):
    for c in cands:
        if os.path.exists(c):
            return c
    raise SystemExit(f"No encuentro ninguna fuente: {cands}")
BOLD = _fuente("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf")
REG = _fuente("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf")
OBL = BOLD
DUCK = 0.15  # volumen de la canción mientras habla Sánchez

def lectura(*textos):
    """Segundos para leerlo: 0,5 s base + 0,2 s por palabra (mín. 1,4 s)."""
    n = sum(len(t.split()) for t in textos if t)
    return max(1.4, 0.5 + 0.2 * n)

def T(anio, tit, sub="", judicial=False, dur=None, sello="", img=None):
    """Dato. img = nombre del fondo en imagenes/<img>.mp4/.jpg (opcional)."""
    return dict(tipo="dato", anio=anio, tit=tit, sub=sub, judicial=judicial, sello=sello, img=img,
                dur=dur or lectura(tit, sub) + (0.3 if judicial else 0))

def V(cita, contexto, voz, dur=None):
    """Frase de Sánchez. voces/<voz>.mp4 (vídeo con sonido) o .mp3 (solo audio)."""
    return dict(tipo="voz", cita=cita, contexto=contexto, voz=voz, dur=dur or lectura(cita) + 0.3)

def R(clip, rotulo="Mientras tanto…", dur=1.7):
    """Plano de contraste (Sánchez riendo, bailando…): reacciones/<clip>.mp4/.jpg. Si no existe, se salta."""
    return dict(tipo="reac", clip=clip, rotulo=rotulo, dur=dur)

TARJETAS = [
    T("", "2018 – 2026", "Lo que ha pasado con Sánchez", dur=1.9, img="intro"),
    R("baile1", "Feb. 2019"),
    T("2020", "COVID: +100.000 muertos", "Confinamiento inconstitucional", img="covid"),
    T("2020", "Ábalos y Delcy en Barajas", img="delcy"),
    T("2021", "53 millones para Plus Ultra", img="plusultra"),
    T("2021", "Ceuta: 10.000 entradas en 2 días", img="ceuta21"),
    T("2021", "Indulta a los 9 condenados del procés", img="indultos"),
    T("2021", "La Palma", "Ayudas que no llegaban", img="palma"),
    T("2022", "«Solo sí es sí»", "+1.000 rebajas a agresores sexuales", img="solosi"),
    T("2022", "Suprime la sedición", "Y rebaja la malversación"),
    T("2023", "«Tito Berni», diputado del PSOE", "A juicio por cohecho (caso Mediador)", True, img="tito"),
    R("baile_iceta", "Jul. 2023"),
    R("risa1", "Nov. 2023"),
    T("2024", "Caso Koldo", "Mascarillas y comisiones", True, img="koldo"),
    T("2024", "Su mujer, investigada", "Begoña Gómez", True, img="begona"),
    T("2024", "Amnistía", "A cambio de 7 votos de Junts", img="amnistia"),
    T("2024", "ERE: el Constitucional anula las condenas", "Chaves y Griñán · 680 M€ malversados", img="ere"),
    T("2024", "DANA: 229 muertos", "Y el presidente dijo…", img="dana"),
    V("Si necesita más recursos, que los pida", "2 nov. 2024, comparecencia tras la DANA", "dana"),
    T("2025", "La expareja de Ábalos cobró de empresas públicas", "Admitió en el Supremo que no fue ni un día"),
    T("2025", "Apagón total", "28 de abril", img="apagon"),
    T("2025", "Su nº 3, Cerdán, a prisión", "", True, img="cerdan"),
    V("Son las cinco, no he comido", "Junio 2025, rueda de prensa en Ferraz", "cinco"),
    T("2025", "Paco Salazar, su mano derecha en Moncloa", "Denuncias de acoso. El PSOE admitió «no estar a la altura»"),
    T("2025", "Leire Díez, «la fontanera» del PSOE", "Imputada por cohecho y tráfico de influencias", True),
    T("2025", "Su hermano, a juicio", "", True, img="hermano"),
    V("Hay jueces haciendo política y políticos que tratan de hacer justicia", "Septiembre 2025, entrevista en TVE", "jueces"),
    V("¿La Fiscalía de quién depende? Pues ya está", "Nov. 2019, entrevista en RNE", "fiscalia"),
    T("2025", "Su fiscal general, condenado", "Por el Supremo", img="fiscal"),
    T("2025", "Ábalos y Koldo, a prisión", "", True, img="abalos"),
    R("risa2", "Nov. 2025"),
    T("2026", "Tren de Adamuz: 46 muertos", img="adamuz"),
    T("2026", "Tercer año sin Presupuestos", "Siguen los de 2023, prorrogados"),
    R("risa_montero26", "Mar. 2026", dur=2.4),
    T("2026", "Regularización masiva", "1,17 millones de solicitudes", img="regularizacion"),
    R("montero_mitin_may", "Mayo 2026", dur=3.0),
    T("2026", "Zapatero, imputado en el caso Plus Ultra", "Primer expresidente imputado", True, img="zapatero"),
    T("2026", "Ábalos, condenado a 24 años", "Koldo, a 19. Por el Supremo", img="abalos_condena"),
    T("2026", "Su hermano, condenado", "9 años de inhabilitación · recurrida", img="hermano_condena"),
    T("2026", "Ceuta: 72.000 entradas en 2 días", "96.000, según la Ciudad", img="ceuta26"),
    R("vacaciones", "Agosto 2026, de vacaciones", dur=2.6),
    T("2026", "Su mujer, a juicio con jurado", "Tráfico de influencias y malversación", True, img="begona_juicio"),
    T("2026", "Ley de nietos", "El Supremo frena su voto"),
    T("2026", "63 subidas de impuestos y cotizaciones", "141 con las encubiertas · Instituto Juan de Mariana"),
    R("baile2", "Oct. 2026"),
    R("montero_mitin_oct", "Oct. 2026", dur=2.4),
    T("2026", "Tren de Urda: 69 muertos", img="urda"),
    R("baile_sevilla", "Nov. 2026", dur=2.4),
    T("", "Yo sí te voy a votar…\n¿sabiendo todo esto?", dur=3.5, sello="29-N"),
]

# Encuadre por clip para el recorte vertical: (centro_x, centro_y, zoom), en fracciones del fotograma
# original. Sin entrada = recorte centrado sin zoom.
ENCUADRE = {}
try:
    with open(os.path.join(AQUI, "encuadre.json"), encoding="utf-8") as fh:
        ENCUADRE = {k: tuple(v) for k, v in json.load(fh).items()}
except FileNotFoundError:
    pass


def recorte(ruta, clave, es_fondo=False):
    """Filtro crop 9:16 centrado en el encuadre de `clave` (o centrado sin zoom)."""
    # Fondos de archivo (NN): zoom ligero hacia arriba para dejar fuera los rótulos de las cadenas.
    defecto = (0.5, 0.42, 1.3) if es_fondo else (0.5, 0.5, 1.0)
    cx, cy, z = ENCUADRE.get(clave, defecto)
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0", ruta], capture_output=True, text=True, check=True)
    iw, ih = map(int, r.stdout.strip().split(",")[:2])
    ch = ih / z
    cw = ch * W / H
    if cw > iw:
        cw = iw; ch = cw * H / W
    x = min(max(cx * iw - cw / 2, 0), iw - cw)
    y = min(max(cy * ih - ch / 2, 0), ih - ch)
    return f"crop={int(cw)}:{int(ch)}:{int(x)}:{int(y)},"


PALETA = [((120, 10, 20), (15, 5, 10)), ((20, 20, 30), (90, 0, 15))]


def fit(draw, texto, fuente_path, max_w, tam, max_lineas=4):
    while tam > 30:
        f = ImageFont.truetype(fuente_path, tam)
        lineas = []
        for parrafo in texto.split("\n"):  # respeta saltos manuales
            act = ""
            for p in parrafo.split():
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


VIDEO = ("mp4", "mov", "m4v", "webm", "mkv")
IMG = ("jpg", "jpeg", "png", "webp")


def fondo(i, t, p=None):
    p = p or buscar("imagenes", t.get("img") or f"{i:02d}", IMG)
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
    if t["tipo"] == "reac":
        y = 1330
        for k, linea in enumerate(t["rotulo"].split("\n")):
            f, ls = fit(d, linea, BOLD, mw, 64 if k == 0 else 46, 2)
            for l in ls:
                w = d.textlength(l, font=f)
                d.rounded_rectangle(((W - w) / 2 - 30, y, (W + w) / 2 + 30, y + f.size + 26), 18, fill=(0, 0, 0, 170))
                d.text(((W - w) / 2, y + 8), l, font=f, fill="white")
                y += f.size + 36
    elif t["tipo"] == "voz":
        fe = ImageFont.truetype(BOLD, 40)
        et = "🔊 EN SUS PALABRAS".replace("🔊 ", "")
        w = d.textlength(et, font=fe)
        if not t.get("video"):
            d.rounded_rectangle(((W - w) / 2 - 26, 640, (W + w) / 2 + 26, 708), 14, fill=(255, 210, 0, 255))
            d.text(((W - w) / 2, 650), et, font=fe, fill="black")
        y0 = 1180 if t.get("video") else 780
        if t.get("video"):
            d.rectangle((0, y0 - 150, W, H - 330), fill=(0, 0, 0, 150))
            d.rounded_rectangle(((W - w) / 2 - 26, y0 - 130, (W + w) / 2 + 26, y0 - 62), 14, fill=(255, 210, 0, 255))
            d.text(((W - w) / 2, y0 - 120), et, font=fe, fill="black")
        f, ls = fit(d, f"«{t['cita']}»", OBL, mw, 80 if t.get("video") else 92, 3)
        y = centrar(d, ls, f, y0, fill="white", stroke_width=5, stroke_fill="black")
        fc, lc = fit(d, t["contexto"], REG, mw, 40, 3)
        centrar(d, lc, fc, y + 40, fill=(200, 200, 200))
    else:
        y = 520 if t.get("sello") else (700 if t["anio"] else 760)
        if t["anio"]:
            f = ImageFont.truetype(BOLD, 64)
            w = d.textlength(t["anio"], font=f)
            d.rounded_rectangle(((W - w) / 2 - 30, y - 15, (W + w) / 2 + 30, y + 85), 18, fill=(220, 20, 40, 255))
            d.text(((W - w) / 2, y), t["anio"], font=f, fill="white")
            y += 140
        f, ls = fit(d, t["tit"], BOLD, mw, 96, 2 if t.get("sello") else 4)
        y = centrar(d, ls, f, y, fill="white", stroke_width=6, stroke_fill="black")
        if t["sub"]:
            fs, ls = fit(d, t["sub"], REG, mw, 54)
            y = centrar(d, ls, fs, y + 25, fill=(255, 225, 120), stroke_width=4, stroke_fill="black")
        if t.get("sello"):
            fb = ImageFont.truetype(BOLD, 210)
            w = d.textlength(t["sello"], font=fb)
            y += 50
            d.rounded_rectangle(((W - w) / 2 - 50, y, (W + w) / 2 + 50, y + 270), 30, fill=(220, 20, 40, 255))
            d.text(((W - w) / 2, y + 15), t["sello"], font=fb, fill="white")
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
    tarjetas, durs, fvoz, fvid = [], [], [], []
    for i, t in enumerate(TARJETAS):
        t = dict(t, n=i)
        v = vid = None
        if t["tipo"] == "voz":
            v = buscar("voces", t["voz"], ("mp3", "m4a", "wav", "aac", "ogg") + VIDEO)
            if not v:
                print(f"aviso: falta voces/{t['voz']}.mp4 — tarjeta sin voz")
            elif v.rsplit(".", 1)[1].lower() in VIDEO:
                vid = v
        elif t["tipo"] == "reac":
            vid = buscar("reacciones", t["clip"], VIDEO)
            if not vid and not buscar("reacciones", t["clip"], IMG):
                print(f"(se salta la reacción reacciones/{t['clip']}: no existe)")
                continue
        if not vid:
            vid = buscar("imagenes", t.get("img") or f"{i:02d}", VIDEO)
        t["video"] = vid
        tarjetas.append(t); fvoz.append(v); fvid.append(vid)
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
    for i, t in enumerate(tarjetas):
        dur = durs[i]
        if fvoz[i]:
            voces.append((fvoz[i], t0 + 0.2, t0, t0 + dur))
        bg, tx = os.path.join(tmp, f"bg{i:02d}.png"), os.path.join(tmp, f"tx{i:02d}.png")
        clip = os.path.join(tmp, f"c{i:02d}.mp4")
        texto_png(t, tx)
        n = round(dur * FPS)
        if fvid[i]:  # vídeo de fondo: recorte a vertical y, si es dato, oscurecido
            osc = "" if t["tipo"] in ("voz", "reac") else ",eq=brightness=-0.25"
            clave = t.get("voz") or t.get("clip") or t.get("img") or f"{i:02d}"
            vf = (f"[0:v]fps={FPS},{recorte(fvid[i], clave, t["tipo"] == "dato")}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
                  f"{osc},tpad=stop_mode=clone:stop_duration=30[b];"
                  f"[1:v]fade=t=in:st=0:d=0.15:alpha=1[t];[b][t]overlay=0:0,format=yuv420p")
            entrada = ["-i", fvid[i]]
        else:
            img = buscar("reacciones", t["clip"], IMG) if t["tipo"] == "reac" else None
            fondo(t["n"], t, img).save(bg)
            vf = (f"[0:v]scale={int(W*1.1)}:{int(H*1.1)},zoompan=z='1+0.08*on/{n}':d={n}"
                  f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}[b];"
                  f"[1:v]fade=t=in:st=0:d=0.15:alpha=1[t];[b][t]overlay=0:0,format=yuv420p")
            entrada = ["-loop", "1", "-i", bg]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *entrada, "-loop", "1", "-i", tx,
                        "-filter_complex", vf, "-frames:v", str(n), "-an", "-c:v", "libx264", "-crf", "18", clip],
                       check=True)
        clips.append(clip)
        t0 += n / FPS
    total = t0
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w", encoding="utf-8") as fh:
        fh.writelines(f"file '{c.replace(os.sep, '/')}'\n" for c in clips)

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
        filtros.append(f"[{base+k}:a]aresample=44100,volume=1.6,alimiter=limit=0.8:level=false,adelay={ms}|{ms}[v{k}]")
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
