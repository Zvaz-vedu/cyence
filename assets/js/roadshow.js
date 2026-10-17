// Roadshow maps (czechia-map.html with "links"): every host region is a
// link to its city page.
// - On every such map, hovering a region or its label highlights the region.
// - On the overview ([data-rs]), clicking a region (or Enter on it) shows that
//   city's panel instead of leaving the page; clicking again returns to the
//   general panel. The selection lives in the URL hash (#brno).

function parts(svg, region) {
  return svg.querySelectorAll(`.stop[data-region="${region}"], .marker[data-region="${region}"]`);
}
// The region of a clicked cell, marker, label – or of the region link itself
// (keyboard Enter clicks the <a>).
const regionOf = (el) => {
  const hit = el.closest("[data-region], [data-rs-select]");
  return hit?.dataset.region || hit?.dataset.rsSelect;
};

function initHover(svg) {
  let hovered = null;
  const set = (region) => {
    if (hovered) parts(svg, hovered).forEach((el) => el.classList.remove("is-hover"));
    hovered = region;
    if (hovered) parts(svg, hovered).forEach((el) => el.classList.add("is-hover"));
  };
  svg.addEventListener("mouseover", (e) => set(regionOf(e.target) || null));
  svg.addEventListener("mouseleave", () => set(null));
  // Label links are mouse-only duplicates of the region links: don't let a
  // click focus them.
  svg.addEventListener("mousedown", (e) => {
    if (e.target.closest("[data-rs-label]")) e.preventDefault();
  });
}

export function initRoadshow() {
  document.querySelectorAll("svg[data-rs-map]").forEach(initHover);

  const root = document.querySelector("[data-rs]");
  if (!root) return;
  const svg = root.querySelector("svg");
  const panels = [...root.querySelectorAll("[data-rs-panel]")];
  const links = [...svg.querySelectorAll("a[data-rs-select]")];
  let selected = null;

  function select(region, { updateHash = true } = {}) {
    if (selected) parts(svg, selected).forEach((el) => el.classList.remove("is-selected"));
    selected = region === selected ? null : region;
    if (selected) parts(svg, selected).forEach((el) => el.classList.add("is-selected"));

    const show = selected || "general";
    panels.forEach((p) => (p.hidden = p.dataset.rsPanel !== show));
    links.forEach((a) => (a.dataset.rsSelect === selected ? a.setAttribute("aria-current", "true") : a.removeAttribute("aria-current")));

    if (updateHash) {
      const city = links.find((a) => a.dataset.rsSelect === selected)?.dataset.rsCity;
      history.replaceState(null, "", city ? `#${city}` : location.pathname + location.search);
    }
  }

  // Region and label links select on the map instead of navigating; the
  // panel's "More about …" button leads to the city page.
  svg.addEventListener("click", (e) => {
    const region = regionOf(e.target);
    if (!region) return;
    e.preventDefault();
    select(region);
  });

  const fromHash = links.find((a) => a.dataset.rsCity === location.hash.slice(1));
  if (fromHash) select(fromHash.dataset.rsSelect, { updateHash: false });
}
