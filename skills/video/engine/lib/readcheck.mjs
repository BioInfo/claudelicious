#!/usr/bin/env node
// Read-time check: is every block of on-screen text held long enough to read?
//   node lib/readcheck.mjs <scene_dir> [<scene_dir> ...] [--json] [--step 0.1]
//   node lib/readcheck.mjs --selftest
// Seeks each scene's paused GSAP timeline (window.__timeline, harness.js contract) every STEP s and
// finds text BLOCKS: block-level elements whose text sits in inline descendants, so SplitText chars
// and words count as one block that is visible only when every piece is. A block is keyed by its DOM
// path, never its text, and its reading clock restarts whenever its text changes: a count-up or a
// typewriter is timed from the frame it settles. Need = letters/15 + 1.5 s, min 1.5 s (15 cps sits
// below common subtitle reading-speed ceilings of 17-20 cps).
// A block still on screen when the scene ends is reported "to end", not failed: the cut decides it.
// Exit: 0 all pass, 1 any short block, 2 nothing checked or a scene failed to load (never a pass).
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';

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
const CPS = 15, PAD = 1.5, MIN = 1.5;

export const need = text => Math.max(MIN, (text.match(/[\p{L}\p{N}]/gu) || []).length / CPS + PAD);

// runs inside the page
function sample(t) {
  window.__timeline.seek(t, false);
  const out = {};
  const W = innerWidth, H = innerHeight;
  const isBlock = el => { const d = getComputedStyle(el).display; return !d.startsWith('inline') && d !== 'contents'; };
  const effOp = el => {
    let o = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity);
    }
    return o;
  };
  const keyOf = el => {
    const p = [];
    for (let e = el; e && e.nodeType === 1 && e !== document.body; e = e.parentElement)
      p.unshift(e.id ? '#' + e.id : e.tagName.toLowerCase() + ':' + Array.prototype.indexOf.call(e.parentElement.children, e));
    return p.join('>');
  };
  for (const el of document.querySelectorAll('body *')) {
    if (['SCRIPT', 'STYLE', 'TEMPLATE'].includes(el.tagName) || el.closest('svg') || !isBlock(el)) continue;
    const own = [...el.childNodes].some(n => (n.nodeType === 3 && n.textContent.trim()) ||
                                         (n.nodeType === 1 && !isBlock(n) && n.textContent.trim()));
    if (!own) continue;
    const txt = el.textContent.replace(/\s+/g, ' ').trim();
    if (!txt) continue;
    const leaves = [...el.querySelectorAll('*')].filter(n => !n.children.length && n.textContent.trim());
    let ok = true;
    for (const n of (leaves.length ? leaves : [el])) {
      const r = n.getBoundingClientRect();
      if (effOp(n) < 0.9 || r.width < 1 || r.left < -1 || r.right > W + 1 || r.top < -1 || r.bottom > H + 1) { ok = false; break; }
    }
    if (ok) out[keyOf(el)] = txt;
  }
  return out;
}

export async function checkScenes(dirs, { step = 0.1 } = {}) {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true,
    args: ['--allow-file-access-from-files', '--hide-scrollbars', '--force-color-profile=srgb'] });
  const scenes = [];
  try {
    for (const dir of dirs) {
      const res = { scene: path.basename(path.resolve(dir)), blocks: [], error: null };
      scenes.push(res);
      const page = await browser.newPage();
      try {
        await page.setViewport({ width: 1920, height: 1080 });
        await page.goto('file://' + path.resolve(dir, 'index.html'), { waitUntil: 'load', timeout: 30000 });
        await page.waitForFunction(() => document.documentElement.dataset.ready === '1' || document.documentElement.dataset.jserror,
                                   { timeout: 30000 });
        const err = await page.evaluate(() => document.documentElement.dataset.jserror || (window.__timeline ? null : 'no window.__timeline'));
        if (err) throw new Error(err);
        const dur = await page.evaluate(() => window.__timeline.duration());
        const runs = {};
        const close = (r, t, toEnd) => {
          const len = t - r.start;
          if (!r.best || len > r.best.len) r.best = { len, text: r.text, start: r.start, toEnd };
          r.start = null;
        };
        const n = Math.floor(dur / step + 1e-6);
        for (let i = 0; i <= n; i++) {
          const t = i * step;
          const vis = await page.evaluate(sample, t);
          for (const [k, r] of Object.entries(runs))
            if (r.start !== null && (!(k in vis) || vis[k] !== r.text)) close(r, t, false);
          for (const [k, txt] of Object.entries(vis)) {
            const r = runs[k] ||= { start: null, best: null, text: null };
            if (r.start === null) { r.start = t; r.text = txt; }
          }
        }
        for (const r of Object.values(runs)) if (r.start !== null) close(r, n * step + step, true);
        for (const [key, r] of Object.entries(runs)) {
          const b = r.best, nd = need(b.text);
          res.blocks.push({ key, text: b.text, start: +b.start.toFixed(2), held: +b.len.toFixed(2), need: +nd.toFixed(2),
                            status: b.len + 1e-6 >= nd ? 'ok' : (b.toEnd ? 'to-end' : 'short') });
        }
        res.blocks.sort((a, b) => a.start - b.start);
      } catch (e) {
        res.error = String(e.message || e);
      } finally {
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }
  return scenes;
}

function exitCode(scenes) {
  if (scenes.some(s => s.error) || !scenes.some(s => s.blocks.length)) return 2;
  return scenes.some(s => s.blocks.some(b => b.status === 'short')) ? 1 : 0;
}

async function selftest() {
  // Two blocks must fail (a 0.5 s flash; a count-up that settles for 0.5 s) and two must pass
  // (a 4 s hold; a count-up held 3 s after it settles). Proves the check can fail, and that it
  // keys count-ups by element rather than reading every frame's digits as new text.
  // GSAP from node_modules when installed, else the same pinned CDN build the kit uses
  const local = path.join(ENGINE, 'hf', 'node_modules', 'gsap', 'dist', 'gsap.min.js');
  const gsapSrc = fs.existsSync(local) ? 'file://' + local : 'https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js';
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'readcheck-'));
  fs.writeFileSync(path.join(dir, 'index.html'), `<!doctype html><html><head><style>
    body{margin:0;width:1920px;height:1080px;background:#000;color:#fff;font:48px sans-serif}
    div{position:absolute;left:100px;opacity:0}</style><script src="${gsapSrc}"></script></head><body>
    <div id="quick" style="top:100px">Flashes by</div><div id="slow" style="top:250px">Held long enough</div>
    <div id="count" style="top:400px">0</div><div id="count2" style="top:550px">0</div><script>
    const tl = gsap.timeline({paused:true}); window.__timeline = tl;
    tl.to('#quick',{opacity:1,duration:0.01},0.5).to('#quick',{opacity:0,duration:0.01},1.0)
      .to('#slow',{opacity:1,duration:0.01},0.5).to('#slow',{opacity:0,duration:0.01},4.5)
      .to('#count',{opacity:1,duration:0.01},0.5).to('#count2',{opacity:1,duration:0.01},0.5);
    const a={v:0}, b={v:0}, c=document.getElementById('count'), d=document.getElementById('count2');
    tl.to(a,{v:100,duration:2,onUpdate:()=>{c.textContent=Math.round(a.v)}},0.5).to('#count',{opacity:0,duration:0.01},5.5)
      .to(b,{v:12345,duration:2,onUpdate:()=>{d.textContent=Math.round(b.v)}},0.5).to('#count2',{opacity:0,duration:0.01},3.0)
      .set({}, {}, 7);
    tl.seek(0,false); document.documentElement.dataset.ready='1';</script></body></html>`);
  const [s] = await checkScenes([dir]);
  fs.rmSync(dir, { recursive: true, force: true });
  if (s.error) { console.error('selftest: scene failed to load:', s.error); return 2; }
  const got = Object.fromEntries(s.blocks.map(b => [b.key.split('>').pop(), b.status]));
  const want = { '#quick': 'short', '#slow': 'ok', '#count': 'ok', '#count2': 'short' };
  let ok = true;
  for (const [k, v] of Object.entries(want)) {
    const pass = got[k] === v;
    ok &&= pass;
    console.log(`${pass ? 'PASS' : 'FAIL'} ${k}: want ${v}, got ${got[k] ?? 'absent'}`);
  }
  console.log(ok ? 'selftest: PASS' : 'selftest: FAIL');
  return ok ? 0 : 1;
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--selftest')) process.exit(await selftest());
  let step = 0.1, json = false;
  const dirs = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json') json = true;
    else if (args[i] === '--step') step = Number(args[++i]);
    else dirs.push(args[i]);
  }
  if (!dirs.length || !(step > 0)) { console.error('usage: readcheck.mjs <scene_dir>... [--json] [--step 0.1] | --selftest'); process.exit(2); }
  const scenes = await checkScenes(dirs, { step });
  const code = exitCode(scenes);
  if (json) console.log(JSON.stringify({ code, step, cps: CPS, pad: PAD, scenes }));
  else {
    for (const s of scenes) {
      if (s.error) { console.log(`ERROR ${s.scene}: ${s.error}`); continue; }
      for (const b of s.blocks.filter(b => b.status !== 'ok'))
        console.log(`${b.status === 'short' ? 'SHORT ' : 'to-end'} ${s.scene} @${b.start}s held ${b.held}s need ${b.need}s "${b.text.slice(0, 70)}"`);
    }
    const all = scenes.flatMap(s => s.blocks), short = all.filter(b => b.status === 'short').length;
    console.log(`${short} short / ${all.length} text blocks${code === 2 ? ' (NOT CHECKED: see errors)' : ''}`);
  }
  process.exit(code);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
