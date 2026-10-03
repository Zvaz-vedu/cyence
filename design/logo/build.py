"""CYENCE logo – the pattern-tile logo (concept D), all versions.

The logo sits on a grid where 1 unit = the frame thickness:
  - canvas 36 × 14 units (≈ 2.57 : 1, like the Zvaž vědu! and Generace
    vesmír logos), frame 1 unit;
  - icon: a fixed 12 × 12 frame of the CYENCE interference pattern, flush
    with the frame on the left;
  - wordmark: CYENCE in ZV! Display, cap height 5 units, right-aligned
    2 units inside the frame, vertically centred.

Pattern rule (same as the website): a cell on a crest of the yellow wave is
yellow, on a crest of the blue wave blue, on both black, else background.
Black & white versions show the yellow wave on its own (its crests in
black): regular rings read as a wave in one colour, where the two-wave
interference would read as random squares (a QR code).

    python design/logo/build.py        (needs fonttools + brotli)

Writes SVGs to design/logo/cyence/.
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "cyence"
FONT = TTFont(ROOT / "static/fonts/zv-display.woff2")

INK, CREAM, YELLOW, BLUE = "#231f20", "#f2ede6", "#ffc300", "#00aeef"
BLACK, WHITE = "#000000", "#ffffff"

W, H = 36, 14  # logo canvas in units
TILE = 12  # pattern tile, units
SOURCES = {  # (x, y, wavelength) in units, inside the tile
    "yellow": (2, 10, 3.2),
    "blue": (11, 3, 4.5),
}
CAP, TEXT_RIGHT, BASELINE = 5, W - 3, 9.5


def crest(i, j, src):
    x, y, wl = src
    return (math.hypot(i + 0.5 - x, j + 0.5 - y) / wl) % 1 < 0.5


def tile_cells(mode="color"):
    """[(col, row, state)] for the 12 × 12 tile; state in cream/yellow/blue/ink.
    mode "mono": one colour – only the yellow wave's crests, as "ink"."""
    if mode == "mono":
        return single_wave("yellow")
    cells = []
    for j in range(TILE):
        for i in range(TILE):
            a, b = crest(i, j, SOURCES["yellow"]), crest(i, j, SOURCES["blue"])
            if mode == "mono":
                state = "ink" if a != b else "bg"
            else:
                state = "ink" if a and b else "yellow" if a else "blue" if b else "bg"
            cells.append((i, j, state))
    return cells


def hatch(cells, fill, ox=1, oy=1, solid_overlap=False):
    """One-colour version with line textures instead of colours: cells on a
    yellow crest get vertical lines, on a blue crest horizontal lines, on both
    a grid (or solid, with solid_overlap). Two lines per cell; they line up
    across neighbouring cells into continuous stripes."""
    out = []
    for i, j, state in cells:
        x, y = ox + i, oy + j
        v = state in ("yellow", "ink")
        h = state in ("blue", "ink")
        if state == "ink" and solid_overlap:
            out.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{fill}"/>')
            continue
        for k in (0.125, 0.625):
            if v:
                out.append(f'<rect x="{x + k}" y="{y}" width="0.25" height="1" fill="{fill}"/>')
            if h:
                out.append(f'<rect x="{x}" y="{y + k}" width="1" height="0.25" fill="{fill}"/>')
    return "".join(out)


def single_wave(which="yellow"):
    """[(col, row, state)] with only one wave's crests ("ink"), for one colour."""
    return [(i, j, "ink" if crest(i, j, SOURCES[which]) else "bg") for j in range(TILE) for i in range(TILE)]


def runs(cells, colors, ox=1, oy=1):
    """Merge horizontal runs of equal cells into <rect>s (offset by the frame)."""
    rows = {}
    for i, j, s in cells:
        rows.setdefault(j, []).append((i, s))
    out = []
    for j, row in rows.items():
        row.sort()
        start, cur = row[0]
        for k in range(1, len(row) + 1):
            i, s = row[k] if k < len(row) else (None, None)
            if s != cur:
                if colors.get(cur):
                    out.append(f'<rect x="{ox + start}" y="{oy + j}" width="{(row[k - 1][0] + 1) - start}" height="1" fill="{colors[cur]}"/>')
                if i is not None:
                    start, cur = i, s
    return "".join(out)


def wordmark(fill, text="CYENCE"):
    gs, cmap, hmtx = FONT.getGlyphSet(), FONT.getBestCmap(), FONT["hmtx"]
    s = CAP / FONT["OS/2"].sCapHeight
    names = [cmap[ord(c)] for c in text]
    x = TEXT_RIGHT - sum(hmtx[n][0] for n in names) * s
    paths = []
    for n in names:
        pen = SVGPathPen(gs)
        gs[n].draw(pen)
        paths.append(f'<path transform="translate({x:.3f} {BASELINE}) scale({s:.6f} {-s:.6f})" d="{pen.getCommands()}"/>')
        x += hmtx[n][0] * s
    return f'<g fill="{fill}">{"".join(paths)}</g>'


# Colour schemes: frame/text colour, inside, tile colours.
SCHEMES = {
    "color": dict(frame=INK, inside=CREAM, mode="color", tile={"ink": INK, "yellow": YELLOW, "blue": BLUE}),
    "color-white": dict(frame=INK, inside=WHITE, mode="color", tile={"ink": INK, "yellow": YELLOW, "blue": BLUE}),
    "black": dict(frame=BLACK, inside=WHITE, mode="mono", tile={"ink": BLACK}),
    "negative": dict(frame=WHITE, inside=BLACK, mode="mono", tile={"ink": WHITE}),
}


def frame_svg(width, height, sc):
    return (f'<rect width="{width}" height="{height}" fill="{sc["frame"]}"/>'
            f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" fill="{sc["inside"]}"/>')


def logo(scheme="color", extra=""):
    sc = SCHEMES[scheme]
    body = frame_svg(W, H, sc) + runs(tile_cells(sc["mode"]), sc["tile"]) + wordmark(sc["frame"]) + extra
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">{body}</svg>'


def icon(scheme="color", extra=""):
    sc = SCHEMES[scheme]
    s = TILE + 2
    body = frame_svg(s, s, sc) + runs(tile_cells(sc["mode"]), sc["tile"]) + extra
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" shape-rendering="crispEdges">{body}</svg>'


def main():
    OUT.mkdir(exist_ok=True)
    for scheme in SCHEMES:
        (OUT / f"cyence-logo-{scheme}.svg").write_text(logo(scheme))
        (OUT / f"cyence-icon-{scheme}.svg").write_text(icon(scheme))
    print("\n".join(sorted(p.name for p in OUT.glob("*.svg"))))


if __name__ == "__main__":
    main()
