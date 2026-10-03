import { InterferencePattern, DEFAULTS } from "./pattern.js";

const PRESETS = {
  // Measured from the designer's 1920 × 1080 render: 64 columns, yellow
  // crests every ~5 cells, blue every ~9.5.
  renders: { cols: 48, wavelengthYellow: 5, wavelengthBlue: 9.5, dutyYellow: 0.5, dutyBlue: 0.45, speed: 0.3 },
  calm: { cols: 32, wavelengthYellow: 7, wavelengthBlue: 11, dutyYellow: 0.45, dutyBlue: 0.45, speed: 0.25 },
  calmer: { cols: 24, wavelengthYellow: 8, wavelengthBlue: 12, dutyYellow: 0.4, dutyBlue: 0.4, speed: 0.2 },
};
const FIELDS = ["aspect", "cols", "wavelengthYellow", "dutyYellow", "wavelengthBlue", "dutyBlue", "speed", "outside"];

const form = document.getElementById("lab-controls");
const el = document.getElementById("lab-pattern");
const json = document.getElementById("lab-json");
const info = document.getElementById("lab-info");

const parseAspect = (v) => v.split("/").reduce((a, b) => a / b);

const state = { ...DEFAULTS, ...PRESETS.calm, aspect: "3/4", interactive: true };
const pattern = new InterferencePattern(el, { ...state, aspect: parseAspect(state.aspect) });

function syncForm() {
  for (const name of FIELDS) {
    form.elements[name].value = state[name];
    const out = form.querySelector(`output[data-for="${name}"]`);
    if (out) out.textContent = state[name];
  }
  json.textContent = JSON.stringify(Object.fromEntries(FIELDS.map((k) => [k, state[k]])), null, 2);
  info.textContent = `${pattern.cols} × ${pattern.rows} cells · ${pattern.cellSize.toFixed(1)} px per cell at this width`;
}

function apply(changes) {
  Object.assign(state, changes);
  const opts = { ...changes };
  if ("aspect" in opts) opts.aspect = parseAspect(opts.aspect);
  pattern.set(opts);
  syncForm();
}

form.addEventListener("input", (e) => {
  const { name, value } = e.target;
  if (!FIELDS.includes(name)) return;
  apply({ [name]: name === "aspect" ? value : Number(value) });
});

form.addEventListener("click", (e) => {
  const preset = e.target.closest("[data-preset]");
  if (preset) apply(PRESETS[preset.dataset.preset]);
});

document.getElementById("lab-reseed").addEventListener("click", () => pattern.resetSources());

const play = document.getElementById("lab-play");
play.addEventListener("click", () => {
  const animate = !pattern.o.animate;
  pattern.set({ animate });
  play.textContent = animate ? "Pause" : "Play";
});

document.getElementById("lab-png").addEventListener("click", () => {
  const a = document.createElement("a");
  a.href = pattern.toPNG();
  a.download = `cyence-pattern-${state.aspect.replace("/", "x")}.png`;
  a.click();
});

const copy = document.getElementById("lab-copy");
copy.addEventListener("click", async () => {
  await navigator.clipboard.writeText(json.textContent);
  copy.textContent = "Copied";
  setTimeout(() => (copy.textContent = "Copy settings"), 1500);
});

syncForm();
