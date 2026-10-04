// "Waves" – the interference pattern filling the screen. Click to move a
// source (yellow, then blue, …). After a while, the hint at the bottom turns
// into a link to the pattern lab.
import { InterferencePattern } from "./pattern.js";

const root = document.querySelector("[data-play]");
const el = root.querySelector("[data-play-field]");
const lab = root.querySelector("[data-play-lab]");
const hint = root.querySelector("[data-play-hint]");

// Edge to edge, in whole square cells: try column counts around the target
// cell size and take the one whose square cells fit the screen height most
// exactly. The remainder (a pixel or two) is cropped at the bottom edge.
function geometry() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const target = w < 640 ? 20 : 26;
  let best = null;
  for (let cols = Math.round(w / (target * 1.25)); cols <= Math.round(w / (target * 0.8)); cols++) {
    const cell = w / cols;
    const rows = Math.ceil(h / cell);
    const overflow = rows * cell - h;
    if (!best || overflow < best.overflow) best = { cols, rows, overflow };
  }
  el.style.width = `${w}px`;
  return { cols: best.cols, aspect: best.cols / best.rows };
}

const pattern = new InterferencePattern(el, {
  ...JSON.parse(el.dataset.patternOptions || "{}"),
  ...geometry(),
  animate: true,
  interactive: true,
});
window.addEventListener("resize", () => pattern.set(geometry()));

// The pattern lab link replaces the hint after 15 s or 6 clicks.
let clicks = 0;
const showLab = () => {
  if (!lab || !lab.hidden) return;
  lab.hidden = false;
  if (hint) hint.hidden = true;
};
setTimeout(showLab, 15000);
el.addEventListener("click", () => {
  if (++clicks >= 6) showLab();
});
