// Renders the social preview images (static/images/og-en.png, og-cs.png)
// from the hidden /og-image/ pages (layouts/og-image.html).
//
//   npm run dev                      (in another terminal)
//   node tools/og-image.mjs [base-url]
//
// Uses an installed Chromium-based browser; set CHROME_PATH if it isn't
// found automatically.
import puppeteer from "puppeteer-core";
import fs from "node:fs";

const base = (process.argv[2] || "http://localhost:1313").replace(/\/$/, "");
const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].filter(Boolean);
const executablePath = candidates.find((p) => fs.existsSync(p));
if (!executablePath) throw new Error("No Chromium-based browser found – set CHROME_PATH.");

const browser = await puppeteer.launch({ executablePath, headless: true });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 1 });
  // Without motion the pattern is drawn once, as a still frame.
  await page.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
  for (const [lang, path] of [["en", "/og-image/"], ["cs", "/cs/og-image/"]]) {
    await page.goto(base + path, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await new Promise((r) => setTimeout(r, 500));
    const out = `static/images/og-${lang}.png`;
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1200, height: 630 } });
    console.log("wrote", out);
  }
} finally {
  await browser.close();
}
