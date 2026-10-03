// CYENCE interference pattern.
//
// Two sources – one yellow, one blue – each send out concentric waves. A cell
// lying on a crest of the yellow wave is yellow, on a crest of the blue wave
// blue; where the two crests overlap they interfere and the cell is black.
// Everything else is cream, the background.
//
// Identity rules this module enforces:
//   - the rectangle is always made of whole square cells (no slivers): the
//     cell size is derived from the element width, and the height snaps to a
//     whole number of rows;
//   - at least one source lies inside the visible rectangle (the other may be
//     outside);
//   - only brand colours; no transparency.

export const BRAND = {
  cream: "#f2ede6",
  ink: "#231f20",
  yellow: "#ffc300",
  blue: "#00aeef",
};

export const DEFAULTS = {
  cols: 24, // number of columns; the cell size follows from the element width
  cell: 0, // alternatively a target cell size in CSS px (0 = use cols)
  aspect: 4 / 3, // target width / height (like CSS aspect-ratio); height snaps to whole rows
  aspectMobile: 0, // optional different aspect below 768 px viewport width (0 = same)
  wavelengthYellow: 6, // distance between crests, in cells – larger = calmer
  wavelengthBlue: 10,
  dutyYellow: 0.45, // share of each wavelength that is crest (0–1)
  dutyBlue: 0.45,
  speed: 0.3, // crests travelling outward, in wavelengths per second
  outside: 0.5, // chance that the second source is placed outside the rectangle
  animate: true,
  match: "", // id of a side-by-side element whose height the pattern should cover
  runFor: 0, // seconds to animate after first coming into view, then freeze (0 = forever)
  slowDown: 2.5, // seconds it takes to ease to a halt after runFor
  interactive: false, // click / tap moves a source there (alternating colours)
  seed: 0, // 0 = random on every load
};

// Small deterministic RNG so static patterns can stay identical between loads.
function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const CREAM = 0;
const YELLOW = 1;
const BLUE = 2;
const INK = 3;
const FILLS = [BRAND.cream, BRAND.yellow, BRAND.blue, BRAND.ink];

export class InterferencePattern {
  constructor(el, options = {}) {
    this.el = el;
    this.o = { ...DEFAULTS, ...options };
    this.canvas = el.querySelector("canvas") || el.appendChild(document.createElement("canvas"));
    this.canvas.setAttribute("aria-hidden", "true");
    this.canvas.style.display = "block";
    this.canvas.style.width = "100%";
    this.ctx = this.canvas.getContext("2d", { alpha: false });
    this.rand = mulberry32(this.o.seed || Math.floor(Math.random() * 2 ** 31));
    this.time = 0;
    this.last = 0;
    this.visible = true;
    this.running = false;
    this.nextClick = "yellow";

    this.resetSources();
    this.resize();

    this.ro = new ResizeObserver(() => this.resize());
    this.ro.observe(el);
    if (this.o.match && document.getElementById(this.o.match)) this.ro.observe(document.getElementById(this.o.match));
    this.io = new IntersectionObserver((entries) => {
      this.visible = entries[entries.length - 1].isIntersecting;
      this.updateLoop();
    });
    this.io.observe(el);

    if (this.o.interactive) {
      this.onClick = (e) => this.moveSourceTo(e);
      this.canvas.addEventListener("click", this.onClick);
      this.canvas.style.cursor = "crosshair";
    }
    this.updateLoop();
  }

  // ---- configuration --------------------------------------------------------

  set(options) {
    const needsSize = ["cols", "cell", "aspect", "aspectMobile"].some((k) => k in options);
    Object.assign(this.o, options);
    if (needsSize) this.resize();
    else this.draw();
    this.updateLoop();
  }

  // Positions are fractions of the rectangle (0–1 = inside). One source is
  // always inside, away from the edges; the other is inside or, with chance
  // `outside`, up to half a rectangle beyond one of its edges.
  resetSources() {
    const r = this.rand;
    const inside = () => ({ x: 0.15 + r() * 0.7, y: 0.15 + r() * 0.7 });
    const outside = () => {
      const along = r();
      const depth = 1.05 + r() * 0.45;
      return [
        { x: along, y: -depth + 1 }, // above
        { x: along, y: depth }, // below
        { x: -depth + 1, y: along }, // left
        { x: depth, y: along }, // right
      ][Math.floor(r() * 4)];
    };
    const a = inside();
    let b = r() < this.o.outside ? outside() : inside();
    // Keep two inside sources apart; if that keeps failing, put the second
    // one outside the frame instead.
    for (let i = 0; i < 40 && Math.hypot(a.x - b.x, a.y - b.y) < 0.4; i++) b = inside();
    if (Math.hypot(a.x - b.x, a.y - b.y) < 0.4) b = outside();
    const [yellow, blue] = r() < 0.5 ? [a, b] : [b, a];
    this.sources = {
      yellow: { ...yellow, phase: r(), prev: null, born: -Infinity },
      blue: { ...blue, phase: r(), prev: null, born: -Infinity },
    };
    this.draw();
  }

  // ---- geometry -------------------------------------------------------------

  resize() {
    const width = this.el.clientWidth;
    if (!width) return;
    const { cell } = this.o;
    const aspect = (window.innerWidth < 768 && this.o.aspectMobile) || this.o.aspect;
    const cols = cell > 0 ? Math.max(4, Math.round(width / cell)) : this.o.cols;
    const cellSize = width / cols;
    let rows = Math.max(1, Math.round(width / aspect / cellSize));
    // Side by side with another element (e.g. a CTA panel): cover its natural
    // height with whole rows and stretch it to exactly the same height, so
    // both bottom edges line up without a partial row.
    const partner = this.o.match && document.getElementById(this.o.match);
    if (partner) {
      partner.style.minHeight = "";
      const sideBySide = Math.abs(partner.getBoundingClientRect().top - this.el.getBoundingClientRect().top) < 1;
      if (sideBySide) {
        rows = Math.max(1, Math.ceil(partner.offsetHeight / cellSize));
        partner.style.minHeight = `${rows * cellSize}px`;
      }
    }
    this.cols = cols;
    this.rows = rows;
    this.cellSize = cellSize;
    // The rectangle's height is exactly `rows` cells. The wrapper's CSS
    // aspect-ratio only reserves space before JS runs; drop it so the
    // wrapper hugs the canvas and no partial row can show.
    this.el.style.aspectRatio = "auto";
    this.canvas.style.height = `${rows * cellSize}px`;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    this.canvas.width = Math.round(width * dpr);
    this.canvas.height = Math.round(rows * cellSize * dpr);
    // Pixel edges for each column/row, rounded so cells tile without gaps.
    this.xEdges = Array.from({ length: cols + 1 }, (_, i) => Math.round((i * this.canvas.width) / cols));
    this.yEdges = Array.from({ length: rows + 1 }, (_, j) => Math.round((j * this.canvas.height) / rows));
    this.values = new Uint8Array(cols * rows);
    this.draw();
  }

  // ---- interaction ----------------------------------------------------------

  // Clicking moves the next source (yellow, then blue, …) to the click point.
  // Its new waves spread out from there and replace the old ones as they go.
  moveSourceTo(event) {
    const rect = this.canvas.getBoundingClientRect();
    const s = this.sources[this.nextClick];
    s.prev = { x: s.x, y: s.y, phase: s.phase };
    s.x = (event.clientX - rect.left) / rect.width;
    s.y = (event.clientY - rect.top) / rect.height;
    s.phase = 0;
    s.born = this.time;
    this.nextClick = this.nextClick === "yellow" ? "blue" : "yellow";
    if (!this.running) this.draw();
    this.updateLoop();
  }

  // ---- rendering ------------------------------------------------------------

  // Is the cell centre (cx, cy) on a crest of this source's wave?
  crest(s, cx, cy, wavelength, duty, shift) {
    const { cols, rows } = this;
    let x = s.x;
    let y = s.y;
    let phase = s.phase;
    let r = Math.hypot(cx - x * cols, cy - y * rows);
    if (s.prev) {
      // Outside the expanding front the old waves are still visible.
      const front = (this.time - s.born) * this.o.speed * wavelength * 3;
      if (r > front) {
        ({ x, y, phase } = s.prev);
        r = Math.hypot(cx - x * cols, cy - y * rows);
      }
    }
    const t = r / wavelength - shift + phase;
    return t - Math.floor(t) < duty;
  }

  draw() {
    if (!this.cols) return;
    const { cols, rows, values, sources } = this;
    const { wavelengthYellow, wavelengthBlue, dutyYellow, dutyBlue, speed } = this.o;
    const shift = speed * this.time;

    for (let j = 0; j < rows; j++) {
      const cy = j + 0.5;
      for (let i = 0; i < cols; i++) {
        const cx = i + 0.5;
        const y = this.crest(sources.yellow, cx, cy, wavelengthYellow, dutyYellow, shift);
        const b = this.crest(sources.blue, cx, cy, wavelengthBlue, dutyBlue, shift);
        values[j * cols + i] = y && b ? INK : y ? YELLOW : b ? BLUE : CREAM;
      }
    }

    // Paint runs of equal cells per row.
    const ctx = this.ctx;
    for (let j = 0; j < rows; j++) {
      const y0 = this.yEdges[j];
      const h = this.yEdges[j + 1] - y0;
      let start = 0;
      for (let i = 1; i <= cols; i++) {
        const v = values[j * cols + start];
        if (i === cols || values[j * cols + i] !== v) {
          ctx.fillStyle = FILLS[v];
          ctx.fillRect(this.xEdges[start], y0, this.xEdges[i] - this.xEdges[start], h);
          start = i;
        }
      }
    }

    // Once a moved source's front has crossed the whole rectangle, forget the
    // old position.
    const diag = Math.hypot(cols, rows) * 2.5;
    for (const [s, wl] of [
      [sources.yellow, wavelengthYellow],
      [sources.blue, wavelengthBlue],
    ]) {
      if (s.prev && (this.time - s.born) * speed * wl * 3 > diag) s.prev = null;
    }
  }

  // ---- animation loop -------------------------------------------------------

  updateLoop() {
    const shouldRun = this.o.animate && this.visible && !reducedMotion() && !document.hidden;
    if (shouldRun && !this.running) {
      this.running = true;
      this.last = performance.now();
      const tick = (now) => {
        if (!this.running) return;
        const dt = Math.min(0.1, (now - this.last) / 1000);
        this.last = now;
        // Play once, then ease to a halt on whatever frame this visitor got:
        // full speed for `runFor` seconds, then slowing down (ease-out)
        // over `slowDown` seconds.
        let rate = 1;
        if (this.o.runFor) {
          this.elapsed = (this.elapsed || 0) + dt;
          const t = (this.elapsed - this.o.runFor) / this.o.slowDown;
          if (t >= 1) {
            this.o.animate = false;
            this.running = false;
            return;
          }
          if (t > 0) rate = (1 - t) ** 2;
        }
        this.time += dt * rate;
        this.draw();
        this.raf = requestAnimationFrame(tick);
      };
      this.raf = requestAnimationFrame(tick);
    } else if (!shouldRun && this.running) {
      this.running = false;
      cancelAnimationFrame(this.raf);
    }
  }

  toPNG() {
    return this.canvas.toDataURL("image/png");
  }

  destroy() {
    this.running = false;
    cancelAnimationFrame(this.raf);
    this.ro.disconnect();
    this.io.disconnect();
    if (this.onClick) this.canvas.removeEventListener("click", this.onClick);
  }
}

// Read options from data-* attributes, e.g.
// <div data-pattern data-cols="24" data-aspect="3/4" data-animate="true">
export function optionsFromDataset(ds) {
  const o = {};
  const nums = ["cols", "cell", "wavelengthYellow", "wavelengthBlue", "dutyYellow", "dutyBlue", "speed", "outside", "seed", "runFor"];
  for (const k of nums) if (ds[k] !== undefined) o[k] = Number(ds[k]);
  const ratio = (v) => (v.includes("/") ? v.split("/").reduce((a, b) => a / b) : Number(v));
  if (ds.aspect) o.aspect = ratio(ds.aspect);
  if (ds.aspectMobile) o.aspectMobile = ratio(ds.aspectMobile);
  if (ds.match) o.match = ds.match;
  if (ds.animate !== undefined) o.animate = ds.animate !== "false";
  if (ds.interactive !== undefined) o.interactive = ds.interactive !== "false";
  return o;
}

export function initPatterns(root = document) {
  const instances = [...root.querySelectorAll("[data-pattern]")].map(
    (el) => (el.pattern = new InterferencePattern(el, optionsFromDataset(el.dataset))),
  );
  document.addEventListener("visibilitychange", () => instances.forEach((p) => p.updateLoop()));
  return instances;
}
