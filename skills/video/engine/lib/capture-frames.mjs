#!/usr/bin/env node
// Fallback renderer: seek a scene's GSAP timeline frame by frame in headless Chrome and pipe PNGs
// to ffmpeg. Reuses puppeteer-core from <engine>/hf/node_modules. Slower than hyperframes; use it
// to cross-check a suspicious render or when hyperframes cannot run.
// Usage: node lib/capture-frames.mjs <scene_dir> -o out.mp4 [--fps 30]
import { createRequire } from 'node:module';
import { spawn, spawnSync } from 'node:child_process';
import { pathToFileURL, fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

const here = path.dirname(fileURLToPath(import.meta.url));
const ENGINE = process.env.MVID_HOME || path.join(here, '..');
const require = createRequire(path.join(ENGINE, 'hf', 'package.json'));
let puppeteer;
try { puppeteer = require('puppeteer-core'); }
catch { console.error(`puppeteer-core not found: run \`npm ci\` in ${path.join(ENGINE, 'hf')}`); process.exit(2); }

// a Chrome/Chromium binary: $CHROME_PATH, else the first common install location that exists
const CHROME = process.env.CHROME_PATH || [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser',
].find(p => fs.existsSync(p)) || 'chrome';

const args = process.argv.slice(2);
let sceneDir, out, fps = 30;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '-o') out = args[++i];
  else if (args[i] === '--fps') fps = Number(args[++i]);
  else if (!sceneDir) sceneDir = args[i];
}
if (!sceneDir || !out || !(fps > 0)) {
  console.error('usage: capture-frames.mjs <scene_dir> -o out.mp4 [--fps 30]');
  process.exit(2);
}
sceneDir = path.resolve(sceneDir);
out = path.resolve(out);
const indexPath = path.join(sceneDir, 'index.html');
if (!fs.existsSync(indexPath)) { console.error(`missing ${indexPath}`); process.exit(2); }
if (!fs.existsSync(CHROME)) { console.error(`Chrome not found at ${CHROME}`); process.exit(2); }

const browser = await puppeteer.launch({
  executablePath: CHROME, headless: true,
  args: ['--allow-file-access-from-files', '--hide-scrollbars', '--force-color-profile=srgb', '--font-render-hinting=none'],
});
let ff;
try {
  const page = await browser.newPage();
  const fileUrl = pathToFileURL(indexPath).href;
  // first load only to read the root's dimensions, then size the viewport and reload
  await page.goto(fileUrl, { waitUntil: 'load' });
  const meta = await page.evaluate(() => {
    const r = document.querySelector('[data-composition-id]');
    return r && { id: r.dataset.compositionId, w: +r.dataset.width, h: +r.dataset.height, d: +r.dataset.duration };
  });
  if (!meta || !meta.id || !(meta.w > 0) || !(meta.h > 0) || !(meta.d > 0)) throw new Error(`root needs data-composition-id/width/height/duration, got ${JSON.stringify(meta)}`);
  await page.setViewport({ width: meta.w, height: meta.h, deviceScaleFactor: 1 });
  await page.goto(fileUrl, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction((id) => !!(window.__timelines && window.__timelines[id]), { timeout: 15000, polling: 50 }, meta.id);

  const total = Math.ceil(meta.d * fps);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(fps), '-movflags', '+faststart', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const ffDone = new Promise((res) => ff.on('close', res));
  ff.stdin.on('error', () => {});

  const t0 = process.hrtime.bigint();
  for (let i = 0; i < total; i++) {
    await page.evaluate((id, t) => { window.__timelines[id].seek(t, false); }, meta.id, i / fps);
    const buf = await page.screenshot({ type: 'png', omitBackground: false });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  const code = await ffDone;
  const secs = Number(process.hrtime.bigint() - t0) / 1e9;
  if (code !== 0) throw new Error(`ffmpeg exited ${code}`);
  console.log(`${total} frames in ${secs.toFixed(2)}s = ${(total / secs).toFixed(1)} frames/sec (${meta.w}x${meta.h} @ ${fps}fps)`);

  // artifact assertion
  const pr = spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', out], { encoding: 'utf8' });
  const dur = parseFloat(pr.stdout);
  if (!(Math.abs(dur - meta.d) <= 1 / fps)) throw new Error(`duration ${dur}s vs data-duration ${meta.d}s exceeds 1 frame`);
  console.log(`OK ${out} duration ${dur.toFixed(3)}s (data-duration ${meta.d})`);
} catch (e) {
  console.error('FAIL:', e.message);
  process.exitCode = 1;
} finally {
  await browser.close();
}
