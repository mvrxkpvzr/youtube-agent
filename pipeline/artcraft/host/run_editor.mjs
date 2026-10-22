// Drive the headless ArtCraft editor host: serve the built host + media from disk (no network),
// call window.artcraft.build(timeline), save the editor's export download and its readback.
// usage: node run_editor.mjs <timeline.json> <out.webm> [--host-dist dir]
// Cloud: open-source Chromium under Xvfb (SwiftShader WebGPU, VP9 only). Mac: PW_CHANNEL=chrome uses the installed Chrome.
import { chromium } from "playwright-core";
import fs from "fs"; import path from "path";
const [tlPath, outPath] = process.argv.slice(2);
const distArg = process.argv.indexOf("--host-dist");
const DIST = path.resolve(distArg > 0 ? process.argv[distArg + 1] : path.join(path.dirname(new URL(import.meta.url).pathname), "dist"));
const tl = JSON.parse(fs.readFileSync(tlPath, "utf8"));
const ORIGIN = "http://localhost:47811";
const MIME = { ".html": "text/html", ".js": "text/javascript", ".wasm": "application/wasm", ".json": "application/json",
  ".mp4": "video/mp4", ".webm": "video/webm", ".wav": "audio/wav", ".mp3": "audio/mpeg", ".ogg": "audio/ogg",
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".otf": "font/otf", ".ttf": "font/ttf", ".woff2": "font/woff2" };
const files = new Map(); // url path -> absolute file
tl.media.forEach((m, i) => { const u = `/media/${i}${path.extname(m.path)}`; files.set(u, path.resolve(m.path)); m.url = u; m.name = path.basename(m.path); });
const exe = process.env.CHROMIUM || "/opt/pw-browsers/chromium";
// Headed under Xvfb: headless Chromium cannot read back a SwiftShader WebGPU canvas (export comes out black).
const browser = await chromium.launch({ headless: !!process.env.HEADLESS, channel: process.env.PW_CHANNEL || undefined,
  executablePath: !process.env.PW_CHANNEL && fs.existsSync(exe) ? exe : undefined,
  args: ["--autoplay-policy=no-user-gesture-required", "--enable-unsafe-swiftshader", "--use-angle=swiftshader", "--enable-unsafe-webgpu", "--enable-features=Vulkan,WebGPU", "--use-vulkan=swiftshader", "--use-webgpu-adapter=swiftshader", "--disable-vulkan-surface"] });
const ctx = await browser.newContext({ acceptDownloads: true, viewport: { width: 1280, height: 800 } });
await ctx.route(`${ORIGIN}/**`, async (route) => {
  const u = new URL(route.request().url()).pathname;
  const f = files.get(u) ?? path.join(DIST, u === "/" ? "index.html" : u);
  if (!f.startsWith(DIST) && !files.has(u)) return route.fulfill({ status: 403 });
  if (!fs.existsSync(f)) return route.fulfill({ status: 404, body: "not found " + u });
  await route.fulfill({ status: 200, body: fs.readFileSync(f), headers: { "content-type": MIME[path.extname(f).toLowerCase()] ?? "application/octet-stream",
    "cross-origin-opener-policy": "same-origin", "cross-origin-embedder-policy": "require-corp" } });
});
await ctx.route(/^(?!http:\/\/localhost:47811).*/, (r) => r.abort()); // offline: nothing leaves the machine
const page = await ctx.newPage();
const logs = [];
page.on("console", (m) => { logs.push(`${m.type()}: ${m.text()}`); if (process.env.VERBOSE || m.type() === "error") console.error(`[page ${m.type()}] ${m.text()}`); });
page.on("pageerror", (e) => { logs.push("pageerror: " + e.message); console.error("[pageerror]", e.message); });
await page.goto(ORIGIN + "/");
await page.waitForFunction(() => window.artcraft?.ready, null, { timeout: 60000 });
const dl = page.waitForEvent("download", { timeout: 0 });
const t0 = Date.now();
const res = await page.evaluate((t) => window.artcraft.build(t), tl);
const d = await dl; await d.saveAs(outPath);
const report = { ...res, out: path.resolve(outPath), wall_s: (Date.now() - t0) / 1000, engine: "artcraft-video-editor (headless)", console: logs.slice(-200) };
fs.writeFileSync(outPath.replace(/\.[^.]+$/, "") + ".editor.json", JSON.stringify(report, null, 1));
console.log(JSON.stringify({ ok: res.ok, bytes: res.bytes, wall_s: report.wall_s, log: res.log }));
await browser.close();
