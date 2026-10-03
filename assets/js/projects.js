// Projects page: filter the server-rendered cards by search text, country
// and field. The filter state lives in the URL (?q=&country=&field=) so a
// filtered view can be shared; the page works without JS (all cards shown).

// Lower-case and strip diacritics, so "gymnazium" finds "Gymnázium".
const normalize = (s) =>
  s
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim();

export function initProjects() {
  const root = document.querySelector("[data-projects]");
  if (!root) return;

  const form = root.querySelector("[data-project-filters]");
  const items = [...root.querySelectorAll("[data-project-list] > li")].map((el) => ({
    el,
    country: el.dataset.country,
    field: el.dataset.field,
    text: normalize(el.dataset.search || ""),
  }));
  const count = root.querySelector("[data-project-count]");
  const empty = root.querySelector("[data-project-empty]");
  const template = root.dataset.countTemplate;
  const total = items.length;

  function read() {
    return {
      q: form.elements.q.value,
      country: form.elements.country.value,
      field: form.elements.field.value,
    };
  }

  function apply() {
    const { q, country, field } = read();
    const words = normalize(q).split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const item of items) {
      const match =
        (!country || item.country === country) &&
        (!field || item.field === field) &&
        words.every((w) => item.text.includes(w));
      item.el.hidden = !match;
      if (match) {
        shown++;
        // A card revealed by filtering after load should simply be visible.
        item.el.classList.add("is-revealed");
      }
    }
    count.textContent = template.replace("{n}", shown).replace("{total}", total);
    empty.hidden = shown > 0;

    const params = new URLSearchParams();
    if (q.trim()) params.set("q", q.trim());
    if (country) params.set("country", country);
    if (field) params.set("field", field);
    const query = params.toString();
    history.replaceState(null, "", query ? `?${query}` : location.pathname);
  }

  // Restore filters from the URL.
  const params = new URLSearchParams(location.search);
  form.elements.q.value = params.get("q") || "";
  if ([...form.elements.country.options].some((o) => o.value === params.get("country"))) {
    form.elements.country.value = params.get("country");
  }
  const fieldInput = [...form.elements.field].find((r) => r.value === (params.get("field") || ""));
  if (fieldInput) fieldInput.checked = true;

  form.addEventListener("input", apply);
  form.addEventListener("change", apply);
  form.addEventListener("reset", () => setTimeout(apply));
  root.querySelector("[data-project-reset]").addEventListener("click", () => form.reset());
  apply();
}
