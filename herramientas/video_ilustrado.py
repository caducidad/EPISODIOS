"""Vídeo ilustrado: como video_ligero.py (mismos fondos, cabecera, barra de progreso y tipos de escena),
más el tipo "ilus", una ilustración dibujada a propósito en SVG con un pie de texto.

Uso:
    python3 video_ilustrado.py escenas.json carpeta_imagenes --serie ia --titulo "Título" [--hoja hoja.jpg] [ids...]

Tipo nuevo:
    ilus  {"fig": nombre de la figura en FIGURAS, "pie": texto bajo la ilustración}

Las figuras se dibujan en un lienzo de 1160x440 (se coloca entre la cabecera y el pie). Cada función recibe el
tema T (colores de la serie) y devuelve el contenido SVG. Para un episodio nuevo, añade sus figuras a FIGURAS.
Figuras actuales: episodios ia01 (Qué es una red neuronal, desde cero), sc02 (Los lobos de Yellowstone)
y fi0-2 (El mapa de las grandes preguntas).
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


# ---------------------------------------------------------------- figuras del episodio sc02 (Los lobos de Yellowstone)
def barras(T, datos, x0, y0, w, h, vmax, col=None, fmt=str, ancho=None, nota_col=None):
    """datos: [(etiqueta, valor, color opcional)]. Dibuja barras verticales con su valor encima."""
    n = len(datos); paso = w / n; bw = ancho or paso * .56; s = ""
    s += linea(x0, y0 + h, x0 + w, y0 + h, T["suave"], 2, .7)
    for i, d in enumerate(datos):
        et, v = d[0], d[1]; c = d[2] if len(d) > 2 else (col or T["linea"])
        bh = max(4, h * v / vmax); x = x0 + i * paso + (paso - bw) / 2
        s += f"<rect x='{x:.1f}' y='{y0 + h - bh:.1f}' width='{bw:.1f}' height='{bh:.1f}' rx='6' fill='{c}'/>"
        s += tx(x + bw / 2, y0 + h - bh - 14, fmt(v), T, 30, T["tinta"], peso=600)
        s += tx(x + bw / 2, y0 + h + 38, et, T, 26, T["suave"])
    return s

def miles(v):
    return f"{v:,}".replace(",", ".")

def f_lobos_bar(T):
    datos = [("1994", 0), ("1995", 14, T["suave"]), ("Máximo", 174, T["acento"]), ("2012", 83), ("2018", 80), ("2024", 108), ("2025", 84)]
    s = barras(T, datos, 40, 40, 1080, 300, 190)
    s += tx(1120, 30, "lobos en el parque", T, 24, T["suave"], anc="end")
    return s

def f_wapities_bar(T):
    datos = [("1995", 17000), ("2013", 3915, T["acento"]), ("2022", 6673)]
    s = barras(T, datos, 200, 40, 760, 300, 18500, fmt=miles, ancho=170)
    s += tx(1120, 30, "wapitíes contados en invierno (rango norte)", T, 24, T["suave"], anc="end")
    return s

def pict_lobo(x, y, T, k=1.0, col=None):
    c = col or T["tinta"]
    pts = [(-34, 10), (-26, -30), (-12, -12), (12, -12), (26, -30), (34, 10), (14, 30), (0, 38), (-14, 30)]
    s = "<polygon points='" + " ".join(f"{x + a * k:.1f},{y + b * k:.1f}" for a, b in pts) + f"' fill='{c}'/>"
    s += f"<circle cx='{x - 12 * k}' cy='{y + 4 * k}' r='{4 * k}' fill='{T['c2']}'/><circle cx='{x + 12 * k}' cy='{y + 4 * k}' r='{4 * k}' fill='{T['c2']}'/>"
    return s

def pict_wapiti(x, y, T, k=1.0, col=None):
    c = col or T["tinta"]; s = ""
    s += f"<ellipse cx='{x}' cy='{y + 14 * k}' rx='{18 * k}' ry='{26 * k}' fill='{c}'/>"
    for sg in (-1, 1):
        s += f"<path d='M{x + sg * 10 * k} {y - 8 * k} L{x + sg * 30 * k} {y - 44 * k} M{x + sg * 20 * k} {y - 26 * k} L{x + sg * 40 * k} {y - 30 * k} M{x + sg * 26 * k} {y - 36 * k} L{x + sg * 22 * k} {y - 56 * k}' stroke='{c}' stroke-width='{5 * k}' stroke-linecap='round' fill='none'/>"
    return s

def pict_sauce(x, y, T, k=1.0, col=None, alto=1.0):
    c = col or T["linea"]; s = linea(x, y + 40 * k, x, y + 40 * k - 70 * k * alto, "#a07850", 6 * k)
    top = y + 40 * k - 70 * k * alto
    for d in range(-3, 4):
        s += f"<path d='M{x} {top} q {d * 10 * k} {-8 * k} {d * 14 * k} {40 * k * alto}' stroke='{c}' stroke-width='{4 * k}' fill='none' stroke-linecap='round'/>"
    return s

def pict_castor(x, y, T, k=1.0):
    s = f"<ellipse cx='{x + 28 * k}' cy='{y + 16 * k}' rx='{20 * k}' ry='{9 * k}' fill='#7a5a3a' transform='rotate(-15 {x + 28 * k} {y + 16 * k})'/>"
    s += f"<ellipse cx='{x - 4 * k}' cy='{y + 4 * k}' rx='{30 * k}' ry='{20 * k}' fill='#a87a4c'/>"
    s += f"<circle cx='{x - 30 * k}' cy='{y - 6 * k}' r='{13 * k}' fill='#a87a4c'/><circle cx='{x - 34 * k}' cy='{y - 10 * k}' r='{3 * k}' fill='{T['c2']}'/>"
    return s

def pict_rio(x, y, T, k=1.0):
    s = ""
    for j in range(3):
        s += f"<path d='M{x - 46 * k} {y - 14 * k + j * 16 * k} q {23 * k} {-14 * k} {46 * k} 0 t {46 * k} 0' stroke='#6fb7e0' stroke-width='{5 * k}' fill='none' stroke-linecap='round'/>"
    return s

def f_cadena(T):
    items = [(110, "Lobo", pict_lobo), (340, "Wapití", pict_wapiti), (580, "Sauce", pict_sauce), (820, "Castor", pict_castor), (1050, "Río", pict_rio)]
    s = ""
    for i, (x, t, f) in enumerate(items):
        s += f"<rect x='{x - 95}' y='60' width='190' height='230' rx='20' fill='{T['panel']}' stroke='{T['acento'] if i == 0 else T['linea']}' stroke-width='3'/>"
        s += f(x, 150, T, 1.3)
        s += tx(x, 268, t, T, 32, peso=600)
        if i < 4:
            s += flecha(x + 100, 175, x + 135, 175, T["acento"], 5)
    for x, t in [(225, "come"), (460, "come"), (700, "alimenta"), (935, "frena")]:
        s += tx(x, 330, t, T, 24, T["suave"])
    s += tx(580, 400, "Si cambia el primer eslabón, ¿cambia todo lo demás?", T, 28, T["tinta"])
    return s

def f_miedo(T):
    s = f"<path d='M0 300 C 200 300 300 120 460 120 C 620 120 640 330 760 330 C 880 330 960 160 1160 160 L1160 440 L0 440 Z' fill='{T['tierra']}' opacity='.9'/>"
    s += f"<path d='M640 335 C 700 342 820 342 880 330' stroke='#6fb7e0' stroke-width='10' fill='none' stroke-linecap='round'/>"
    s += f"<ellipse cx='760' cy='310' rx='170' ry='90' fill='{CORAL}' opacity='.22'/>"
    s += tx(760, 378, "zona de riesgo", T, 28, CORAL, peso=600)
    for xx in (690, 730, 800, 840):
        s += pict_sauce(xx, 255, T, .8, alto=1.0)
    s += pict_lobo(1010, 120, T, 1.1, CORAL)
    for (xx, yy) in [(330, 150), (400, 120), (250, 200)]:
        s += pict_wapiti(xx, yy, T, .9)
    s += flecha(560, 170, 460, 150, T["acento"], 4)
    s += tx(300, 300, "lugares abiertos, con buena vista", T, 26, T["tinta"])
    s += tx(760, 426, "barrancos y riberas: fácil emboscada", T, 26, T["tinta"])
    return s

def f_castores(T):
    datos = [("1996", 49), ("2007", 127, T["acento"]), ("2024", 121)]
    s = barras(T, datos, 40, 40, 640, 300, 140, ancho=150)
    s += f"<rect x='740' y='70' width='400' height='250' rx='18' fill='{T['panel']}' stroke='{CORAL}' stroke-width='3'/>"
    s += tx(940, 140, "Pero entre 1986 y 1999", T, 28, CORAL, peso=600)
    s += tx(940, 200, "se soltaron 129 castores", T, 30, peso=600)
    s += tx(940, 245, "al norte del parque", T, 28)
    s += tx(940, 290, "(Servicio Forestal)", T, 24, T["suave"])
    s += tx(360, 30, "colonias de castores en todo el parque", T, 24, T["suave"])
    return s

def f_carrona(T):
    s = ""; grupos = [("Marzo", 27, 4), ("Abril", 66, 11)]
    y0, h = 50, 290
    s += linea(80, y0 + h, 1100, y0 + h, T["suave"], 2, .7)
    for i, (mes, sin, con) in enumerate(grupos):
        cx = 330 + i * 500
        for j, (v, c, et) in enumerate([(sin, CORAL, "sin lobos"), (con, T["linea"], "con lobos")]):
            x = cx - 150 + j * 170; bh = h * v / 70
            s += f"<rect x='{x}' y='{y0 + h - bh}' width='130' height='{bh}' rx='6' fill='{c}'/>"
            s += tx(x + 65, y0 + h - bh - 14, f"−{v} %", T, 32, peso=600)
            s += tx(x + 65, y0 + h + 34, et, T, 24, T["suave"])
        s += tx(cx - 20, y0 + h + 80, mes, T, 30, peso=600)
    return s

def f_reloj(T):
    cx, cy, r = 340, 215, 170; s = ""
    s += f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{T['panel']}' stroke='{T['suave']}' stroke-width='3'/>"
    def arco(h0, h1, col):
        a0 = math.radians(h0 / 24 * 360 - 90); a1 = math.radians(h1 / 24 * 360 - 90)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0); x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if (h1 - h0) % 24 > 12 else 0
        return f"<path d='M{cx} {cy} L{x0:.1f} {y0:.1f} A {r} {r} 0 {large} 1 {x1:.1f} {y1:.1f} Z' fill='{col}' opacity='.85'/>"
    s += arco(5, 9, CORAL) + arco(17, 21, CORAL)
    for h, t in [(0, "0 h"), (6, "6 h"), (12, "12 h"), (18, "18 h")]:
        a = math.radians(h / 24 * 360 - 90)
        s += tx(cx + (r + 34) * math.cos(a), cy + (r + 34) * math.sin(a) + 9, t, T, 24, T["suave"])
    s += f"<circle cx='{cx}' cy='{cy}' r='8' fill='{T['tinta']}'/>"
    s += f"<rect x='640' y='90' width='34' height='34' rx='6' fill='{CORAL}'/>" + tx(694, 117, "Lobos activos: amanecer y anochecer", T, 28, anc="start")
    s += f"<rect x='640' y='180' width='34' height='34' rx='6' fill='{T['panel']}' stroke='{T['suave']}'/>" + tx(694, 207, "El resto del día: poco activos", T, 28, anc="start")
    s += tx(640, 300, "Los wapitíes evitan las zonas de riesgo", T, 28, T["acento"], anc="start", peso=600)
    s += tx(640, 340, "solo en las horas peligrosas", T, 28, T["acento"], anc="start", peso=600)
    return s

def f_altos(T):
    r = random.Random(7); s = ""
    alturas = [r.uniform(.15, .55) for _ in range(22)]
    for i in r.sample(range(22), 5):
        alturas[i] = r.uniform(.8, 1.0)
    altos = sorted(range(22), key=lambda i: -alturas[i])[:5]
    for i, a in enumerate(alturas):
        x = 60 + i * 50; base = 330; hh = 260 * a
        col = T["acento"] if i in altos else T["linea"]
        s += linea(x, base, x, base - hh, "#cfc7b8", 5)
        s += f"<ellipse cx='{x}' cy='{base - hh}' rx='16' ry='{14 + 10 * a:.0f}' fill='{col}' opacity='{1 if i in altos else .55}'/>"
    s += linea(30, 332, 1130, 332, T["suave"], 2, .7)
    s += f"<circle cx='{60 + 0}' cy='395' r='10' fill='{T['acento']}'/>" + tx(80, 404, "Los 5 más altos: «se recupera deprisa»", T, 26, anc="start")
    s += f"<circle cx='680' cy='395' r='10' fill='{T['linea']}'/>" + tx(700, 404, "Al azar: recuperación más lenta", T, 26, anc="start")
    return s

def f_parcelas(T):
    s = ""; base = 330
    cols = [("Control", .28, False, False), ("Solo valla", .55, True, False), ("Solo presa", .38, False, True), ("Valla y presa", 1.0, True, True)]
    for i, (t, a, valla, presa) in enumerate(cols):
        x = 145 + i * 290
        s += f"<rect x='{x - 125}' y='40' width='250' height='{base - 30}' rx='14' fill='{T['panel']}'/>"
        if presa:
            s += f"<rect x='{x - 115}' y='{base - 26}' width='230' height='22' rx='4' fill='#6fb7e0' opacity='.8'/>"
        for dx in (-55, 0, 55):
            hh = 250 * a
            s += linea(x + dx, base, x + dx, base - hh, "#a07850", 5)
            for d in range(-2, 3):
                s += f"<path d='M{x + dx} {base - hh} q {d * 8} -6 {d * 12} {min(60, hh * .5):.0f}' stroke='{T['linea']}' stroke-width='4' fill='none'/>"
        if valla:
            for k in range(6):
                s += linea(x - 118 + k * 47, base, x - 118 + k * 47, base - 70, T["tinta"], 3, .8)
            s += linea(x - 118, base - 60, x + 117, base - 60, T["tinta"], 2, .8) + linea(x - 118, base - 30, x + 117, base - 30, T["tinta"], 2, .8)
        s += tx(x, base + 40, t, T, 28, T["acento"] if i == 3 else T["tinta"], peso=600)
    s += tx(580, base + 90, "Solo con valla y agua alta los sauces crecen más de tres veces", T, 26, T["suave"])
    return s

def f_cauce(T):
    s = ""
    for k, (x0, titulo, enc) in enumerate([(0, "Con presas de castor", False), (600, "Sin presas: arroyo encajado", True)]):
        s += tx(x0 + 280, 34, titulo, T, 30, T["acento"] if k == 0 else CORAL, peso=600)
        if not enc:
            s += f"<path d='M{x0 + 20} 200 L{x0 + 220} 200 Q{x0 + 280} 235 {x0 + 340} 200 L{x0 + 540} 200 L{x0 + 540} 380 L{x0 + 20} 380 Z' fill='{T['tierra']}'/>"
            s += f"<path d='M{x0 + 228} 204 Q{x0 + 280} 232 {x0 + 332} 204 Z' fill='#6fb7e0'/>"
            s += linea(x0 + 20, 225, x0 + 540, 225, "#6fb7e0", 3, .9, "10 8")
            for xx in (x0 + 80, x0 + 150, x0 + 410, x0 + 480):
                s += pict_sauce(xx, 150, T, 1.0, alto=1.0)
                s += f"<path d='M{xx} 200 l -6 22 M{xx} 200 l 6 24' stroke='#a07850' stroke-width='3'/>"
        else:
            s += f"<path d='M{x0 + 20} 200 L{x0 + 240} 200 L{x0 + 255} 330 L{x0 + 305} 330 L{x0 + 320} 200 L{x0 + 540} 200 L{x0 + 540} 380 L{x0 + 20} 380 Z' fill='{T['tierra']}'/>"
            s += f"<rect x='{x0 + 257}' y='310' width='46' height='20' fill='#6fb7e0'/>"
            s += linea(x0 + 20, 320, x0 + 540, 320, "#6fb7e0", 3, .9, "10 8")
            for xx in range(x0 + 40, x0 + 540, 26):
                if abs(xx - (x0 + 280)) > 50:
                    s += f"<path d='M{xx} 200 l -4 -16 M{xx} 200 l 4 -14 M{xx} 200 l 0 -18' stroke='#c9b46a' stroke-width='3'/>"
            s += pict_sauce(x0 + 110, 172, T, .6, alto=.6)
        s += tx(x0 + 280, 420, "agua subterránea alta" if not enc else "el agua queda lejos de las raíces", T, 26, T["suave"])
    s += linea(580, 60, 580, 420, T["suave"], 2, .4)
    return s

def f_estados(T):
    s = ""
    pts = []
    for i in range(0, 1001, 10):
        x = 60 + i * 1.04; u = i / 1000
        y = 330 - 210 * math.exp(-((u - .5) / .13) ** 2) - 60 * (math.exp(-((u + .05) / .12) ** 2) + math.exp(-((u - 1.05) / .12) ** 2))
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    s += f"<path d='{d} L1100 440 L60 440 Z' fill='{T['tierra']}' opacity='.8'/>"
    s += f"<path d='{d}' stroke='{T['linea']}' stroke-width='4' fill='none'/>"
    s += f"<circle cx='{60 + 250 * 1.04 - 30}' cy='{316}' r='24' fill='{T['suave']}' opacity='.5' stroke='{T['tinta']}' stroke-dasharray='5 5'/>"
    s += f"<circle cx='{60 + 780 * 1.04}' cy='{314}' r='26' fill='{T['acento']}'/>"
    s += f"<path d='M300 250 Q 580 20 860 250' stroke='{CORAL}' stroke-width='4' fill='none' stroke-dasharray='12 10'/>"
    s += f"<polygon points='860,250 842,236 852,262' fill='{CORAL}'/>"
    s += tx(250, 400, "Pradera húmeda con sauces", T, 28)
    s += tx(880, 400, "Pradera seca", T, 28)
    s += tx(580, 60, "70 años sin lobos", T, 28, CORAL, peso=600)
    return s

def f_actores(T):
    cx, cy = 580, 215; s = ""
    s += f"<circle cx='{cx}' cy='{cy}' r='88' fill='{T['panel']}' stroke='{T['acento']}' stroke-width='4'/>"
    s += pict_wapiti(cx, cy - 10, T, 1.0) + tx(cx, cy + 66, "Wapitíes", T, 26, peso=600)
    act = [("Lobos", -160), ("Pumas", -110), ("Osos grizzly", -60), ("Cazadores", -10), ("Sequía", 40), ("Bisontes", 140), ("Agua y castores", 200)]
    for t, ang in act:
        a = math.radians(ang); x = cx + 390 * math.cos(a); y = cy + 175 * math.sin(a)
        s += flecha(x - (x - cx) * .22, y - (y - cy) * .22, cx + 105 * math.cos(a), cy + 100 * math.sin(a), T["linea"], 3, .8)
        w = 26 * len(t) * .62 + 40
        s += f"<rect x='{x - w / 2:.0f}' y='{y - 30:.0f}' width='{w:.0f}' height='58' rx='14' fill='{T['panel']}' stroke='{T['acento'] if t == 'Lobos' else T['linea']}' stroke-width='2'/>"
        s += tx(x, y + 9, t, T, 28, T["acento"] if t == "Lobos" else T["tinta"], peso=600)
    return s

def f_circular(T):
    s = ""
    cajas = [(250, 110, "Altura del sauce"), (910, 110, "Volumen de la copa"), (580, 340, "«La altura predice el volumen»")]
    for x, y, t in cajas:
        w = 420 if "predice" in t else 340
        s += f"<rect x='{x - w / 2}' y='{y - 42}' width='{w}' height='84' rx='18' fill='{T['panel']}' stroke='{T['linea']}' stroke-width='3'/>"
        s += tx(x, y + 10, t, T, 30, peso=600)
    s += flecha(425, 110, 735, 110, T["acento"], 5) + tx(580, 92, "se calcula con", T, 24, T["suave"])
    s += flecha(860, 158, 700, 292, T["acento"], 5)
    s += flecha(460, 292, 300, 158, CORAL, 5)
    s += tx(300, 250, "¿círculo?", T, 30, CORAL, peso=600)
    return s

def f_mollie(T):
    s = f"<path d='M150 40 L560 40 L560 400 L180 400 L150 330 Z' fill='{T['tierra']}' stroke='{T['linea']}' stroke-width='4'/>"
    s += tx(355, 80, "Parque Nacional de Yellowstone", T, 26, T["suave"])
    s += f"<ellipse cx='330' cy='300' rx='110' ry='38' fill='#6fb7e0' opacity='.5'/>" + tx(330, 308, "lago Yellowstone", T, 22, T["tinta"])
    s += f"<circle cx='420' cy='200' r='14' fill='{T['tinta']}'/>" + tx(420, 245, "Valle de Pelican", T, 28, peso=600)
    s += f"<path d='M440 190 C 560 120 640 120 730 160' stroke='{T['acento']}' stroke-width='6' fill='none' stroke-dasharray='14 10'/>"
    s += f"<polygon points='740,166 716,166 730,146' fill='{T['acento']}'/>"
    s += f"<circle cx='760' cy='175' r='16' fill='{T['acento']}'/>" + tx(785, 160, "Cuenca de Sunlight", T, 30, T["acento"], anc="start", peso=600)
    s += tx(785, 200, "fuera del parque: zona de caza", T, 24, CORAL, anc="start")
    s += f"<circle cx='980' cy='300' r='10' fill='{T['tinta']}'/>" + tx(1000, 309, "Cody", T, 26, anc="start")
    s += tx(1100, 420, "Esquema, sin escala", T, 22, T["suave"], anc="end")
    return s

# ---------------------------------------------------------------- figuras del episodio fi0-2 (El mapa de las grandes preguntas)
AZUL = "#8fc1e3"
VERDE = "#4f8a63"

def pildora(x, y, t, T, size=28, col=None, borde=None, pad=22, peso=600, fondo=None, w=None):
    w = w or (len(t) * size * .56 + 2 * pad); h = size * 1.95
    return (f"<rect x='{x - w / 2:.0f}' y='{y - h / 2:.0f}' width='{w:.0f}' height='{h:.0f}' rx='{h / 2:.0f}' fill='{fondo or T['panel']}' "
            f"stroke='{borde or T['linea']}' stroke-width='2.5'/>" + tx(x, y + size * .36, t, T, size, col or T["tinta"], peso=peso))

def caja(x, y, w, h, T, borde=None, fondo=None, sw=3, rx=18):
    return f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fondo or T['panel']}' stroke='{borde or T['linea']}' stroke-width='{sw}'/>"

def blob(cx, cy, rx, ry, seed, n=14, jit=.15):
    r = random.Random(seed); pts = []
    for i in range(n):
        a = 2 * math.pi * i / n; k = 1 + r.uniform(-jit, jit)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6); c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + "Z"

def visto(x, y, col, k=1.0):
    return f"<path d='M{x - 14 * k:.0f} {y:.0f} l{10 * k:.0f} {11 * k:.0f} l{20 * k:.0f} {-24 * k:.0f}' stroke='{col}' stroke-width='{6 * k:.0f}' fill='none' stroke-linecap='round' stroke-linejoin='round'/>"

def f_frontera(T):
    s = tx(300, 62, "filósofo natural", T, 40, T["suave"], fam="Corm", peso=600)
    s += linea(160, 50, 440, 50, CORAL, 3, .9)
    s += flecha(490, 50, 660, 50, T["acento"], 5)
    s += tx(860, 66, "científico", T, 56, T["acento"], fam="Corm", peso=700)
    s += linea(580, 110, 580, 430, T["acento"], 4, .9, dash="14 12")
    # lado de la filosofía
    s += tx(290, 330, "?", T, 230, T["tinta"], fam="Corm", peso=700)
    s += tx(290, 410, "Filosofía", T, 36, peso=600)
    # lado de la ciencia: matraz y telescopio
    s += (f"<path d='M770 170 L770 250 L715 345 Q705 372 735 372 L845 372 Q875 372 865 345 L810 250 L810 170' fill='none' stroke='{T['tinta']}' stroke-width='5' stroke-linejoin='round'/>"
          f"<line x1='758' y1='170' x2='822' y2='170' stroke='{T['tinta']}' stroke-width='5' stroke-linecap='round'/>"
          f"<path d='M738 310 L842 310 L862 348 Q868 364 846 364 L734 364 Q712 364 718 348 Z' fill='{AZUL}' opacity='.75'/>")
    s += (f"<g transform='rotate(-28 990 250)'><rect x='900' y='232' width='130' height='36' rx='6' fill='none' stroke='{T['tinta']}' stroke-width='5'/>"
          f"<rect x='1030' y='224' width='60' height='52' rx='6' fill='none' stroke='{T['tinta']}' stroke-width='5'/></g>"
          + linea(985, 262, 940, 372, T["tinta"], 5) + linea(985, 262, 1030, 372, T["tinta"], 5) + linea(985, 262, 985, 372, T["tinta"], 5))
    s += tx(870, 410, "Ciencia", T, 36, peso=600)
    return s

def huevo_path(cx, cy, rx, ry):
    # contorno de huevo: más estrecho arriba
    return (f"M{cx} {cy - ry * 1.12:.0f} C{cx + rx * .78:.0f} {cy - ry * 1.12:.0f} {cx + rx:.0f} {cy - ry * .1:.0f} {cx + rx:.0f} {cy + ry * .28:.0f} "
            f"C{cx + rx:.0f} {cy + ry * .78:.0f} {cx + rx * .55:.0f} {cy + ry:.0f} {cx} {cy + ry:.0f} "
            f"C{cx - rx * .55:.0f} {cy + ry:.0f} {cx - rx:.0f} {cy + ry * .78:.0f} {cx - rx:.0f} {cy + ry * .28:.0f} "
            f"C{cx - rx:.0f} {cy - ry * .1:.0f} {cx - rx * .78:.0f} {cy - ry * 1.12:.0f} {cx} {cy - ry * 1.12:.0f}Z")

def f_huevo(T):
    cx, cy = 360, 232
    s = f"<path d='{huevo_path(cx, cy, 165, 190)}' fill='#f7f1e3' stroke='#cdb98f' stroke-width='16'/>"
    s += f"<circle cx='{cx}' cy='{cy + 40}' r='78' fill='#e9b33a' stroke='#c98f1e' stroke-width='4'/>"
    filas = [(70, "Cáscara", "Lógica", cx + 150, cy - 110), (220, "Clara", "Ética", cx + 110, cy - 20), (370, "Yema", "Física", cx + 60, cy + 60)]
    for y, parte, rama, px, py in filas:
        s += linea(px, py, 640, y - 8, T["acento"], 3, .9) + f"<circle cx='{px}' cy='{py}' r='7' fill='{T['acento']}'/>"
        s += tx(660, y, parte, T, 30, T["suave"], anc="start")
        s += tx(820, y + 4, rama, T, 56, T["tinta"], anc="start", fam="Corm", peso=700)
    return s

def f_huerto(T):
    s = f"<rect x='60' y='330' width='1040' height='70' rx='10' fill='{T['tierra']}'/>"
    for i, x in enumerate([250, 480, 710, 930]):
        s += f"<rect x='{x - 13}' y='210' width='26' height='125' rx='6' fill='#7a5a3a'/>"
        s += f"<circle cx='{x}' cy='165' r='82' fill='{VERDE}'/><circle cx='{x - 52}' cy='200' r='48' fill='{VERDE}'/><circle cx='{x + 52}' cy='200' r='48' fill='{VERDE}'/>"
        for dx, dy in [(-45, -10), (20, -45), (48, 22), (-12, 28), (-62, 44)]:
            s += f"<circle cx='{x + dx}' cy='{165 + dy}' r='12' fill='{T['acento']}' stroke='#8a6420' stroke-width='2'/>"
    # valla
    s += f"<rect x='60' y='322' width='1050' height='12' fill='#b39c6c' stroke='#6b5a3c' stroke-width='2'/><rect x='60' y='366' width='1050' height='12' fill='#b39c6c' stroke='#6b5a3c' stroke-width='2'/>"
    for x in range(70, 1100, 46):
        s += f"<path d='M{x} 404 L{x} 300 L{x + 11} 286 L{x + 22} 300 L{x + 22} 404 Z' fill='{T['costa']}' stroke='#6b5a3c' stroke-width='2'/>"
    s += pildora(140, 40, "Fruto: ética", T, 30, T["acento"], T["acento"])
    s += linea(190, 68, 228, 150, T["acento"], 3, .9)
    s += pildora(590, 40, "Tierra y árboles: física", T, 30)
    s += linea(560, 70, 500, 120, T["linea"], 3, .8) + linea(620, 70, 690, 120, T["linea"], 3, .8)
    s += pildora(1010, 40, "Valla: lógica", T, 30)
    s += linea(1040, 70, 1076, 284, T["linea"], 3, .8)
    return s

def f_aristoteles(T):
    cols = [("Teóricos", "conocer por conocer", ["Física", "Matemáticas", "Filosofía primera"]),
            ("Prácticos", "orientar la acción", ["Ética", "Política"]),
            ("Productivos", "hacer cosas", ["Poética", "Retórica"])]
    s = ""
    for i, (t, sub, items) in enumerate(cols):
        x = 10 + i * 385
        s += caja(x, 6, 370, 318, T, borde=T["acento"] if i == 0 else T["linea"])
        s += tx(x + 185, 62, t, T, 52, T["acento"], fam="Corm", peso=700)
        s += tx(x + 185, 100, sub, T, 26, T["suave"])
        s += linea(x + 60, 122, x + 310, 122, T["suave"], 2, .5)
        for j, it in enumerate(items):
            s += tx(x + 185, 172 + j * 50, it, T, 34, peso=500)
    s += caja(10, 350, 1140, 80, T, borde=T["acento"], rx=40)
    s += tx(580, 402, "Órganon · la lógica, instrumento para todos los saberes", T, 32, peso=600)
    return s

def f_arbol(T):
    s = linea(40, 300, 1120, 300, T["suave"], 3, .6, dash="6 10")
    # raíces
    for d in ["M580 300 C560 350 470 350 400 400", "M580 300 C580 360 560 380 540 425", "M580 300 C600 350 690 350 760 400", "M580 300 C585 360 610 380 630 425"]:
        s += f"<path d='{d}' stroke='#9a7a52' stroke-width='10' fill='none' stroke-linecap='round'/>"
    # tronco y ramas
    s += f"<path d='M552 300 L562 190 L598 190 L608 300 Z' fill='#7a5a3a'/>"
    for x, y in [(330, 95), (580, 60), (830, 95)]:
        s += f"<path d='M580 200 Q{(580 + x) / 2:.0f} {y + 95:.0f} {x} {y + 40}' stroke='#7a5a3a' stroke-width='16' fill='none' stroke-linecap='round'/>"
    for x, y, t in [(330, 95, "Medicina"), (580, 60, "Mecánica"), (830, 95, "Moral")]:
        s += f"<circle cx='{x}' cy='{y}' r='74' fill='{VERDE}'/><circle cx='{x - 58}' cy='{y + 22}' r='44' fill='{VERDE}'/><circle cx='{x + 58}' cy='{y + 22}' r='44' fill='{VERDE}'/>"
        for dx, dy in [(-70, 40), (66, 44), (0, -52)]:
            s += f"<circle cx='{x + dx}' cy='{y + dy}' r='11' fill='{T['acento']}' stroke='#8a6420' stroke-width='2'/>"
        s += tx(x, y + 14, t, T, 34, T["tinta"], peso=600, extra="stroke='#1d3a28' stroke-width='5' paint-order='stroke'")
    s += tx(640, 262, "Física", T, 40, T["tinta"], anc="start", fam="Corm", peso=700)
    s += tx(640, 290, "el tronco", T, 24, T["suave"], anc="start")
    s += tx(860, 392, "Metafísica", T, 46, T["acento"], anc="start", fam="Corm", peso=700)
    s += tx(860, 424, "las raíces", T, 24, T["suave"], anc="start")
    s += tx(60, 392, "Las ramas dan el fruto", T, 28, T["suave"], anc="start")
    return s

def f_enciclopedia(T):
    s = pildora(580, 40, "Entendimiento", T, 30, T["suave"])
    cols = [(200, "Memoria", "Historia", False), (580, "Razón", "Filosofía", True), (960, "Imaginación", "Poesía", False)]
    for x, fac, saber, prin in cols:
        s += linea(580, 70, x, 132, T["linea"], 3, .6)
        s += f"<ellipse cx='{x}' cy='190' rx='125' ry='56' fill='{T['panel']}' stroke='{T['acento'] if prin else T['linea']}' stroke-width='4'/>"
        s += tx(x, 201, fac, T, 32, peso=600)
        s += flecha(x, 250, x, 300, T["acento"] if prin else T["linea"], 4)
        w = 300
        s += caja(x - w / 2, 310, w, 86, T, borde=T["acento"] if prin else T["linea"])
        s += tx(x, 370, saber, T, 52, T["acento"] if prin else T["tinta"], fam="Corm", peso=700)
    s += tx(580, 432, "incluía las ciencias de Dios, del hombre y de la naturaleza", T, 24, T["suave"])
    return s

def f_wolff(T):
    s = caja(20, 120, 380, 200, T, borde=T["acento"])
    s += tx(210, 180, "Metafísica general", T, 30, T["suave"])
    s += tx(210, 240, "Ontología", T, 60, T["acento"], fam="Corm", peso=700)
    s += tx(210, 286, "el ser en cuanto tal", T, 28)
    s += tx(830, 36, "Metafísica especial", T, 30, T["suave"])
    filas = [(105, "Cosmología", "el mundo"), (225, "Psicología racional", "el alma"), (345, "Teología natural", "Dios")]
    for y, t, o in filas:
        s += flecha(400, 220, 520, y, T["linea"], 3, .8)
        s += caja(530, y - 50, 610, 100, T)
        s += tx(560, y + 16, t, T, 44, T["tinta"], anc="start", fam="Corm", peso=700)
        s += tx(1110, y + 12, o, T, 30, T["acento"], anc="end", peso=600)
    return s

def _kant(T, final):
    filas = [("¿Qué puedo saber?", "Metafísica"), ("¿Qué debo hacer?", "Moral"), ("¿Qué me cabe esperar?", "Religión"), ("¿Qué es el hombre?", "Antropología")]
    s = ""
    for i, (q, d) in enumerate(filas):
        y = 62 + i * 104; ult = i == 3
        op = 1 if (ult or not final) else .55
        col = T["acento"] if ult else T["tinta"]
        s += f"<g opacity='{op}'>"
        if ult:
            s += caja(20, y - 52, 1120, 96, T, borde=T["acento"], rx=20)
        s += tx(50, y + 14, q, T, 54 if ult else 48, col, anc="start", fam="Corm", peso=700 if ult else 600, extra="font-style='italic'")
        s += flecha(640, y, 730, y, T["suave"], 3, .8)
        s += tx(760, y + 11, d, T, 34, col, anc="start", peso=600)
        s += "</g>"
    # las tres primeras remiten a la cuarta
    s += f"<path d='M1040 62 L1090 62 L1090 322' stroke='{T['acento']}' stroke-width='4' fill='none' opacity='.9'/>"
    s += linea(1040, 166, 1090, 166, T["acento"], 4, .9) + linea(1040, 270, 1090, 270, T["acento"], 4, .9)
    s += f"<polygon points='1090,326 1078,304 1102,304' fill='{T['acento']}'/>"
    return s

def f_kant(T):
    return _kant(T, False)

def f_kant_fin(T):
    return _kant(T, True)

ISLAS = [("meta", "Metafísica", 185, 118, 150, 86, 11), ("epis", "Epistemología", 525, 108, 168, 82, 23), ("logi", "Lógica", 860, 118, 128, 78, 37),
         ("etic", "Ética", 200, 322, 140, 84, 41), ("poli", "Política", 525, 330, 152, 80, 59), ("este", "Estética", 850, 326, 128, 80, 67)]

def _mapa(T, hl=None):
    s = ""
    # rutas entre islas
    for a, b in [(0, 1), (1, 2), (0, 3), (3, 4), (4, 5), (1, 4), (2, 5)]:
        s += linea(ISLAS[a][2], ISLAS[a][3], ISLAS[b][2], ISLAS[b][3], T["suave"], 2, .35, dash="4 10")
    for k, nombre, cx, cy, rx, ry, sem in ISLAS:
        activa = hl == k; apagada = hl is not None and not activa
        d = blob(cx, cy, rx, ry, sem)
        relleno = "#c79a47" if activa else ("#262433" if apagada else T["tierra"])
        borde = "#fff3cf" if activa else ("#6f6a78" if apagada else T["costa"])
        s += f"<path d='{d}' fill='{relleno}' stroke='{borde}' stroke-width='{6 if activa else 3}'/>"
        s += f"<path d='{blob(cx, cy, rx * .72, ry * .68, sem + 5)}' fill='none' stroke='{borde}' stroke-width='1.5' opacity='.35'/>"
        s += tx(cx, cy + 14, nombre, T, 46 if len(nombre) < 11 else 42, "#1b1408" if activa else ("#8f8a99" if apagada else T["tinta"]), fam="Corm", peso=700)
    # archipiélago de las «filosofías de»
    r = random.Random(7)
    s += f"<g opacity='{.4 if hl else 1}'>"
    for i, y in enumerate([92, 160, 228, 296, 364]):
        x = 1085 + (22 if i % 2 else -18)
        s += f"<path d='{blob(x, y, 30 + r.uniform(-5, 6), 22 + r.uniform(-4, 4), 90 + i, n=9)}' fill='{T['tierra']}' stroke='{T['costa']}' stroke-width='2.5'/>"
    s += tx(1085, 38, "filosofías de…", T, 26, T["suave"])
    s += "</g>"
    return s

def f_mapa(T):
    return _mapa(T)

def f_estanteria(T):
    s = f"<rect x='40' y='340' width='1080' height='18' rx='4' fill='#7a5a3a'/>"
    r = random.Random(3); x = 80
    for i in range(8):
        h = r.randint(150, 200); w = 30
        s += f"<rect x='{x}' y='{340 - h}' width='{w}' height='{h}' rx='4' fill='#3f5f8a' stroke='{AZUL}' stroke-width='2'/>"
        x += w + 6
    fin_fis = x
    x += 70; ini_meta = x
    for i in range(14):
        h = r.randint(150, 200); w = 30
        s += f"<rect x='{x}' y='{340 - h}' width='{w}' height='{h}' rx='4' fill='#8a6a2c' stroke='{T['acento']}' stroke-width='2'/>"
        x += w + 6
    s += tx((80 + fin_fis) / 2, 110, "Física", T, 46, AZUL, fam="Corm", peso=700)
    s += tx((ini_meta + x) / 2, 78, "«después de la Física»", T, 46, T["acento"], fam="Corm", peso=700)
    s += tx((ini_meta + x) / 2, 116, "catorce libros sin título común", T, 26, T["suave"])
    s += flecha(fin_fis + 4, 250, ini_meta - 8, 250, T["tinta"], 4)
    s += tx(1100, 410, "Aristóteles la llamaba «filosofía primera»", T, 28, T["tinta"], anc="end")
    return s

def f_reloj_parado(T):
    cx, cy, r = 260, 218, 185
    s = f"<circle cx='{cx}' cy='{cy}' r='{r}' fill='{T['panel']}' stroke='{T['tinta']}' stroke-width='8'/>"
    for i in range(12):
        a = math.radians(i * 30); r0 = r - (30 if i % 3 == 0 else 18)
        s += linea(cx + r0 * math.sin(a), cy - r0 * math.cos(a), cx + (r - 8) * math.sin(a), cy - (r - 8) * math.cos(a), T["tinta"], 6 if i % 3 == 0 else 3)
    s += linea(cx, cy, cx, cy - 140, T["tinta"], 7) + linea(cx, cy, cx + 95, cy, T["acento"], 10)
    s += f"<circle cx='{cx}' cy='{cy}' r='12' fill='{T['acento']}'/>"
    s += tx(cx, cy + 96, "parado desde ayer", T, 26, CORAL, peso=600)
    filas = ["Crees que son las tres", "Es verdad: son las tres", "Tienes buenas razones"]
    for i, t in enumerate(filas):
        y = 78 + i * 76
        s += visto(560, y, VERDE if False else "#7fd49a", 1.1) + tx(600, y + 12, t, T, 38, anc="start")
    s += tx(545, 370, "¿Lo sabías?", T, 84, T["acento"], anc="start", fam="Corm", peso=700)
    return s

def f_silogismo(T):
    s = ""
    for i, t in enumerate(["Todos los griegos son humanos", "Todos los humanos son mortales"]):
        s += tx(30, 110 + i * 70, t, T, 38, anc="start")
    s += linea(30, 220, 590, 220, T["acento"], 4)
    s += tx(30, 290, "Todos los griegos son mortales", T, 38, T["acento"], anc="start", peso=600)
    s += tx(30, 380, "Si todo A es B y todo B es C, todo A es C", T, 28, T["suave"], anc="start")
    cx, cy = 900, 220
    s += f"<circle cx='{cx}' cy='{cy}' r='205' fill='{T['panel']}' stroke='{T['linea']}' stroke-width='4'/>"
    s += tx(cx, cy - 150, "mortales", T, 30)
    s += f"<circle cx='{cx}' cy='{cy + 40}' r='135' fill='{T['panel']}' stroke='{AZUL}' stroke-width='4'/>"
    s += tx(cx, cy - 52, "humanos", T, 30, AZUL)
    s += f"<circle cx='{cx}' cy='{cy + 85}' r='70' fill='#8a6a2c' stroke='{T['acento']}' stroke-width='4'/>"
    s += tx(cx, cy + 95, "griegos", T, 28, T["tinta"], peso=600)
    return s

def f_pisos(T):
    s = f"<path d='M40 62 L290 6 L540 62 Z' fill='{T['panel']}' stroke='{T['linea']}' stroke-width='4' stroke-linejoin='round'/>"
    filas = [("Metaética", "¿Qué significa «bueno»? ¿Hay verdades morales?"), ("Ética normativa", "¿Qué hace que una acción sea correcta?"),
             ("Ética aplicada", "¿Qué hacemos en este caso concreto?")]
    for i, (t, q) in enumerate(filas):
        y = 62 + i * 122
        s += caja(60, y, 460, 122, T, borde=T["acento"] if i == 1 else T["linea"], rx=0)
        s += tx(290, y + 76, t, T, 52, T["acento"] if i == 1 else T["tinta"], fam="Corm", peso=700)
        s += linea(520, y + 61, 580, y + 61, T["suave"], 3, .7)
        pal = q.split(" "); corte = len(pal) // 2 if len(q) > 36 else len(pal)
        l1, l2 = " ".join(pal[:corte]), " ".join(pal[corte:])
        if l2:
            s += tx(600, y + 52, l1, T, 30, anc="start") + tx(600, y + 90, l2, T, 30, anc="start")
        else:
            s += tx(600, y + 72, l1, T, 30, anc="start")
    return s

def pct(v):
    return f"{v} %"

def f_empate(T):
    datos = [("Virtudes", 37, T["acento"]), ("Deberes", 32, AZUL), ("Consecuencias", 31, T["tinta"])]
    s = barras(T, datos, 150, 50, 860, 300, 46, fmt=pct, ancho=190)
    return s

def f_filosofias_de(T):
    cx, cy = 580, 222; s = ""
    s += f"<ellipse cx='{cx}' cy='{cy}' rx='170' ry='70' fill='{T['panel']}' stroke='{T['acento']}' stroke-width='4'/>"
    s += tx(cx, cy + 16, "Filosofía de…", T, 50, T["acento"], fam="Corm", peso=700)
    act = [("la mente", -150), ("el lenguaje", -90), ("la ciencia", -30), ("la religión", 30), ("el derecho", 90), ("la historia", 150), ("las matemáticas", 180), ("la técnica", 0)]
    for t, ang in act:
        a = math.radians(ang); x = cx + 420 * math.cos(a); y = cy + 178 * math.sin(a)
        s += linea(cx + 175 * math.cos(a), cy + 74 * math.sin(a), x - (x - cx) * .3, y - (y - cy) * .22, T["linea"], 3, .6)
        s += pildora(x, y, t, T, 30)
    return s

def f_taxonomia(T):
    s = caja(10, 180, 190, 80, T, borde=T["acento"])
    s += tx(105, 232, "Filosofía", T, 40, T["acento"], fam="Corm", peso=700)
    areas = ["Metafísica y epistemología", "Teoría del valor", "Ciencia, lógica y matemáticas", "Historia de la filosofía occidental", "Tradiciones filosóficas"]
    r = random.Random(5)
    for i, t in enumerate(areas):
        y = 44 + i * 88
        s += linea(200, 220, 250, y, T["linea"], 3, .7)
        s += caja(250, y - 34, 480, 68, T, rx=14)
        s += tx(270, y + 10, t, T, 28, anc="start", peso=500)
        for j in range(3):
            y2 = y - 26 + j * 26
            s += linea(730, y, 790, y2, T["suave"], 2, .7) + f"<circle cx='{794}' cy='{y2}' r='5' fill='{T['suave']}'/>"
            for k in range(3):
                y3 = y2 - 8 + k * 8
                s += linea(799, y2, 850, y3, T["suave"], 1.2, .6) + f"<circle cx='{853}' cy='{y3}' r='2.5' fill='{T['acento']}' opacity='.9'/>"
    s += tx(1010, 210, "5.647", T, 96, T["acento"], fam="Corm", peso=700)
    s += tx(1010, 252, "categorías", T, 32)
    s += tx(1010, 290, "(finales de 2020)", T, 24, T["suave"])
    return s

def f_cruce(T):
    cx, cy = 580, 215; s = ""
    nodos = [(215, 70, "Filosofía de la mente", "¿Qué es pensar?"), (945, 70, "Filosofía del lenguaje", "¿Qué es entender?"),
             (215, 362, "Ética", "¿Qué le debemos?"), (945, 362, "Filosofía política", "¿Quién decide sus valores?")]
    for x, y, t, q in nodos:
        s += linea(cx, cy, x, y, CORAL, 4, .9, dash="12 10")
    for x, y, t, q in nodos:
        s += caja(x - 205, y - 62, 410, 124, T, fondo="#0a0e22")
        s += tx(x, y - 10, t, T, 38, T["tinta"], fam="Corm", peso=700)
        s += tx(x, y + 34, q, T, 28, T["suave"])
    s += f"<ellipse cx='{cx}' cy='{cy}' rx='190' ry='78' fill='{T['c2']}' stroke='{T['acento']}' stroke-width='5'/>"
    s += tx(cx, cy - 4, "¿Puede pensar", T, 44, T["acento"], fam="Corm", peso=700)
    s += tx(cx, cy + 40, "una máquina?", T, 44, T["acento"], fam="Corm", peso=700)
    return s

def f_fines(T):
    datos = [("Comprender", 56, T["acento"]), ("Verdad y conocimiento", 42, None), ("Sabiduría", 31, None), ("Bondad y justicia", 23, None), ("Felicidad", 13, None)]
    s = ""
    for i, (t, v, c) in enumerate(datos):
        y = 26 + i * 82
        s += tx(390, y + 40, t, T, 32, T["tinta"], anc="end", peso=600 if c else 500)
        s += f"<rect x='410' y='{y}' width='{v * 10.6:.0f}' height='56' rx='8' fill='{c or AZUL}'/>"
        s += tx(410 + v * 10.6 + 18, y + 40, f"{v} %", T, 34, T["tinta"], anc="start", peso=600)
    return s

def f_progreso(T):
    datos = [("Ninguno", 4, T["suave"]), ("Un poco", 47, AZUL), ("Mucho", 42, T["acento"])]
    return barras(T, datos, 150, 50, 860, 300, 56, fmt=pct, ancho=190)

FIGURAS_FI02 = {"frontera": f_frontera, "huevo": f_huevo, "huerto": f_huerto, "aristoteles": f_aristoteles, "arbol": f_arbol,
                "enciclopedia": f_enciclopedia, "wolff": f_wolff, "kant": f_kant, "kant_fin": f_kant_fin, "mapa": f_mapa,
                "estanteria": f_estanteria, "reloj_parado": f_reloj_parado, "silogismo": f_silogismo, "pisos": f_pisos, "empate": f_empate,
                "filosofias_de": f_filosofias_de, "taxonomia": f_taxonomia, "cruce": f_cruce, "fines": f_fines, "progreso": f_progreso}
for _k in ("meta", "epis", "logi", "etic", "poli", "este"):
    FIGURAS_FI02["mapa_" + _k] = (lambda k: (lambda T: _mapa(T, k)))(_k)

FIGURAS = {"movil": f_movil, "neurona_bio": f_neurona_bio, "disparo": f_disparo, "mcp": f_mcp, "perceptron": f_perceptron,
           "suma": f_suma, "mark1": f_mark1, "recta": f_recta, "xor": f_xor, "capas": f_capas, "culpa": f_culpa,
           "sigmoide": f_sigmoide, "montana": f_montana, "retro": f_retro, "digito": f_digito, "rasgos": f_rasgos,
           "lobos_bar": f_lobos_bar, "wapities_bar": f_wapities_bar, "cadena": f_cadena, "miedo": f_miedo, "castores": f_castores,
           "carrona": f_carrona, "reloj": f_reloj, "altos": f_altos, "parcelas": f_parcelas, "cauce": f_cauce, "estados": f_estados,
           "actores": f_actores, "circular": f_circular, "mollie": f_mollie}
FIGURAS.update(FIGURAS_FI02)

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
