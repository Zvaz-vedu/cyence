"""Rasterise the Czech regions (kraje) into the pixel grid used by the
CYENCE map. Output: data/czechia.json. Upper-case letters are region
cells, lower-case letters region cells on a border with another region.

Source data: ČÚZK regions via https://github.com/siwekm/czech-geojson
(kraje.json). Re-run only if the grid size changes:

    pip install shapely fonttools brotli
    python tools/build-map.py path/to/kraje.json [cols]
"""
import json
import math
import sys

from fontTools.ttLib import TTFont
from shapely.geometry import Point, shape
from shapely.prepared import prep

# nationalCode in the GeoJSON -> (grid char, ISO-like code, English name)
REGIONS = {
    "19": ("A", "PHA", "Prague"),
    "27": ("B", "STC", "Central Bohemian Region"),
    "35": ("C", "JHC", "South Bohemian Region"),
    "43": ("D", "PLK", "Plzeň Region"),
    "51": ("E", "KVK", "Karlovy Vary Region"),
    "60": ("F", "ULK", "Ústí nad Labem Region"),
    "78": ("G", "LBK", "Liberec Region"),
    "86": ("H", "HKK", "Hradec Králové Region"),
    "94": ("I", "PAK", "Pardubice Region"),
    "108": ("J", "VYS", "Vysočina Region"),
    "116": ("K", "JHM", "South Moravian Region"),
    "124": ("L", "OLK", "Olomouc Region"),
    "132": ("M", "MSK", "Moravian-Silesian Region"),
    "141": ("N", "ZLK", "Zlín Region"),
}


def label_width(text, font):
    """Advance width of `text` in ZV! Display, in em (for sizing map labels)."""
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upem = font["head"].unitsPerEm
    return round(sum(hmtx[cmap[ord(ch)]][0] for ch in text if ord(ch) in cmap) / upem, 3)


def main(path, cols=96):
    font = TTFont("static/fonts/zv-display.woff2")
    features = json.load(open(path, encoding="utf-8"))["features"]
    shapes = [(REGIONS[f["nationalCode"]], f["name"], shape(f["geometry"])) for f in features]
    minx = min(s.bounds[0] for *_, s in shapes)
    miny = min(s.bounds[1] for *_, s in shapes)
    maxx = max(s.bounds[2] for *_, s in shapes)
    maxy = max(s.bounds[3] for *_, s in shapes)
    # Equirectangular projection around the country's mid latitude.
    k = math.cos(math.radians((miny + maxy) / 2))
    cell = (maxx - minx) * k / cols
    rows = math.ceil((maxy - miny) / cell)
    prepared = [(meta, prep(s)) for meta, _, s in shapes]

    def lonlat_to_cell(lon, lat):
        return int((lon - minx) * k / cell), int((maxy - lat) / cell)

    grid = []
    for j in range(rows):
        row = ""
        lat = maxy - (j + 0.5) * cell
        for i in range(cols):
            lon = minx + (i + 0.5) * cell / k
            p = Point(lon, lat)
            row += next((meta[0] for meta, s in prepared if s.contains(p)), ".")
        grid.append(row)

    # Region outlines: where two regions touch, the cell on the left/top side
    # of the boundary is marked with the lowercase letter of its region. The
    # map draws those as gaps, which outlines each region with a 1-cell line.
    cells = [list(r) for r in grid]
    for j in range(rows):
        for i in range(cols):
            c = grid[j][i]
            if c == ".":
                continue
            right = grid[j][i + 1] if i + 1 < cols else "."
            below = grid[j + 1][i] if j + 1 < rows else "."
            if (right not in (".", c)) or (below not in (".", c)):
                cells[j][i] = c.lower()
    grid = ["".join(r) for r in cells]

    cities = {
        "praha": ("Praha", "Prague", 14.4378, 50.0755),
        "brno": ("Brno", "Brno", 16.6068, 49.1951),
        "plzen": ("Plzeň", "Pilsen", 13.3776, 49.7384),
        "ostrava": ("Ostrava", "Ostrava", 18.2625, 49.8209),
        "liberec": ("Liberec", "Liberec", 15.0543, 50.7663),
        "olomouc": ("Olomouc", "Olomouc", 17.2509, 49.5938),
        "ceske-budejovice": ("České Budějovice", "České Budějovice", 14.4744, 48.9745),
        "hradec-kralove": ("Hradec Králové", "Hradec Králové", 15.8328, 50.2092),
        "usti-nad-labem": ("Ústí nad Labem", "Ústí nad Labem", 14.0323, 50.6607),
        "pardubice": ("Pardubice", "Pardubice", 15.7812, 50.0343),
        "zlin": ("Zlín", "Zlín", 17.6627, 49.2265),
        "jihlava": ("Jihlava", "Jihlava", 15.5870, 49.3961),
        "karlovy-vary": ("Karlovy Vary", "Karlovy Vary", 12.8712, 50.2306),
    }
    def bbox(char):
        """[x, y, width, height] of a region's cells, for cropped region maps."""
        pts = [(i, j) for j, r in enumerate(grid) for i, c in enumerate(r) if c.upper() == char]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return [min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1]

    out = {
        "cols": cols,
        "rows": rows,
        "source": "ČÚZK via github.com/siwekm/czech-geojson",
        "regions": {
            meta[0]: {"code": meta[1], "nameCs": name, "nameEn": meta[2], "bbox": bbox(meta[0])}
            for meta, name, _ in shapes
        },
        "cities": {
            key: {
                "nameCs": cs,
                "nameEn": en,
                "x": lonlat_to_cell(lon, lat)[0],
                "y": lonlat_to_cell(lon, lat)[1],
                # Upper-case label widths in em, so label tags fit exactly.
                "widthCs": label_width(cs.upper(), font),
                "widthEn": label_width(en.upper(), font),
            }
            for key, (cs, en, lon, lat) in cities.items()
        },
        "grid": grid,
    }
    with open("data/czechia.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("\n".join(grid))
    print(cols, "x", rows)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 96)
