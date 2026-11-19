"""Genera los SVG animados del README (escritorio en el espacio, títulos y tarjetas).

Uso:   python tools/generate_assets.py
Salida: assets/david-perfil.svg, assets/sobre-mi-tarjeta.svg, assets/*.svg
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

PX = 4            # tamaño de cada "pixel"
W, H = 160, 60    # grid -> 640 x 240
BG = "#0b0f1a"
STAR_COLORS = ["#ffffff", "#e6edf3", "#c9d1d9", "#ffffff"]
FLOOR = 50        # fila donde empieza el suelo

WHITE, WHITE_SH = "#e6edf3", "#30363d"
GREEN, GREEN_SH = "#3fb950", "#0f4d1f"
CYAN, CYAN_SH   = "#00a8e8", "#004b6e"
BLUE, BLUE_SH   = "#58a6ff", "#1f6feb"


def r(x, y, w=1, h=1, fill="#fff", extra=""):
    return (f'<rect x="{x*PX}" y="{y*PX}" width="{w*PX}" height="{h*PX}" '
            f'fill="{fill}" shape-rendering="crispEdges"{extra}/>')


def sprite(rows, palette, ox, oy):
    """Dibuja un sprite desde ASCII; los caracteres sin color son transparentes."""
    out = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in palette:
                out.append(r(ox + x, oy + y, 1, 1, palette[ch]))
    return "".join(out)


def drift(content, dx, dy, dur, begin=0, back=False, key_times=None):
    """Mueve un grupo de (0,0) a (dx,dy) en bucle; back=True vuelve al origen."""
    values = f"0 0;{dx} {dy}" + (";0 0" if back else "")
    kt = f' keyTimes="{key_times}"' if key_times else ""
    if key_times:
        values = f"0 0;0 0;{dx} {dy}"
    return (f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="{values}"{kt} dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'{content}</g>')


def star_layer(n, seed, size, colors, dur):
    """Capa de estrellas que se desplaza a la izquierda en bucle sin cortes."""
    rnd = random.Random(seed)
    stars = [(rnd.randint(0, W - 1), rnd.randint(0, FLOOR - 3), rnd.choice(colors)) for _ in range(n)]
    items = [r(x + off, y, size, size, c) for off in (0, W) for x, y, c in stars]
    return drift("".join(items), -W * PX, 0, dur)


def rocket(y, scale, dur, begin, body="#00a8e8", fin="#0077b6", shade="#023e8a", window="#ffffff"):
    """Cohete que sube en diagonal de izquierda a derecha, con estela."""
    p = [
        r(3, 1, 8, 1, body), r(1, 2, 11, 1, body), r(3, 3, 8, 1, shade),
        r(0, 2, 2, 1, fin), r(8, 0, 3, 1, fin), r(8, 4, 3, 1, fin),
        r(6, 2, 2, 1, window),
        r(12, 2, 5, 1, "#f0883e",
          '><animate attributeName="opacity" values="1;0.3;1" dur="0.2s" repeatCount="indefinite"/></rect><rect width="0" height="0"'),
        r(12, 1, 2, 1, "#f2cc3c"), r(12, 3, 2, 1, "#f2cc3c"),
        r(18, 2, 1, 1, "#8b949e", ' opacity="0.6"'), r(21, 2, 1, 1, "#8b949e", ' opacity="0.4"'),
        r(24, 2, 1, 1, "#8b949e", ' opacity="0.2"'),
    ]
    dx, dy = W + 42, -40
    angle = -math.degrees(math.atan2(-dy, dx))
    inner = (f'<g transform="rotate({angle:.1f} {-8.5*PX*scale} {2.5*PX*scale}) scale({-scale},{scale})">'
             + "".join(p) + "</g>")
    return (f'<g transform="translate({-2*PX},{y*PX})">'
            + drift(inner, dx * PX, dy * PX, dur, begin) + "</g>")


def asteroid(y, dur, begin, rows=None):
    rows = rows or [".GG.", "GGGG", "GDGG", ".GG."]
    s = sprite(rows, {"G": "#6e7681", "D": "#484f58"}, W + 2, y)
    return drift(s, -(W + 10) * PX, 4 * PX, dur, begin)


# --- fuente pixelada 5x7 completa ---------------------------------------------
FONT = {
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "B": ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
    "C": [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    "F": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "X...."],
    "G": [".XXXX", "X....", "X....", "X.XXX", "X...X", "X...X", ".XXXX"],
    "H": ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "I": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "XXXXX"],
    "J": ["..XXX", "....X", "....X", "....X", "....X", "X...X", ".XXX."],
    "K": ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "M": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X", "X...X", "X...X"],
    "N": ["X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "Q": [".XXX.", "X...X", "X...X", "X...X", "X.X.X", "X..X.", ".XX.X"],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "V": ["X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."],
    "W": ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    "X": ["X...X", "X...X", ".X.X.", "..X..", ".X.X.", "X...X", "X...X"],
    "Y": ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    "Z": ["XXXXX", "....X", "...X.", "..X..", ".X...", "X....", "XXXXX"],
    ">": ["X....", ".X...", "..X..", "...X.", "..X..", ".X...", "X...."],
    ",": [".....", ".....", ".....", ".....", "..X..", "..X..", ".X..."],
    ".": [".....", ".....", ".....", ".....", ".....", "..X..", "..X.."],
    "-": [".....", ".....", ".....", "XXXXX", ".....", ".....", "....."],
    "&": [".XX..", "X..X.", ".XX..", ".X.X.", "X..X.", "X..X.", ".XX.X"],
    "|": ["..X..", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "/": ["....X", "...X.", "..X..", ".X...", "X....", ".....", "....."],
}


def pixel_text(runs, x, y, dur=14):
    """Texto pixelado por tramos [(texto, color, sombra)], se escribe letra por letra."""
    out, cx, n = [], x, 0
    for text, color, shadow in runs:
        for ch in text:
            if ch == " ":
                cx += 4
                continue
            glyph = FONT.get(ch, FONT["."])
            cells = [(gx_, gy) for gy, row in enumerate(glyph) for gx_, c in enumerate(row) if c == "X"]
            pix = "".join(r(cx + gx_ + 1, y + gy + 1, 1, 1, shadow) for gx_, gy in cells)
            pix += "".join(r(cx + gx_, y + gy, 1, 1, color) for gx_, gy in cells)
            t = 0.03 + n * 0.03
            out.append(
                f'<g opacity="0"><animate attributeName="opacity" values="0;1;0;0" '
                f'keyTimes="0;{t:.3f};0.95;1" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>'
                f'{pix}</g>')
            cx += 6
            n += 1
    return "".join(out), cx, 0.03 + n * 0.03


def cursor_block(x, y, color, t_start, dur=14):
    """Cursor de bloque que aparece al terminar de escribir y parpadea."""
    return (
        f'<g opacity="0"><animate attributeName="opacity" values="0;1;0;0" '
        f'keyTimes="0;{t_start:.3f};0.95;1" calcMode="discrete" dur="{dur}s" repeatCount="indefinite"/>'
        + r(x, y, 4, 7, color,
            '><animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" '
            'repeatCount="indefinite"/></rect><rect width="0" height="0"')
        + "</g>")


# --- personaje: estilo David (pelo oscuro, lentes, buzo tech azul) ----------
DEV = [
    "...HHHHH...",
    "..HHHHHHH..",
    ".HHHHHHHHH.",
    ".HHHJHHHHH.",
    "..GLGSGLG..",
    "..SSSSSSS..",
    "..SSSMSSS..",
    "...SSSSS...",
    "....SSS....",
    "..PPPPPPP..",
    ".PPPPPPPPP.",
    ".PPPPPPPPP.",
    "..PPPPPPP..",
]
DEV_PAL = {
    "H": "#1b1f24",   # pelo oscuro
    "J": "#32383f",   # brillo pelo
    "S": "#f2cc9b",   # piel
    "G": "#111111",   # lentes marco
    "L": "#58a6ff",   # reflejo lente
    "M": "#c0504d",   # boca
    "P": "#0d3b66",   # buzo / hoodie tech
}

DEV_X = 46
DEV_Y = 31       # sentado: la cabeza queda a la altura de la pantalla
MOON = ["..WWW.", ".WWW..", "WWW...", "WWW...", "WWW...", ".WWW..", "..WWW."]
CORE_PULSE = [".BB.BB.", "BBBBBBB", "BBBBBBB", ".BBBBB.", "..BBB..", "...B..."]


def scene():
    runs = [
        ("> ", GREEN, GREEN_SH),
        ("HOLA, SOY DAVID ", WHITE, WHITE_SH),
        ("BRITTO", CYAN, CYAN_SH),
    ]
    start_x, start_y = 9, 5
    p = [f'<rect width="{W*PX}" height="{H*PX}" fill="{BG}"/>']

    # espacio: estrellas con parallax, parpadeos, luna, asteroides
    p.append(star_layer(26, 1, 1, ["#484f58", "#6e7681"], 60))
    p.append(star_layer(18, 2, 1, ["#8b949e", "#c9d1d9"], 30))
    p.append(star_layer(16, 3, 2, ["#ffffff", "#e6edf3"], 16))
    rnd = random.Random(11)
    for _ in range(30):
        x, y = rnd.randint(2, W - 3), rnd.randint(1, FLOOR - 6)
        p.append(
            f'<rect x="{x*PX}" y="{y*PX}" width="{PX}" height="{PX}" fill="{rnd.choice(STAR_COLORS)}" opacity="0.2">'
            f'<animate attributeName="opacity" values="0.1;1;0.1" dur="{rnd.choice([2, 2.5, 3, 3.5])}s" '
            f'begin="{round(rnd.uniform(0, 3), 1)}s" repeatCount="indefinite"/></rect>')
    p.append(sprite(MOON, {"W": "#e6edf3"}, 148, 18))
    p.append(asteroid(6, 20, -3))
    p.append(asteroid(24, 26, -14, ["..GG.", ".GGGG", "GGDGG", "GGGG.", ".GG.."]))

    # cohete que pasa
    p.append(rocket(22, 1, 9, -2))

    # saludo en pixel art con panel tipo terminal
    txt, end_x, t_end = pixel_text(runs, start_x, start_y)
    px0, py0 = start_x - 4, start_y - 3
    pw = end_x - start_x + 14
    p.append(r(px0, py0, pw, 13, "#0d1117", ' opacity="0.9"'))
    p.append(r(px0, py0, pw, 1, "#30363d"))
    p.append(r(px0, py0 + 12, pw, 1, "#30363d"))
    p.append(r(px0, py0, 1, 13, "#30363d"))
    p.append(r(px0 + pw - 1, py0, 1, 13, "#30363d"))
    p.append(txt)
    p.append(cursor_block(end_x, start_y, GREEN, t_end))

    # suelo (plataforma lunar / asteroide)
    p.append(r(0, FLOOR, W, H - FLOOR, "#161b22"))
    p.append(r(0, FLOOR, W, 1, "#30363d"))
    for x, y, w in [(8, 53, 4), (30, 56, 3), (96, 54, 5), (120, 57, 3), (145, 53, 4), (70, 57, 2)]:
        p.append(r(x, y, w, 1, "#21262d"))

    # silla y piernas
    gx = DEV_X
    p.append(r(gx - 3, 36, 2, 12, "#484f58"))            # respaldo
    p.append(r(gx + 1, 46, 11, 2, "#6e7681"))            # asiento
    p.append(r(gx + 5, 48, 2, 1, "#484f58"))             # pie
    p.append(r(gx + 1, 49, 11, 1, "#484f58"))            # base
    p.append(r(gx + 2, 44, 13, 2, "#1f2428"))            # cadera y muslos (pantalón oscuro)
    p.append(r(gx + 13, 46, 2, 3, "#1f2428"))            # pantorrilla
    p.append(r(gx + 13, 49, 4, 1, "#e6edf3"))            # zapatillas blancas

    # escritorio
    dx0, dx1, dy = 56, 112, 44
    p.append(r(dx0, dy, dx1 - dx0, 1, "#a06a42"))
    p.append(r(dx0, dy + 1, dx1 - dx0, 1, "#6e4a2e"))
    p.append(r(dx0 + 2, dy + 2, 2, FLOOR - dy - 2, "#6e4a2e"))
    p.append(r(dx1 - 4, dy + 2, 2, FLOOR - dy - 2, "#6e4a2e"))

    # laptop con código que se escribe (Python / TypeScript / AI)
    lx, ly = 71, 31
    p.append(r(lx - 2, ly - 2, 23, 16, "#00a8e8",
               ' opacity="0.05"><animate attributeName="opacity" values="0.03;0.08;0.03" dur="3s" '
               'repeatCount="indefinite"/></rect><rect width="0" height="0"'))   # brillo de la pantalla
    p.append(r(lx, ly, 19, 12, "#484f58"))
    p.append(r(lx + 1, ly + 1, 17, 10, "#0b1d33"))
    p.append(r(lx - 2, 43, 23, 1, "#8b949e"))
    p.append(r(lx + 7, 43, 5, 1, "#6e7681"))
    for i, (dy2, wl, col) in enumerate([(2, 8, "#3fb950"), (4, 12, "#00a8e8"),
                                        (6, 7, "#d2a8ff"), (8, 10, "#ffa657")]):
        ind = 1 if i in (1, 3) else 0
        p.append(
            f'<rect x="{(lx+2+ind)*PX}" y="{(ly+dy2)*PX+1}" height="{PX-2}" fill="{col}" width="0">'
            f'<animate attributeName="width" values="0;0;{wl*PX};{wl*PX};0" '
            f'keyTimes="0;{0.05+i*0.18:.2f};{0.18+i*0.18:.2f};0.93;1" dur="6s" repeatCount="indefinite"/></rect>')

    p.append(r(lx + 2, ly + 10, 1, 1, "#e6edf3",
               '><animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" '
               'repeatCount="indefinite"/></rect><rect width="0" height="0"'))   # cursor

    # planta sobre el escritorio
    p.append(r(104, 42, 4, 2, "#b5651d"))
    p.append(r(105, 39, 2, 3, "#3fb950"))
    p.append(r(103, 40, 2, 1, "#2ea043"))
    p.append(r(107, 40, 2, 1, "#2ea043"))

    # taza con café y vapor
    p.append(sprite(["MMMM.", "MMMMM", "MMMM.", "MMMM."], {"M": "#00a8e8"}, 98, 40))
    for i, sx in enumerate((98, 100)):
        p.append(
            f'<rect x="{sx*PX+2}" y="{38*PX}" width="{PX//2}" height="{PX}" fill="#8b949e" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.8;0" dur="2s" begin="{i*0.8}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -{PX*2}" '
            f'dur="2s" begin="{i*0.8}s" repeatCount="indefinite"/></rect>')

    # David
    p.append(sprite(DEV, DEV_PAL, DEV_X, DEV_Y))
    for ex in (3, 7):                                    # parpadeo cada 4 s
        p.append(
            f'<rect x="{(gx+ex)*PX}" y="{(DEV_Y+4)*PX}" width="{PX}" height="{PX}" fill="#111" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.9;0.93;0.97;1" '
            f'dur="4s" repeatCount="indefinite"/></rect>')
    
    # brazo y mano que teclea
    p.append(r(gx + 9, 39, 2, 4, "#0d3b66"))             # brazo superior
    p.append(r(gx + 9, 42, 11, 2, "#0d3b66"))            # antebrazo
    p.append(
        '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" '
        'dur="0.4s" repeatCount="indefinite"/>'
        + r(gx + 20, 42, 4, 2, "#f2cc9b") + "</g>")

    # pulso / core AI flotante (cyan brillante latiendo)
    p.append(drift(sprite(CORE_PULSE, {"B": "#00a8e8"}, 36, 24), 0, -6 * PX, 1.6, back=True))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W*PX} {H*PX}" '
            f'width="{W*PX}" height="{H*PX}" role="img" '
            f'aria-label="Hola, soy David Britto. AI Engineer &amp; MLOps Architect programando en el espacio con un cohete pasando">'
            + "".join(p) + "</svg>")


def universe(width, height, seed, uid):
    """Fondo de universo oscuro para tarjetas: estrellas pixeladas que parpadean."""
    rnd = random.Random(seed)
    parts = [
        '<defs>'
        f'<clipPath id="{uid}c"><rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="6"/></clipPath>'
        '</defs>',
        f'<g clip-path="url(#{uid}c)">',
        f'<rect width="{width}" height="{height}" fill="#0b0f1a"/>',
    ]
    for _ in range(int(width * height / 3200)):
        x, y = rnd.randint(4, width - 6), rnd.randint(4, height - 6)
        c = rnd.choice(["#484f58", "#6e7681", "#8b949e", "#e6edf3"])
        parts.append(f'<rect x="{x}" y="{y}" width="2" height="2" fill="{c}"/>')
    for _ in range(6):
        x, y = rnd.randint(10, width - 10), rnd.randint(6, height - 6)
        dur = rnd.choice([2, 3, 4])
        beg = rnd.choice([0, 0.5, 1, 1.5])
        parts.append(
            f'<rect x="{x}" y="{y}" width="2" height="2" fill="#00a8e8">'
            f'<animate attributeName="opacity" values="0.1;1;0.1" dur="{dur}s" begin="{beg}s" '
            f'repeatCount="indefinite"/></rect>')
    parts.append("</g>")
    parts.append(f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="6" fill="none" stroke="#30363d"/>')
    return "".join(parts)


def title_svg(text, unit=3, width=W * PX, height=44):
    """Título de sección: mini panel de terminal con prompt, texto pixelado y cursor."""
    def glyph(ch, x, y, color, shadow):
        if ch not in FONT:
            return ""
        cells = [(gx, gy) for gy, row in enumerate(FONT[ch]) for gx, c in enumerate(row) if c == "X"]
        box = lambda gx, gy, col, o=0: (f'<rect x="{x + gx*unit + o}" y="{y + gy*unit + o}" '
                                        f'width="{unit}" height="{unit}" fill="{col}"/>')
        return "".join(box(gx, gy, shadow, 2) for gx, gy in cells) + "".join(box(gx, gy, color) for gx, gy in cells)

    y = (height - 7 * unit) // 2
    x = 22
    parts = [universe(width, height, sum(map(ord, text)), "t" + str(abs(hash(text)) % 10000))]
    parts.append(glyph(">", x, y, GREEN, GREEN_SH))
    x += 10 * unit
    for ch in text:
        if ch == " ":
            x += 4 * unit
            continue
        parts.append(glyph(ch, x, y, WHITE, WHITE_SH))
        x += 6 * unit
    parts.append(
        f'<rect x="{x}" y="{y}" width="{4*unit}" height="{7*unit}" fill="{GREEN}">'
        f'<animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" '
        f'repeatCount="indefinite"/></rect>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
            f'height="{height}" role="img" aria-label="{text.title()}" shape-rendering="crispEdges">'
            + "".join(parts) + "</svg>")


def about_card(width=W * PX):
    """Tarjeta 'sobre mí' con aspecto de terminal UNIX."""
    lines = [
        ("whoami", "David Britto"),
        ("cat rol.txt", "Senior AI Engineer | MLOps &amp; AIOps Architect | Agent Systems"),
        ("cat arquitectura.txt", "Harnesses de agentes deterministas (AWS Strands SDK, Bedrock),"),
        (None, "evals continuas de LLMs y sistemas Cloud SRE de alto rendimiento."),
        ("cat frugal-ai.txt", "Werner Vogels Frugal Architect: edge deciders sub-115ms para"),
        (None, "eliminar el gasto excesivo de tokens y maximizar el ROI de negocio."),
        ("cat proyectos.txt", "SolariA · AI Agent Stack · Specly (SDD) · ResQ-Cloud"),
        ("cat disponibilidad.txt", "Open for Full-time &amp; High-Impact Contracts (Remote Worldwide)"),
        ("cat estado.txt", "Concepts &amp; Economics &gt; Wrappers. Un commit a la vez."),
    ]
    mono = "Consolas,Menlo,'DejaVu Sans Mono',monospace"
    body, y = [], 36
    for i, (cmd, out) in enumerate(lines):
        if cmd:
            body.append(f'<text x="24" y="{y}" font-family="{mono}" font-size="14" fill="#3fb950">$ '
                        f'<tspan fill="#e6edf3">{cmd}</tspan></text>')
            y += 22
        body.append(f'<text x="24" y="{y}" font-family="{mono}" font-size="14" fill="#8b949e">{out}</text>')
        continues = i + 1 < len(lines) and lines[i + 1][0] is None
        y += 20 if continues else 32
    body.append(f'<text x="24" y="{y}" font-family="{mono}" font-size="14" fill="#3fb950">$ </text>'
                f'<rect x="42" y="{y-13}" width="9" height="16" fill="#3fb950">'
                f'<animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" '
                f'repeatCount="indefinite"/></rect>')
    height = y + 22
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
            f'height="{height}" role="img" aria-label="Sobre mí: David Britto, Senior AI Engineer y MLOps Architect">'
            + universe(width, height, 7, "ab")
            + "".join(body) + "</svg>")


if __name__ == "__main__":
    with open(os.path.join(OUT, "david-perfil.svg"), "w", encoding="utf-8") as f:
        f.write(scene())
    for name, text in [
        ("sobre-mi", "SOBRE MI"),
        ("proyectos", "PROYECTOS"),
        ("stack", "STACK"),
        ("estadisticas", "ESTADISTICAS"),
        ("actividad", "ACTIVIDAD"),
        ("contacto", "CONTACTO"),
    ]:
        with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as f:
            f.write(title_svg(text))
    with open(os.path.join(OUT, "espacio.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*PX}" height="24" viewBox="0 0 {W*PX} 24"/>')
    with open(os.path.join(OUT, "sobre-mi-tarjeta.svg"), "w", encoding="utf-8") as f:
        f.write(about_card())
    print("OK -> assets/david-perfil.svg + secciones generadas exitosamente")
