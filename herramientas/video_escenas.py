# Herramienta del piloto fi0-1 (Temporada 0 de filosofía), guardada como referencia y punto de partida.
# Rutas a ajustar: FONTS (fuentes @fontsource instaladas con npm), MAPA (mapa_base.png creado con global-land-mask).
# Uso: python3 video_escenas.py escenas.json carpeta_imagenes [ids...]
"""Dibuja un JPEG 1280x720 por escena a partir de escenas.json."""
import json, sys, os, random, base64, asyncio, html
from playwright.async_api import async_playwright

ESC = sys.argv[1]          # escenas.json
OUT = sys.argv[2]          # carpeta de salida
ONLY = sys.argv[3:]        # ids opcionales
FONTS = "/home/claude/video/fonts/node_modules/@fontsource"
MAPA = "/home/claude/video/mapa_base.png"
W, H = 1280, 720

GOLD, CREAM, MUTED, TERRA, SEA, INK = "#e7c27d", "#f3ead8", "#aab2c8", "#d9825b", "#2b4a7a", "#0a0f22"

def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()

FONTFACE = ""
for fam, fname, w, st in [
    ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-500-normal.woff2", 500, "normal"),
    ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-600-normal.woff2", 600, "normal"),
    ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-700-normal.woff2", 700, "normal"),
    ("Corm", "cormorant-garamond/files/cormorant-garamond-latin-500-italic.woff2", 500, "italic"),
    ("Inter", "inter/files/inter-latin-400-normal.woff2", 400, "normal"),
    ("Inter", "inter/files/inter-latin-500-normal.woff2", 500, "normal"),
    ("Inter", "inter/files/inter-latin-600-normal.woff2", 600, "normal")]:
    FONTFACE += f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b64(os.path.join(FONTS, fname))}) format('woff2');font-weight:{w};font-style:{st}}}\n"

def stars(n=220, seed=7, ymax=H, big=True):
    r = random.Random(seed); out = []
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, ymax)
        s = r.choice([0.6, 0.8, 1.0, 1.2, 1.6 if big else 1.0, 2.2 if big else 1.2])
        o = r.uniform(0.35, 1.0)
        out.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{s}' fill='#fff' opacity='{o:.2f}'/>")
    return "".join(out)

BG = f"""<defs><radialGradient id='bg' cx='50%' cy='35%' r='80%'><stop offset='0' stop-color='#16204a'/><stop offset='1' stop-color='#05070f'/></radialGradient>
<radialGradient id='glow' cx='50%' cy='50%' r='50%'><stop offset='0' stop-color='{GOLD}' stop-opacity='.55'/><stop offset='1' stop-color='{GOLD}' stop-opacity='0'/></radialGradient></defs>
<rect width='{W}' height='{H}' fill='url(#bg)'/>"""

def svg(body, extra_bg=True, nstars=220, seed=7):
    return f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>{BG if extra_bg else ''}{stars(nstars, seed) if nstars else ''}{body}</svg>"

def figure(x, y, s=1.0, color="#0b0f1e", look_up=False):
    """Silueta humana sencilla con túnica; (x,y) = pies."""
    hy = y - 150 * s
    head = f"<circle cx='{x + (6 * s if look_up else 0)}' cy='{hy}' r='{18 * s}' fill='{color}'/>"
    body = f"<path d='M{x - 30 * s},{y} L{x - 14 * s},{hy + 20 * s} Q{x},{hy + 12 * s} {x + 14 * s},{hy + 20 * s} L{x + 30 * s},{y} Z' fill='{color}'/>"
    return head + body

# ---------------- ilustraciones ----------------
def ilu_cielo_mileto():
    band = "<ellipse cx='700' cy='230' rx='760' ry='120' fill='#c9d4ff' opacity='.06' transform='rotate(-14 700 230)'/>"
    sea = f"<rect x='0' y='540' width='{W}' height='180' fill='#0b1633'/>" + "".join(
        f"<line x1='{x}' y1='{560 + (x * 7) % 120}' x2='{x + 60}' y2='{560 + (x * 7) % 120}' stroke='#3b5a8f' stroke-width='2' opacity='.5'/>" for x in range(40, 1280, 130))
    hill = "<path d='M0,560 Q300,470 620,540 T1280,520 L1280,720 L0,720 Z' fill='#070a16'/>"
    temple = "<g fill='#070a16'><polygon points='860,430 1010,385 1160,430'/><rect x='870' y='430' width='280' height='14'/>" + "".join(
        f"<rect x='{880 + i * 40}' y='444' width='14' height='96'/>" for i in range(7)) + "<rect x='860' y='540' width='300' height='14'/></g>"
    return svg(band + sea + hill + temple + figure(360, 548, 1.0, "#070a16", True), nstars=320, seed=3)

def ilu_tales_pozo():
    well = (f"<ellipse cx='560' cy='470' rx='150' ry='38' fill='#1c2440' stroke='{MUTED}' stroke-width='3'/>"
            "<path d='M410,470 L410,600 Q560,650 710,600 L710,470' fill='#262f52' stroke='#aab2c8' stroke-width='3'/>"
            + "".join(f"<path d='M{410 + i * 50},{500 + (i % 2) * 40} l50,0' stroke='#3c4870' stroke-width='3'/>" for i in range(6))
            + "<ellipse cx='560' cy='470' rx='128' ry='28' fill='#05070f'/>")
    legs = (f"<path d='M540,470 L515,360 L532,356 L560,462 Z' fill='{CREAM}'/>"
            f"<path d='M572,468 L610,368 L626,375 L594,470 Z' fill='{CREAM}'/>"
            f"<ellipse cx='520' cy='354' rx='16' ry='9' fill='{TERRA}'/><ellipse cx='620' cy='366' rx='16' ry='9' fill='{TERRA}'/>")
    woman = figure(930, 640, 1.05, "#c9a46a") + "<path d='M905,470 q15,-12 30,0' stroke='#05070f' stroke-width='4' fill='none'/>"
    laugh = "".join(f"<text x='{975 + i * 26}' y='{430 - i * 22}' fill='{GOLD}' font-family='Corm' font-size='{38 - i * 4}' font-style='italic'>ja</text>" for i in range(3))
    ground = f"<rect x='0' y='620' width='{W}' height='100' fill='#070a16'/>"
    return svg(ground + well + legs + woman + laugh, nstars=260, seed=11)

def ilu_prensas_olivo():
    trunk = "<path d='M330,640 Q350,520 320,430 Q360,470 380,430 Q370,540 400,640 Z' fill='#5a4632'/>"
    leaves = "".join(f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}' fill='#4f6b47' opacity='.95'/>" for cx, cy, rx, ry in
                     [(300, 380, 110, 70), (410, 360, 120, 80), (350, 300, 120, 70), (250, 330, 80, 55), (470, 420, 80, 50)])
    olives = "".join(f"<circle cx='{x}' cy='{y}' r='9' fill='#1f2a1a'/>" for x, y in [(280, 360), (330, 330), (420, 340), (450, 400), (370, 380), (240, 345), (395, 300)])
    press = (f"<ellipse cx='860' cy='600' rx='190' ry='48' fill='#3a3f57' stroke='{MUTED}' stroke-width='3'/>"
             f"<rect x='670' y='520' width='380' height='80' fill='#3a3f57'/><ellipse cx='860' cy='520' rx='190' ry='48' fill='#4a5070' stroke='{MUTED}' stroke-width='3'/>"
             f"<rect x='780' y='410' width='160' height='110' rx='14' fill='#6b7090' stroke='{MUTED}' stroke-width='3'/>"
             f"<rect x='850' y='300' width='20' height='120' fill='#8a6a45'/><rect x='700' y='300' width='320' height='18' rx='9' fill='#8a6a45'/>")
    coins = "".join(f"<ellipse cx='{1100 + (i % 2) * 18}' cy='{640 - i * 14}' rx='34' ry='10' fill='{GOLD}' stroke='#9b7a3c' stroke-width='2'/>" for i in range(6))
    ground = f"<rect x='0' y='640' width='{W}' height='80' fill='#070a16'/>"
    return svg(ground + trunk + leaves + olives + press + coins, nstars=90, seed=5)

def ilu_eclipse():
    corona = "<circle cx='640' cy='280' r='190' fill='url(#glow)'/>" + "".join(
        f"<line x1='640' y1='280' x2='{640 + 210 * __import__('math').cos(a / 12 * 6.283):.0f}' y2='{280 + 210 * __import__('math').sin(a / 12 * 6.283):.0f}' stroke='{GOLD}' stroke-width='2' opacity='.35'/>" for a in range(12))
    disk = "<circle cx='640' cy='280' r='112' fill='#020308' stroke='#fff3d0' stroke-width='3'/>"
    import math
    spears = ""
    for i in range(26):
        x = 60 + i * 47; h = 120 + (i * 37) % 60
        spears += f"<line x1='{x}' y1='720' x2='{x + 18}' y2='{720 - h - 40}' stroke='#05070f' stroke-width='5'/>"
        spears += f"<circle cx='{x + 4}' cy='{720 - h + 30}' r='16' fill='#05070f'/>"
    hills = "<path d='M0,640 Q320,560 640,620 T1280,600 L1280,720 L0,720 Z' fill='#0a0d18'/>"
    return svg(corona + disk + hills + spears, nstars=180, seed=13)

def ilu_agua_arje():
    ocean = "".join(f"<path d='M0,{430 + i * 40} Q160,{410 + i * 40} 320,{430 + i * 40} T640,{430 + i * 40} T960,{430 + i * 40} T1280,{430 + i * 40}' stroke='#4f7bc0' stroke-width='3' fill='none' opacity='{0.9 - i * 0.12}'/>" for i in range(7))
    disc = (f"<ellipse cx='640' cy='410' rx='300' ry='52' fill='#5a4b38' stroke='{GOLD}' stroke-width='3'/>"
            "<ellipse cx='640' cy='400' rx='300' ry='48' fill='#6f7f4f'/>")
    dome = f"<path d='M330,400 A310,300 0 0,1 950,400' fill='none' stroke='{GOLD}' stroke-width='2' stroke-dasharray='6 8' opacity='.7'/>"
    drop = f"<path d='M1080,150 C1080,150 1020,230 1020,270 A60,60 0 0,0 1140,270 C1140,230 1080,150 1080,150 Z' fill='#4f7bc0' stroke='{CREAM}' stroke-width='3'/>"
    return svg(ocean + dome + disc + drop, nstars=160, seed=17)

def ilu_homero_hesiodo():
    lyre = (f"<g transform='translate(330,160)' stroke='{GOLD}' stroke-width='10' fill='none' stroke-linecap='round'>"
            "<path d='M40,360 Q-20,200 60,40'/><path d='M260,360 Q320,200 240,40'/><line x1='60' y1='60' x2='240' y2='60'/>"
            "<path d='M40,360 Q150,420 260,360'/></g>"
            + "".join(f"<line x1='{420 + i * 30}' y1='225' x2='{420 + i * 30}' y2='520' stroke='{CREAM}' stroke-width='2'/>" for i in range(5)))
    scroll = (f"<rect x='770' y='220' width='260' height='330' fill='#e9dcc0'/>"
              f"<rect x='750' y='200' width='300' height='34' rx='17' fill='#cbb88f'/><rect x='750' y='536' width='300' height='34' rx='17' fill='#cbb88f'/>"
              + "".join(f"<line x1='800' y1='{270 + i * 32}' x2='{1000 - (i % 3) * 30}' y2='{270 + i * 32}' stroke='#6b5a3c' stroke-width='5' stroke-linecap='round'/>" for i in range(8)))
    return svg(lyre + scroll, nstars=120, seed=19)

def node(x, y, title, sym, color):
    return (f"<circle cx='{x}' cy='{y}' r='120' fill='#141b38' stroke='{color}' stroke-width='4'/>"
            f"<text x='{x}' y='{y + 22}' text-anchor='middle' font-family='Corm' font-size='92' fill='{color}'>{sym}</text>"
            f"<text x='{x}' y='{y + 175}' text-anchor='middle' font-family='Inter' font-weight='600' font-size='34' fill='{CREAM}'>{title}</text>")

def ilu_discusion():
    arrow = lambda x1, x2: (f"<path d='M{x1},300 Q{(x1 + x2) / 2},210 {x2},300' stroke='{GOLD}' stroke-width='3' fill='none' marker-end='url(#ah)'/>"
                            f"<text x='{(x1 + x2) / 2}' y='232' text-anchor='middle' font-family='Inter' font-size='28' fill='{GOLD}'>crítica</text>")
    defs = f"<defs><marker id='ah' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='8' markerHeight='8' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='{GOLD}'/></marker></defs>"
    return svg(defs + node(260, 380, "Tales: agua", "≈", "#6f9be0") + node(640, 380, "Anaximandro: ápeiron", "∞", GOLD)
               + node(1020, 380, "Anaxímenes: aire", "~", "#b9d0e8") + arrow(370, 525) + arrow(750, 905), nstars=100, seed=23)

def ilu_festival():
    cols = "".join(f"<rect x='{120 + i * 160}' y='180' width='34' height='380' fill='#1b2347'/>" for i in range(7)) + "<rect x='90' y='150' width='1100' height='36' fill='#1b2347'/>"
    floor = f"<rect x='0' y='560' width='{W}' height='160' fill='#0a0e1f'/>"
    p1 = figure(520, 600, 1.4, "#c9a46a") + figure(800, 600, 1.4, "#8fa6d6", False)
    labels = (f"<text x='520' y='660' text-anchor='middle' font-family='Inter' font-weight='600' font-size='32' fill='{CREAM}'>Pitágoras</text>"
              f"<text x='800' y='660' text-anchor='middle' font-family='Inter' font-weight='600' font-size='32' fill='{CREAM}'>Leonte</text>"
              f"<text x='660' y='330' text-anchor='middle' font-family='Corm' font-style='italic' font-size='54' fill='{GOLD}'>«Soy filósofo»</text>")
    return svg(cols + floor + p1 + labels, nstars=60, seed=29)

def ilu_entre():
    line = f"<line x1='180' y1='380' x2='1100' y2='380' stroke='{MUTED}' stroke-width='4'/>"
    ends = (f"<circle cx='180' cy='380' r='18' fill='{MUTED}'/><circle cx='1100' cy='380' r='18' fill='{GOLD}'/>"
            f"<text x='180' y='460' text-anchor='middle' font-family='Inter' font-weight='600' font-size='34' fill='{CREAM}'>Ignorancia</text>"
            f"<text x='180' y='500' text-anchor='middle' font-family='Inter' font-size='26' fill='{MUTED}'>no busca</text>"
            f"<text x='1080' y='460' text-anchor='middle' font-family='Inter' font-weight='600' font-size='34' fill='{CREAM}'>Sabiduría</text>"
            f"<text x='1080' y='500' text-anchor='middle' font-family='Inter' font-size='26' fill='{MUTED}'>los dioses: no buscan</text>")
    phil = (figure(640, 372, 0.9, TERRA) + f"<path d='M700,300 L820,300' stroke='{GOLD}' stroke-width='5' marker-end='url(#ah2)'/>"
            f"<text x='640' y='460' text-anchor='middle' font-family='Corm' font-weight='700' font-size='54' fill='{GOLD}'>El filósofo</text>"
            f"<text x='640' y='505' text-anchor='middle' font-family='Inter' font-size='26' fill='{MUTED}'>sabe que no sabe, y busca</text>")
    defs = f"<defs><marker id='ah2' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='6' markerHeight='6' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='{GOLD}'/></marker></defs>"
    return svg(defs + line + ends + phil, nstars=80, seed=31)

def ilu_asombro():
    arcs = "".join(f"<path d='M{640 - r},560 A{r},{r} 0 0,1 {640 + r},560' fill='none' stroke='{GOLD}' stroke-width='2' opacity='{0.7 - i * 0.12}'/>" for i, r in enumerate([150, 260, 370, 480, 590]))
    eye = (f"<path d='M520,560 Q640,470 760,560 Q640,650 520,560 Z' fill='{CREAM}'/><circle cx='640' cy='560' r='46' fill='{SEA}'/><circle cx='640' cy='560' r='20' fill='#05070f'/><circle cx='652' cy='548' r='7' fill='#fff'/>")
    objs = (f"<circle cx='470' cy='360' r='26' fill='#d8dbe8'/><circle cx='482' cy='352' r='24' fill='#11183a'/>"
            f"<circle cx='820' cy='250' r='38' fill='{GOLD}'/>" + "".join(f"<circle cx='{x}' cy='{y}' r='4' fill='#fff'/>" for x, y in [(300, 140), (980, 120), (640, 90), (1100, 260), (190, 300)]))
    labels = "".join(f"<text x='{x}' y='{y}' text-anchor='middle' font-family='Inter' font-size='26' fill='{MUTED}'>{t}</text>" for x, y, t in
                     [(470, 420, "la luna"), (820, 318, "el sol"), (640, 70, "los astros"), (1110, 610, "lo más grande"), (170, 610, "lo cercano")])
    return svg(arcs + eye + objs + labels, nstars=140, seed=37)

def ilu_arbol():
    trunk = f"<path d='M600,700 Q620,520 610,420 L670,420 Q660,520 680,700 Z' fill='#6b5236'/>"
    tx = f"<text x='640' y='640' text-anchor='middle' font-family='Corm' font-weight='700' font-size='44' fill='{CREAM}' transform='rotate(-90 640 600)'></text>"
    branches = [("Física", 200, 250), ("Astronomía", 400, 160), ("Matemáticas", 640, 130), ("Biología", 880, 160), ("Química", 1080, 250),
                ("Psicología", 260, 400), ("Lógica", 1020, 400)]
    out = ""
    for name, x, y in branches:
        out += f"<path d='M640,430 Q{(640 + x) / 2},{(430 + y) / 2 + 60} {x},{y + 30}' stroke='#6b5236' stroke-width='14' fill='none' stroke-linecap='round'/>"
    for name, x, y in branches:
        out += f"<ellipse cx='{x}' cy='{y + 20}' rx='{len(name) * 11 + 40}' ry='42' fill='#3f5b3b'/><text x='{x}' y='{y + 31}' text-anchor='middle' font-family='Inter' font-weight='600' font-size='28' fill='{CREAM}'>{name}</text>"
    root = f"<rect x='470' y='600' width='340' height='70' rx='35' fill='{GOLD}'/><text x='640' y='648' text-anchor='middle' font-family='Corm' font-weight='700' font-size='46' fill='#1a1406'>Filosofía</text>"
    return svg(trunk + out + root + tx, nstars=70, seed=41)

def ilu_fragmentos():
    import math
    r = random.Random(4); out = ""
    letters = ["ΑΡΧΗ", "ΥΔΩΡ", "ΑΠΕΙΡΟΝ", "ΛΟΓΟΣ", "ΦΥΣΙΣ", "ΚΟΣΜΟΣ"]
    pos = [(250, 260), (560, 200), (880, 250), (330, 500), (680, 470), (1000, 500)]
    for (x, y), t in zip(pos, letters):
        pts = []
        n = r.randint(5, 7)
        for k in range(n):
            a = k / n * 6.283 + r.uniform(-.3, .3); rad = r.uniform(85, 130)
            pts.append(f"{x + rad * math.cos(a):.0f},{y + rad * 0.75 * math.sin(a):.0f}")
        out += f"<polygon points='{' '.join(pts)}' fill='#b0643f' stroke='#e7a77a' stroke-width='3'/>"
        out += f"<text x='{x}' y='{y + 14}' text-anchor='middle' font-family='DejaVu Serif, serif' font-size='34' fill='#1a0f08' opacity='.8'>{t}</text>"
    return svg(out, nstars=60, seed=43)

def ilu_vesubio():
    plume = "".join(f"<circle cx='{640 + dx}' cy='{220 - dy}' r='{rr}' fill='#3a3540' opacity='.9'/>" for dx, dy, rr in
                    [(0, 0, 70), (-60, 40, 60), (60, 50, 70), (-20, 110, 80), (70, 130, 60), (-90, 120, 50), (10, 180, 70)])
    glow = f"<ellipse cx='640' cy='300' rx='90' ry='30' fill='{TERRA}' opacity='.8'/>"
    volcano = "<path d='M240,600 L570,300 L710,300 L1040,600 Z' fill='#2a2230'/>"
    flows = f"<path d='M600,310 Q560,420 480,520' stroke='{TERRA}' stroke-width='10' fill='none' opacity='.8'/><path d='M680,310 Q720,430 800,540' stroke='{TERRA}' stroke-width='8' fill='none' opacity='.7'/>"
    villa = "<g fill='#c9b48a'><rect x='880' y='560' width='200' height='60'/><polygon points='870,560 980,525 1090,560'/></g>" + "".join(f"<rect x='{895 + i * 36}' y='575' width='12' height='45' fill='#7a6a50'/>" for i in range(5))
    sea = f"<rect x='0' y='620' width='{W}' height='100' fill='#0b1633'/>"
    return svg(volcano + glow + flows + plume + villa + sea, nstars=90, seed=47)

def ilu_papiro():
    scroll = ("<rect x='340' y='300' width='420' height='150' rx='75' fill='#1a1412'/>"
              "<ellipse cx='340' cy='375' rx='40' ry='75' fill='#0d0a09' stroke='#3b302a' stroke-width='3'/>"
              + "".join(f"<ellipse cx='340' cy='375' rx='{40 - i * 7}' ry='{75 - i * 13}' fill='none' stroke='#3b302a' stroke-width='2'/>" for i in range(1, 5)))
    beams = "".join(f"<line x1='{420 + i * 60}' y1='220' x2='{420 + i * 60}' y2='520' stroke='#5ad1ff' stroke-width='2' opacity='.45'/>" for i in range(6))
    sheet = (f"<rect x='830' y='230' width='340' height='290' fill='#e9dcc0' opacity='.95'/>"
             f"<text x='1000' y='300' text-anchor='middle' font-family='DejaVu Serif, serif' font-size='30' fill='#2a1d0e'>ΦΙΛΟΔΗΜΟΥ</text>"
             f"<text x='1000' y='345' text-anchor='middle' font-family='DejaVu Serif, serif' font-size='30' fill='#2a1d0e'>ΠΛΑΤΩΝ</text>"
             + "".join(f"<line x1='860' y1='{385 + i * 26}' x2='{1140 - (i % 3) * 40}' y2='{385 + i * 26}' stroke='#6b5a3c' stroke-width='4' stroke-linecap='round'/>" for i in range(5)))
    arrow = f"<path d='M770,375 L815,375' stroke='{GOLD}' stroke-width='5'/><path d='M815,362 L835,375 L815,388 Z' fill='{GOLD}'/>"
    return svg(beams + scroll + arrow + sheet, nstars=70, seed=53)

def ilu_cielo_final():
    band = "".join(f"<ellipse cx='640' cy='260' rx='{820 - i * 120}' ry='{140 - i * 22}' fill='#c9d4ff' opacity='.05' transform='rotate(-20 640 260)'/>" for i in range(5))
    hill = "<path d='M0,600 Q400,520 760,580 T1280,560 L1280,720 L0,720 Z' fill='#05070f'/>"
    return svg(band + hill + figure(820, 592, 0.8, "#05070f", True), nstars=480, seed=59)

ILU = {k[4:]: v for k, v in globals().items() if k.startswith("ilu_")}

# ---------------- plantillas HTML ----------------
CSS = f"""{FONTFACE}
*{{margin:0;padding:0;box-sizing:border-box;font-variant-numeric:lining-nums}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:#05070f;color:{CREAM};font-family:Inter,sans-serif}}
.bg{{position:absolute;inset:0}}
.wrap{{position:absolute;inset:60px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}}
.big{{font-family:Corm;font-weight:600;font-size:76px;line-height:1.08;color:{CREAM};max-width:1080px}}
.sub{{font-size:32px;color:{GOLD};margin-top:26px;max-width:1000px;line-height:1.3}}
.rule{{width:120px;height:2px;background:{GOLD};margin:30px auto 0;opacity:.8}}
.cap.top{{top:52px;bottom:auto}}
.cap{{position:absolute;left:60px;bottom:52px;padding:12px 22px;border-radius:12px;background:rgba(5,7,15,.72);font-size:30px;color:{CREAM};border-left:4px solid {GOLD}}}
.q{{font-family:Corm;font-style:italic;font-weight:500;font-size:64px;line-height:1.15;max-width:1060px}}
.qm{{font-family:Corm;font-size:180px;color:{GOLD};line-height:.6;height:70px}}
.att{{font-size:30px;color:{MUTED};margin-top:30px}}
.cols{{display:flex;gap:60px;width:100%}}
.col{{flex:1;background:rgba(20,27,56,.75);border-radius:20px;padding:34px 36px;text-align:left;border-top:5px solid {GOLD}}}
.col h2{{font-family:Corm;font-size:72px;font-weight:700;color:{GOLD};margin-bottom:14px}}
.col p{{font-size:34px;line-height:1.55;color:{CREAM}}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;width:100%}}
.cell{{background:rgba(20,27,56,.8);border-radius:18px;padding:30px 24px;border-top:4px solid {GOLD}}}
.cell .n{{font-family:Corm;font-weight:700;font-size:48px;color:{CREAM};line-height:1.1}}
.cell .m{{font-size:26px;color:{GOLD};margin-top:12px}}
.h{{font-family:Corm;font-weight:700;font-size:58px;color:{CREAM};margin-bottom:34px}}
ol.list{{list-style:none;text-align:left;width:900px}}
ol.list li{{font-size:38px;padding:14px 0;border-bottom:1px solid rgba(231,194,125,.25);display:flex;gap:26px}}
ol.list li span{{font-family:Corm;font-weight:700;color:{GOLD};font-size:40px;width:40px}}
"""

def bg_svg(nstars=200, seed=7):
    return f"<div class='bg'>{svg('', nstars=nstars, seed=seed)}</div>"

def page(inner):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{inner}</body></html>"

def esc(t): return html.escape(t)

def render_scene(sc):
    t, p = sc["tipo"], sc["params"]
    if t == "titulo":
        return page(bg_svg(320, 2) + f"<div class='wrap'><div class='big' style='font-size:104px'>{esc(p['t'])}</div><div class='rule'></div><div class='sub'>{esc(p['s'])}</div></div>")
    if t == "rotulo":
        sub = f"<div class='sub'>{esc(p['s'])}</div>" if p.get("s") else ""
        return page(bg_svg(160, hash(sc['id']) % 97) + f"<div class='wrap'><div class='big'>{esc(p['t'])}</div><div class='rule'></div>{sub}</div>")
    if t == "cita":
        return page(bg_svg(140, 5) + f"<div class='wrap'><div class='qm'>“</div><div class='q'>{esc(p['q'])}</div><div class='att'>{esc(p['a'])}</div></div>")
    if t == "ilu":
        cap = f"<div class='cap{' top' if p['svg'] in ('festival', 'arbol', 'entre') else ''}'>{esc(p['cap'])}</div>" if p.get("cap") else ""
        return page(f"<div class='bg'>{ILU[p['svg']]()}</div>{cap}")
    if t == "comparar":
        L, R = p["izq"], p["der"]
        col = lambda a: f"<div class='col'><h2>{esc(a[0])}</h2>" + "".join(f"<p>· {esc(x)}</p>" for x in a[1:]) + "</div>"
        return page(bg_svg(90, 61) + f"<div class='wrap'><div class='cols'>{col(L)}{col(R)}</div></div>")
    if t == "festival3":
        cells = [("Los atletas", "buscan la gloria"), ("Los comerciantes", "buscan la ganancia"), ("Los espectadores", "quieren mirar y entender")]
        icons = [f"<svg viewBox='0 0 100 100' width='120' height='120'><path d='M20,60 Q10,30 30,15 M80,60 Q90,30 70,15' stroke='{GOLD}' stroke-width='6' fill='none'/>" + "".join(f"<ellipse cx='{22 + i * 3}' cy='{52 - i * 9}' rx='7' ry='4' fill='{GOLD}' transform='rotate(-40 {22 + i * 3} {52 - i * 9})'/><ellipse cx='{78 - i * 3}' cy='{52 - i * 9}' rx='7' ry='4' fill='{GOLD}' transform='rotate(40 {78 - i * 3} {52 - i * 9})'/>" for i in range(4)) + "</svg>",
                 f"<svg viewBox='0 0 100 100' width='120' height='120'>" + "".join(f"<ellipse cx='50' cy='{78 - i * 12}' rx='30' ry='9' fill='{GOLD}' stroke='#9b7a3c' stroke-width='2'/>" for i in range(5)) + "</svg>",
                 f"<svg viewBox='0 0 100 100' width='120' height='120'><path d='M8,50 Q50,10 92,50 Q50,90 8,50 Z' fill='{CREAM}'/><circle cx='50' cy='50' r='17' fill='{SEA}'/><circle cx='50' cy='50' r='8' fill='#05070f'/></svg>"]
        html_cells = "".join(f"<div class='cell' style='padding:36px 20px{';border-top-color:#fff' if i == 2 else ''}'>{icons[i]}<div class='n' style='margin-top:16px'>{esc(a)}</div><div class='m'>{esc(b)}</div></div>" for i, (a, b) in enumerate(cells))
        return page(bg_svg(100, 67) + f"<div class='wrap'><div class='h'>La vida es como los Juegos</div><div class='grid'>{html_cells}</div></div>")
    if t == "preguntas":
        ramas = ["Metafísica", "Teoría del conocimiento", "Lógica", "Ética", "Política", "Estética"]
        cells = "".join(f"<div class='cell'><div class='n'>{esc(q)}</div><div class='m'>{esc(r)}</div></div>" for q, r in zip(p["items"], ramas))
        return page(bg_svg(90, 71) + f"<div class='wrap'><div class='h'>Las grandes preguntas</div><div class='grid'>{cells}</div></div>")
    if t == "proximos":
        lis = "".join(f"<li><span>{i + 2}</span>{esc(x)}</li>" for i, x in enumerate(p["items"]))
        return page(bg_svg(160, 73) + f"<div class='wrap'><div class='h'>Próximamente en la Temporada 0</div><ol class='list'>{lis}</ol></div>")
    if t == "tiempo":
        marks = [("585 a. C.", "Eclipse de Tales"), ("399 a. C.", "Muerte de Sócrates"), ("hacia 387 a. C.", "Platón funda la Academia"),
                 ("79 d. C.", "El Vesubio sepulta Herculano"), ("1752", "Aparecen los papiros"), ("2024", "La tumba de Platón"), ("2026", "Nuevos títulos y autores")]
        n = len(marks); x0, x1 = 110, 1170
        body = f"<line x1='{x0}' y1='380' x2='{x1}' y2='380' stroke='{GOLD}' stroke-width='3'/>"
        for i, (y, l) in enumerate(marks):
            x = x0 + i * (x1 - x0) / (n - 1); up = i % 2 == 0
            col = GOLD if i == n - 1 else CREAM
            body += f"<circle cx='{x:.0f}' cy='380' r='{14 if i == n - 1 else 9}' fill='{col}'/>"
            ty = 300 if up else 470
            body += f"<line x1='{x:.0f}' y1='380' x2='{x:.0f}' y2='{(ty + 22) if up else (ty - 48)}' stroke='{MUTED}' stroke-width='1.5' opacity='.6'/>"
            body += f"<text x='{x:.0f}' y='{ty - 34 if up else ty}' text-anchor='middle' font-family='Corm' font-weight='700' font-size='38' fill='{col}'>{esc(y)}</text>"
            words = l.split(" "); half = (len(words) + 1) // 2
            for j, line in enumerate([" ".join(words[:half]), " ".join(words[half:])]):
                body += f"<text x='{x:.0f}' y='{(ty + 4 if up else ty + 40) + j * 30}' text-anchor='middle' font-family='Inter' font-size='25' fill='{MUTED}'>{esc(line)}</text>"
        body += f"<text x='640' y='120' text-anchor='middle' font-family='Corm' font-weight='700' font-size='56' fill='{CREAM}'>Una historia que se sigue escribiendo</text>"
        body += f"<text x='640' y='660' text-anchor='middle' font-family='Inter' font-size='24' fill='{MUTED}'>Fechas sin escala</text>"
        return page(f"<div class='bg'>{svg(body, nstars=120, seed=79)}</div>")
    if t == "mapa":
        lon0, lon1, lat0, lat1 = 18.0, 47.0, 27.5, 41.0
        C = {"Mileto": (37.53, 27.28), "Samos": (37.75, 26.98), "Quíos": (38.37, 26.14), "Éfeso": (37.94, 27.34), "Sardes": (38.49, 28.04),
             "Atenas": (37.98, 23.73), "Babilonia": (32.54, 44.42), "Menfis": (29.85, 31.25)}
        off = {"Mileto": (14, 40, "start"), "Samos": (-14, 34, "end"), "Quíos": (-14, -6, "end"), "Éfeso": (14, -2, "start"), "Sardes": (14, -14, "start"),
               "Atenas": (-14, -10, "end"), "Babilonia": (-14, -16, "end"), "Menfis": (14, 10, "start")}
        body = f"<image href='data:image/png;base64,{b64(MAPA)}' x='0' y='0' width='{W}' height='{H}'/>"
        for name in p["puntos"]:
            la, lo = C[name]; x = (lo - lon0) / (lon1 - lon0) * W; y = (lat1 - la) / (lat1 - lat0) * H
            main = name == "Mileto"
            dx, dy, anc = off[name]
            body += f"<circle cx='{x:.0f}' cy='{y:.0f}' r='{12 if main else 7}' fill='{GOLD if main else CREAM}' stroke='#05070f' stroke-width='2'/>"
            body += f"<text x='{x + dx:.0f}' y='{y + dy:.0f}' text-anchor='{anc}' font-family='Inter' font-weight='600' font-size='{40 if main else 28}' fill='{GOLD if main else CREAM}' stroke='#05070f' stroke-width='5' paint-order='stroke'>{esc(name)}</text>"
        body += f"<text x='60' y='640' font-family='Corm' font-weight='700' font-size='54' fill='{CREAM}' stroke='#05070f' stroke-width='6' paint-order='stroke'>{esc(p['titulo'])}</text>"
        body += f"<text x='60' y='690' font-family='Inter' font-size='22' fill='{MUTED}'>Costas actuales; el antiguo puerto de Mileto quedó tierra adentro por los sedimentos del río Meandro</text>"
        return page(f"<div class='bg'><svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>{body}</svg></div>")
    raise ValueError(t)

async def main():
    scenes = json.load(open(ESC)); os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": W, "height": H})
        for sc in scenes:
            if ONLY and sc["id"] not in ONLY: continue
            await pg.set_content(render_scene(sc)); await pg.wait_for_timeout(150)
            await pg.screenshot(path=os.path.join(OUT, sc["id"] + ".jpg"), type="jpeg", quality=92)
            print(sc["id"], flush=True)
        await b.close()
asyncio.run(main())
