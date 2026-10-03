"""CYENCE logo concepts, in the system of the Zvaž vědu! / Generace vesmír
logos: a 2.56 : 1 rectangle with a thick frame, an icon on the left that
interacts with the frame, the name set right in ZV! Display.

Everything sits on one grid: 1 cell = the frame thickness. The canvas is
36 × 14 cells (aspect 2.57), the inside 34 × 12.

    python design/logo/concepts/generate.py   (needs fonttools + brotli)
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

INK, CREAM, YELLOW, BLUE = "#231f20", "#f2ede6", "#ffc300", "#00aeef"
W, H = 36, 14  # canvas in cells; frame = 1 cell
OUT = Path(__file__).parent
FONT = TTFont("static/fonts/zv-display.woff2")


def wordmark(text, cap_height, right, baseline):
    """`text` as SVG paths in ZV! Display, right-aligned at x=`right`."""
    gs, cmap, hmtx = FONT.getGlyphSet(), FONT.getBestCmap(), FONT["hmtx"]
    s = cap_height / FONT["OS/2"].sCapHeight
    names = [cmap[ord(c)] for c in text]
    width = sum(hmtx[n][0] for n in names) * s
    x, out = right - width, []
    for n in names:
        pen = SVGPathPen(gs)
        gs[n].draw(pen)
        out.append(f'<path transform="translate({x:.3f} {baseline}) scale({s:.6f} {-s:.6f})" d="{pen.getCommands()}"/>')
        x += hmtx[n][0] * s
    return f'<g fill="{INK}">{"".join(out)}</g>', right - width


def frame(gaps=()):
    """Frame 1 cell thick; `gaps` = cells (x, y) left open (the slits)."""
    cells = [(i, j) for j in range(H) for i in range(W) if i in (0, W - 1) or j in (0, H - 1)]
    return [(i, j, INK) for i, j in cells if (i, j) not in gaps]


def rings(src, radii, cells):
    """Cells lying on 1-cell-thick rings of the given radii around src."""
    sx, sy = src
    return {(i, j) for i, j in cells if any(abs(math.hypot(i + 0.5 - sx, j + 0.5 - sy) - r) < 0.5 for r in radii)}


def svg(cells, extra="", cream_inside=True):
    rects = "".join(f'<rect x="{i}" y="{j}" width="1" height="1" fill="{c}"/>' for i, j, c in cells)
    bg = f'<rect width="{W}" height="{H}" fill="{CREAM}"/>' if cream_inside else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">{bg}{rects}{extra}</svg>'


inside = [(i, j) for j in range(1, H - 1) for i in range(1, W - 1)]
text, text_left = wordmark("CYENCE", 5, W - 3, 9.5)
big_text, big_text_left = wordmark("CYENCE", 7, W - 2.5, 10.5)
icon_area = [(i, j) for i, j in inside if i < 14]


def interference(a, b):
    out = []
    for i, j in icon_area:
        ya, yb = (i, j) in a, (i, j) in b
        if ya or yb:
            out.append((i, j, INK if ya and yb else YELLOW if ya else BLUE))
    return out


# A – double slit: two gaps in the left frame, waves come through and interfere.
slit_y, slit_b = (0, 4), (0, 9)
ya = rings((0.5, 4.5), [2, 4, 6, 8, 10, 12], icon_area)
bb = rings((0.5, 9.5), [2, 4, 6, 8, 10, 12], icon_area)
A = frame(gaps={slit_y, slit_b}) + [(0, 4, YELLOW), (0, 9, BLUE)] + interference(ya, bb)
(OUT / "a-double-slit.svg").write_text(svg(A, text))

# B – same idea, wider rings (every 3 cells): calmer at small sizes.
ya = rings((0.5, 4.5), [2.5, 5.5, 8.5, 11.5], icon_area)
bb = rings((0.5, 9.5), [2.5, 5.5, 8.5, 11.5], icon_area)
B = frame(gaps={slit_y, slit_b}) + [(0, 4, YELLOW), (0, 9, BLUE)] + interference(ya, bb)
(OUT / "b-double-slit-calm.svg").write_text(svg(B, text))

# C – corner ripples: yellow from the bottom-left corner, blue from the top-left.
ya = rings((1, 13), [3, 5, 7, 9, 11], icon_area)
bb = rings((1, 1), [3, 5, 7, 9, 11], icon_area)
C = frame() + interference(ya, bb)
(OUT / "c-corner-ripples.svg").write_text(svg(C, text))

# D – the brand pattern itself as a square icon (phase interference, 12 × 12).
D = frame()
for i, j in inside:
    if i > 12:
        continue
    t1 = (math.hypot(i + 0.5 - 2, j + 0.5 - 10) / 3.2) % 1 < 0.5
    t2 = (math.hypot(i + 0.5 - 11, j + 0.5 - 3) / 4.5) % 1 < 0.5
    D.append((i, j, INK if t1 and t2 else YELLOW if t1 else BLUE if t2 else CREAM))
(OUT / "d-pattern-tile.svg").write_text(svg(D, text))



def annulus(cx, cy, r_in, r_out):
    """A full ring as a filled path (even-odd), for clipping and drawing."""
    def circle(r):
        return f"M{cx - r},{cy} a{r},{r} 0 1,0 {2 * r},0 a{r},{r} 0 1,0 {-2 * r},0 "
    return circle(r_out) + circle(r_in)


def vector_slit(radii, thickness, name, text_svg):
    """E – double slit with smooth rings; overlaps drawn black via clipPath."""
    a = "".join(annulus(0.5, 4.5, r - thickness / 2, r + thickness / 2) for r in radii)
    b = "".join(annulus(0.5, 9.5, r - thickness / 2, r + thickness / 2) for r in radii)
    body = f"""
      <defs>
        <clipPath id="inner"><rect x="1" y="1" width="{W - 2}" height="{H - 2}"/></clipPath>
        <clipPath id="icon"><rect x="1" y="1" width="{text_left_icon}" height="{H - 2}"/></clipPath>
        <clipPath id="ringsA"><path fill-rule="evenodd" clip-rule="evenodd" d="{a}"/></clipPath>
      </defs>
      <rect width="{W}" height="{H}" fill="{INK}"/>
      <rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="{CREAM}"/>
      <rect x="0" y="4" width="1" height="1" fill="{YELLOW}"/>
      <rect x="0" y="9" width="1" height="1" fill="{BLUE}"/>
      <g clip-path="url(#icon)">
        <path fill-rule="evenodd" fill="{YELLOW}" d="{a}"/>
        <path fill-rule="evenodd" fill="{BLUE}" d="{b}"/>
        <g clip-path="url(#ringsA)"><path fill-rule="evenodd" fill="{INK}" d="{b}"/></g>
      </g>
      {text_svg}"""
    (OUT / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body}</svg>')


text_left_icon = 12.5
vector_slit([2.5, 5, 7.5, 10], 1.25, "e-double-slit-vector.svg", big_text)

# F – double slit on a finer pixel grid (3 sub-cells per frame cell).
k = 3
fine = []
for j in range(1 * k, (H - 1) * k):
    for i in range(1 * k, int(12.5 * k)):
        cx, cy = (i + 0.5) / k, (j + 0.5) / k
        def on(src):
            d = math.hypot(cx - src[0], cy - src[1])
            return any(abs(d - r) < 0.62 for r in [2.5, 5, 7.5, 10])
        a, b = on((0.5, 4.5)), on((0.5, 9.5))
        if a or b:
            fine.append((i / k, j / k, INK if a and b else YELLOW if a else BLUE))
rects = "".join(f'<rect x="{x:.4f}" y="{y:.4f}" width="{1/k:.4f}" height="{1/k:.4f}" fill="{c}"/>' for x, y, c in fine)
F = frame(gaps={(0, 4), (0, 9)}) + [(0, 4, YELLOW), (0, 9, BLUE)]
(OUT / "f-double-slit-fine-pixels.svg").write_text(svg(F, rects + big_text))
print("text starts at x =", round(text_left, 2), "| big:", round(big_text_left, 2))


# ---- Round 2: slits further apart, fewer rings, icon and name separated ----
def slit_logo(name, slits=(3.5, 10.5), radii=(3, 6, 9, 12), thick=1.3, icon_w=13, cap=5.4, pixel=0):
    """Double-slit logo. pixel=0 → smooth rings, pixel=k → k sub-cells per cell."""
    words, left = wordmark("CYENCE", cap, W - 2.5, 7 + cap / 2)
    ya, yb = slits
    parts = [f'<rect width="{W}" height="{H}" fill="{INK}"/>',
             f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" fill="{CREAM}"/>']
    if pixel:
        k = pixel
        for j in range(k, (H - 1) * k):
            for i in range(k, icon_w * k):
                cx, cy = (i + 0.5) / k, (j + 0.5) / k
                on = lambda sy: any(abs(math.hypot(cx - 0.5, cy - sy) - r) < thick / 2 for r in radii)
                a, b = on(ya), on(yb)
                if a or b:
                    c = INK if a and b else YELLOW if a else BLUE
                    parts.append(f'<rect x="{i / k:.4f}" y="{j / k:.4f}" width="{1 / k:.4f}" height="{1 / k:.4f}" fill="{c}"/>')
    else:
        ra = "".join(annulus(0.5, ya, r - thick / 2, r + thick / 2) for r in radii)
        rb = "".join(annulus(0.5, yb, r - thick / 2, r + thick / 2) for r in radii)
        parts.append(f"""<defs>
          <clipPath id="icon-{name}"><rect x="1" y="1" width="{icon_w - 1}" height="{H - 2}"/></clipPath>
          <clipPath id="a-{name}"><path clip-rule="evenodd" d="{ra}"/></clipPath></defs>
          <g clip-path="url(#icon-{name})">
            <path fill-rule="evenodd" fill="{YELLOW}" d="{ra}"/>
            <path fill-rule="evenodd" fill="{BLUE}" d="{rb}"/>
            <g clip-path="url(#a-{name})"><path fill-rule="evenodd" fill="{INK}" d="{rb}"/></g>
          </g>""")
    # The slits: openings in the left frame, in the colour of their wave.
    parts.append(f'<rect x="0" y="{ya - 0.5}" width="1" height="1" fill="{YELLOW}"/>')
    parts.append(f'<rect x="0" y="{yb - 0.5}" width="1" height="1" fill="{BLUE}"/>')
    parts.append(words)
    (OUT / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" shape-rendering="{"crispEdges" if pixel else "geometricPrecision"}">{"".join(parts)}</svg>')
    return left


print("G text left:", round(slit_logo("g-slit-smooth.svg"), 2))
print("H text left:", round(slit_logo("h-slit-pixel.svg", pixel=2), 2))
print("I text left:", round(slit_logo("i-slit-smooth-3rings.svg", radii=(3.5, 7, 10.5), thick=1.6), 2))


# ---- Icon only (favicon / social avatar): the slits in a square frame ----
def slit_icon(name, size=14, slits=(3.5, 10.5), radii=(3.5, 7, 10.5), thick=1.6):
    ya, yb = slits
    ra = "".join(annulus(0.5, ya, r - thick / 2, r + thick / 2) for r in radii)
    rb = "".join(annulus(0.5, yb, r - thick / 2, r + thick / 2) for r in radii)
    body = f"""<defs><clipPath id="in"><rect x="1" y="1" width="{size - 2}" height="{size - 2}"/></clipPath>
      <clipPath id="ca"><path clip-rule="evenodd" d="{ra}"/></clipPath></defs>
      <rect width="{size}" height="{size}" fill="{INK}"/>
      <rect x="1" y="1" width="{size - 2}" height="{size - 2}" fill="{CREAM}"/>
      <g clip-path="url(#in)">
        <path fill-rule="evenodd" fill="{YELLOW}" d="{ra}"/>
        <path fill-rule="evenodd" fill="{BLUE}" d="{rb}"/>
        <g clip-path="url(#ca)"><path fill-rule="evenodd" fill="{INK}" d="{rb}"/></g>
      </g>
      <rect x="0" y="{ya - 0.5}" width="1" height="1" fill="{YELLOW}"/>
      <rect x="0" y="{yb - 0.5}" width="1" height="1" fill="{BLUE}"/>"""
    (OUT / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">{body}</svg>')


slit_icon("i-icon.svg")
