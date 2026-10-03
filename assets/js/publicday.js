// Public Day map: hovering a host region previews it, clicking it (or a city
// button) shows that city's panel; clicking again returns to the general
// panel. The selection is kept in the URL hash (#brno) so it can be shared.

export function initPublicDay() {
  const root = document.querySelector("[data-pd]");
  if (!root) return;

  const svg = root.querySelector("svg");
  const panels = [...root.querySelectorAll("[data-pd-panel]")];
  const buttons = [...root.querySelectorAll("[data-pd-select]")];
  const parts = (region) => svg.querySelectorAll(`.stop[data-region="${region}"], .marker[data-region="${region}"]`);
  const regionOf = (el) => el.closest(".stop, .marker, .label")?.dataset.region;
  let selected = null;
  let hovered = null;

  function setHover(region) {
    if (hovered) parts(hovered).forEach((el) => el.classList.remove("is-hover"));
    hovered = region;
    if (hovered) parts(hovered).forEach((el) => el.classList.add("is-hover"));
  }

  function select(region, { updateHash = true } = {}) {
    if (selected) parts(selected).forEach((el) => el.classList.remove("is-selected"));
    selected = region === selected ? null : region;
    if (selected) parts(selected).forEach((el) => el.classList.add("is-selected"));

    const show = selected || "general";
    panels.forEach((p) => (p.hidden = p.dataset.pdPanel !== show));
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.pdSelect === selected)));

    if (updateHash) {
      const city = buttons.find((b) => b.dataset.pdSelect === selected)?.dataset.pdCity;
      history.replaceState(null, "", city ? `#${city}` : location.pathname + location.search);
    }
  }

  svg.addEventListener("click", (e) => {
    const region = regionOf(e.target);
    if (region) select(region);
  });
  svg.addEventListener("mouseover", (e) => setHover(regionOf(e.target) || null));
  svg.addEventListener("mouseleave", () => setHover(null));

  // City buttons select on the map; they are real links for no-JS visitors.
  for (const b of buttons) {
    b.addEventListener("click", (e) => {
      e.preventDefault();
      select(b.dataset.pdSelect);
    });
  }

  const fromHash = buttons.find((b) => b.dataset.pdCity === location.hash.slice(1));
  if (fromHash) select(fromHash.dataset.pdSelect, { updateHash: false });
}
