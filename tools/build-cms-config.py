"""Generates static/admin/config.yml for Sveltia CMS.

The block types (homepage/page sections) are defined once here and reused by
every collection that has `sections`; country, field and city options come
from the data files. Re-run after adding a block type or changing those
data files:

    pip install pyyaml
    python tools/build-cms-config.py

"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = "pgersl/cyence"  # GitHub "owner/repo"
BRANCH = "main"

data = lambda name: yaml.safe_load((ROOT / "data" / f"{name}.yaml").read_text(encoding="utf-8"))
countries = data("countries")
fields = data("fields")
czechia = __import__("json").loads((ROOT / "data/czechia.json").read_text(encoding="utf-8"))
regions = sorted(r["code"] for r in czechia["regions"].values())
stops = [s["city"] for s in data("publicday")["stops"]]


# ---- small helpers ---------------------------------------------------------
def s(name, label, hint=None, **kw):
    f = {"name": name, "label": label, "widget": "string", **kw}
    if hint:
        f["hint"] = hint
    return f


def text(name, label, **kw):
    return {"name": name, "label": label, "widget": "text", **kw}


def md(name, label, **kw):
    return {"name": name, "label": label, "widget": "markdown", "buttons": ["bold", "italic", "link", "bulleted-list", "numbered-list", "heading-two", "heading-three", "quote"], "editor_components": [], **kw}


def boolean(name, label, **kw):
    return {"name": name, "label": label, "widget": "boolean", "required": False, **kw}


def select(name, label, options, **kw):
    return {"name": name, "label": label, "widget": "select", "options": options, **kw}


def number(name, label, **kw):
    return {"name": name, "label": label, "widget": "number", "value_type": "int", **kw}


def lst(name, label, fields_, summary=None, **kw):
    f = {"name": name, "label": label, "widget": "list", "fields": fields_, **kw}
    if summary:
        f["summary"] = summary
    return f


def obj(name, label, fields_, **kw):
    return {"name": name, "label": label, "widget": "object", "fields": fields_, **kw}


opt = {"required": False}
LINK_HINT = "A page path such as /apply or /about/event (works in both languages), or a full URL."
link_fields = [s("label", "Label"), s("link", "Link", LINK_HINT)]
button = lambda name="link", label="Button": obj(name, label, link_fields, required=False, collapsed=True)
heading = [s("kicker", "Kicker (small label above)", **opt), s("title", "Heading", **opt)]
pattern = obj("pattern", "Pattern settings", [
    s("aspect", "Format (width/height, e.g. 1/1, 4/3)", **opt),
    number("cols", "Columns", **opt),
    {"name": "wavelengthYellow", "label": "Yellow wavelength (cells)", "widget": "number", "value_type": "float", "required": False},
    {"name": "wavelengthBlue", "label": "Blue wavelength (cells)", "widget": "number", "value_type": "float", "required": False},
    {"name": "speed", "label": "Speed", "widget": "number", "value_type": "float", "required": False},
    number("seed", "Seed (fixed pattern; empty = new every visit)", **opt),
], required=False, collapsed=True, hint="Optional. Leave empty for the defaults.")

# ---- block types (one per partial in layouts/_partials/sections/) -----------
BLOCKS = [
    {"name": "hero", "label": "Hero (homepage)", "fields": [
        s("headline", "Headline"), text("lead", "Lead", **opt),
        lst("ctas", "Buttons", link_fields + [boolean("primary", "Yellow (primary)")], summary="{{fields.label}}"),
        pattern]},
    {"name": "news", "label": "News strip", "fields": heading + [number("limit", "How many items", **opt)]},
    {"name": "intro", "label": "Text: heading + paragraphs", "fields": heading + [
        md("text", "Text"), lst("links", "Buttons", link_fields + [boolean("primary", "Yellow (primary)")], required=False, summary="{{fields.label}}")]},
    {"name": "slogan", "label": "Slogan", "fields": [
        s("text", "Slogan", "Wrap the words to underline in *asterisks*, e.g. Science has *no borders.*"),
        select("color", "Underline colour", ["yellow", "blue"], **opt), select("align", "Alignment", ["center", "left"], **opt)]},
    {"name": "split", "label": "Half visual, half text", "fields": heading + [
        md("text", "Text"), button(),
        boolean("reverse", "Visual on the right"),
        select("visual", "Visual", [{"label": "Pattern", "value": "pattern"}, {"label": "Map of Czechia", "value": "map"}], **opt),
        {"name": "image", "label": "Photo (instead of a pattern)", "widget": "image", "required": False},
        s("alt", "Photo description (for screen readers)", **opt),
        select("frame", "Photo frame colour", ["yellow", "blue"], **opt),
        s("caption", "Caption", **opt), pattern]},
    {"name": "stats", "label": "Numbers (bento)", "fields": heading + [
        lst("items", "Numbers (1st = big yellow tile, 2nd black, 3rd blue, 4th outlined)",
            [s("value", "Number"), s("label", "Label"), text("text", "Text", **opt)], summary="{{fields.value}} {{fields.label}}", max=4)]},
    {"name": "facts", "label": "Numbers (row)", "fields": [s("title", "Heading (screen readers only)", **opt),
        lst("items", "Numbers", [s("value", "Number"), s("label", "Label")], summary="{{fields.value}} {{fields.label}}")]},
    {"name": "highlights", "label": "Numbered items", "fields": heading + [
        lst("items", "Items", [s("title", "Title"), text("text", "Text")], summary="{{fields.title}}"), button()]},
    {"name": "schedule", "label": "Programme (days)", "fields": [
        text("note", "Note above the programme", **opt),
        lst("days", "Days", [
            {"name": "date", "label": "Date", "widget": "datetime", "time_format": False, "date_format": "D. M. YYYY", "format": "YYYY-MM-DD"},
            s("title", "Title"), text("text", "Text", **opt), boolean("highlight", "Highlight in blue"),
            button(),
            lst("items", "Items", [s("time", "Time (e.g. 9:00)", **opt), s("title", "Title"), text("text", "Text", **opt), s("place", "Place", **opt)],
                required=False, summary="{{fields.time}} {{fields.title}}")],
            summary="{{fields.date}} – {{fields.title}}")]},
    {"name": "faq", "label": "Questions & answers", "fields": heading + [
        lst("items", "Questions", [s("q", "Question"), md("a", "Answer")], summary="{{fields.q}}")]},
    {"name": "people", "label": "Team (from the Team data)", "fields": [s("kicker", "Kicker", **opt)]},
    {"name": "partners", "label": "Partners (from the Partners data)", "fields": []},
    {"name": "downloads", "label": "Downloads", "fields": heading + [
        lst("items", "Files", [s("label", "Name"), text("text", "Description", **opt),
                               {"name": "file", "label": "File", "widget": "file"}, s("format", "Format (e.g. SVG, PDF)")], summary="{{fields.label}}")]},
    {"name": "contacts", "label": "Contact cards", "fields": heading + [
        lst("items", "Contacts", [s("title", "Title"), text("text", "Text", **opt), s("name", "Name", **opt),
                                  s("email", "E-mail", **opt), s("phone", "Phone", **opt)], summary="{{fields.title}}")]},
    {"name": "news-list", "label": "News of one category", "fields": heading + [
        select("category", "Category", ["news", "event", "press"]), s("empty", "Text when there are none", **opt)]},
    {"name": "quotes", "label": "Quotes (they said about us)", "fields": heading + [
        lst("items", "Quotes", [text("quote", "Quote"), s("name", "Name"), s("role", "Role", **opt)], summary="{{fields.name}}")]},
    {"name": "coverage", "label": "Media coverage (they wrote about us)", "fields": heading + [
        s("empty", "Text when there is none", **opt),
        lst("items", "Articles", [
            {"name": "date", "label": "Date", "widget": "datetime", "time_format": False, "format": "YYYY-MM-DD"},
            s("outlet", "Outlet"), s("title", "Title"), s("url", "Link"),
            select("kind", "Type", ["article", "tv", "radio", "podcast"])], summary="{{fields.outlet}} – {{fields.title}}")]},
    {"name": "cta", "label": "Call to action (yellow)", "fields": heading + [text("text", "Text", **opt), button("button", "Button"), pattern]},
]
SECTIONS = {"name": "sections", "label": "Page blocks", "widget": "list", "types": BLOCKS, "typeKey": "type",
            "required": False, "i18n": True, "hint": "The page is built from these blocks, top to bottom."}

page_fields = [
    s("title", "Title", i18n=True),
    s("slug", "URL slug (Czech only, e.g. prihlaska)", i18n=True, required=False),
    text("lead", "Lead (below the title)", i18n=True, required=False),
    text("description", "Description for search engines", i18n=True, required=False),
    SECTIONS,
    md("body", "Text (below the title, above the blocks)", i18n=True, required=False),
]


def page(name, label, path):
    return {"name": name, "label": label, "file": f"content/{path}.md", "i18n": True, "fields": page_fields}


PAGES = [
    page("home", "Homepage", "_index"),
    page("about", "About", "about/_index"),
    page("about-event", "About › The Event", "about/event"),
    page("about-team", "About › Our Team", "about/team"),
    page("about-brno", "About › Brno", "about/brno"),
    page("about-south-moravia", "About › South Moravia", "about/south-moravia"),
    page("apply", "Apply", "apply"),
    page("programme", "Programme", "programme"),
    page("public-day", "Public Day (overview)", "public-day/_index"),
    page("projects", "Projects (page text)", "projects/_index"),
    page("news-index", "News (page text)", "news/_index"),
    page("media", "Media", "media"),
    page("partners", "Partners", "partners"),
    page("contact", "Contact", "contact"),
    page("privacy", "Privacy policy", "privacy"),
]
# The About section page can also have blocks above its subpage cards.
PAGES[1]["fields"] = page_fields[:4] + [dict(SECTIONS, name="before", label="Blocks above the subpage cards")] + page_fields[4:]

country_options = sorted(({"label": v["en"], "value": k} for k, v in countries.items()), key=lambda o: o["label"])
field_options = [{"label": v["en"], "value": k} for k, v in fields.items()]
city_names = {k: czechia["cities"][k]["nameEn"] for k in stops}

config = {
    "backend": {"name": "github", "repo": REPO, "branch": BRANCH},
    "site_url": "https://cyence.eu",
    "media_folder": "static/images/uploads",
    "public_folder": "/images/uploads",
    "i18n": {"structure": "multiple_files", "locales": ["en", "cs"], "default_locale": "en",
             "omit_default_locale_from_file_path": True, "initial_locales": "all"},
    "collections": [
        {"name": "pages", "label": "Pages", "icon": "description", "files": PAGES},
        {"name": "news", "label": "News", "icon": "newspaper", "folder": "content/news", "create": True, "i18n": True,
         "slug": "{{slug}}", "sortable_fields": ["date", "title"],
         "summary": "{{date | date('D. M. YYYY')}} · {{title}}",
         "fields": [
             s("title", "Title", i18n=True),
             {"name": "date", "label": "Date", "widget": "datetime", "time_format": False, "format": "YYYY-MM-DD", "i18n": "duplicate"},
             select("category", "Category", [{"label": "News", "value": "news"}, {"label": "Event", "value": "event"}, {"label": "Press release", "value": "press"}], i18n="duplicate"),
             text("summary", "Summary (on the card)", i18n=True),
             s("link", "Link instead of an article page", LINK_HINT + " Used when the text below is empty.", i18n=True, required=False),
             s("cta", "Link label (e.g. Register)", i18n=True, required=False),
             md("body", "Article text (optional)", i18n=True, required=False),
         ]},
        {"name": "projects", "label": "Projects", "icon": "science", "folder": "projects", "create": True,
         "slug": "{{slug}}", "sortable_fields": ["title", "country", "field"],
         "summary": "{{title}} · {{country}}",
         "fields": [
             s("title", "Title"),
             {"name": "students", "label": "Students", "widget": "list", "field": s("name", "Name")},
             select("country", "Country", country_options),
             select("field", "Field", field_options),
             s("school", "School"),
             text("summary", "One-sentence summary (on the card)"),
             md("body", "Abstract"),
             {"name": "poster", "label": "Poster (PDF)", "widget": "file", "required": False},
             s("video", "Talk video (YouTube link)", **opt),
             s("contact", "Contact (e-mail or URL – only with the student's consent)", **opt),
             select("publicDay", "Presents on the Public Day in", [{"label": city_names[k], "value": k} for k in stops], **opt),
         ]},
        {"name": "public-day-cities", "label": "Public Day cities", "icon": "location_city", "folder": "content/public-day",
         "create": False, "delete": False, "i18n": True,
         "fields": [
             s("title", "City name", i18n=True),
             select("city", "City (map & data key)", [{"label": city_names[k], "value": k} for k in stops], i18n="duplicate"),
             s("slug", "URL slug", i18n=True),
             number("weight", "Order", i18n="duplicate", required=False),
             text("lead", "Lead", i18n=True, required=False),
             SECTIONS,
             md("body", "Text", i18n=True, required=False),
         ]},
        {"name": "data", "label": "Lists & data", "icon": "dataset", "files": [
            {"name": "team", "label": "Team", "file": "data/team.yaml", "fields": [
                lst("groups", "Groups", [
                    obj("name", "Group name", [s("en", "English"), s("cs", "Czech")]),
                    lst("people", "People", [
                        s("name", "Name"),
                        obj("role", "Role", [s("en", "English"), s("cs", "Czech")]),
                        s("email", "E-mail", **opt),
                        {"name": "photo", "label": "Photo (square)", "widget": "image", "required": False},
                    ], summary="{{fields.name}} – {{fields.role.en}}"),
                ], summary="{{fields.name.en}}")]},
            {"name": "partners", "label": "Partners", "file": "data/partners.yaml", "fields": [
                lst("tiers", "Tiers", [
                    s("id", "ID"),
                    select("size", "Logo size", [{"label": "Normal", "value": "normal"}, {"label": "Large (two per row)", "value": "large"}], **opt),
                    obj("name", "Tier name", [s("en", "English"), s("cs", "Czech")]),
                    lst("partners", "Partners", [s("name", "Name"), {"name": "logo", "label": "Logo", "widget": "image", "required": False}, s("url", "Website")],
                        required=False, summary="{{fields.name}}"),
                ], summary="{{fields.name.en}}")]},
            {"name": "publicday", "label": "Public Day data", "file": "data/publicday.yaml", "fields": [
                {"name": "date", "label": "Date", "widget": "datetime", "time_format": False, "format": "YYYY-MM-DD"},
                s("time", "Time of the conferences (e.g. 9:00–15:00)"),
                lst("stops", "Cities", [
                    select("city", "City", [{"label": c["nameEn"], "value": k} for k, c in czechia["cities"].items()]),
                    select("region", "Region on the map", regions),
                    number("capacity", "Audience (students)"),
                    s("venue", "Venue"),
                    boolean("tentative", "Venue not confirmed yet"),
                ], summary="{{fields.city}} – {{fields.venue}}",
                    hint="Each city also needs a page under Public Day cities with the same city key."),
            ]},
        ]},
    ],
}

header = (
    "# Sveltia CMS configuration – GENERATED by tools/build-cms-config.py.\n"
    "# Edit that script and re-run it instead of editing this file.\n"
)
out = ROOT / "static/admin/config.yml"
out.parent.mkdir(parents=True, exist_ok=True)


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


out.write_text(header + yaml.dump(config, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} kB)")
