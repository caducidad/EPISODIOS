"""Vídeo ligero: un rótulo por escena (título, dato, fecha, persona, cita, lista, mapa, línea de tiempo...)
sobre el fondo propio de cada serie, con cabecera y barra de progreso.

Uso:
    python3 video_ligero.py escenas.json carpeta_imagenes --serie sc --titulo "Título del episodio" [--hoja hoja.jpg] [ids...]

escenas.json es el que deja narrar.py (id, tipo, params, dur). Tipos y parámetros:
    titulo    {"t": título, "s": subtítulo}
    capitulo  {"n": "Primera parte", "t": título de la parte}
    rotulo    {"t": frase grande, "s": línea pequeña opcional}
    dato      {"v": "40.000", "t": qué es, "s": nota opcional}
    fecha     {"a": "1610", "t": qué pasó, "s": lugar u otra nota opcional}
    persona   {"n": nombre, "r": quién era, "a": "1564 – 1635"}
    cita      {"q": cita breve, "a": autor y obra}
    lista     {"t": encabezado, "items": [hasta 6 elementos]}
    comparar  {"izq": [título, elementos...], "der": [título, elementos...]}
    tiempo    {"t": título, "marcas": [["585 a. C.", "Eclipse"], ...]}   (de 3 a 7 marcas, sin escala)
    mapa      {"titulo": ..., "region": [lon0, lon1, lat0, lat1], "puntos": [{"n": "Mileto", "lat": 37.5, "lon": 27.3, "p": true, "pos": "der"}], "nota": opcional}
    fin       {"t": "Próximamente", "items": [...]}
"""
import argparse, asyncio, base64, hashlib, html, json, math, os, random, subprocess, sys

W, H = 1280, 720
AQUI = os.path.dirname(os.path.abspath(__file__))
DIR_FUENTES = os.path.join(AQUI, "_fuentes")
FUENTES = os.path.join(DIR_FUENTES, "node_modules", "@fontsource")

TEMAS = {
    "sc": dict(nombre="Sistemas complejos", fondo="red", c1="#12282c", c2="#040a0b", tinta="#eef4f3", suave="#a3bbb8",
               acento="#f2b134", linea="#45c2b3", panel="rgba(4,12,13,.62)", tierra="#2d4542", mar="#0b1c1f", costa="#86d1c6", oscuro=True),
    "sh": dict(nombre="Los Sherlock de la historia", fondo="papel", c1="#f3e9d3", c2="#dcc8a1", tinta="#2a2017", suave="#6b5843",
               acento="#8c2f1b", linea="#8a6f4d", panel="rgba(243,233,211,.72)", tierra="#d9c49a", mar="#b7c6c1", costa="#6f5a40", oscuro=False),
    "ia": dict(nombre="Inteligencia artificial: lo que emerge", fondo="neuronas", c1="#161137", c2="#05040f", tinta="#efedff", suave="#aaa6d0",
               acento="#7fe3f5", linea="#9b7bff", panel="rgba(5,4,15,.62)", tierra="#2a2652", mar="#0b0a1f", costa="#9b7bff", oscuro=True),
    "an": dict(nombre="La mente contra sí misma", fondo="calma", c1="#26304f", c2="#4a4372", tinta="#f6f3fb", suave="#d0cae4",
               acento="#f7b6a8", linea="#ddd5f5", panel="rgba(22,24,48,.45)", tierra="#5a5488", mar="#2a3152", costa="#ddd5f5", oscuro=True),
    "fi": dict(nombre="Historia de la filosofía", fondo="cielo", c1="#16204a", c2="#05070f", tinta="#f3ead8", suave="#aab2c8",
               acento="#e7c27d", linea="#ffffff", panel="rgba(5,7,15,.55)", tierra="#5c4e3c", mar="#0e1e3e", costa="#d6be8c", oscuro=True),
}

# ---------------------------------------------------------------- fuentes
def asegurar_fuentes():
    if not os.path.isdir(os.path.join(FUENTES, "inter")):
        os.makedirs(DIR_FUENTES, exist_ok=True)
        subprocess.run(["npm", "install", "--silent", "--prefix", DIR_FUENTES, "@fontsource/cormorant-garamond", "@fontsource/inter"], check=True)

def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()

def css_fuentes():
    out = ""
    for fam, fichero, peso, estilo in [
        ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-500-normal.woff2", 500, "normal"),
        ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-600-normal.woff2", 600, "normal"),
        ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-700-normal.woff2", 700, "normal"),
        ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-500-italic.woff2", 500, "italic"),
        ("Inter", "inter/files/inter-latin-400-normal.woff2", 400, "normal"),
        ("Inter", "inter/files/inter-latin-500-normal.woff2", 500, "normal"),
        ("Inter", "inter/files/inter-latin-600-normal.woff2", 600, "normal")]:
        out += f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b64(os.path.join(FUENTES, fichero))}) format('woff2');font-weight:{peso};font-style:{estilo}}}\n"
    return out

# ---------------------------------------------------------------- fondos
def semilla(texto):
    return int(hashlib.md5(texto.encode()).hexdigest()[:8], 16)

def oscurecer_centro(T):
    if not T["oscuro"]:
        return ("<defs><radialGradient id='vig' cx='50%' cy='50%' r='75%'><stop offset='.55' stop-color='#000' stop-opacity='0'/>"
                "<stop offset='1' stop-color='#5a3c1e' stop-opacity='.28'/></radialGradient></defs><rect width='100%' height='100%' fill='url(#vig)'/>")
    return (f"<defs><radialGradient id='cen' cx='50%' cy='52%' r='55%'><stop offset='0' stop-color='{T['c2']}' stop-opacity='.78'/>"
            f"<stop offset='1' stop-color='{T['c2']}' stop-opacity='0'/></radialGradient></defs><rect width='100%' height='100%' fill='url(#cen)'/>")

def fondo_red(T, r):
    pts = [(r.uniform(-20, W + 20), r.uniform(-20, H + 20)) for _ in range(70)]
    s = ""
    for i, (x, y) in enumerate(pts):
        cerca = sorted(range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:4]
        for j in cerca:
            if j > i:
                s += f"<line x1='{x:.0f}' y1='{y:.0f}' x2='{pts[j][0]:.0f}' y2='{pts[j][1]:.0f}' stroke='{T['linea']}' stroke-width='1.2' opacity='.22'/>"
    for k, (x, y) in enumerate(pts):
        c = T["acento"] if k % 11 == 0 else T["linea"]
        s += f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{r.choice([2.5, 3.5, 4.5])}' fill='{c}' opacity='{.75 if c == T['acento'] else .45}'/>"
    return s

def fondo_papel(T, r):
    s = "".join(f"<line x1='{x}' y1='0' x2='{x}' y2='{H}' stroke='{T['linea']}' stroke-width='1' opacity='.09'/>" for x in range(0, W, 80))
    s += "".join(f"<line x1='0' y1='{y}' x2='{W}' y2='{y}' stroke='{T['linea']}' stroke-width='1' opacity='.09'/>" for y in range(0, H, 80))
    s += "".join(f"<circle cx='{r.uniform(0, W):.0f}' cy='{r.uniform(0, H):.0f}' r='{r.uniform(.6, 1.8):.1f}' fill='#6b4e2e' opacity='{r.uniform(.05, .16):.2f}'/>" for _ in range(500))
    x0, y0 = r.uniform(80, 400), r.uniform(450, 650); x3, y3 = r.uniform(900, 1200), r.uniform(80, 300)
    s += (f"<path d='M{x0:.0f},{y0:.0f} C{r.uniform(300, 600):.0f},{r.uniform(100, 400):.0f} {r.uniform(600, 900):.0f},{r.uniform(300, 650):.0f} {x3:.0f},{y3:.0f}'"
          f" stroke='{T['acento']}' stroke-width='3' fill='none' stroke-dasharray='2 12' stroke-linecap='round' opacity='.35'/>")
    cx, cy = (1140, 590) if r.random() < .5 else (1140, 150)
    s += f"<g opacity='.22' stroke='{T['linea']}' fill='none' stroke-width='2'><circle cx='{cx}' cy='{cy}' r='70'/><circle cx='{cx}' cy='{cy}' r='52'/>"
    for k in range(8):
        a = k * math.pi / 4; L = 90 if k % 2 == 0 else 55
        s += f"<line x1='{cx}' y1='{cy}' x2='{cx + L * math.cos(a):.0f}' y2='{cy + L * math.sin(a):.0f}'/>"
    s += "</g>"
    return s

def fondo_neuronas(T, r):
    cols = 7; xs = [80 + i * (W - 160) / (cols - 1) for i in range(cols)]
    capas = [[(x + r.uniform(-12, 12), y) for y in sorted(r.uniform(60, H - 60) for _ in range(r.randint(4, 7)))] for x in xs]
    s = ""
    for a, b in zip(capas, capas[1:]):
        for (x1, y1) in a:
            for (x2, y2) in b:
                if r.random() < .55:
                    s += f"<line x1='{x1:.0f}' y1='{y1:.0f}' x2='{x2:.0f}' y2='{y2:.0f}' stroke='{T['linea']}' stroke-width='1' opacity='{r.uniform(.06, .22):.2f}'/>"
    for capa in capas:
        for (x, y) in capa:
            c = T["acento"] if r.random() < .18 else T["linea"]
            s += f"<circle cx='{x:.0f}' cy='{y:.0f}' r='14' fill='{c}' opacity='.10'/><circle cx='{x:.0f}' cy='{y:.0f}' r='5' fill='{c}' opacity='.6'/>"
    return s

def fondo_calma(T, r):
    s = ""
    for _ in range(3):
        s += (f"<circle cx='{r.uniform(0, W):.0f}' cy='{r.uniform(0, H):.0f}' r='{r.uniform(160, 300):.0f}' fill='{T['acento']}' opacity='.07'/>")
    for k in range(7):
        amp = r.uniform(18, 46); fase = r.uniform(0, 6.28); y0 = 120 + k * 80 + r.uniform(-20, 20); per = r.uniform(380, 640)
        pts = " ".join(f"{x},{y0 + amp * math.sin(2 * math.pi * x / per + fase):.1f}" for x in range(0, W + 21, 20))
        s += f"<polyline points='{pts}' fill='none' stroke='{T['linea']}' stroke-width='2' opacity='{r.uniform(.10, .22):.2f}'/>"
    return s

def fondo_cielo(T, r):
    s = f"<ellipse cx='{r.uniform(400, 900):.0f}' cy='{r.uniform(200, 400):.0f}' rx='760' ry='120' fill='#c9d4ff' opacity='.05' transform='rotate({r.uniform(-25, -5):.0f} 640 300)'/>"
    for _ in range(280):
        s += (f"<circle cx='{r.uniform(0, W):.0f}' cy='{r.uniform(0, H):.0f}' r='{r.choice([.6, .8, 1.0, 1.2, 1.6, 2.1])}'"
              f" fill='#fff' opacity='{r.uniform(.3, 1):.2f}'/>")
    return s

FONDOS = {"red": fondo_red, "papel": fondo_papel, "neuronas": fondo_neuronas, "calma": fondo_calma, "cielo": fondo_cielo}

def fondo(T, sid):
    r = random.Random(semilla(sid))
    grad = (f"<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='{T['c1']}'/>"
            f"<stop offset='1' stop-color='{T['c2']}'/></linearGradient></defs><rect width='{W}' height='{H}' fill='url(#g)'/>")
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>{grad}{FONDOS[T['fondo']](T, r)}{oscurecer_centro(T)}</svg>"

# ---------------------------------------------------------------- mapa
def mapa_png(region, T):
    lon0, lon1, lat0, lat1 = region
    clave = hashlib.md5(json.dumps([region, T["tierra"], T["mar"], T["costa"]]).encode()).hexdigest()[:10]
    ruta = f"/tmp/mapa_{clave}.png"
    if os.path.exists(ruta):
        return ruta
    try:
        from global_land_mask import globe
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "global-land-mask"], check=True)
        from global_land_mask import globe
    import numpy as np
    from PIL import Image
    LO, LA = np.meshgrid(np.linspace(lon0, lon1, W), np.linspace(lat1, lat0, H))
    tierra = globe.is_land(LA, LO)
    hexrgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    img = np.zeros((H, W, 3), np.uint8); img[:] = hexrgb(T["mar"]); img[tierra] = hexrgb(T["tierra"])
    borde = np.zeros_like(tierra)
    borde[1:-1, 1:-1] = tierra[1:-1, 1:-1] & ~(tierra[:-2, 1:-1] & tierra[2:, 1:-1] & tierra[1:-1, :-2] & tierra[1:-1, 2:])
    img[borde] = hexrgb(T["costa"])
    Image.fromarray(img).save(ruta)
    return ruta

# ---------------------------------------------------------------- plantillas
def e(t):
    return html.escape(str(t))

def tam(texto, base, minimo, umbral):
    n = len(str(texto))
    return base if n <= umbral else max(minimo, int(base * (umbral / n) ** 0.5))

def css(T):
    return f"""{FUENTES_CSS}
*{{margin:0;padding:0;box-sizing:border-box;font-variant-numeric:lining-nums;text-wrap:balance}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{T['c2']};color:{T['tinta']};font-family:Inter,sans-serif}}
.bg{{position:absolute;inset:0}}
.cab{{position:absolute;left:60px;top:40px;right:60px}}
.cab .s{{font-size:22px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:{T['acento']}}}
.cab .e{{font-size:22px;color:{T['suave']};margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.prog{{position:absolute;left:60px;right:60px;bottom:26px;height:5px;border-radius:3px;background:{T['suave']};opacity:.35}}
.progf{{position:absolute;left:60px;bottom:26px;height:5px;border-radius:3px;background:{T['acento']}}}
.zona{{position:absolute;left:60px;right:60px;top:110px;bottom:60px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
.corm{{font-family:Corm;font-weight:600;line-height:1.08}}
.sub{{font-size:32px;color:{T['acento']};margin-top:24px;line-height:1.3;max-width:1060px}}
.nota{{font-size:26px;color:{T['suave']};margin-top:18px;max-width:1000px;line-height:1.35}}
.raya{{width:110px;height:3px;background:{T['acento']};margin:26px auto 0;opacity:.85}}
.etq{{font-size:26px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:{T['acento']};margin-bottom:18px}}
.panel{{background:{T['panel']};border-radius:22px;padding:34px 46px}}
.q{{font-family:Corm;font-style:italic;font-weight:500;line-height:1.16;max-width:1060px}}
.qm{{font-family:Corm;font-size:170px;color:{T['acento']};line-height:.55;height:64px}}
ol.l{{list-style:none;text-align:left;min-width:760px;max-width:1080px}}
ol.l li{{font-size:36px;padding:12px 0;border-bottom:1px solid {T['suave']}55;display:flex;gap:24px;line-height:1.25}}
ol.l li span{{font-family:Corm;font-weight:700;color:{T['acento']};font-size:40px;min-width:36px}}
.cols{{display:flex;gap:44px;width:100%}}
.col{{flex:1;background:{T['panel']};border-radius:20px;padding:30px 34px;text-align:left;border-top:5px solid {T['acento']}}}
.col h2{{font-family:Corm;font-size:60px;font-weight:700;color:{T['acento']};margin-bottom:12px}}
.col p{{font-size:32px;line-height:1.5}}
"""

def plantilla(sc, T, titulo_ep):
    t, p = sc["tipo"], sc.get("params", {})
    if t == "titulo":
        return (f"<div class='zona' style='top:60px'><div class='etq'>{e(T['nombre'])}</div>"
                f"<div class='corm' style='font-size:{tam(p['t'], 96, 60, 28)}px;max-width:1120px'>{e(p['t'])}</div><div class='raya'></div>"
                + (f"<div class='sub'>{e(p['s'])}</div>" if p.get("s") else "") + "</div>")
    if t == "capitulo":
        return (f"<div class='zona'>" + (f"<div class='etq'>{e(p['n'])}</div>" if p.get("n") else "")
                + f"<div class='corm' style='font-size:{tam(p['t'], 84, 54, 30)}px;max-width:1100px'>{e(p['t'])}</div><div class='raya'></div></div>")
    if t == "rotulo":
        return (f"<div class='zona'><div class='corm' style='font-size:{tam(p['t'], 76, 50, 40)}px;max-width:1100px'>{e(p['t'])}</div><div class='raya'></div>"
                + (f"<div class='sub'>{e(p['s'])}</div>" if p.get("s") else "") + "</div>")
    if t == "dato":
        return (f"<div class='zona'><div class='corm' style='font-weight:700;font-size:{tam(p['v'], 170, 90, 7)}px;color:{T['acento']}'>{e(p['v'])}</div>"
                f"<div style='font-size:{tam(p['t'], 40, 30, 50)}px;font-weight:500;margin-top:10px;max-width:1060px;line-height:1.3'>{e(p['t'])}</div>"
                + (f"<div class='nota'>{e(p['s'])}</div>" if p.get("s") else "") + "</div>")
    if t == "fecha":
        return (f"<div class='zona'><div class='corm' style='font-weight:700;font-size:{tam(p['a'], 150, 84, 9)}px;color:{T['acento']}'>{e(p['a'])}</div>"
                f"<div style='font-size:{tam(p['t'], 40, 30, 50)}px;font-weight:500;margin-top:12px;max-width:1060px;line-height:1.3'>{e(p['t'])}</div>"
                + (f"<div class='nota'>{e(p['s'])}</div>" if p.get("s") else "") + "</div>")
    if t == "persona":
        return (f"<div class='zona'><div class='corm' style='font-size:{tam(p['n'], 88, 56, 22)}px'>{e(p['n'])}</div><div class='raya'></div>"
                f"<div style='font-size:34px;margin-top:22px;max-width:1040px;line-height:1.3'>{e(p.get('r', ''))}</div>"
                + (f"<div class='sub' style='margin-top:14px'>{e(p['a'])}</div>" if p.get("a") else "") + "</div>")
    if t == "cita":
        return (f"<div class='zona'><div class='qm'>“</div><div class='q' style='font-size:{tam(p['q'], 62, 42, 70)}px'>{e(p['q'])}</div>"
                f"<div class='nota' style='margin-top:26px'>{e(p.get('a', ''))}</div></div>")
    if t in ("lista", "fin"):
        lis = "".join(f"<li><span>{i + 1}</span>{e(x)}</li>" for i, x in enumerate(p.get("items", [])[:6]))
        return (f"<div class='zona'><div class='corm' style='font-size:56px;font-weight:700;margin-bottom:26px'>{e(p.get('t', ''))}</div>"
                f"<div class='panel'><ol class='l'>{lis}</ol></div></div>")
    if t == "comparar":
        col = lambda a: f"<div class='col'><h2>{e(a[0])}</h2>" + "".join(f"<p>· {e(x)}</p>" for x in a[1:]) + "</div>"
        return f"<div class='zona'><div class='cols'>{col(p['izq'])}{col(p['der'])}</div></div>"
    if t == "tiempo":
        marcas = p["marcas"]; n = len(marcas); x0, x1 = 140, 1140; yl = 400
        s = f"<line x1='{x0}' y1='{yl}' x2='{x1}' y2='{yl}' stroke='{T['acento']}' stroke-width='3'/>"
        for i, (f, l) in enumerate(marcas):
            x = x0 + i * (x1 - x0) / max(1, n - 1); arriba = i % 2 == 0
            s += f"<circle cx='{x:.0f}' cy='{yl}' r='9' fill='{T['acento']}'/>"
            ty = yl - 66 if arriba else yl + 60
            s += f"<text x='{x:.0f}' y='{ty}' text-anchor='middle' font-family='Corm' font-weight='700' font-size='38' fill='{T['tinta']}'>{e(f)}</text>"
            pal = str(l).split(" "); mitad = (len(pal) + 1) // 2
            for j, linea in enumerate([" ".join(pal[:mitad]), " ".join(pal[mitad:])]):
                yy = (ty + 30 + j * 28) if arriba else (ty + 34 + j * 28)
                if arriba:
                    yy = ty - 74 + j * 28
                s += f"<text x='{x:.0f}' y='{yy}' text-anchor='middle' font-family='Inter' font-size='24' fill='{T['suave']}'>{e(linea)}</text>"
        s += f"<text x='640' y='150' text-anchor='middle' font-family='Corm' font-weight='700' font-size='54' fill='{T['tinta']}'>{e(p.get('t', ''))}</text>"
        return f"<div class='bg'><svg viewBox='0 0 {W} {H}' width='{W}' height='{H}'>{s}</svg></div>"
    if t == "mapa":
        lon0, lon1, lat0, lat1 = p["region"]
        s = f"<image href='data:image/png;base64,{b64(mapa_png(p['region'], T))}' x='0' y='0' width='{W}' height='{H}'/>"
        borde = "#05070f" if T["oscuro"] else "#f3e9d3"
        for pt in p["puntos"]:
            x = (pt["lon"] - lon0) / (lon1 - lon0) * W; y = (lat1 - pt["lat"]) / (lat1 - lat0) * H
            prin = pt.get("p", False); pos = pt.get("pos", "izq" if x > W - 300 else "der")
            dx, dy, anc = {"der": (16, 10, "start"), "izq": (-16, 10, "end"), "arriba": (0, -20, "middle"), "abajo": (0, 40, "middle")}[pos]
            col = T["acento"] if prin else T["tinta"]
            s += f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{12 if prin else 7}' fill='{col}' stroke='{borde}' stroke-width='2'/>"
            s += (f"<text x='{x + dx:.0f}' y='{y + dy:.0f}' text-anchor='{anc}' font-family='Inter' font-weight='600' font-size='{40 if prin else 30}'"
                  f" fill='{col}' stroke='{borde}' stroke-width='6' paint-order='stroke'>{e(pt['n'])}</text>")
        s += (f"<text x='60' y='{H - 80}' font-family='Corm' font-weight='700' font-size='54' fill='{T['tinta']}' stroke='{borde}' stroke-width='6'"
              f" paint-order='stroke'>{e(p.get('titulo', ''))}</text>")
        if p.get("nota"):
            s += f"<text x='60' y='{H - 46}' font-family='Inter' font-size='24' fill='{T['suave']}' stroke='{borde}' stroke-width='4' paint-order='stroke'>{e(p['nota'])}</text>"
        return f"<div class='bg'><svg viewBox='0 0 {W} {H}' width='{W}' height='{H}'>{s}</svg></div>"
    raise ValueError(f"Tipo de escena desconocido: {t}")

def pagina(sc, T, titulo_ep, frac):
    con_fondo = sc["tipo"] != "mapa"
    cab = "" if sc["tipo"] in ("titulo", "mapa") else f"<div class='cab'><div class='s'>{e(T['nombre'])}</div><div class='e'>{e(titulo_ep)}</div></div>"
    prog = f"<div class='prog'></div><div class='progf' style='width:{max(4, frac * (W - 120)):.0f}px'></div>"
    bg = f"<div class='bg'>{fondo(T, sc['id'])}</div>" if con_fondo else ""
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{css(T)}</style></head><body>{bg}{plantilla(sc, T, titulo_ep)}{cab}{prog}</body></html>"

async def dibujar(escenas, T, titulo_ep, salida, solo):
    from playwright.async_api import async_playwright
    total = sum(s.get("dur", 1) for s in escenas); acum = 0.0; hechos = []
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": W, "height": H})
        for sc in escenas:
            frac = acum / total; acum += sc.get("dur", 1)
            if solo and sc["id"] not in solo:
                continue
            await pg.set_content(pagina(sc, T, titulo_ep, frac)); await pg.wait_for_timeout(120)
            ruta = os.path.join(salida, sc["id"] + ".jpg")
            await pg.screenshot(path=ruta, type="jpeg", quality=92); hechos.append(ruta)
        await b.close()
    return hechos

def hoja(rutas, destino, columnas=4):
    from PIL import Image
    ims = [Image.open(r).resize((320, 180)) for r in rutas]
    filas = (len(ims) + columnas - 1) // columnas
    h = Image.new("RGB", (columnas * 320, filas * 180), "black")
    for i, im in enumerate(ims):
        h.paste(im, ((i % columnas) * 320, (i // columnas) * 180))
    h.save(destino, quality=88)

def main():
    global FUENTES_CSS
    ap = argparse.ArgumentParser()
    ap.add_argument("escenas"); ap.add_argument("salida"); ap.add_argument("ids", nargs="*")
    ap.add_argument("--serie", required=True, choices=sorted(TEMAS)); ap.add_argument("--titulo", default="")
    ap.add_argument("--hoja")
    a = ap.parse_args()
    asegurar_fuentes(); FUENTES_CSS = css_fuentes()
    escenas = json.load(open(a.escenas, encoding="utf-8")); os.makedirs(a.salida, exist_ok=True)
    rutas = asyncio.run(dibujar(escenas, TEMAS[a.serie], a.titulo, a.salida, set(a.ids)))
    if a.hoja:
        hoja(rutas, a.hoja)
    print(f"{len(rutas)} imágenes en {a.salida}")

FUENTES_CSS = ""
if __name__ == "__main__":
    main()
