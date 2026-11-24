#!/usr/bin/env python3
"""Generate the dark-medieval pixel-art SVGs for the profile README.

All art is original. Run:  python3 assets/gen.py
Stdlib only. Output goes next to this file.
"""
import os
import random

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
VOID = "#0b0606"
SILHOUETTE = "#120808"
IRON = "#2a2a2e"
IRON_LIGHT = "#5b5d63"
STEEL = "#9aa0a6"
BLOOD = "#8b0000"
BLOOD_DARK = "#4a0000"
BLOOD_DEEP = "#2a0000"
EMBER = "#ff4d00"
FLAME = "#ffb000"
HOT = "#ffe08a"
BONE = "#e8dcc0"
BONE_DARK = "#a89878"
WOOD = "#5a2a10"

# ---------------------------------------------------------------- 5x7 font
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".....", "..#.."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "*": [".....", ".....", "..#..", ".###.", "..#..", ".....", "....."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}


def text_width(s, scale=1):
    return (len(s) * 6 - 1) * scale


# ---------------------------------------------------------------- canvas
class Canvas:
    """Collects SVG elements in grid units; scaled by `px` on output."""

    def __init__(self, w, h, px):
        self.w, self.h, self.px = w, h, px
        self.defs = []
        self.body = []

    def rect(self, x, y, w, h, fill, extra=""):
        self.body.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'
        )

    def raw(self, s):
        self.body.append(s)

    def group(self, inner, attrs=""):
        self.body.append(f"<g{attrs}>{''.join(inner)}</g>")

    def save(self, name, title):
        W, H = self.w * self.px, self.h * self.px
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {self.w} {self.h}" shape-rendering="crispEdges" '
            f'role="img" aria-label="{title}">'
            f"<title>{title}</title>"
            f"<defs>{''.join(self.defs)}</defs>"
            f"{''.join(self.body)}</svg>\n"
        )
        with open(os.path.join(OUT, name), "w") as f:
            f.write(svg)
        print(f"wrote {name} ({len(svg) // 1024} KB)")


def runs(rows):
    """Yield (x, y, length, char) horizontal runs from a list of strings."""
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c = row[x]
            if c == ".":
                x += 1
                continue
            start = x
            while x < len(row) and row[x] == c:
                x += 1
            yield start, y, x - start, c


def sprite(rows, colors, ox, oy, s=1):
    """Return rect strings for a char-map sprite."""
    out = []
    for x, y, n, c in runs(rows):
        out.append(
            f'<rect x="{ox + x * s}" y="{oy + y * s}" width="{n * s}" '
            f'height="{s}" fill="{colors[c]}"/>'
        )
    return out


def text_rects(s, ox, oy, scale, fill):
    out = []
    for i, ch in enumerate(s.upper()):
        glyph = FONT.get(ch, FONT[" "])
        out += sprite(glyph, {"#": fill}, ox + i * 6 * scale, oy, scale)
    return out


def fancy_text(cv, s, ox, oy, scale, grad_id, depth=2, glow=True):
    """Extruded, gradient-filled pixel text with a pulsing ember glow."""
    h = 7 * scale
    cv.defs.append(
        f'<linearGradient id="{grad_id}" x1="0" y1="{oy}" x2="0" y2="{oy + h}" '
        f'gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff3c8"/>'
        f'<stop offset="0.45" stop-color="{FLAME}"/>'
        f'<stop offset="1" stop-color="{EMBER}"/></linearGradient>'
    )
    if glow:
        cv.defs.append(
            f'<filter id="{grad_id}-glow" x="-10%" y="-40%" width="120%" height="180%">'
            f'<feGaussianBlur stdDeviation="{max(1, scale)}"/></filter>'
        )
        cv.group(
            text_rects(s, ox, oy, scale, EMBER),
            f' filter="url(#{grad_id}-glow)" opacity="0.6"'
            f'><animate attributeName="opacity" values="0.35;0.8;0.5;0.75;0.35" '
            f'dur="2.4s" repeatCount="indefinite"/',
        )
    shades = [BLOOD_DEEP, BLOOD_DARK, BLOOD]
    for k in range(depth, 0, -1):
        cv.group(text_rects(s, ox + k, oy + k, scale, shades[-k]))
    cv.group(text_rects(s, ox, oy, scale, f"url(#{grad_id})"))


# ---------------------------------------------------------------- effects
def fire(cv, y_base, height_min, height_max, frames=4, dur=0.6, seed=1):
    """Animated pixel fire: chunky 2px tongues built from layered waves."""
    import math
    rnd = random.Random(seed)
    colors = [(0.28, HOT), (0.32, FLAME), (0.26, EMBER), (0.14, BLOOD)]
    mid = (height_min + height_max) / 2
    amp = (height_max - height_min) / 2
    for f in range(frames):
        ph = [rnd.uniform(0, 6.28) for _ in range(3)]
        rects = []
        for x in range(0, cv.w, 2):
            v = (0.5 * math.sin(x * 0.045 + ph[0])
                 + 0.35 * math.sin(x * 0.13 + ph[1])
                 + 0.35 * abs(math.sin(x * 0.31 + ph[2])))
            h = int(round(mid + amp * v + rnd.uniform(-1, 1.5)))
            h = max(2, h)
            y = y_base
            for frac, col in colors:
                seg = max(1, int(round(h * frac)))
                rects.append(f'<rect x="{x}" y="{y - seg}" width="2" height="{seg}" fill="{col}"/>')
                y -= seg
            if rnd.random() < 0.25:  # stray flicker pixel above the tongue
                rects.append(f'<rect x="{x + rnd.randrange(2)}" y="{y - 2}" width="1" height="1" fill="{EMBER}"/>')
        vals = ";".join("1" if i == f else "0" for i in range(frames))
        cv.group(
            rects,
            f' opacity="{1 if f == 0 else 0}"><animate attributeName="opacity" '
            f'values="{vals}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/',
        )


def embers(cv, n, y_from, y_to, seed=2):
    rnd = random.Random(seed)
    for _ in range(n):
        x = rnd.uniform(2, cv.w - 2)
        dx = rnd.uniform(-8, 8)
        d = rnd.uniform(2.5, 5.5)
        b = rnd.uniform(0, d)
        col = rnd.choice([FLAME, EMBER, HOT])
        cv.raw(
            f'<rect x="{x:.1f}" y="{y_from}" width="1" height="1" fill="{col}">'
            f'<animate attributeName="y" from="{y_from}" to="{y_to}" dur="{d:.2f}s" begin="-{b:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="x" from="{x:.1f}" to="{x + dx:.1f}" dur="{d:.2f}s" begin="-{b:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;0.8;0" dur="{d:.2f}s" begin="-{b:.2f}s" repeatCount="indefinite"/>'
            f"</rect>"
        )


def flicker(min_o=0.55, dur=1.7, begin=0.0):
    return (
        f'<animate attributeName="opacity" values="1;{min_o};0.9;{min_o + 0.15};1" '
        f'dur="{dur:.2f}s" begin="-{begin:.2f}s" repeatCount="indefinite"/>'
    )


# ---------------------------------------------------------------- sprites
SKULL = [
    "...bbbbbb...",
    "..bbbbbbbb..",
    ".bbbbbbbbbb.",
    ".bbbbbbbbbd.",
    ".brrbbbbrrd.",
    ".brrbbbbrrd.",
    ".bbbbbbbbbd.",
    "..bbb..bbd..",
    "...bbbbbd...",
    "...b.bb.d...",
    "...bbbbbd...",
    "............",
]
SKULL_C = {"b": BONE, "d": BONE_DARK, "r": EMBER}

SHIELD = [
    ".iiiiiiiiii.",
    ".irrrffrrri.",
    ".irrrffrrri.",
    ".iffffffffi.",
    ".irrrffrrri.",
    ".irrrffrrri.",
    ".irrrffrrri.",
    "..irrffrri..",
    "..irrffrri..",
    "...irffri...",
    "....iffi....",
    ".....ii.....",
]
SHIELD_C = {"i": IRON_LIGHT, "r": BLOOD, "f": FLAME}

ANVIL = [
    "............",
    "............",
    "............",
    "..hhhhhhhhhh",
    "iiiiiiiiiiii",
    "..iiiiiiiiii",
    "....iiiiii..",
    ".....iiii...",
    ".....iiii...",
    "...iiiiiiii.",
    "..iiiiiiiiii",
    "............",
]
ANVIL_C = {"h": STEEL, "i": IRON_LIGHT}

BRAZIER = [
    "............",
    "............",
    "............",
    "............",
    "............",
    ".iiiiiiiiii.",
    "..iiiiiiii..",
    "...iiiiii...",
    ".....ii.....",
    ".....ii.....",
    "...iiiiii...",
    "............",
]
BRAZIER_FLAMES = [
    [
        ".....f......",
        "....ff..f...",
        "...fyf.ff...",
        "..ffyyfyff..",
        "..fyyhhyyf..",
    ],
    [
        "......f.....",
        "...f..ff....",
        "...ff.fyf...",
        "..ffyfyyff..",
        "..fyyhhyyf..",
    ],
    [
        "....f..f....",
        "....ff.ff...",
        "..f.fyffy...",
        "..ffyyyyff..",
        "..fyhhhyyf..",
    ],
]
FLAME_C = {"f": EMBER, "y": FLAME, "h": HOT}


def sword_rows():
    g = [["."] * 12 for _ in range(12)]
    for i in range(7):  # blade, up-right from the guard
        x, y = 5 + i, 6 - i
        g[y][x] = "w"
        if y + 1 < 12 and x + 1 < 12:
            g[y + 1][x + 1] = "s"
    for x, y in [(2, 5), (3, 6), (4, 7), (5, 8), (6, 9)]:  # cross-guard
        g[y][x] = "g"
    for x, y in [(3, 8), (2, 9), (1, 10)]:  # grip
        g[y][x] = "h"
    g[11][0] = "p"  # pommel
    return ["".join(r) for r in g]


SWORD_C = {"w": "#e6e8ea", "s": STEEL, "g": FLAME, "h": WOOD, "p": BLOOD}


def icon_with_anim(name, ox, oy, s):
    """Icon rects; some icons get a little life."""
    if name == "skull":
        out = sprite(SKULL, {**SKULL_C, "r": BLOOD_DARK}, ox, oy, s)
        eyes = sprite([r.replace("b", ".").replace("d", ".") for r in SKULL], {"r": EMBER}, ox, oy, s)
        out.append(f"<g>{''.join(eyes)}{flicker(0.2, 1.3)}</g>")
        return out
    if name == "sword":
        out = sprite(sword_rows(), SWORD_C, ox, oy, s)
        out.append(
            f'<rect x="{ox + 10 * s}" y="{oy}" width="{s}" height="{s}" fill="#ffffff" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0" dur="2.2s" repeatCount="indefinite"/></rect>'
        )
        return out
    if name == "shield":
        out = sprite(SHIELD, SHIELD_C, ox, oy, s)
        cross = sprite([r.replace("i", ".").replace("r", ".") for r in SHIELD], {"f": HOT}, ox, oy, s)
        out.append(f'<g opacity="0">{"".join(cross)}<animate attributeName="opacity" values="0;0.7;0" dur="2.6s" repeatCount="indefinite"/></g>')
        return out
    if name == "anvil":
        out = sprite(ANVIL, ANVIL_C, ox, oy, s)
        for i, (sx, sy) in enumerate([(3, 1), (6, 0), (9, 1), (8, 2)]):
            out.append(
                f'<rect x="{ox + sx * s}" y="{oy + sy * s}" width="{s}" height="{s}" fill="{FLAME if i % 2 else HOT}" opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0;0" dur="1.1s" begin="-{i * 0.27:.2f}s" repeatCount="indefinite"/></rect>'
            )
        return out
    if name == "brazier":
        out = sprite(BRAZIER, {"i": IRON_LIGHT}, ox, oy, s)
        n = len(BRAZIER_FLAMES)
        for f, rows in enumerate(BRAZIER_FLAMES):
            vals = ";".join("1" if i == f else "0" for i in range(n))
            out.append(
                f'<g opacity="{1 if f == 0 else 0}">{"".join(sprite(rows, FLAME_C, ox, oy, s))}'
                f'<animate attributeName="opacity" values="{vals}" dur="0.5s" calcMode="discrete" repeatCount="indefinite"/></g>'
            )
        return out
    raise ValueError(name)


# ---------------------------------------------------------------- banner
def lerp_hex(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def sky(cv, top, bottom, band=5):
    n = (cv.h + band - 1) // band
    cols = [lerp_hex(top, bottom, i / (n - 1)) for i in range(n)]
    for i, c in enumerate(cols):
        cv.rect(0, i * band, cv.w, band, c)
    # checker dither on each band boundary
    for i in range(1, n):
        pid = f"dith{i}"
        cv.defs.append(
            f'<pattern id="{pid}" width="2" height="2" patternUnits="userSpaceOnUse">'
            f'<rect x="0" y="0" width="1" height="1" fill="{cols[i]}"/>'
            f'<rect x="1" y="1" width="1" height="1" fill="{cols[i]}"/></pattern>'
        )
        cv.rect(0, i * band - 1, cv.w, 1, f"url(#{pid})")


def moon(cv, cx, cy, r):
    for k, op in [(r + 6, 0.06), (r + 4, 0.1), (r + 2, 0.16)]:
        cv.raw(f'<circle cx="{cx}" cy="{cy}" r="{k}" fill="{EMBER}" opacity="{op}" shape-rendering="auto"/>')
    for y in range(-r, r + 1):
        xs = [x for x in range(-r, r + 1) if x * x + y * y <= r * r]
        if xs:
            shade = lerp_hex("#ff7a3d", BLOOD, (y + r) / (2 * r))
            cv.rect(cx + xs[0], cy + y, len(xs), 1, shade)
    for dx, dy, w in [(-3, -2, 2), (2, 1, 3), (-1, 4, 2), (3, -4, 1)]:
        cv.rect(cx + dx, cy + dy, w, 1, BLOOD_DARK)
        cv.rect(cx + dx, cy + dy + 1, w, 1, "#a0200a")


def stars(cv, n, max_y, seed=7):
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.randrange(cv.w), rnd.randrange(max_y)
        op = rnd.uniform(0.3, 0.9)
        anim = ""
        if i % 3 == 0:
            anim = (
                f'<animate attributeName="opacity" values="{op:.2f};0.1;{op:.2f}" '
                f'dur="{rnd.uniform(2, 5):.1f}s" begin="-{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/>'
            )
        cv.raw(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{BONE}" opacity="{op:.2f}">{anim}</rect>')


def castle(cv, base_row, towers, seed=3):
    rnd = random.Random(seed)
    hm = [base_row] * cv.w
    for x in range(cv.w):  # curtain wall crenellations
        if (x // 3) % 2 == 0:
            hm[x] = base_row - 2
    windows = []
    for x0, w, top, kind in towers:
        for c in range(x0, x0 + w):
            if not 0 <= c < cv.w:
                continue
            if kind == "spire":
                d = min(c - x0, x0 + w - 1 - c)
                t = top - 2 * d
            elif kind == "cren":
                t = top - 2 if ((c - x0) // 2) % 2 == 0 else top
            else:
                t = top
            hm[c] = min(hm[c], t)
        if kind == "spire":
            mid = x0 + (w - 1) // 2
            tip = top - 2 * ((w - 1) // 2)
            cv.rect(mid, tip - 3, 1 + (w + 1) % 2, 3, SILHOUETTE)
            # banner flag on the spire tip
            fl = [f'<rect x="{mid + 1}" y="{tip - 3}" width="3" height="1" fill="{BLOOD}"/><rect x="{mid + 1}" y="{tip - 2}" width="2" height="1" fill="{BLOOD}"/>',
                  f'<rect x="{mid + 1}" y="{tip - 3}" width="2" height="1" fill="{BLOOD}"/><rect x="{mid + 1}" y="{tip - 2}" width="3" height="1" fill="{BLOOD}"/>']
            for i, f in enumerate(fl):
                cv.raw(f'<g opacity="{1 - i}">{f}<animate attributeName="opacity" values="{"1;0" if i == 0 else "0;1"}" dur="0.8s" calcMode="discrete" repeatCount="indefinite"/></g>')
        # windows: column of slits down the tower body
        body_top = top + 3
        for wy in range(body_top, base_row - 3, 6):
            for wx in range(x0 + 2, x0 + w - 2, 4):
                windows.append((wx, wy))
    for x, h in enumerate(hm):
        cv.rect(x, h, 1, cv.h - h, SILHOUETTE)
    for i, (x, y) in enumerate(windows):
        if rnd.random() < 0.7:
            cv.raw(
                f'<rect x="{x}" y="{y}" width="1" height="2" fill="{FLAME if rnd.random() < 0.6 else EMBER}">'
                f"{flicker(rnd.uniform(0.2, 0.6), rnd.uniform(1.2, 3), rnd.uniform(0, 3))}</rect>"
            )
    return hm


def gate(cv, cx, base_row):
    # glowing arched gate in the curtain wall
    rows = [".hhh.", "hhhhh", "hhhhh", "hhhhh", "hhhhh"]
    rows = [r.replace("h", "x") for r in rows]
    rects = sprite(rows, {"x": EMBER}, cx - 2, base_row + 1)
    inner = sprite([".....", ".yyy.", ".yyy.", ".yyy.", ".yyy."], {"y": FLAME}, cx - 2, base_row + 1)
    cv.raw(f"<g>{''.join(rects)}{''.join(inner)}{flicker(0.6, 1.1)}</g>")


def banner():
    cv = Canvas(240, 70, 4)
    sky(cv, "#050202", "#5a0d06")
    stars(cv, 70, 40)
    moon(cv, 222, 13, 8)
    hm = castle(
        cv,
        56,
        [
            (2, 13, 46, "spire"),
            (17, 8, 44, "cren"),
            (28, 9, 44, "spire"),
            (40, 6, 50, "cren"),
            (96, 48, 47, "cren"),
            (112, 15, 49, "spire"),
            (180, 7, 48, "cren"),
            (190, 9, 44, "spire"),
            (202, 8, 42, "cren"),
            (213, 15, 48, "spire"),
            (232, 8, 44, "cren"),
        ],
    )
    gate(cv, 120, 52)
    fire(cv, 70, 5, 15, frames=4, dur=0.5, seed=11)
    embers(cv, 26, 64, 30)
    title = "CON-GIF-STACK"
    fancy_text(cv, title, (cv.w - text_width(title, 2)) // 2, 5, 2, "tg", depth=3)
    sub = "BUSINESS GRAD * CLAUDE CODE INITIATE"
    sx = (cv.w - text_width(sub)) // 2
    cv.group(text_rects(sub, sx + 1, 25, 1, BLOOD_DEEP))
    cv.group(text_rects(sub, sx, 24, 1, BONE))
    cv.save("banner.svg", "con-gif-stack: a pixel-art castle burning under a blood moon")


# ---------------------------------------------------------------- headers
def header(fname, label, icon):
    s = 2
    w = 18 + text_width(label, s) + 6
    cv = Canvas(w, 19, 3)
    cv.group(icon_with_anim(icon, 1, 2, 1))
    fancy_text(cv, label, 17, 1, s, "hg", depth=2, glow=True)
    cv.defs.append(
        f'<linearGradient id="ul" x1="0" x2="1"><stop offset="0" stop-color="{EMBER}"/>'
        f'<stop offset="0.6" stop-color="{BLOOD}"/><stop offset="1" stop-color="{BLOOD}" stop-opacity="0"/></linearGradient>'
    )
    cv.rect(1, 17, w - 1, 1, "url(#ul)")
    cv.save(fname, label.title())


# ---------------------------------------------------------------- divider
def divider():
    cv = Canvas(300, 9, 3)
    cv.defs.append(
        f'<linearGradient id="fade" x1="0" x2="1">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset="0.2" stop-color="#fff" stop-opacity="1"/>'
        f'<stop offset="0.8" stop-color="#fff" stop-opacity="1"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="m"><rect x="0" y="0" width="300" height="9" fill="url(#fade)"/></mask>'
    )
    link_h = ["####.", "#..#.", "####."]
    links = []
    cx = cv.w // 2
    for x in range(0, cv.w, 7):
        if abs(x + 3 - cx) < 9:
            continue
        links += sprite(link_h, {"#": IRON_LIGHT}, x, 3)
        links.append(f'<rect x="{x + 4}" y="4" width="3" height="1" fill="{IRON}"/>')
    cv.group(links, ' mask="url(#m)"')
    rune = ["...#...", "..#.#..", ".#.#.#.", "#.###.#", ".#.#.#.", "..#.#..", "...#..."]
    cv.defs.append('<filter id="rg" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.2"/></filter>')
    glow = sprite(rune, {"#": EMBER}, cx - 3, 1)
    cv.raw(f'<g filter="url(#rg)">{"".join(glow)}<animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/></g>')
    cv.group(sprite(rune, {"#": FLAME}, cx - 3, 1))
    cv.save("divider.svg", "divider")


# ---------------------------------------------------------------- footer
def footer():
    cv = Canvas(240, 34, 4)
    cv.rect(0, 0, cv.w, cv.h, VOID)
    cv.defs.append(
        f'<linearGradient id="pit" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{VOID}"/><stop offset="1" stop-color="#3a0804"/></linearGradient>'
    )
    cv.rect(0, 0, cv.w, cv.h, "url(#pit)")
    fire(cv, 34, 5, 17, frames=4, dur=0.5, seed=21)
    embers(cv, 18, 28, 2, seed=5)
    msg = "RIP AND COMMIT"
    fancy_text(cv, msg, (cv.w - text_width(msg)) // 2, 4, 1, "fg", depth=1)
    cv.save("footer.svg", "Rip and commit")


if __name__ == "__main__":
    banner()
    header("h-codex.svg", "THE CODEX", "skull")
    header("h-crusade.svg", "THE CRUSADE", "sword")
    header("h-forging.svg", "FORGING", "anvil")
    header("h-arsenal.svg", "ARSENAL", "shield")
    header("h-war.svg", "WAR RECORD", "brazier")
    divider()
    footer()
