# CYENCE website – project plan

CYENCE – Czech Youth Expo & Conference 2027 · Brno, 5–12 September 2027 · organised by Zvaž vědu!, z. s.

## 1. Stack

| Area | Choice | Notes |
|---|---|---|
| Site generator | Hugo (extended), pinned per project | Installed via npm (`hugo-extended`) as a project dev-dependency, so this project's Hugo version is independent of the global one used by other projects. Same version set in `netlify.toml`. |
| CSS | Tailwind CSS v4 via Hugo's built-in `css.TailwindCSS` | Brand palette is the *only* palette; Tailwind's default colours are removed. |
| JS | Plain ES modules bundled with Hugo's `js.Build` | No framework. |
| Hosting | Netlify | Builds on push; deploy previews for branches/PRs. |
| Content editing | Directly in the repository (Markdown + data files) | No CMS: the admins edit the files themselves, largely with an LLM. |
| Forms | HTML forms → Google Apps Script web app → Google Sheet | Deferred (see §8); until then registration links go to the placeholder page `/register/`. |

## 2. Visual identity rules (from the designer)

- **Colours (only these):** cream `#f2ede6` (background), ZV! black `#231f20` (text, key info), ZV! yellow `#ffc300`, Cyence blue `#00aeef`. White appears in the logo SVG only. Any new colour must be approved by the designer.
- **Light mode only.** No dark mode or `prefers-color-scheme` handling.
- **No transparency/opacity on brand colours** – it would create colours outside the palette.
- **Contrast:** body text is black only. Yellow and blue are used as solid areas (patterns, fills, highlights), never as text colour on cream.
- **Typography:**
  - ZV! Display, ALL CAPS – headings, short texts, key info.
  - ZV! Regular – paragraphs and everything else.
  - ZV! Bold – emphasis inside Regular text, same size (like bold in Word).
  - Fonts converted `.woff` → `.woff2` (lossless; only the compression differs). All three weights already contain the full Czech character set.
- **Layout:** 12-column grid using halves, thirds and quarters (6/6, 4/4/4, 3/3/3/3, 8/4, 9/3). Generous spacing between elements (the ZV! font needs it); lots of whitespace.
- **Logo:** pattern-tile proposal (36 × 14 units, 12 × 12 interference tile + CYENCE in ZV! Display), see the logo manual. Inlined from `assets/images/logo.svg`.

## 3. Pattern engine (interference)

**How the patterns work:** two wave sources, one yellow and one blue, each send out concentric rings on a grid of square cells. A cell on a yellow crest is yellow, on a blue crest blue; where the crests overlap they interfere and the cell is black. Everything else is cream (the background). Each source has its own wavelength – in the 1920 × 1080 render (30 px cells) yellow crests repeat every ~5 cells and blue every ~9.5, and the blue source sits outside the frame.

**Rules:**
- Patterns appear only inside axis-aligned rectangles (rotation 0/90/180/270° only).
- At least one wave source must lie inside the visible rectangle (the other may be outside).
- Rectangle sizes are whole numbers of cells, so there are no thin slivers at the edges.
- Density must be calmer than in the renders (longer wavelength / fewer bands). Exact values will be set on a test page with sliders, together with the designer.

**Implementation:**
- One JS module draws the field on a small canvas, one canvas pixel per cell, scaled up with `image-rendering: pixelated`. Very cheap.
- Animated mode (homepage hero):
  - 2 sources start at random positions inside the rectangle.
  - Clicking/tapping adds a source.
  - Pauses when off-screen (IntersectionObserver).
  - Shows a static frame for visitors with `prefers-reduced-motion`.
- Static mode: smaller pattern rectangles marking sections on inner pages.
- A build-time/static export for social-media preview (OG) images.

**Open (needs the designer):**
- What is the second allowed way to use patterns? Their message mentions two but describes one.
- Waves interacting with text / page-wide waves are out of scope unless the designer approves them.

## 4. Languages

- English (primary) at `/`, Czech at `/cs/`, with translated URLs (e.g. `/about/event/` ↔ `/cs/o-akci/akce/`).
- UI strings in `i18n/en.toml` and `i18n/cs.toml`. More languages can be added later through configuration and translation files.
- Language switcher links to the translated version of the current page; `hreflang` tags for search engines.

## 5. Sitemap

- Home – hero, about, numbers bento, Roadshow map, organisers, CTA (the news strip is hidden until there is real news)
- News – `/news/` (`/cs/aktuality/`): news, events and press releases; an item is a full article or a short card linking elsewhere. **Hidden** for now (team request): `build`/`cascade` in `content/{en,cs}/news/_index.md`
- About
  - About the Event
  - About Our Team
  - About Brno
  - About South Moravia
- Apply (`/apply/`, `/cs/prihlaska/`) – who can participate/apply, projects, expectations, costs (team doc v2, p. 17). "Express your interest" goes to `/register/` (the form; placeholder for now). All "Apply" buttons and end-of-page boxes lead here.
- Programme – day-by-day schedule
- Projects – all projects on one page
- CYENCE Roadshow (`/roadshow/`, `/cs/roadshow/`; was "Public Day" for a while, old URLs redirect) – 9 Sept, "multiple cities": Brno, Prague, Pilsen, Liberec confirmed, more to be announced (Ostrava and České Budějovice removed, their URLs redirect to the overview)
- Media – press releases, press kit / logo downloads, photos/video. **Hidden** for now (team request): `build` in `content/{en,cs}/media.md`, removed from the menus
- Partners – partner logos by tier
- Contact
- Privacy policy (GDPR)
- 404

## 6. Projects

- One Markdown file per project in `/projects/<slug>.md` (English only; mounted into both language sites):
  - `title`, `students` (list), `country` (ISO code, names in `data/countries.yaml`), `field` (key from `data/fields.yaml`), `school`, `summary` (card text), body = abstract.
  - Optional: `poster` (file path), `video` (YouTube link → embedded), `contact` (e-mail or URL, only with the student's consent), `roadshow` (city key, e.g. `brno` – lists the project on that city's Roadshow page).
- **All projects on a single page.** Hugo outputs a JSON index of projects; plain JS filters client-side by:
  - country
  - topic
  - full-text search
- Around 100 projects, so no search service is needed. Filter state goes into the URL, so a filtered view can be shared.
- Each project has its own page with related projects from the same field.

## 7. Roadshow map

- Map of the 14 Czech regions (kraje), drawn as a pixel grid in the identity's cell style.
- Inline SVG, one group per region; clickable and keyboard-accessible.
- A linked list of regions as fallback.
- Selecting a region shows its venue(s), date, and participating projects, linked to the projects page with a filter.
- Region content in Markdown/data files.

## 8. Forms (deferred)

- Google Apps Script web app receives submissions and writes them to a Google Sheet.
- Honeypot field for spam; GDPR consent.
- Planned split:
  1. "I am registering myself" – adults only
  2. "My guardian is registering me" – minors, with parental consent
- Until the forms exist, every registration link points to the "We're working on it" page `/register/`.
- Exact forms (international delegations, Czech participants, Roadshow sign-ups for schools) and the consent wording are to be decided with the team.

## 9. Phases

1. ✅ **Foundations** (done 2026-10-03)
   - Project setup with Hugo pinned via npm, Tailwind v4 and the Netlify config.
   - Fonts (woff2), colours, grid, spacing and typography scale.
   - Language setup (content in `content/en` + `content/cs`); base layout, header with language switch, footer, logo component.
2. ✅ **Pattern engine** (done 2026-10-03 – lab at `/pattern-lab/`)
   - Test page with sliders (density, cell size, speed) to agree on values with the designer.
   - Reusable pattern rectangle component (static + animated).
3. ✅ **Homepage and shared templates** (done 2026-10-03) – page `sections` built from blocks: `hero`, `facts`, `intro`, `highlights`, `split`, `cta` (`layouts/_partials/sections/`).
4. ✅ **Content pages** (done 2026-10-03) – all pages built from blocks; new blocks: `schedule`, `faq`, `people` (data/team.yaml), `partners` (data/partners.yaml), `downloads`, `contacts`, `news-list`.
5. ✅ **Projects** (done 2026-10-03) – one file per project in `/projects/` (shown on both language sites), filters by search / country / field with URL state, detail pages with optional video, contact and poster.
6. ✅ **Roadshow** (done 2026-10-03, renamed from "Public Day" 2026-10-16) – overview with interactive map (click a region → city preview panel, `#city` links) + a page per city (`content/{en,cs}/roadshow/<city>.md`) with its region graphic, key facts, and projects tagged `roadshow: <city>`. Stops in `data/roadshow.yaml`.
7. ~~**CMS**~~ – built (Sveltia CMS), then removed on 2026-10-16: the admins edit the repository directly.
8. **Forms** – once designed with the team. Placeholder until then: `/register/` (`/cs/registrace/`, layout `soon`, noindex), linked from every "Apply" button and the Roadshow pages. When the form is ready, replace that page (or redirect `/register/` to the form).
9. ✅ **Easter egg: "Waves"** (done 2026-10-04) – hidden full-screen pattern `/play/` (`/cs/vlny/`, `assets/js/play.js`): click to move the wave sources; after 15 s or 6 clicks a link to the pattern lab appears. Entrances: type "waves"/"vlny" anywhere, click the hero pattern 5×, link on the 404 page.
10. **Final checks** – checks done 2026-10-16, launch pending:
   - ✅ Accessibility: axe-core (WCAG 2.1 AA + best practice) on all 67 pages, desktop and mobile – no violations. Lighthouse accessibility 100.
   - ✅ SEO: per-page descriptions (front-matter `description`, else the page lead), social preview images `static/images/og-<lang>.png` (rendered from the hidden `/og-image/` pages by `tools/og-image.mjs`), Event structured data on the homepage, robots.txt with the sitemap (blocks everything outside production builds), sitemap + hreflang. Lighthouse SEO and best practices 100.
   - ✅ Performance: Lighthouse (mobile) 99 on the tested pages; reveal measures all elements before changing them (no layout thrashing); fingerprinted CSS/JS cached for a year.
   - [ ] Launch (done by the team): Netlify site from the repo, `cyence.org` as primary domain with `cyence.cz` and `cyence.eu` as domain aliases, DNS, HTTPS.

## Repository

- Content is split by language: `content/en/` and `content/cs/` with the same file names (pages with the same path are translations; Czech URLs come from `slug`). Projects are in `projects/` (English, shown on both sites).
- `design/` (logo generator, manual, master files, designer's renders, original fonts) and `.claude/` are gitignored – they live on the maintainer's computer only.
- `tools/` (map builder, logo recolouring) and this plan stay in the repo for maintenance.

## 10. Pending inputs

- [ ] Logo: our pattern-tile proposal is live (manual: https://claude.ai/artifact/4R4VStteZWPErp6ocrkpY4) – to be reviewed with the designer. Sources (local only, `design/` is gitignored): `design/logo/build.py` → `design/logo/cyence/`; after regenerating, copy `cyence-logo-color.svg` → `assets/images/logo.svg`, `cyence-icon-color.svg` → `static/favicon.svg` (+ `static/apple-touch-icon.png`), and the three logos → `static/downloads/`.
- [ ] Final pattern parameters – designer to tune in `/pattern-lab/` and send "Copy settings" output
- [ ] Second allowed pattern usage (designer)
- [x] Team content ("WEB CYENCE.pdf", 2026-10-16): About the Event, Brno, South Moravia, Programme, Roadshow – in CS and translated to EN; technical notes applied (slower hero, Apply → form, news hidden, no SOČ mentions, new About text, "winners of Czech national competitions").
- [x] Team content v2 ("WEB CYENCE (1).pdf", 2026-10-17): Apply page, four Roadshow cities, new end-of-page slogans (students can't apply themselves, no whole classes at the Roadshow), partners per note 7 (Planetum dropped), Media hidden, team page (committee + team, photos from zvazvedu.cz, Wikimedia Commons for J. Dušek (CC BY 3.0, credited) and msmt.gov.cz for R. Plaga).
- [ ] Open from the team:
  - [ ] link to the interest FORM for national organisers ("Express your interest" → `/register/` placeholder)
  - [ ] official rules PDF (button prepared as a comment in `content/{en,cs}/apply.md`)
  - [x] pixel graphics (note 9), 2026-10-17: 80 cells, 8 tones ink→cream (`tools/pixelate.py` → `static/images/pixel/`), split block `image` + `pixelated: true` + `photo` (a click sends a wave that reveals the original, `assets/js/pixel-photo.js`) + `credit`. Brno: Mendel (public domain), astronomical clock (Wikimedia, CC0), Petrov (Wikimedia, Kojot333, CC BY 3.0). South Moravia: Lednice Chateau (Wikimedia, Pelish, CC BY-SA 3.0), Pálava hills (Wikimedia, Jan Sapák, CC BY-SA 3.0), Macocha, Venus and the vineyards with the Slunečná lookout tower (South Moravia Tourist Board photo bank, jizni-morava.cz/cz/fotobanka; Venus traced by hand with `--subject-polygon`). Source photos and the Venus outline are in the session scratchpad only – re-download from the credited pages if a picture needs redoing
  - [ ] confirm the photo-bank use with CCRJM (info@ccrjm.cz) – their page asks to be contacted
  - [ ] programme header in the doc says 5.–11. September, the day list still ends with departures on 12 September – site keeps 5–12
- [x] Logos (2026-10-16): organisers Hvězdárna Brno + Zvaž vědu!, general partners Brno + JMK, partner ESERO (Planetum dropped in v2) – in `data/partners.yaml`, shown on the Partners page. Taken from the organisations' websites and recoloured to ink with `tools/recolor-logo.py` (Zvaž vědu! kept in its own ink + yellow). Still open:
  - [x] ESERO logo (from eserocz.cz) and a larger Hvězdárna logo (748 px, from the team); a vector Hvězdárna logo would still be sharper
  - [ ] Brno's consent to use its logo (form at brno.cz/logo)
- [ ] Real content for all pages (team), in particular:
  - [ ] privacy policy – complete and get legal review
  - [ ] programme times (the day-by-day outline is in)
  - [ ] registration dates
  - [ ] number of countries ("XX" on Home)
  - [ ] replace sample news items
  - [ ] replace the 12 sample projects in `/projects/`
- [ ] Form scope + parental-consent wording (team)
- [x] Domains (2026-10-16): main `cyence.org` (`baseURL`); `cyence.cz` → Czech version, `cyence.eu` → same page on .org (redirects in `netlify.toml`; add both as domain aliases in Netlify). Contact: one address for everything, `info@zvazvedu.cz` (`email` in `hugo.toml`).
