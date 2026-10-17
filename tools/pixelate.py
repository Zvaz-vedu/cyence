"""Turns a photo into a pixel graphic: a tone ramp from ink (#231f20) to cream
(#f2ede6), saved to static/images/pixel/<name>.png. The file is already
enlarged (`--scale` screen pixels per cell, default 16) so every browser
shows sharp cells without smoothing (split block: `image` + `pixelated: true`).
It also saves the same crop of the original photo as <name>-photo.jpg, which
the site reveals on hover / tap (split block: `photo`).

    python tools/pixelate.py <photo> <name> [--cells 80] [--tones 8]
        [--crop left,top,right,bottom] [--bg-low 3 --bg-low-from 0.62] [--scale 16]

The background becomes plain cream: light tones (the lightest two) that are
connected to the picture's edge are cleared. Studio shadows around a figure
are darker – `--bg-low` clears tones down to that level too, but only from
`--bg-low-from` (a fraction of the height) downwards, so the face is safe.
For landscapes and scenes, `--keep-bg` skips the background cleanup.
`--equalize` boosts contrast for low-contrast photos (e.g. brown on brown).
`--subject-saturation 95` is for a grey or dark object on a colourful
background (e.g. a figurine on clay): the largest connected area with
saturation below the value (0–255), holes filled, is the subject; everything
else becomes cream, and the contrast is stretched over the subject alone.
`--subject-polygon "x,y;x,y;…"` does the same with a hand-traced outline
(points in the cropped photo's pixels) – the most precise option.
Needs Pillow (`pip install pillow`).
"""
import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

INK, CREAM = (0x23, 0x1F, 0x20), (0xF2, 0xED, 0xE6)
OUT_DIR = Path(__file__).resolve().parent.parent / "static/images/pixel"


def clear_background(t, w, h, light, low=None, low_from=1.0):
    """Sets light tones connected to the edge to cream (index light-max)."""
    top = max(t)
    seen = [False] * len(t)
    queue = deque(p for i in range(w) for p in (i, (h - 1) * w + i)) + deque(p for j in range(h) for p in (j * w, j * w + w - 1))
    while queue:
        p = queue.popleft()
        x, y = p % w, p // w
        limit = low if low is not None and y >= h * low_from else light
        if seen[p] or t[p] < limit:
            continue
        seen[p] = True
        t[p] = top
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < w and 0 <= y + dy < h:
                queue.append((y + dy) * w + x + dx)
    # Lone cells left in the background.
    for p in range(len(t)):
        x, y = p % w, p // w
        n = [t[(y + dy) * w + x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < w and 0 <= y + dy < h]
        if t[p] != top and all(v == top for v in n):
            t[p] = top


def subject_mask(colour, cells, rows, threshold):
    """The largest low-saturation region (holes filled), as a cells × rows mask."""
    w, h = cells * 3, rows * 3
    sat = colour.convert("HSV").getchannel("S").filter(ImageFilter.GaussianBlur(5)).resize((w, h), Image.BOX)
    low = [v < threshold for v in sat.get_flattened_data()]
    seen = [False] * len(low)
    best = []
    for start in range(len(low)):
        if not low[start] or seen[start]:
            continue
        comp, queue = [], deque([start])
        seen[start] = True
        while queue:
            p = queue.popleft()
            comp.append(p)
            x, y = p % w, p // w
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= x + dx < w and 0 <= y + dy < h:
                    k = (y + dy) * w + x + dx
                    if low[k] and not seen[k]:
                        seen[k] = True
                        queue.append(k)
        if len(comp) > len(best):
            best = comp
    inside = [False] * len(low)
    for p in best:
        inside[p] = True
    # Fill holes: everything not reachable from the border is subject.
    outside = [False] * len(low)
    queue = deque(p for p in range(len(low)) if (p % w in (0, w - 1) or p // w in (0, h - 1)) and not inside[p])
    for p in queue:
        outside[p] = True
    while queue:
        p = queue.popleft()
        x, y = p % w, p // w
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= x + dx < w and 0 <= y + dy < h:
                k = (y + dy) * w + x + dx
                if not inside[k] and not outside[k]:
                    outside[k] = True
                    queue.append(k)
    mask = Image.new("L", (w, h))
    mask.putdata([0 if o else 255 for o in outside])
    return mask.resize((cells, rows), Image.BOX).point(lambda v: 255 if v >= 128 else 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("name")
    ap.add_argument("--cells", type=int, default=80, help="width in cells (height follows the crop)")
    ap.add_argument("--tones", type=int, default=8)
    ap.add_argument("--crop", help="left,top,right,bottom in photo pixels")
    ap.add_argument("--bg-low", type=int, help="also clear tones down to this level near the bottom")
    ap.add_argument("--bg-low-from", type=float, default=0.62)
    ap.add_argument("--keep-bg", action="store_true", help="no background cleanup (landscapes)")
    ap.add_argument("--equalize", action="store_true", help="boost contrast")
    ap.add_argument("--subject-saturation", type=int, help="subject = largest region with saturation below this")
    ap.add_argument("--subject-polygon", help="subject outline: x,y;x,y;… in cropped-photo pixels")
    ap.add_argument("--scale", type=int, default=16, help="pixels per cell in the saved file")
    a = ap.parse_args()

    colour = Image.open(a.photo).convert("RGB")
    if a.crop:
        colour = colour.crop(tuple(int(v) for v in a.crop.split(",")))
    im = colour.convert("L")
    rows = round(a.cells * im.height / im.width)
    subject = subject_mask(colour, a.cells, rows, a.subject_saturation) if a.subject_saturation else None
    if a.subject_polygon:
        outline = Image.new("L", colour.size)
        points = [tuple(float(v) for v in xy.split(",")) for xy in a.subject_polygon.split(";")]
        ImageDraw.Draw(outline).polygon(points, fill=255)
        subject = outline.resize((a.cells, rows), Image.BOX).point(lambda v: 255 if v >= 128 else 0)
    if subject:
        im = ImageOps.autocontrast(im, cutoff=1, mask=subject.resize(im.size))
    else:
        im = ImageOps.equalize(im) if a.equalize else ImageOps.autocontrast(im, cutoff=1)
    small = im.filter(ImageFilter.UnsharpMask(2, 80, 2)).resize((a.cells, rows), Image.LANCZOS)

    n = a.tones
    t = [min(n - 1, v * n // 256) for v in small.get_flattened_data()]
    if subject:
        t = [v if m else n - 1 for v, m in zip(t, subject.get_flattened_data())]
    elif not a.keep_bg:
        clear_background(t, a.cells, rows, light=n - 2, low=a.bg_low, low_from=a.bg_low_from)

    ramp = [tuple(round(INK[c] + (CREAM[c] - INK[c]) * k / (n - 1)) for c in range(3)) for k in range(n)]
    out = Image.new("RGB", (a.cells, rows))
    out.putdata([ramp[v] for v in t])
    out = out.resize((a.cells * a.scale, rows * a.scale), Image.NEAREST)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{a.name}.png"
    out.save(path, optimize=True)
    print(f"wrote {path} ({a.cells} × {rows} cells, {n} tones, {out.width} × {out.height} px)")
    # The original photo, same crop, for the hover reveal.
    photo = Image.open(a.photo).convert("RGB")
    if a.crop:
        photo = photo.crop(tuple(int(v) for v in a.crop.split(",")))
    photo = photo.resize((a.cells * a.scale // 2, rows * a.scale // 2), Image.LANCZOS)
    photo_path = OUT_DIR / f"{a.name}-photo.jpg"
    photo.save(photo_path, quality=85, optimize=True)
    print(f"wrote {photo_path}")


if __name__ == "__main__":
    main()
