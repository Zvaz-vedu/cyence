// Scroll reveal: elements marked [data-reveal] assemble from square cells.
//
// Until revealed, the element is visibility:hidden (see main.css). When it
// scrolls into view, a canvas painted in the background colour behind the
// element covers it, the element becomes visible, and the canvas's cells are
// cleared one by one in random order (drifting slightly top to bottom) – the
// element appears to assemble from pixels. Only brand colours are ever drawn.

const CELL = 14; // px
const DURATION = 750; // ms
const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// The solid colour behind the element (the first ancestor with a background).
function backdrop(el) {
  for (let node = el.parentElement; node; node = node.parentElement) {
    const bg = getComputedStyle(node).backgroundColor;
    if (bg && bg !== "transparent" && !bg.startsWith("rgba(0, 0, 0, 0")) return bg;
  }
  return "#f2ede6";
}

function assemble(el) {
  const delay = parseFloat(getComputedStyle(el).getPropertyValue("--reveal-delay")) || 0;
  const rect = el.getBoundingClientRect();
  const cols = Math.max(1, Math.ceil(rect.width / CELL));
  const rows = Math.max(1, Math.ceil(rect.height / CELL));
  const dpr = Math.min(window.devicePixelRatio || 1, 2);

  const canvas = document.createElement("canvas");
  canvas.width = Math.ceil(rect.width * dpr);
  canvas.height = Math.ceil(rect.height * dpr);
  canvas.setAttribute("aria-hidden", "true");
  // Cover the border box too (absolute positioning starts inside borders).
  const cs = getComputedStyle(el);
  Object.assign(canvas.style, {
    position: "absolute",
    top: `-${cs.borderTopWidth}`,
    left: `-${cs.borderLeftWidth}`,
    width: `${rect.width}px`,
    height: `${rect.height}px`,
    pointerEvents: "none",
    zIndex: "5",
  });
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = backdrop(el);
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  if (cs.position === "static") el.style.position = "relative";
  el.appendChild(canvas);
  el.classList.add("is-revealed");

  // Each cell disappears at its own moment: random, with a top-to-bottom drift.
  const cells = [];
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      cells.push({ i, j, t: Math.random() * 0.65 + (j / rows) * 0.35 });
    }
  }
  cells.sort((a, b) => a.t - b.t);

  const xs = (i) => Math.round(i * CELL * dpr);
  let next = 0;
  let start = null;
  const tick = (now) => {
    if (start === null) start = now + delay;
    const progress = Math.max(0, (now - start) / DURATION);
    while (next < cells.length && cells[next].t <= progress) {
      const { i, j } = cells[next++];
      ctx.clearRect(xs(i), xs(j), xs(i + 1) - xs(i), xs(j + 1) - xs(j));
    }
    if (next < cells.length) requestAnimationFrame(tick);
    else canvas.remove();
  };
  requestAnimationFrame(tick);
}

export function initReveal() {
  const els = document.querySelectorAll("[data-reveal]");
  if (reduced()) {
    els.forEach((el) => el.classList.add("is-revealed"));
    return;
  }
  const io = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        io.unobserve(entry.target);
        assemble(entry.target);
      }
    },
    { rootMargin: "0px 0px -8% 0px" },
  );
  els.forEach((el) => io.observe(el));
}
