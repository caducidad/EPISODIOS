"""Vídeo ilustrado: como video_ligero.py (mismos fondos, cabecera, barra de progreso y tipos de escena),
más el tipo "ilus", una ilustración dibujada a propósito en SVG con un pie de texto.

Uso:
    python3 video_ilustrado.py escenas.json carpeta_imagenes --serie ia --titulo "Título" [--hoja hoja.jpg] [ids...]

Tipo nuevo:
    ilus  {"fig": nombre de la figura en FIGURAS, "pie": texto bajo la ilustración}

Las figuras se dibujan en un lienzo de 1160x440 (se coloca entre la cabecera y el pie). Cada función recibe el
tema T (colores de la serie) y devuelve el contenido SVG. Para un episodio nuevo, añade sus figuras a FIGURAS.
Figuras actuales: episodio ia01 (Qué es una red neuronal, desde cero).
"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_ligero as VL

FW, FH = 1160, 440
CORAL = "#ff8a7a"

def tx(x, y, t, T, size=28, col=None, anc="middle", peso=500, fam="Inter", extra=""):
    col = col or T["tinta"]
    return (f"<text x='{x}' y='{y}' text-anchor='{anc}' font-family='{fam}' font-weight='{peso}' font-size='{size}' "
            f"fill='{col}' {extra}>{VL.e(t)}</text>")

def nodo(x, y, r, T, fill=None, stroke=None, sw=3):
    return f"<circle cx='{x}' cy='{y}' r='{r}' fill='{fill or T['c2']}' stroke='{stroke or T['acento']}' stroke-width='{sw}'/>"

def linea(x1, y1, x2, y2, col, w=3, op=1, dash=None):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{col}' stroke-width='{w}' opacity='{op}'{d} stroke-linecap='round'/>"

def flecha(x1, y1, x2, y2, col, w=4, op=1):
    ang = math.atan2(y2 - y1, x2 - x1); L = 16
    a1 = (x2 - L * math.cos(ang - .45), y2 - L * math.sin(ang - .45)); a2 = (x2 - L * math.cos(ang + .45), y2 - L * math.sin(ang + .45))
    return (linea(x1, y1, x2, y2, col, w, op) +
            f"<polygon points='{x2:.1f},{y2:.1f} {a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f}' fill='{col}' opacity='{op}'/>")

def red(capas, x0, x1, y0, y1, T, r=16, col=None, op=.45, w=2):
    """Devuelve (svg, posiciones) de una red totalmente conectada."""
    pos = []
    for i, n in enumerate(capas):
        x = x0 + i * (x1 - x0) / (len(capas) - 1)
        pos.append([(x, y0 + (j + .5) * (y1 - y0) / n) for j in range(n)])
    s = ""
    for a, b in zip(pos, pos[1:]):
        for p in a:
            for q in b:
                s += linea(p[0], p[1], q[0], q[1], col or T["linea"], w, op)
    for capa in pos:
        for (x, y) in capa:
            s += nodo(x, y, r, T)
    return s, pos

# ---------------------------------------------------------------- figuras del episodio ia01
def f_movil(T):
    s = f"<rect x='500' y='40' width='160' height='300' rx='26' fill='{T['c2']}' stroke='{T['tinta']}' stroke-width='4'/>"
    s += f"<rect x='514' y='70' width='132' height='240' rx='8' fill='{T['c1']}'/>"
    sr, pos = red([3, 4, 2], 535, 625, 100, 290, T, r=9, op=.6)
    s += sr
    items = [(170, 90, "Desbloqueo con la cara"), (990, 90, "Traducción"), (170, 300, "Filtro de correo basura"), (990, 300, "Fotos agrupadas")]
    for x, y, t in items:
        s += linea(580 + (x - 580) * .18, 190 + (y - 190) * .18, x + (150 if x < 580 else -150), y, T["linea"], 2, .7, "6 8")
        s += f"<rect x='{x - 160}' y='{y - 36}' width='320' height='64' rx='14' fill='{T['panel']}' stroke='{T['acento']}' stroke-width='2'/>"
        s += tx(x, y + 9, t, T, 26)
    s += tx(580, 400, "Una red neuronal dentro de cada gesto cotidiano", T, 26, T["suave"])
    return s

def f_neurona_bio(T):
    r = random.Random(3); s = ""
    cx, cy = 360, 220
    def rama(x, y, ang, largo, nivel):
        nonlocal s
        x2, y2 = x + largo * math.cos(ang), y + largo * math.sin(ang)
        s += linea(x, y, x2, y2, T["acento"], max(1.5, 6 - nivel * 1.4), .9)
        if nivel < 3:
            for d in (-.45, .4):
                rama(x2, y2, ang + d + r.uniform(-.15, .15), largo * .68, nivel + 1)
    for ang in (2.3, 2.8, 3.3, 3.8, 4.2, 1.9, 4.6):
        rama(cx, cy, ang, 70, 0)
    s += f"<path d='M{cx} {cy - 34} C {cx + 50} {cy - 40}, {cx + 70} {cy - 8}, {cx + 70} {cy} C {cx + 70} {cy + 8}, {cx + 50} {cy + 40}, {cx} {cy + 34} C {cx - 45} {cy + 30}, {cx - 45} {cy - 30}, {cx} {cy - 34} Z' fill='{T['linea']}' opacity='.9'/>"
    s += f"<circle cx='{cx + 8}' cy='{cy}' r='13' fill='{T['c2']}'/>"
    s += linea(cx + 70, cy, 900, cy, T["acento"], 6)
    for k in range(6):
        x = 455 + k * 74
        s += f"<rect x='{x}' y='{cy - 13}' width='62' height='26' rx='13' fill='{T['linea']}' opacity='.85'/>"
    for d in (-.6, -.2, .2, .6):
        x2, y2 = 900 + 70 * math.cos(d), cy + 70 * math.sin(d)
        s += linea(900, cy, x2, y2, T["acento"], 4) + f"<circle cx='{x2:.0f}' cy='{y2:.0f}' r='8' fill='{T['acento']}'/>"
    s += f"<path d='M1030 120 C 990 180, 990 260, 1030 320' fill='none' stroke='{T['suave']}' stroke-width='5' opacity='.7'/>"
    s += tx(0, 20, "Dendritas", T, 30, T["acento"], anc="start", peso=600)
    s += tx(0, 52, "recogen señales", T, 24, T["suave"], anc="start")
    s += tx(cx + 75, cy + 100, "Cuerpo", T, 30, T["acento"], anc="start", peso=600)
    s += tx(cx + 75, cy + 132, "suma y decide", T, 24, T["suave"], anc="start")
    s += tx(640, cy - 50, "Axón", T, 30, T["acento"], peso=600)
    s += tx(720, cy + 66, "transmite el impulso", T, 24, T["suave"])
    s += tx(1010, 380, "Sinapsis", T, 30, T["acento"], peso=600)
    s += tx(1010, 412, "contacto con otra neurona", T, 24, T["suave"])
    s += flecha(620, 330, 820, 330, T["tinta"], 3, .6)
    return s

def f_disparo(T):
    s = ""
    entradas = [("+", 60), ("+", 140), ("−", 220), ("+", 300), ("−", 380)]
    for sg, y in entradas:
        col = T["acento"] if sg == "+" else CORAL
        s += flecha(130, y, 395, 220 + (y - 220) * .25, col, 4, .9)
        s += nodo(105, y, 24, T, stroke=col) + tx(105, y + 11, sg, T, 34, col, peso=700)
    s += nodo(450, 220, 58, T, fill=T["panel"], sw=4) + tx(450, 236, "Σ", T, 54, T["tinta"], peso=600)
    s += tx(450, 320, "suma", T, 26, T["suave"])
    # medidor
    s += f"<rect x='590' y='60' width='70' height='320' rx='12' fill='none' stroke='{T['suave']}' stroke-width='3'/>"
    s += f"<rect x='596' y='120' width='58' height='254' rx='8' fill='{T['acento']}' opacity='.85'/>"
    s += linea(570, 160, 680, 160, CORAL, 5) + tx(700, 170, "umbral", T, 28, CORAL, anc="start", peso=600)
    s += flecha(512, 220, 580, 220, T["tinta"], 3, .7)
    pts = "720,300 800,300 815,300 830,110 845,330 860,300 1120,300"
    s += f"<polyline points='{pts}' fill='none' stroke='{T['acento']}' stroke-width='5' stroke-linejoin='round'/>"
    s += tx(960, 250, "¡Dispara!", T, 40, T["acento"], peso=700, fam="Corm")
    s += tx(960, 360, "impulso por el axón", T, 26, T["suave"])
    return s

def f_mcp(T):
    s = ""
    vals = [1, 1, 0]
    for i, v in enumerate(vals):
        y = 90 + i * 130
        col = T["acento"] if v else T["suave"]
        s += f"<rect x='130' y='{y - 40}' width='80' height='80' rx='14' fill='{T['panel']}' stroke='{col}' stroke-width='3'/>"
        s += tx(170, y + 18, str(v), T, 52, col, peso=700, fam="Corm")
        s += flecha(215, y, 470, 220 + (y - 220) * .3, col, 4, .9)
    s += tx(170, 435, "Entradas: sí (1) o no (0)", T, 24, T["suave"])
    s += nodo(560, 220, 90, T, fill=T["panel"], sw=4)
    s += tx(560, 205, "Umbral", T, 28, T["suave"]) + tx(560, 262, "2", T, 64, T["acento"], peso=700, fam="Corm")
    s += tx(560, 360, "1 + 1 + 0 = 2", T, 34, T["tinta"], peso=600)
    s += flecha(655, 220, 860, 220, T["acento"], 5)
    s += f"<rect x='880' y='160' width='120' height='120' rx='18' fill='{T['acento']}'/>"
    s += tx(940, 245, "1", T, 80, T["c2"], peso=700, fam="Corm")
    s += tx(940, 330, "Se enciende", T, 30, T["acento"], peso=600)
    return s

def f_perceptron(T):
    s = ""
    ent = [("Sol", "1", "× 2", T["acento"]), ("Tiempo libre", "1", "× 3", T["acento"]), ("Frío", "1", "× (−1)", CORAL)]
    for i, (n, v, w, col) in enumerate(ent):
        y = 80 + i * 140
        s += tx(150, y + 10, n, T, 32, T["tinta"], anc="end", peso=600)
        s += nodo(205, y, 30, T) + tx(205, y + 12, v, T, 34, T["acento"], peso=700, fam="Corm")
        s += flecha(240, y, 500, 220 + (y - 220) * .3, col, 5 if "3" in w else 3.5, .9)
        s += tx(360, y + (220 - y) * .15 - 16, w, T, 30, col, peso=700)
    s += tx(360, 425, "Los pesos: cuánto importa cada dato", T, 24, T["suave"])
    s += nodo(580, 220, 72, T, fill=T["panel"], sw=4) + tx(580, 238, "Σ", T, 58, T["tinta"])
    s += flecha(655, 220, 760, 220, T["tinta"], 4, .8)
    s += f"<rect x='770' y='170' width='150' height='100' rx='16' fill='{T['panel']}' stroke='{T['acento']}' stroke-width='3'/>"
    s += tx(845, 212, "¿más de", T, 26, T["suave"]) + tx(845, 252, "3?", T, 36, T["acento"], peso=700)
    s += flecha(925, 220, 990, 220, T["tinta"], 4, .8)
    s += tx(1080, 210, "Sí:", T, 32, T["acento"], peso=700) + tx(1080, 248, "a caminar", T, 30, T["tinta"])
    return s

def f_suma(T):
    s = ""
    filas = [("Sol", "1 × 2", "= 2", T["acento"]), ("Tiempo libre", "1 × 3", "= 3", T["acento"]), ("Frío", "1 × (−1)", "= −1", CORAL)]
    for i, (n, op, r, col) in enumerate(filas):
        y = 70 + i * 82
        s += tx(390, y, n, T, 38, T["suave"], anc="end")
        s += tx(560, y, op, T, 44, T["tinta"], peso=600, fam="Corm")
        s += tx(760, y, r, T, 48, col, anc="start", peso=700, fam="Corm")
    s += linea(330, 300, 900, 300, T["suave"], 2, .7)
    s += tx(390, 360, "Total", T, 38, T["suave"], anc="end")
    s += tx(760, 365, "4", T, 70, T["acento"], anc="start", peso=700, fam="Corm")
    s += tx(980, 330, "4 > 3", T, 40, T["tinta"], peso=600, fam="Corm") + tx(980, 380, "→ Sí", T, 40, T["acento"], peso=700, fam="Corm")
    return s

def f_mark1(T):
    r = random.Random(5); s = ""
    x0, y0, c = 60, 40, 17
    for i in range(20):
        for j in range(20):
            on = (4 <= i <= 6 and 3 <= j <= 16) or (6 <= i <= 16 and 8 <= j <= 11)
            s += f"<rect x='{x0 + j * c}' y='{y0 + i * c}' width='{c - 3}' height='{c - 3}' rx='2' fill='{T['acento'] if on else T['panel']}' stroke='{T['suave']}' stroke-opacity='.25'/>"
    s += tx(x0 + 170, 400, "400 fotocélulas (20 × 20)", T, 24, T["suave"])
    ys = [50 + k * 26 for k in range(13)]
    for k in range(40):
        s += linea(x0 + 340, y0 + r.uniform(0, 340), 520, r.choice(ys), T["linea"], 1.5, .45)
    for y in ys:
        s += f"<circle cx='530' cy='{y}' r='8' fill='{T['linea']}'/>"
    s += tx(530, 400, "512 unidades", T, 24, T["suave"]) + tx(530, 428, "conectadas al azar", T, 22, T["suave"])
    for k in range(4):
        y = 70 + k * 85
        s += linea(540, ys[k * 3 + 1], 700, y, T["linea"], 2, .5)
        s += nodo(740, y, 30, T, stroke=T["tinta"]) + linea(740, y, 740 + 22 * math.cos(-1 + k), y + 22 * math.sin(-1 + k), T["acento"], 4)
        s += f"<rect x='790' y='{y - 16}' width='50' height='32' rx='6' fill='{T['suave']}' opacity='.6'/>"
        s += linea(770, y, 790, y, T["suave"], 3)
        s += flecha(780, y, 940, 220 + (y - 220) * .5, T["acento"], 3, .8)
    s += tx(790, 400, "Pesos: mandos girados", T, 24, T["suave"]) + tx(790, 428, "por pequeños motores", T, 22, T["suave"])
    s += f"<rect x='950' y='170' width='170' height='100' rx='16' fill='{T['panel']}' stroke='{T['acento']}' stroke-width='3'/>"
    s += tx(1035, 230, "Respuesta", T, 30, T["acento"], peso=600)
    return s

def puntos_clases(T, xs, ys, clase):
    s = ""
    for x, y in zip(xs, ys):
        if clase:
            s += f"<circle cx='{x:.0f}' cy='{y:.0f}' r='12' fill='{T['acento']}'/>"
        else:
            s += linea(x - 10, y - 10, x + 10, y + 10, CORAL, 5) + linea(x - 10, y + 10, x + 10, y - 10, CORAL, 5)
    return s

def ejes(T, x0, y0, x1, y1, nx, ny):
    s = flecha(x0, y1, x1, y1, T["suave"], 3) + flecha(x0, y1, x0, y0, T["suave"], 3)
    s += tx((x0 + x1) / 2, y1 + 40, nx, T, 26, T["suave"])
    s += tx(x0 - 22, (y0 + y1) / 2, ny, T, 26, T["suave"], extra=f"transform='rotate(-90 {x0 - 22} {(y0 + y1) / 2})'")
    return s

def f_recta(T):
    r = random.Random(8); s = ejes(T, 200, 20, 900, 380, "Temperatura", "Humedad")
    a = [(r.uniform(260, 520), r.uniform(200, 360)) for _ in range(9)]
    a = [(x, y) for x, y in a if y > 0.6 * x - 30]
    b = [(r.uniform(560, 860), r.uniform(40, 300)) for _ in range(10)]
    s += linea(330, 20, 760, 380, T["tinta"], 4, .9, "14 10")
    s += puntos_clases(T, [p[0] for p in a], [p[1] for p in a], True)
    s += puntos_clases(T, [p[0] for p in b], [p[1] for p in b], False)
    s += f"<circle cx='980' cy='140' r='12' fill='{T['acento']}'/>" + tx(1005, 150, "Sí", T, 30, anc="start")
    s += linea(970, 210, 990, 230, CORAL, 5) + linea(970, 230, 990, 210, CORAL, 5) + tx(1005, 232, "No", T, 30, anc="start")
    s += linea(965, 300, 1000, 300, T["tinta"], 4, .9, "8 6") + tx(1010, 310, "la recta", T, 28, anc="start")
    return s

def f_xor(T):
    s = ejes(T, 330, 20, 790, 380, "Llave de abajo", "Llave de arriba")
    P = {(0, 0): 0, (1, 1): 0, (0, 1): 1, (1, 0): 1}
    for (a, b), on in P.items():
        x, y = 420 + a * 280, 330 - b * 260
        if on:
            s += f"<circle cx='{x}' cy='{y}' r='30' fill='{T['acento']}'/>" + tx(x, y + 64 if b == 0 else y - 44, "luz", T, 26, T["acento"], peso=600)
        else:
            s += f"<circle cx='{x}' cy='{y}' r='30' fill='none' stroke='{CORAL}' stroke-width='5'/>" + tx(x, y + 64 if b == 0 else y - 44, "apagada", T, 26, CORAL, peso=600)
    s += linea(360, 140, 780, 260, T["suave"], 3, .6, "10 10") + linea(500, 30, 640, 380, T["suave"], 3, .6, "10 10")
    s += tx(1000, 190, "¿Una recta", T, 34, T["tinta"], peso=600, fam="Corm") + tx(1000, 232, "que los separe?", T, 34, T["tinta"], peso=600, fam="Corm")
    s += tx(1000, 290, "Imposible", T, 36, CORAL, peso=700, fam="Corm")
    s += tx(140, 210, "Interruptor", T, 28, T["suave"]) + tx(140, 244, "de escalera", T, 28, T["suave"])
    return s

def f_capas(T):
    s = ""
    E = [(180, 120, "Llave A"), (180, 320, "Llave B")]
    O = [(560, 120, "o"), (560, 320, "y")]
    for (x, y, _) in E:
        for (u, v, _) in O:
            s += flecha(x + 40, y, u - 44, v, T["linea"], 3, .8)
    s += flecha(604, 120, 860, 210, T["acento"], 4)
    s += flecha(604, 320, 860, 232, CORAL, 4)
    s += tx(760, 310, "bloquea", T, 24, CORAL, peso=600)
    for (x, y, n) in E:
        s += nodo(x, y, 40, T) + tx(x - 60, y + 9, n, T, 28, T["tinta"], anc="end", peso=600)
    for (x, y, n) in O:
        s += nodo(x, y, 44, T, fill=T["panel"]) + tx(x, y + 14, n, T, 42, T["acento"], peso=700, fam="Corm")
    s += nodo(900, 220, 44, T, fill=T["panel"])
    s += f"<circle cx='1060' cy='210' r='34' fill='{T['acento']}' opacity='.9'/><rect x='1046' y='244' width='28' height='24' rx='4' fill='{T['suave']}'/>"
    s += flecha(944, 220, 1018, 214, T["acento"], 4)
    s += tx(180, 420, "Entrada", T, 26, T["suave"]) + tx(560, 420, "Capa oculta", T, 26, T["acento"], peso=600) + tx(900, 420, "Salida", T, 26, T["suave"])
    return s

def f_culpa(T):
    sr, pos = red([4, 5, 5, 2], 140, 860, 30, 410, T, r=18, op=.35)
    s = sr
    r = random.Random(4)
    for k in range(6):
        a = r.randrange(3); i = r.randrange(len(pos[a])); j = r.randrange(len(pos[a + 1]))
        (x1, y1), (x2, y2) = pos[a][i], pos[a + 1][j]
        s += linea(x1, y1, x2, y2, CORAL, 4, .9)
        s += tx((x1 + x2) / 2, (y1 + y2) / 2 - 8, "?", T, 40, CORAL, peso=700, extra=f"stroke='{T['c2']}' stroke-width='6' paint-order='stroke'")
    (x, y) = pos[3][0]
    s += f"<rect x='{x + 50}' y='{y - 40}' width='220' height='80' rx='16' fill='{T['panel']}' stroke='{CORAL}' stroke-width='3'/>"
    s += tx(x + 160, y + 12, "¡Error!", T, 38, CORAL, peso=700, fam="Corm")
    s += tx(1020, 330, "¿Quién tiene", T, 32, T["tinta"], fam="Corm", peso=600) + tx(1020, 370, "la culpa?", T, 32, T["tinta"], fam="Corm", peso=600)
    return s

def curva(T, x0, x1, y0, y1, f, col, w=5):
    pts = " ".join(f"{x0 + k * (x1 - x0) / 200:.1f},{y1 - f(-6 + 12 * k / 200) * (y1 - y0):.1f}" for k in range(201))
    return f"<polyline points='{pts}' fill='none' stroke='{col}' stroke-width='{w}' stroke-linejoin='round'/>"

def f_sigmoide(T):
    s = ""
    for k, (titulo, f, col) in enumerate([("Antes: un escalón", lambda z: 1.0 if z > 0 else 0.0, CORAL),
                                            ("Después: una curva suave", lambda z: 1 / (1 + math.exp(-z)), T["acento"])]):
        x0 = 90 + k * 560; x1 = x0 + 440
        s += f"<rect x='{x0 - 30}' y='10' width='500' height='400' rx='20' fill='{T['panel']}'/>"
        s += tx((x0 + x1) / 2, 60, titulo, T, 34, col, peso=700, fam="Corm")
        s += linea(x0, 340, x1, 340, T["suave"], 2, .6) + linea((x0 + x1) / 2, 100, (x0 + x1) / 2, 350, T["suave"], 2, .4)
        s += curva(T, x0, x1, 110, 340, f, col)
        s += tx(x0 - 6, 118, "1", T, 26, T["suave"], anc="end") + tx(x0 - 6, 348, "0", T, 26, T["suave"], anc="end")
        s += tx((x0 + x1) / 2, 385, "suma de la neurona →", T, 24, T["suave"])
    return s

def f_montana(T):
    f = lambda x: 300 - 230 * math.exp(-((x - 260) / 190) ** 2) - 120 * math.exp(-((x - 760) / 160) ** 2) + 0.0 * x
    g = lambda x: 390 - 300 * (1 - math.exp(-((x - 820) / 300) ** 2))
    pts = " ".join(f"{x},{g(x):.1f}" for x in range(40, 1121, 10))
    s = f"<defs><linearGradient id='niebla' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{T['tinta']}' stop-opacity='.10'/><stop offset='1' stop-color='{T['tinta']}' stop-opacity='0'/></linearGradient></defs>"
    s += f"<polygon points='40,430 {pts} 1120,430' fill='{T['linea']}' opacity='.28'/>"
    s += f"<polyline points='{pts}' fill='none' stroke='{T['linea']}' stroke-width='4'/>"
    xs = [200, 320, 430, 520, 600, 670, 730, 780, 815]
    for a, b in zip(xs, xs[1:]):
        s += flecha(a, g(a) - 26, b, g(b) - 26, T["acento"], 3.5)
    for x in xs:
        s += f"<circle cx='{x}' cy='{g(x) - 26:.0f}' r='7' fill='{T['acento']}'/>"
    s += f"<rect x='0' y='0' width='{FW}' height='190' fill='url(#niebla)'/>"
    s += tx(60, g(200) - 70, "Pesos al azar: error alto", T, 26, T["tinta"], peso=600, anc="start")
    s += tx(900, 300, "Error bajo", T, 30, T["acento"], anc="start", peso=700)
    s += tx(1000, 60, "Niebla: solo vemos", T, 24, T["suave"]) + tx(1000, 90, "la pendiente a nuestros pies", T, 24, T["suave"])
    return s

def f_retro(T):
    sr, pos = red([3, 4, 4, 2], 200, 960, 60, 360, T, r=18, op=.3)
    s = sr
    s += flecha(220, 20, 940, 20, T["suave"], 4, .8) + tx(580, 10, "Hacia delante: la respuesta", T, 26, T["suave"], extra="dy='-0'")
    s += flecha(940, 410, 220, 410, CORAL, 5) + tx(580, 445, "Hacia atrás: el error, capa a capa", T, 26, CORAL, peso=600)
    for a in (3, 2, 1):
        for p in pos[a][:2]:
            q = pos[a - 1][1]
            s += flecha(p[0] - 22, p[1], q[0] + 24, q[1], CORAL, 3, .9)
    s += f"<rect x='1000' y='{pos[3][0][1] - 34}' width='140' height='68' rx='14' fill='{T['panel']}' stroke='{CORAL}' stroke-width='3'/>"
    s += tx(1070, pos[3][0][1] + 10, "Error", T, 30, CORAL, peso=700)
    return s

def pixeles_tres():
    import numpy as np
    yy, xx = np.mgrid[0:28, 0:28].astype(float)
    img = np.zeros((28, 28))
    for cy, cx, rr in ((9.0, 13.5, 5.2), (18.5, 13.5, 5.8)):
        d = np.abs(np.hypot(yy - cy, xx - cx) - rr)
        ang = np.degrees(np.arctan2(yy - cy, xx - cx))
        abierto = (ang > 130) | (ang < -150) if cy < 12 else (ang > 150) | (ang < -130)
        v = np.exp(-(d / 1.1) ** 2); v[abierto] = 0
        img = np.maximum(img, v)
    img[13:15, 10:14] = np.maximum(img[13:15, 10:14], .9)
    return img

def f_digito(T):
    img = pixeles_tres(); s = ""; c = 14; x0, y0 = 40, 20
    for i in range(28):
        for j in range(28):
            v = img[i, j]
            s += f"<rect x='{x0 + j * c}' y='{y0 + i * c}' width='{c - 1}' height='{c - 1}' fill='{T['tinta']}' fill-opacity='{0.06 + 0.94 * v:.2f}'/>"
    s += tx(x0 + 196, 440, "28 × 28 píxeles", T, 24, T["suave"])
    s += flecha(450, 215, 520, 215, T["tinta"], 4, .8)
    nums = ["0", "0", "0,2", "0,9", "1", "0,8", "0,1", "0", "…"]
    for k, n in enumerate(nums):
        s += tx(575, 50 + k * 42, n, T, 28, T["acento"] if n not in ("0", "…") else T["suave"], peso=600)
    s += tx(575, 440, "784 números", T, 24, T["suave"])
    sr, pos = red([6, 5, 10], 680, 1000, 20, 410, T, r=11, op=.3, w=1.5)
    s += sr
    for k, (x, y) in enumerate(pos[2]):
        col = T["acento"] if k == 3 else T["suave"]
        s += tx(x + 40, y + 9, str(k), T, 26 if k != 3 else 34, col, anc="start", peso=700 if k == 3 else 500)
        if k == 3:
            s += f"<circle cx='{x}' cy='{y}' r='11' fill='{T['acento']}'/>"
    s += tx(840, 440, "capas ocultas", T, 24, T["suave"])
    return s

def f_rasgos(T):
    s = ""; img = pixeles_tres(); c = 6
    for i in range(28):
        for j in range(28):
            s += f"<rect x='{40 + j * c}' y='{130 + i * c}' width='{c}' height='{c}' fill='{T['tinta']}' fill-opacity='{0.05 + 0.95 * img[i, j]:.2f}'/>"
    cols = [(120, "Píxeles"), (420, "Trazos"), (730, "Formas"), (1030, "«Es un tres»")]
    for k, ang in enumerate((0, 45, 90, 135)):
        x, y = 360 + (k % 2) * 120, 110 + (k // 2) * 120
        s += f"<rect x='{x}' y='{y}' width='100' height='100' rx='10' fill='{T['panel']}' stroke='{T['linea']}'/>"
        dx, dy = 32 * math.cos(math.radians(ang)), 32 * math.sin(math.radians(ang))
        s += linea(x + 50 - dx, y + 50 - dy, x + 50 + dx, y + 50 + dy, T["acento"], 6)
    for k in range(2):
        x, y = 670, 110 + k * 120
        s += f"<rect x='{x}' y='{y}' width='120' height='100' rx='10' fill='{T['panel']}' stroke='{T['linea']}'/>"
        s += f"<path d='M{x + 35} {y + 25} A 30 26 0 1 1 {x + 40} {y + 80}' fill='none' stroke='{T['acento']}' stroke-width='6'/>"
    s += tx(1030, 270, "3", T, 190, T["acento"], peso=700, fam="Corm")
    for xa in (230, 610, 860):
        s += flecha(xa, 215, xa + 50, 215, T["tinta"], 4, .7)
    for x, t in cols:
        s += tx(x, 390, t, T, 30, T["tinta"], peso=600)
    return s

FIGURAS = {"movil": f_movil, "neurona_bio": f_neurona_bio, "disparo": f_disparo, "mcp": f_mcp, "perceptron": f_perceptron,
           "suma": f_suma, "mark1": f_mark1, "recta": f_recta, "xor": f_xor, "capas": f_capas, "culpa": f_culpa,
           "sigmoide": f_sigmoide, "montana": f_montana, "retro": f_retro, "digito": f_digito, "rasgos": f_rasgos}

# ---------------------------------------------------------------- integración con video_ligero
_plantilla_base = VL.plantilla

def plantilla(sc, T, titulo_ep):
    if sc["tipo"] != "ilus":
        return _plantilla_base(sc, T, titulo_ep)
    p = sc["params"]
    fig = FIGURAS[p["fig"]](T)
    pie = (f"<div style='position:absolute;left:60px;right:60px;bottom:52px;text-align:center;font-size:{VL.tam(p.get('pie', ''), 30, 24, 70)}px;"
           f"line-height:1.3;color:{T['tinta']}'><span style='background:{T['panel']};padding:8px 20px;border-radius:12px;"
           f"box-decoration-break:clone;-webkit-box-decoration-break:clone'>{VL.e(p.get('pie', ''))}</span></div>") if p.get("pie") else ""
    return (f"<div class='bg'><svg viewBox='0 0 {VL.W} {VL.H}' width='{VL.W}' height='{VL.H}'>"
            f"<g transform='translate(60,118)'>{fig}</g></svg></div>{pie}")

VL.plantilla = plantilla

if __name__ == "__main__":
    VL.main()
