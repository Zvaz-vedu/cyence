# CYENCE website – project plan

CYENCE – Czech Youth Expo & Conference 2027 · Brno, 5–12 September 2027 · organised by Zvaž vědu!, z. s.

## 1. Stack

| Area | Choice | Notes |
|---|---|---|
| Site generator | Hugo (extended), pinned per project | Installed via npm (`hugo-extended`) as a project dev-dependency, so this project's Hugo version is independent of the global one used by other projects. Same version set in `netlify.toml`. |
| CSS | Tailwind CSS v4 via Hugo's built-in `css.TailwindCSS` | Brand palette is the *only* palette; Tailwind's default colours are removed. |
| JS | Plain ES modules bundled with Hugo's `js.Build` | No framework. |
| Hosting | Netlify | Builds on push; deploy previews for branches/PRs. |
| CMS | Sveltia CMS (free, open source, Decap-compatible config) | Served at `/admin/`. Editors log in with a (free) GitHub account and get access to the repo. Strong EN/CS side-by-side editing. If needed, the same config also works with Decap CMS. |
| Forms | HTML forms → Google Apps Script web app → Google Sheet | Design deferred (see §8). |

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
- **Logo:** pattern-tile proposal (36 × 14 units, 12 × 12 interference tile + CYENCE in ZV! Display), see the logo manual. Inlined from `assets/images/logo.svg`; the original placeholder is kept in `design/logo/logo-placeholder.svg`.

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

- Home – hero, news strip, about, numbers bento, roadshow map, organiser, CTA
- News – `/news/` (`/cs/aktuality/`): news, events and press releases; an item is a full article or a short card linking elsewhere
- About
  - About the Event
  - About Our Team
  - About Brno
  - About South Moravia
- Apply – information for applicants
- Programme – day-by-day schedule
- Projects – all projects on one page
- Public Day (`/public-day/`, `/cs/verejny-den/`; formerly "Roadshow", redirected) – 9 Sept, six cities, pixel map of Czechia
- Media – press releases, press kit / logo downloads, photos/video
- Partners – partner logos by tier
- Contact
- Privacy policy (GDPR)
- 404

## 6. Projects

- One Markdown file per project in `/projects/<slug>.md` (English only; mounted into both language sites):
  - `title`, `students` (list), `country` (ISO code, names in `data/countries.yaml`), `field` (key from `data/fields.yaml`), `school`, `summary` (card text), body = abstract.
  - Optional: `poster` (file path), `video` (YouTube link → embedded), `contact` (e-mail or URL, only with the student's consent), `publicDay` (city key, e.g. `brno` – lists the project on that city's Public Day page).
- **All projects on a single page.** Hugo outputs a JSON index of projects; plain JS filters client-side by:
  - country
  - topic
  - full-text search
- Around 100 projects, so no search service is needed. Filter state goes into the URL, so a filtered view can be shared.
- Each project has its own page with related projects from the same field.

## 7. Public Day map

- Map of the 14 Czech regions (kraje), drawn as a pixel grid in the identity's cell style.
- Inline SVG, one group per region; clickable and keyboard-accessible.
- A linked list of regions as fallback.
- Selecting a region shows its venue(s), date, and participating projects, linked to the projects page with a filter.
- Region content in Markdown/data files so the CMS can edit it.

## 8. Forms (deferred)

- Google Apps Script web app receives submissions and writes them to a Google Sheet.
- Honeypot field for spam; GDPR consent.
- Planned split:
  1. "I am registering myself" – adults only
  2. "My guardian is registering me" – minors, with parental consent
- Exact forms (international applicants, SOČ nominees, regional/public-day sign-ups) and the consent wording are to be decided with the team.

## 9. Phases

1. ✅ **Foundations** (done 2026-10-03)
   - Project setup with Hugo pinned via npm, Tailwind v4 and the Netlify config.
   - Fonts (woff2), colours, grid, spacing and typography scale.
   - Language setup; base layout, header with language switch, footer, logo component.
2. ✅ **Pattern engine** (done 2026-10-03 – lab at `/pattern-lab/`)
   - Test page with sliders (density, cell size, speed) to agree on values with the designer.
   - Reusable pattern rectangle component (static + animated).
3. ✅ **Homepage and shared templates** (done 2026-10-03) – page `sections` built from blocks: `hero`, `facts`, `intro`, `highlights`, `split`, `cta` (`layouts/_partials/sections/`).
4. ✅ **Content pages** (done 2026-10-03) – all pages built from blocks; new blocks: `schedule`, `faq`, `people` (data/team.yaml), `partners` (data/partners.yaml), `downloads`, `contacts`, `news-list`.
5. ✅ **Projects** (done 2026-10-03) – one file per project in `/projects/` (shown on both language sites), filters by search / country / field with URL state, detail pages with optional video, contact and poster.
6. ✅ **Public Day** (done 2026-10-03) – overview with interactive map (click a region → city preview panel, `#city` links) + a page per city (`content/public-day/<city>.md`) with its region graphic, key facts, and projects tagged `publicDay: <city>`.
7. ✅ **CMS** (done 2026-10-03) – Sveltia CMS at `/admin/`; config generated by `tools/build-cms-config.py`; editor guide in `docs/editor-guide.md`. To go live:
   1. ✅ Repository on GitHub: `pgersl/cyence` (set in `tools/build-cms-config.py`).
   2. Create a GitHub OAuth App (callback URL `https://api.netlify.com/auth/done`) and add it in Netlify under the site's OAuth / access settings (provider: GitHub).
   3. Add editors as collaborators on the GitHub repository.
8. **Forms** – once designed with the team.
9. **Easter egg: full-screen pattern game** – a hidden page where visitors move the yellow and blue sources around a full-screen interference field.
10. **Final checks**
   - Accessibility, SEO (meta, OG images, sitemap, hreflang), performance.
   - Netlify domain + launch.

## 10. Pending inputs

- [ ] Logo: our pattern-tile proposal is live (manual: https://claude.ai/artifact/4R4VStteZWPErp6ocrkpY4) – to be reviewed with the designer. Sources: `design/logo/build.py` → `design/logo/cyence/`; after regenerating, copy `cyence-logo-color.svg` → `assets/images/logo.svg`, `cyence-icon-color.svg` → `static/favicon.svg` (+ `static/apple-touch-icon.png`), and the three logos → `static/downloads/`.
- [ ] Final pattern parameters – designer to tune in `/pattern-lab/` and send "Copy settings" output
- [ ] Second allowed pattern usage (designer)
- [ ] Real content for all pages (team), in particular:
  - [ ] team names, roles and photos (`data/team.yaml`)
  - [ ] contact e-mails (placeholders `info@`, `press@`, `partners@cyence.eu`) and press contact name
  - [ ] privacy policy – complete and get legal review
  - [ ] confirmed programme outline and times
  - [ ] application details: registration dates, fees, steps
  - [ ] partners and logos (`data/partners.yaml`)
  - [ ] number of countries ("XX" on Home and About the Event)
  - [ ] replace sample news items
  - [ ] replace the 12 sample projects in `/projects/`
- [ ] Form scope + parental-consent wording (team)
- [ ] Domain name (`baseURL` and contact e-mail in `hugo.toml` are placeholders)
