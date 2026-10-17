"""Recolours a partner logo to the site's ink colour (#231f20), so all logos
match the text. The result goes to static/images/logos/.

    python tools/recolor-logo.py <input> <output-name>

- SVG: every fill and stroke colour becomes ink; hidden elements
  (display:none) are dropped; fixed width/height are removed so the logo
  scales with CSS.
- PNG / WebP / JPG: the logo's shape is kept and filled with ink. For images
  with transparency, the alpha channel is the shape; for images on a solid
  background (white, blue, …), everything that differs from the background
  colour is the shape. Needs Pillow (`pip install pillow`).
"""
import re
import sys
from pathlib import Path

INK = "#231f20"
INK_RGB = (0x23, 0x1F, 0x20)
OUT_DIR = Path(__file__).resolve().parent.parent / "static/images/logos"


def recolor_svg(src: str) -> str:
    svg = re.sub(r"<\?xml[^>]*>|<!--.*?-->|<!DOCTYPE[^>]*>", "", src, flags=re.S)
    # Drop hidden groups (e.g. unused frames of an animated logo).
    while True:
        new = re.sub(r'<g[^>]*style="display: ?none;?"[^>]*>(?:(?!<g[\s>]).)*?</g>', "", svg, flags=re.S)
        if new == svg:
            break
        svg = new
    colour = r"(?:#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|[a-zA-Z]+)"
    svg = re.sub(rf'(fill|stroke)="(?!none|url)({colour})"', rf'\1="{INK}"', svg)
    svg = re.sub(rf"(fill|stroke):\s*(?!none|url)({colour})", rf"\1:{INK}", svg)
    # Paths without a fill default to black – make that ink too.
    svg = re.sub(r"<svg\b", f'<svg fill="{INK}"', svg, count=1)
    # Scale with CSS: no fixed size or inline style on the root.
    root = re.search(r"<svg\b[^>]*>", svg).group(0)
    clean = re.sub(r'\s(width|height|style|x|y|enable-background|xml:space|id)="[^"]*"', "", root)
    return svg.replace(root, clean, 1).strip() + "\n"


def recolor_raster(path: Path, out: Path) -> None:
    from PIL import Image

    im = Image.open(path).convert("RGBA")
    alpha = im.getchannel("A")
    if alpha.getextrema()[0] == 255:
        # No transparency: the background is the colour of the top-left
        # pixel; the further a pixel's colour is from it, the more opaque.
        rgb = im.convert("RGB")
        bg = rgb.getpixel((0, 0))
        dist = [sum((c - b) ** 2 for c, b in zip(px, bg)) ** 0.5 for px in rgb.getdata()]
        top = max(dist) or 1
        alpha = Image.new("L", im.size)
        alpha.putdata([round(255 * min(1, d / top)) for d in dist])
    ink = Image.new("RGBA", im.size, INK_RGB + (0,))
    ink.putalpha(alpha)
    ink = ink.crop(alpha.getbbox())
    ink.save(out)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, name = Path(sys.argv[1]), sys.argv[2]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".svg":
        out = OUT_DIR / f"{Path(name).stem}.svg"
        out.write_text(recolor_svg(src.read_text(encoding="utf-8")), encoding="utf-8")
    else:
        out = OUT_DIR / f"{Path(name).stem}.png"
        recolor_raster(src, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
