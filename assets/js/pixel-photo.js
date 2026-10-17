// Pixel graphics (split block with `pixelated: true` and `photo`): a small
// toy. The picture starts as pixels. A click (tap, Enter/Space) sends a wave
// out from that point that flips the picture to the opposite of what is
// shown where you clicked: pixels → the original photo, photo → pixels.
// Every wave runs to the end; several can run at once, and where they
// overlap the newer one wins. When the waves have settled and some photo is
// showing, it turns back to pixels by itself after a while. With reduced
// motion the picture switches without a wave.
//
// <div class="relative" data-pixel-photo="/images/pixel/x-photo.jpg"
//      data-cells="80" role="button" tabindex="0"><img …></div>

const SPEED = 20; // cells per second – how fast the front travels
const SCATTER = 9; // cells: blocks switch scattered over this band around the front
const BLOCK = 2; // the wave works in blocks of BLOCK × BLOCK picture cells
const STAY = 7000; // ms the photo stays before turning back by itself

const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function setup(box) {
  const cells = Number(box.dataset.cells) || 80;
  // The original photo loads only once the picture comes near the screen.
  const photo = new Image();
  const io = new IntersectionObserver(
    (entries) => {
      if (!entries.some((e) => e.isIntersecting)) return;
      photo.src = box.dataset.pixelPhoto;
      io.disconnect();
    },
    { rootMargin: "300px" },
  );
  io.observe(box);

  const canvas = document.createElement("canvas");
  canvas.setAttribute("aria-hidden", "true");
  Object.assign(canvas.style, { position: "absolute", inset: "0", width: "100%", height: "100%", pointerEvents: "none" });
  box.append(canvas);
  const ctx = canvas.getContext("2d");

  let rows = cells;
  let state = new Uint8Array(0); // what each cell shows now: 1 = photo
  let stamp = new Float64Array(0); // start time of the wave that last set the cell
  let jitter = new Float32Array(0); // per-cell (per-block) offset of the front
  let waves = []; // { x, y, start, to, last }
  let backTimer = 0;
  let raf = 0;

  const cx = (i, w) => Math.round((i * w) / cells);
  const cy = (j, h) => Math.round((j * h) / rows);

  const paintCell = (k, on) => {
    const i = k % cells;
    const j = Math.floor(k / cells);
    const W = canvas.width;
    const H = canvas.height;
    const [x, y, w, h] = [cx(i, W), cy(j, H), cx(i + 1, W) - cx(i, W), cy(j + 1, H) - cy(j, H)];
    if (on) {
      const pw = photo.naturalWidth;
      const ph = photo.naturalHeight;
      ctx.drawImage(photo, cx(i, pw), cy(j, ph), cx(i + 1, pw) - cx(i, pw), cy(j + 1, ph) - cy(j, ph), x, y, w, h);
    } else {
      ctx.clearRect(x, y, w, h);
    }
  };

  const set = (k, on) => {
    if (state[k] !== on) {
      state[k] = on;
      paintCell(k, on);
    }
  };

  const size = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(box.clientWidth * dpr);
    canvas.height = Math.round(box.clientHeight * dpr);
    rows = Math.round((cells * box.clientHeight) / box.clientWidth) || cells;
    const old = state;
    state = new Uint8Array(cells * rows);
    stamp = new Float64Array(cells * rows);
    // One random offset per wave block (within ±SCATTER/2), shared by its
    // cells: blocks switch a little ahead of or behind the front.
    const blockJitter = new Map();
    jitter = Float32Array.from({ length: cells * rows }, (_, k) => {
      const b = `${Math.floor((k % cells) / BLOCK)},${Math.floor(Math.floor(k / cells) / BLOCK)}`;
      if (!blockJitter.has(b)) blockJitter.set(b, (Math.random() - 0.5) * SCATTER);
      return blockJitter.get(b);
    });
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Keep showing what was shown (e.g. after rotating a phone).
    if (old.length === state.length && photo.naturalWidth) old.forEach((v, k) => v && set(k, 1));
  };

  // Distance from (x, y) to the centre of cell k's wave block.
  const dist = (k, x, y) => {
    const bx = (Math.floor((k % cells) / BLOCK) + 0.5) * BLOCK;
    const by = (Math.floor(Math.floor(k / cells) / BLOCK) + 0.5) * BLOCK;
    return Math.hypot(bx - x, by - y);
  };

  // Each wave sets every cell its front has passed (give or take the
  // cell's offset) – unless a newer wave already set it.
  const tick = (now) => {
    for (const w of waves) {
      const r = ((now - w.start) / 1000) * SPEED;
      for (let k = 0; k < cells * rows; k++) {
        if (stamp[k] > w.start || dist(k, w.x, w.y) >= r + jitter[k]) continue;
        stamp[k] = w.start;
        set(k, w.to);
      }
      w.done = r > w.reach + SCATTER;
    }
    waves = waves.filter((w) => !w.done);
    if (waves.length) {
      raf = requestAnimationFrame(tick);
      return;
    }
    raf = 0;
    settled();
  };

  // All waves have finished: if any photo is showing, turn it back later.
  const settled = () => {
    const anyPhoto = state.some((v) => v);
    box.setAttribute("aria-pressed", String(anyPhoto));
    if (anyPhoto) backTimer = setTimeout(() => start(cells / 2, rows / 2, 0), STAY);
  };

  // A new wave from (x, y), in cells. It flips to the opposite of what the
  // clicked cell shows, unless `to` is given.
  function start(x, y, to) {
    if (!photo.complete || !photo.naturalWidth) return;
    clearTimeout(backTimer);
    const k = Math.min(rows - 1, Math.max(0, Math.floor(y))) * cells + Math.min(cells - 1, Math.max(0, Math.floor(x)));
    if (to === undefined) to = state[k] ? 0 : 1;
    if (reduced()) {
      for (let n = 0; n < cells * rows; n++) set(n, to);
      settled();
      return;
    }
    // How far the front must travel to pass the farthest corner.
    const far = Math.max(...[0, cells].flatMap((cx2) => [0, rows].map((cy2) => Math.hypot(cx2 - x, cy2 - y))));
    waves.push({ x, y, to, start: performance.now(), reach: far });
    box.setAttribute("aria-pressed", String(Boolean(to)));
    if (!raf) raf = requestAnimationFrame(tick);
  }

  size();
  new ResizeObserver(size).observe(box);

  box.addEventListener("click", (e) => {
    const rect = box.getBoundingClientRect();
    start(((e.clientX - rect.left) / rect.width) * cells, ((e.clientY - rect.top) / rect.height) * rows);
  });
  box.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    start(cells / 2, rows / 2);
  });
}

export function initPixelPhoto() {
  document.querySelectorAll("[data-pixel-photo]").forEach(setup);
}
