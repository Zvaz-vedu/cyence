import { initPatterns } from "./pattern.js";
import { initReveal } from "./reveal.js";
import { initProjects } from "./projects.js";
import { initPublicDay } from "./publicday.js";

initPatterns();

initProjects();
initPublicDay();
initReveal();

// Mobile menu: full-screen panel toggled by the MENU button.
const toggle = document.querySelector("[data-menu-toggle]");
const panel = document.querySelector("[data-mobile-nav]");

function setMenu(open) {
  toggle.setAttribute("aria-expanded", String(open));
  panel.hidden = !open;
  toggle.querySelector("[data-label-closed]").hidden = open;
  toggle.querySelector("[data-label-open]").hidden = !open;
  document.documentElement.classList.toggle("overflow-hidden", open);
}

if (toggle && panel) {
  toggle.addEventListener("click", () => setMenu(panel.hidden));
  window.matchMedia("(min-width: 80rem)").addEventListener("change", (e) => {
    if (e.matches) setMenu(false);
  });
}

// Desktop dropdowns: toggle on click, close on Escape / outside click / focus leaving.
const dropdowns = [...document.querySelectorAll("[data-dropdown]")];

function setDropdown(dd, open) {
  dd.querySelector("button").setAttribute("aria-expanded", String(open));
  dd.querySelector("ul").hidden = !open;
}

for (const dd of dropdowns) {
  const button = dd.querySelector("button");
  button.addEventListener("click", () => setDropdown(dd, button.getAttribute("aria-expanded") !== "true"));
  dd.addEventListener("focusout", (e) => {
    if (!dd.contains(e.relatedTarget)) setDropdown(dd, false);
  });
}

document.addEventListener("click", (e) => {
  for (const dd of dropdowns) if (!dd.contains(e.target)) setDropdown(dd, false);
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  for (const dd of dropdowns) {
    if (dd.querySelector("button").getAttribute("aria-expanded") === "true") {
      setDropdown(dd, false);
      dd.querySelector("button").focus();
    }
  }
  if (panel && !panel.hidden) {
    setMenu(false);
    toggle.focus();
  }
});

// News carousel: previous / next scroll by one card.
for (const carousel of document.querySelectorAll("[data-carousel]")) {
  const track = carousel.querySelector("[data-carousel-track]");
  const step = (dir) => {
    const card = track.firstElementChild;
    const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
    track.scrollBy({ left: dir * (card.offsetWidth + gap), behavior: "smooth" });
  };
  carousel.querySelector("[data-carousel-prev]").addEventListener("click", () => step(-1));
  carousel.querySelector("[data-carousel-next]").addEventListener("click", () => step(1));
}
