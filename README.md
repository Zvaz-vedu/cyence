# CYENCE website

Website of **CYENCE – Czech Youth Expo & Conference 2027**, an international science competition and conference for young researchers (15–20), Brno, 5–12 September 2027. Organised by Zvaž vědu!, z. s. and Hvězdárna a planetárium Brno.

Static site: **Hugo** (pinned via npm) + **Tailwind CSS v4** + plain ES modules. English is the main language (`/`), Czech lives under `/cs/`. Hosted on **Netlify**; main domain `cyence.org` (`cyence.cz` and `cyence.eu` redirect to it).

This README is written so that a person or an AI assistant can work on the site without further context.

## Quick start

```bash
npm install
npm run dev      # dev server on http://localhost:1313
npm run build    # production build into public/
```

- **Always use `npm run dev` / `npm run build`, never a global `hugo`.** Hugo is pinned in `package.json` (`hugo-extended`, 0.166); an older global Hugo fails on this config (e.g. `:contentbasename`).
- The dev server sometimes caches stale templates or content (missing stylesheet, old values). Stop it, delete `public/` and `resources/_gen/`, start again. If in doubt, `npm run build` is the truth.
- Netlify builds with `npm run build` (`netlify.toml`, Node 24).

## Repository map

| Path | What it is |
|---|---|
| `content/en/`, `content/cs/` | Pages per language. **Same file name = translation** of each other. Czech URLs come from `slug:` in the Czech file. A page that exists only in `en/` is English-only. |
| `projects/` | One Markdown file per participant project (English), shown on both sites. Currently empty – see *Hidden pages*. |
| `data/` | `team.yaml`, `partners.yaml`, `roadshow.yaml` (stops of the Roadshow day), `countries.yaml`, `fields.yaml`, `czechia.json` (pixel map). |
| `i18n/en.toml`, `i18n/cs.toml` | UI strings used by templates (`T "key"`). Add every new key to both files. |
| `layouts/` | Templates (Hugo's newer layout scheme): `baseof.html`, `home.html`, `page.html`, `section.html`, `404.html`, `soon.html` (placeholder page), `play.html` (hidden "Waves" page), `pattern-lab.html`, `og-image.html`, `roadshow/`, `projects/`, `news/`. |
| `layouts/_partials/sections/` | **Content blocks** – one file per block type (see below). |
| `layouts/_partials/` | Shared parts: `head`, `header`, `footer`, `pattern` (interference pattern), `czechia-map`, `logo`, `section-heading`, `link-to`, … |
| `assets/css/main.css` | Tailwind v4 theme (colours, type scale, spacing) and a few utilities (`wrap`, `grid-12`, `display`, `btn-*`, `prose-zv`, `slogan`). |
| `assets/js/` | `main.js` (entry), `pattern.js` (pattern engine), `reveal.js` (scroll reveal), `roadshow.js` (map), `projects.js` (filters), `pixel-photo.js` (pixel pictures), `play.js` (Waves page), `lab.js` (pattern lab). |
| `assets/images/logo.svg` | The CYENCE logo (inlined). |
| `static/` | Served as is: fonts, favicon, `downloads/` (logo files), `images/logos/`, `images/team/`, `images/pixel/`, `images/og-*.png`. |
| `hugo.toml` | Site config: languages, menus, Czech section URLs, content mounts, params (`email`, dates). |
| `netlify.toml` | Build, caching headers, redirects (domains, renamed/removed pages, 404s). |

## Pages are built from blocks

Most pages have no body text; they list blocks in front matter:

```yaml
---
title: "Brno"
lead: "One-sentence intro under the title (also the meta description)."
slug: "brno"            # Czech files: the Czech URL segment
sections:
  - type: split
    kicker: "City of science"
    title: "Genetics started here"
    text: |
      Markdown text…
```

`layouts/_partials/sections.html` renders each entry with `sections/<type>.html`. Block types:

| `type` | Use | Main fields |
|---|---|---|
| `hero` | Homepage top | `headline`, `lead`, `ctas` (label, link, primary), `pattern` options |
| `intro` | Heading left, text right | `kicker`, `title`, `text` (Markdown), `links` |
| `split` | Half visual, half text | `kicker`, `title`, `text`, `reverse`, `link`; visual: pattern (default), `visual: map`, `image` (+ `frame`), or pixel picture (`image` + `pixelated: true` + `photo` + `alt` + `credit`) |
| `slogan` | Big statement | `text` (wrap words in `*…*` to underline), `color: blue` |
| `stats` | Bento of key numbers (3 or 4) | `items`: value, label, text |
| `facts` | Numbers in quarters | `items`: value, label |
| `highlights` | Numbered items | `kicker`, `title`, `text`, `items` (title, text), `link` |
| `schedule` | Day-by-day programme | `note`, `days` (date, title, text, items, highlight, link) |
| `cta` | Yellow call-to-action panel + pattern | `kicker`, `title`, `text`, `button` (label, link) |
| `people` | Team grid from `data/team.yaml` | `kicker` |
| `partners` | Partner tiers from `data/partners.yaml` | – |
| `contacts` | Contact cards | `items`: title, text, name, email, phone |
| `quotes` | Quotes | `items`: quote, name, role |
| `faq` | Questions and answers | `items`: q, a (currently unused) |
| `news`, `news-list`, `coverage`, `downloads` | News strip, news by category, media coverage, file downloads | see each template's header comment |

Links in content (`link:`) are written as page paths (`/apply`, `/about/event`) and resolve to the right language automatically (`link-to.html`). External links start with `https://`.

## Brand rules (keep them)

- **Colours:** only cream `#f2ede6` (background), ink `#231f20` (text), yellow `#ffc300`, blue `#00aeef`. Tailwind's default palette is removed. Yellow = actions (primary buttons, CTA panels), blue = highlights. No dark mode. No opacity tricks that create new colours.
- **Type:** ZV! Display in capitals for headings and key info (`display` class), ZV! Regular for text, ZV! Bold for emphasis. Fine print (photo credits) uses `text-xs`.
- **Layout:** 12-column grid (`grid-12`) with halves, thirds, quarters; generous whitespace.
- **Patterns** (`pattern.html` + `pattern.js`): yellow and blue wave sources, black where crests overlap, cream elsewhere; always whole square cells in unrotated rectangles, at least one source visible. Section patterns play briefly when scrolled into view, then stop.
- **Partner logos** are one colour (ink `#231f20`) on cream, except the Zvaž vědu! logo (ink + yellow).

## Images

- **Team photos:** `static/images/team/<surname>.webp`, square, 600 × 600. Add `photo:` (and `credit:` if the licence needs it) in `data/team.yaml`.
- **Partner logos:** `static/images/logos/`, SVG (preferred) or PNG with transparency, recoloured to ink `#231f20`. Listed in `data/partners.yaml` (tiers: organisers / general partners / partners).
- **Pixel pictures** (Brno and South Moravia pages): a photo reduced to **80 cells wide, 8 grey tones from ink to cream**, background cleared to plain cream where it helps. Saved as `static/images/pixel/<name>.png` with each cell already enlarged to **16 × 16 px** (so 1280 px wide; never rely on browser upscaling). Next to it `<name>-photo.jpg`: the **same crop** of the original photo, about 640 px wide – a click on the picture sends a wave that reveals it (`pixel-photo.js`). Put the source and licence in `credit:`.
- **Social preview images:** `static/images/og-en.png`, `og-cs.png` (1200 × 630) are screenshots of the hidden `/og-image/` and `/cs/og-image/` pages (`layouts/og-image.html`). Regenerate them when the logo or dates change.
- Photos from Wikimedia Commons need the credit their licence asks for (CC BY / BY-SA). Photos from the South Moravia Tourist Board photo bank are credited "South Moravia Tourist Board (CCRJM)".

## Hidden pages and placeholders

| What | How it is hidden | To publish |
|---|---|---|
| News (`/news/`, homepage "What's happening" strip) | `build: render/list: never` + `cascade` in `content/{en,cs}/news/_index.md`; strip removed from the homepage | Delete those lines, add the `news` block back to `content/{en,cs}/_index.md` (commented there) |
| Media (`/media/`) | `build` in `content/{en,cs}/media.md`, removed from menus | Delete `build`, add the menu entry in `hugo.toml` |
| Projects (`/projects/`) | `build` in `content/{en,cs}/projects/_index.md`, removed from menus, no project files | Add files to `projects/`, delete `build`, add the menu entry |
| Registration / interest form | Every "Apply" / "Express your interest" button points to `/register/` (`/cs/registrace/`), a "We're working on it" page (`layout: soon`) | Replace the page or redirect `/register/` to the real form |

Project file format (`projects/<slug>.md`): `title`, `students` (list), `country` (ISO code from `data/countries.yaml`), `field` (key from `data/fields.yaml`), `school`, `summary`; body = abstract. Optional: `poster`, `video` (YouTube), `contact`, `roadshow` (city key – lists the project on that Roadshow city page).

## Roadshow

The Roadshow day (9 September) visits several Czech cities. Stops are in `data/roadshow.yaml` (city key, region code, capacity, venue, `tentative`); each city has `content/{en,cs}/roadshow/<city>.md`. The pixel map (`czechia-map.html`, `data/czechia.json`) links each host region to its city page. Adding a city = a stop in the data file + the two city pages.

## Hidden extras

- **Waves** (`/play/`, `/cs/vlny/`): full-screen interactive pattern. Opened by typing "waves"/"vlny" anywhere, clicking the homepage hero pattern 5×, or from the 404 page. After 15 s or 6 clicks it links to the **pattern lab** (`/pattern-lab/`, English only), a tool for tuning pattern settings.

## Before you finish a change

- `npm run build` must run without errors or warnings.
- Update both languages (`content/en` and `content/cs`, both `i18n` files).
- Check the page in the dev server at desktop and phone width; respect `prefers-reduced-motion` in any new animation.
- Keep `netlify.toml` redirects in mind when renaming or removing pages.
