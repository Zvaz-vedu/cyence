"""Builds the CYENCE logo manual (design/logo/manual.html) from the same code
as the logo files, so the manual always shows exactly what the files contain.

    python design/logo/manual.py
"""
import base64
import math
from datetime import date

import build as L

FONTS = {name: base64.b64encode((L.ROOT / f"static/fonts/zv-{name}.woff2").read_bytes()).decode() for name in ("display", "regular", "bold")}


def wave_tile(which):
    """The 12 × 12 tile showing one wave only (or both), with its source(s)."""
    cells = []
    for j in range(L.TILE):
        for i in range(L.TILE):
            a = L.crest(i, j, L.SOURCES["yellow"]) and which in ("yellow", "both")
            b = L.crest(i, j, L.SOURCES["blue"]) and which in ("blue", "both")
            cells.append((i, j, "ink" if a and b else "yellow" if a else "blue" if b else "bg"))
    rects = L.runs(cells, {"ink": L.INK, "yellow": L.YELLOW, "blue": L.BLUE}, ox=0, oy=0)
    marks = ""
    for name, (x, y, _) in L.SOURCES.items():
        if which in (name, "both"):
            marks += (f'<circle cx="{x}" cy="{y}" r="0.42" fill="{L.CREAM}" stroke="{L.INK}" stroke-width="0.14"/>')
    return (f'<svg viewBox="-0.5 -0.5 {L.TILE + 1} {L.TILE + 1}" shape-rendering="crispEdges" role="img" aria-label="{which} wave">'
            f'<rect x="0" y="0" width="{L.TILE}" height="{L.TILE}" fill="{L.CREAM}"/>{rects}'
            f'<g shape-rendering="geometricPrecision">{marks}</g>'
            f'<rect x="0" y="0" width="{L.TILE}" height="{L.TILE}" fill="none" stroke="{L.INK}" stroke-width="0.06"/></svg>')


def construction():
    """The logo on its unit grid with dimension call-outs."""
    W, H = L.W, L.H
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(W + 1))
    grid += "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(H + 1))
    inner = L.logo("color").split(">", 1)[1].rsplit("</svg>", 1)[0]
    cap_top = L.BASELINE - L.CAP

    def dim_h(x1, x2, y, label, above=True):
        ty = y - 0.55 if above else y + 1.5
        return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/><line x1="{x1}" y1="{y - 0.25}" x2="{x1}" y2="{y + 0.25}"/>'
                f'<line x1="{x2}" y1="{y - 0.25}" x2="{x2}" y2="{y + 0.25}"/>'
                f'<text x="{(x1 + x2) / 2}" y="{ty}" text-anchor="middle" stroke="none">{label}</text>')

    def dim_v(y1, y2, x, label, left=False):
        tx = x - 0.45 if left else x + 0.45
        anchor = "end" if left else "start"
        return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/><line x1="{x - 0.25}" y1="{y1}" x2="{x + 0.25}" y2="{y1}"/>'
                f'<line x1="{x - 0.25}" y1="{y2}" x2="{x + 0.25}" y2="{y2}"/>'
                f'<text x="{tx}" y="{(y1 + y2) / 2 + 0.45}" text-anchor="{anchor}" stroke="none">{label}</text>')

    dims = (dim_h(0, W, -1.2, "36 x")
            + dim_h(1, 13, H + 1.1, "tile 12 x", above=False)
            + dim_h(L.TEXT_RIGHT, W - 1, H + 1.1, "2 x", above=False)
            + dim_h(0, 1, H + 1.1, "1 x", above=False)
            + dim_v(0, H, W + 1.2, "14 x")
            + dim_v(cap_top, L.BASELINE, -1.2, "cap height 5 x", left=True))
    return (f'<svg viewBox="-13 -3.8 {W + 18} {H + 7}" role="img" aria-label="Logo construction on the unit grid">'
            f'<g shape-rendering="crispEdges">{inner}</g>'
            f'<g stroke="{L.INK}" stroke-width="0.025" opacity="1" shape-rendering="crispEdges" class="grid">{grid}</g>'
            f'<g fill="{L.INK}" stroke="{L.INK}" stroke-width="0.06" font-family="ZV Display" font-size="1.25" stroke-linecap="square" class="dims">{dims}</g></svg>')


def clearspace():
    W, H, c = L.W, L.H, 2
    inner = L.logo("color").split(">", 1)[1].rsplit("</svg>", 1)[0]
    return (f'<svg viewBox="{-c - 0.2} {-c - 0.2} {W + 2 * c + 0.4} {H + 2 * c + 0.4}" role="img" aria-label="Clear space of 2 x around the logo">'
            f'<rect x="{-c}" y="{-c}" width="{W + 2 * c}" height="{H + 2 * c}" fill="{L.YELLOW}"/>'
            f'<g shape-rendering="crispEdges">{inner}</g>'
            f'<rect x="{-c}" y="{-c}" width="{W + 2 * c}" height="{H + 2 * c}" fill="none" stroke="{L.INK}" stroke-width="0.08" stroke-dasharray="0.4 0.3"/>'
            f'<g fill="{L.INK}" font-family="ZV Display" font-size="0.9"><text x="{-c + 0.3}" y="{-c + 1.3}">2 x</text></g></svg>')


def misuse():
    """Six incorrect uses, drawn from the real logo."""
    logo = L.logo("color")
    body = logo.split(">", 1)[1].rsplit("</svg>", 1)[0]
    vb = f'viewBox="-3 -3 {L.W + 6} {L.H + 6}"'
    other = L.SOURCES.copy()
    L.SOURCES = {"yellow": (6, 6, 2), "blue": (6, 6, 2.6)}
    wrong_tile = L.logo("color").split(">", 1)[1].rsplit("</svg>", 1)[0]
    L.SOURCES = other
    no_frame = body.replace(f'<rect width="{L.W}" height="{L.H}" fill="{L.INK}"/>', "", 1).replace(f'fill="{L.CREAM}"', f'fill="none"', 1)
    recolor = body.replace(f'<g fill="{L.INK}">', f'<g fill="{L.BLUE}">')
    typed = body.split('<g fill="#231f20"><path')[0] + f'<text x="{L.TEXT_RIGHT}" y="{L.BASELINE}" text-anchor="end" font-family="Georgia, serif" font-size="6.4" fill="{L.INK}">Cyence</text>'
    items = [
        ("Do not stretch or squash", f'<svg {vb}><g transform="translate(0 2) scale(1 0.62)">{body}</g></svg>'),
        ("Do not rotate", f'<svg {vb}><g transform="rotate(-8 18 7)">{body}</g></svg>'),
        ("Do not recolour the wordmark", f'<svg {vb}>{recolor}</svg>'),
        ("Do not remove the frame", f'<svg {vb}>{no_frame}</svg>'),
        ("Do not swap in another pattern", f'<svg {vb}>{wrong_tile}</svg>'),
        ("Do not retype the name", f'<svg {vb}>{typed}</svg>'),
    ]
    return "".join(f'<figure class="dont"><div class="dont-art">{svg}<span class="x" aria-hidden="true">×</span></div><figcaption>{t}</figcaption></figure>' for t, svg in items)


def page():
    color, white, black, neg = (L.logo(s) for s in ("color", "color-white", "black", "negative"))
    icons = {s: L.icon(s) for s in ("color", "black", "negative")}
    today = date.today().strftime("%-d %B %Y")
    swatches = [("Cream", "#f2ede6", "242 237 230", "Background, inside the frame"), ("ZV! Black", "#231f20", "35 31 32", "Frame, wordmark, overlaps"),
                ("ZV! Yellow", "#ffc300", "255 195 0", "Yellow wave"), ("CYENCE Blue", "#00aeef", "0 174 239", "Blue wave")]
    swatch_html = "".join(
        f'<div class="swatch"><div class="chip" style="background:{h}"></div><p class="label">{n}</p><dl><div><dt>HEX</dt><dd>{h.upper()}</dd></div><div><dt>RGB</dt><dd>{rgb}</dd></div></dl><p class="note">{use}</p></div>'
        for n, h, rgb, use in swatches)
    files = [("cyence-logo-color.svg", "Primary logo – on cream, white, yellow or blue"), ("cyence-logo-color-white.svg", "Primary logo with a white inside – for print on white paper"),
             ("cyence-logo-black.svg", "Black & white – one-colour print, stamps, engraving"), ("cyence-logo-negative.svg", "Negative – on black or dark photos"),
             ("cyence-icon-color.svg", "Icon – favicon, social media avatar"), ("cyence-icon-black.svg", "Icon, black & white"), ("cyence-icon-negative.svg", "Icon, negative")]
    files_html = "".join(f'<li><code>design/logo/cyence/{f}</code><span>{d}</span></li>' for f, d in files)

    return f"""<title>CYENCE Logo Manual</title>
<meta name="description" content="How to use the CYENCE logo: construction, versions, colours, sizes and misuse.">
<style>
@font-face {{ font-family: "ZV Display"; src: url(data:font/woff2;base64,{FONTS["display"]}) format("woff2"); font-display: block; }}
@font-face {{ font-family: "ZV"; src: url(data:font/woff2;base64,{FONTS["regular"]}) format("woff2"); font-weight: 400; font-display: block; }}
@font-face {{ font-family: "ZV"; src: url(data:font/woff2;base64,{FONTS["bold"]}) format("woff2"); font-weight: 700; font-display: block; }}

/* One visual world: the CYENCE identity is light-only, so the manual is too.
   Layout: a 12-column sheet, sections numbered like a real manual. */
:root {{
  --cream: #f2ede6; --ink: #231f20; --yellow: #ffc300; --blue: #00aeef; --white: #ffffff; --black: #000000;
  --display: "ZV Display", "Arial Narrow", sans-serif;
  --body: "ZV", "Arial", sans-serif;
  --gutter: clamp(16px, 4vw, 56px);
  color-scheme: light;
}}
body {{ background: var(--cream); color: var(--ink); font-family: var(--body); font-size: 18px; line-height: 1.55; font-synthesis: none; }}
.sheet {{ max-width: 1200px; margin: 0 auto; padding-inline: var(--gutter); padding-block: 40px 96px; display: flex; flex-direction: column; gap: 112px; }}
h1, h2, h3, .label, .eyebrow, dt, figcaption, .x {{ font-family: var(--display); text-transform: uppercase; font-weight: 400; }}
h1 {{ font-size: clamp(48px, 9vw, 120px); line-height: .92; margin: 0; text-wrap: balance; }}
h2 {{ font-size: clamp(32px, 4.5vw, 56px); line-height: 1; margin: 0; text-wrap: balance; }}
h3 {{ font-size: 22px; line-height: 1.1; margin: 0; }}
p {{ margin: 0; max-width: 62ch; }}
strong {{ font-weight: 700; }}
code {{ font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 14px; }}
svg {{ display: block; width: 100%; height: auto; }}
.eyebrow {{ font-size: 16px; letter-spacing: .02em; }}

header.cover {{ display: grid; gap: 40px; }}
.cover-meta {{ display: flex; flex-wrap: wrap; gap: 8px 32px; align-items: baseline; }}
.status {{ font-family: var(--display); text-transform: uppercase; background: var(--blue); padding: 6px 12px 4px; }}
.cover-logo {{ background: var(--cream); }}

section {{ display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 32px var(--gutter); border-top: 2px solid var(--ink); padding-top: 24px; }}
.sec-head {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 16px var(--gutter); align-items: baseline; }}
.sec-head .num {{ grid-column: span 2; font-family: var(--display); font-size: 22px; }}
.sec-head h2 {{ grid-column: span 10; }}
.sec-head p {{ grid-column: 3 / -1; }}
.full {{ grid-column: 1 / -1; }}

.waves {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--gutter); }}
.waves figure, .versions figure, .bgs figure {{ margin: 0; display: flex; flex-direction: column; gap: 12px; }}
figcaption {{ font-size: 16px; }}
figcaption span {{ display: block; font-family: var(--body); text-transform: none; font-size: 15px; }}

.construction {{ grid-column: 1 / -1; background: var(--white); padding: 24px; }}
.construction .grid {{ opacity: .35; }}
.specs {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px var(--gutter); margin: 0; }}
.specs div {{ border-top: 2px solid var(--ink); padding-top: 8px; }}
.specs dd {{ margin: 4px 0 0; }}

.versions {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 40px var(--gutter); }}
.tile {{ padding: 32px; }}
.on-white {{ background: var(--white); }} .on-cream {{ background: var(--cream); outline: 2px solid var(--ink); outline-offset: -2px; }}
.on-yellow {{ background: var(--yellow); }} .on-blue {{ background: var(--blue); }} .on-black {{ background: var(--black); }} .on-ink {{ background: var(--ink); }}
.icons {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--gutter); }}
.icons .tile {{ display: grid; place-items: center; }}
.icons .tile svg {{ width: min(180px, 100%); }}

.bgs {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px var(--gutter); }}
.swatches {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--gutter); }}
.swatch .chip {{ aspect-ratio: 1; outline: 2px solid var(--ink); outline-offset: -2px; }}
.swatch .label {{ font-size: 22px; margin-top: 12px; }}
.swatch dl {{ margin: 8px 0; display: grid; gap: 2px; font-variant-numeric: tabular-nums; }}
.swatch dl div {{ display: flex; gap: 12px; }}
.swatch dt {{ width: 44px; font-size: 15px; }}
.swatch dd {{ margin: 0; font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 14px; }}
.note {{ font-size: 15px; }}

.sizes {{ grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 32px 64px; align-items: flex-end; background: var(--white); padding: 32px; }}
.sizes figure {{ margin: 0; display: flex; flex-direction: column; gap: 10px; }}

.donts {{ grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 40px var(--gutter); }}
.dont {{ margin: 0; display: flex; flex-direction: column; gap: 10px; }}
.dont-art {{ position: relative; background: var(--white); }}
.x {{ position: absolute; top: 6px; right: 10px; font-size: 40px; line-height: 1; }}

.files {{ grid-column: 1 / -1; list-style: none; margin: 0; padding: 0; }}
.files li {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: 4px 24px; padding: 12px 0; border-top: 2px solid var(--ink); }}
.files li:last-child {{ border-bottom: 2px solid var(--ink); }}
.files code {{ overflow-wrap: anywhere; }}

@media (max-width: 760px) {{
  .sec-head .num, .sec-head h2, .sec-head p {{ grid-column: 1 / -1; }}
  .waves, .versions, .icons, .bgs, .donts {{ grid-template-columns: minmax(0, 1fr); }}
  .swatches, .specs {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .files li {{ grid-template-columns: minmax(0, 1fr); }}
  .tile {{ padding: 20px; }}
}}
</style>

<main class="sheet">
  <header class="cover">
    <div class="cover-meta">
      <span class="eyebrow">CYENCE – Czech Youth Expo &amp; Conference</span>
      <span class="status">Proposal · {today}</span>
    </div>
    <h1>Logo manual</h1>
    <div class="cover-logo">{color}</div>
    <p>This proposal follows the logo system of Zvaž vědu! and Generace vesmír: a framed rectangle with an icon on the left and the name on the right. The icon is the CYENCE interference pattern itself. It is a proposal to discuss with the identity designer; nothing here is final.</p>
  </header>

  <section aria-labelledby="s1">
    <div class="sec-head"><span class="num">01</span><h2 id="s1">The icon is a frozen wave</h2>
      <p>Two sources, one yellow and one blue, each send out circular waves. A cell on a yellow crest is yellow, on a blue crest blue, on both black, and on neither it stays cream. The icon is one fixed 12 × 12 frame of this interference, the same rule that draws every pattern on the website.</p></div>
    <div class="waves">
      <figure>{wave_tile("yellow")}<figcaption>Yellow wave<span>Source at column 2, row 10; a crest every 3.2 cells. On its own, this wave is the black &amp; white logo.</span></figcaption></figure>
      <figure>{wave_tile("blue")}<figcaption>Blue wave<span>Source at column 11, row 3; a crest every 4.5 cells.</span></figcaption></figure>
      <figure>{wave_tile("both")}<figcaption>Interference<span>Where both crests meet, the cell turns black.</span></figcaption></figure>
    </div>
  </section>

  <section aria-labelledby="s2">
    <div class="sec-head"><span class="num">02</span><h2 id="s2">Construction</h2>
      <p>Everything sits on one grid. The unit <strong>x</strong> is the thickness of the frame, and every other measure is a whole number of x: the icon, the wordmark and the margins all snap to the same cells.</p></div>
    <div class="construction">{construction()}</div>
    <dl class="specs">
      <div><dt>Logo</dt><dd>36 × 14 x (2.57 : 1)</dd></div>
      <div><dt>Frame</dt><dd>1 x on all sides</dd></div>
      <div><dt>Icon</dt><dd>12 × 12 x, flush with the frame</dd></div>
      <div><dt>Wordmark</dt><dd>ZV! Display, cap height 5 x, 2 x from the frame</dd></div>
    </dl>
    <div class="full">{clearspace()}</div>
    <p class="full">Keep a clear space of at least <strong>2 x</strong> around the logo (yellow above). No text, image edge or other logo may enter it.</p>
  </section>

  <section aria-labelledby="s3">
    <div class="sec-head"><span class="num">03</span><h2 id="s3">Versions</h2>
      <p>Use the primary colour logo wherever colour is available. The black &amp; white version is for one-colour print. In one colour the two waves cannot be told apart and their interference would read as random squares, so it shows the yellow wave alone: the same tile, the same rings, one colour.</p></div>
    <div class="versions">
      <figure><div class="tile on-cream">{color}</div><figcaption>Primary<span>Colour on cream. The default everywhere.</span></figcaption></figure>
      <figure><div class="tile on-white">{white}</div><figcaption>Primary, white inside<span>For print on white paper.</span></figcaption></figure>
      <figure><div class="tile on-white">{black}</div><figcaption>Black &amp; white<span>One-colour print, stamps, engraving, fax-quality copies.</span></figcaption></figure>
      <figure><div class="tile on-black">{neg}</div><figcaption>Negative<span>White on black or on dark, calm photos.</span></figcaption></figure>
    </div>
    <div class="icons">
      <figure><div class="tile on-cream">{icons["color"]}</div><figcaption>Icon<span>Favicon, app and social media avatar.</span></figcaption></figure>
      <figure><div class="tile on-white">{icons["black"]}</div><figcaption>Icon, black &amp; white</figcaption></figure>
      <figure><div class="tile on-black">{icons["negative"]}</div><figcaption>Icon, negative</figcaption></figure>
    </div>
  </section>

  <section aria-labelledby="s4">
    <div class="sec-head"><span class="num">04</span><h2 id="s4">Backgrounds</h2>
      <p>The logo is a closed rectangle, so the colour version holds on every brand colour. On black or dark photos switch to the negative.</p></div>
    <div class="bgs">
      <figure><div class="tile on-cream">{color}</div><figcaption>Cream</figcaption></figure>
      <figure><div class="tile on-yellow">{color}</div><figcaption>Yellow</figcaption></figure>
      <figure><div class="tile on-blue">{color}</div><figcaption>Blue</figcaption></figure>
      <figure><div class="tile on-white">{white}</div><figcaption>White</figcaption></figure>
      <figure><div class="tile on-ink">{neg}</div><figcaption>ZV! Black</figcaption></figure>
      <figure><div class="tile on-black">{neg}</div><figcaption>Black</figcaption></figure>
    </div>
  </section>

  <section aria-labelledby="s5">
    <div class="sec-head"><span class="num">05</span><h2 id="s5">Colour &amp; type</h2>
      <p>The logo uses only the four CYENCE colours. The wordmark is ZV! Display in capitals; it is part of the artwork, so always use the files rather than typing the name. Print values (CMYK, Pantone) are to be confirmed with the designer.</p></div>
    <div class="swatches">{swatch_html}</div>
  </section>

  <section aria-labelledby="s6">
    <div class="sec-head"><span class="num">06</span><h2 id="s6">Minimum size</h2>
      <p>Below these sizes the pattern turns into noise. Use the icon on its own where the full logo would be smaller.</p></div>
    <div class="sizes">
      <figure><div style="width:120px">{color}</div><figcaption>Logo: 120 px wide<span>30 mm in print</span></figcaption></figure>
      <figure><div style="width:32px">{icons["color"]}</div><figcaption>Icon: 32 px<span>10 mm in print</span></figcaption></figure>
    </div>
  </section>

  <section aria-labelledby="s7">
    <div class="sec-head"><span class="num">07</span><h2 id="s7">Don’t</h2>
      <p>The logo works because every part is fixed to the grid. Keep it whole.</p></div>
    <div class="donts">{misuse()}</div>
  </section>

  <section aria-labelledby="s8">
    <div class="sec-head"><span class="num">08</span><h2 id="s8">Files</h2>
      <p>All versions are SVG files generated by <code>design/logo/build.py</code> in the CYENCE website repository. Change the pattern or proportions there and every file, and this manual, update together.</p></div>
    <ul class="files">{files_html}</ul>
  </section>
</main>
"""


if __name__ == "__main__":
    L.main()
    out = L.Path(__file__).parent / "manual.html"
    out.write_text(page())
    print("manual:", out, round(out.stat().st_size / 1024), "kB")
