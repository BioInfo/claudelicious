#!/usr/bin/env python3
"""render.py: HyperFrames scene renderer for mvid.

  render.py <film_dir> [scene...] [--draft] [--no-check] [--jobs N] [--expect SEC]
  render.py --sync-durations <film_dir> [scene...]
  render.py --scaffold <film_dir> <scene...>

Each scene: lint+check (skip with --no-check) -> hyperframes render -w 1 -> renders/<id>.silent.mp4
-> mux audio/narration.wav -> renders/<id>.mp4. Passes on the ARTIFACT (ffprobe), never the exit code.
Standard library only, so `mvid scene` and `mvid render` need no Python environment.
"""
import argparse, json, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ENGINE = Path(os.environ.get("MVID_HOME") or Path(__file__).resolve().parent.parent)
HF_DIR = ENGINE / "hf"
HF_VERSION = "0.8.62"   # pinned; keep in step with hf/package.json
HF_ENV = {
    "HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1",
    "HYPERFRAMES_NO_UPDATE_CHECK": "1", "HYPERFRAMES_NO_AUTO_INSTALL": "1",
    "HYPERFRAMES_SKIP_SKILLS": "1",
}
FFMPEG = os.environ.get("MVID_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("MVID_FFPROBE") or shutil.which("ffprobe") or "ffprobe"


def hf_cmd():
    """The pinned renderer: $MVID_HYPERFRAMES, else <engine>/hf/node_modules, else npx at the pinned version."""
    env = os.environ.get("MVID_HYPERFRAMES")
    if env:
        return [env]
    local = HF_DIR / "node_modules" / ".bin" / "hyperframes"
    if local.exists():
        return [str(local)]
    if shutil.which("npx"):
        return ["npx", "--yes", f"hyperframes@{HF_VERSION}"]
    return None


TOL = 0.1


def load_film(film):
    return json.loads((film / "film.json").read_text())


def scene_ids(film, wanted):
    cfg = load_film(film)
    allids = cfg.get("scenes", [])
    if not wanted:
        return cfg, list(allids)
    for w in wanted:
        if w not in allids:
            sys.exit(f"render: scene '{w}' not in film.json scenes {allids}")
    return cfg, list(wanted)


def root_duration(index_html):
    """data-duration on the #root element."""
    txt = index_html.read_text()
    m = re.search(r'<[^>]*\bid=["\']root["\'][^>]*>', txt)
    if not m:
        return None
    d = re.search(r'data-duration=["\']([0-9.]+)["\']', m.group(0))
    return float(d.group(1)) if d else None


def probe(path):
    """(has_video, duration) from ffprobe; (False, 0.0) if unreadable."""
    r = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "stream=codec_type:format=duration",
         "-of", "json", str(path)], capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
        has_v = any(s.get("codec_type") == "video" for s in j.get("streams", []))
        return has_v, float(j["format"]["duration"])
    except Exception:
        return False, 0.0


def sync_durations(film, wanted):
    cfg, ids = scene_ids(film, wanted)
    for sid in ids:
        sd = film / "scenes" / sid
        idx, cues = sd / "index.html", sd / "audio" / "cues.json"
        if not idx.exists() or not cues.exists():
            print(f"  {sid}: skip (need index.html and audio/cues.json)")
            continue
        total = float(json.loads(cues.read_text())["total"])
        txt = idx.read_text()
        m = re.search(r'<[^>]*\bid=["\']root["\'][^>]*>', txt)
        if not m:
            print(f"  {sid}: FAIL no #root element")
            continue
        tag = m.group(0)
        val = f"{total:g}"
        if re.search(r'data-duration=["\'][^"\']*["\']', tag):
            new = re.sub(r'data-duration=["\'][^"\']*["\']', f'data-duration="{val}"', tag)
        else:
            new = tag[:-1] + f' data-duration="{val}">'
        idx.write_text(txt.replace(tag, new, 1))
        print(f"  {sid}: data-duration={val}")


def write_film_js(film, cfg):
    """scenes/<id>/film.js: each scene's start in the assembled film, so the HUD timecode runs on film time."""
    xf, off, offs = float(cfg.get("xfade", 0.4)), 0.0, {}
    for sid in cfg.get("scenes", []):
        offs[sid] = round(off, 3)
        idx = film / "scenes" / sid / "index.html"
        d = root_duration(idx) if idx.exists() else None
        off += (d or 0.0) - xf
    total = round(off + xf, 3)
    js = "window.MV_FILM = " + json.dumps({"total": total, "offsets": offs}) + ";\n"
    for sid in cfg.get("scenes", []):
        sd = film / "scenes" / sid
        if sd.is_dir():
            (sd / "film.js").write_text(js)


def ensure_kit_link(sd):
    """The renderer serves only the scene dir and 404s fonts behind ../ paths, so a scene reaches the kit
    through a relative _kit symlink (scenes/<id>/_kit -> ../../_kit -> the engine kit)."""
    link = sd / "_kit"
    if not link.is_symlink() and not link.exists():
        link.symlink_to(Path("..") / ".." / "_kit")
    if not (link / "harness.js").is_file():
        sys.exit(f"render: {link} does not reach the kit (expected {link}/harness.js)")


def scaffold(film, ids):
    tpl = film / "_kit" / "templates" / "scene.html"
    if not tpl.exists():
        sys.exit(f"render: missing {tpl}")
    cfg = load_film(film)
    for sid in ids:
        sd = film / "scenes" / sid
        sd.mkdir(parents=True, exist_ok=True)
        ensure_kit_link(sd)
        idx = sd / "index.html"
        if idx.exists():
            print(f"  {sid}: index.html exists, left as is")
        else:
            txt = tpl.read_text().replace('data-composition-id="scene-id"', f'data-composition-id="{sid}"', 1)
            txt = txt.replace('data-width="1920"', f'data-width="{cfg.get("width", 1920)}"', 1)
            txt = txt.replace('data-height="1080"', f'data-height="{cfg.get("height", 1080)}"', 1)
            idx.write_text(txt)
            print(f"  {sid}: scaffolded from template")
        (sd / "narration.txt").touch()
        if sid not in cfg.get("scenes", []):
            cfg.setdefault("scenes", []).append(sid)
    tr = cfg.setdefault("transitions", [])
    tr.extend(["slideleft"] * max(0, len(cfg["scenes"]) - 1 - len(tr)))
    (film / "film.json").write_text(json.dumps(cfg, indent=2) + "\n")
    write_film_js(film, cfg)


def hf(args, cwd, log):
    env = dict(os.environ, **HF_ENV)
    cmd = hf_cmd()
    log.write(f"\n$ {' '.join(cmd)} {' '.join(args)}\n"); log.flush()
    p = subprocess.run([*cmd, *args], cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
    return p.returncode


def hf_cwd():
    return HF_DIR if HF_DIR.is_dir() else ENGINE


def render_scene(film, cfg, sid, draft, check, expect):
    t0 = time.time()
    sd = film / "scenes" / sid
    ensure_kit_link(sd)
    rd = film / "renders"
    rd.mkdir(exist_ok=True)
    silent, final = rd / f"{sid}.silent.mp4", rd / f"{sid}.mp4"
    logp = rd / f"{sid}.log"

    def result(ok, msg):
        return sid, ok, msg, time.time() - t0

    if not (sd / "index.html").exists():
        return result(False, "no index.html")
    want = expect if expect is not None else root_duration(sd / "index.html")
    if want is None:
        return result(False, "no data-duration on #root")
    with open(logp, "w") as log:
        if check:
            for verb in ("lint", "check"):
                if hf([verb, str(sd)], hf_cwd(), log) != 0:
                    return result(False, f"{verb} failed (see {logp.name})")
        silent.unlink(missing_ok=True)
        fps = int(cfg.get("fps", 30))
        # film.json "mblur": N renders at N x fps and blends N sub-frames per output frame (motion blur).
        # film.json "grain": strength adds seeded temporal film grain (ffmpeg, never in-page: keeps capture fast).
        mblur = 1 if draft else max(1, int(cfg.get("mblur", 1)))
        grain = 0 if draft else int(cfg.get("grain", 0))
        raw = rd / f"{sid}.raw.mp4" if (mblur > 1 or grain) else silent
        args = ["render", str(sd), "-w", "1", "-o", str(raw), "-f", str(fps * mblur)]
        if draft:
            args += ["-q", "draft"]
        hf(args, hf_cwd(), log)  # exit code ignored on purpose; the artifact decides
        if raw != silent and raw.exists():
            vf = []
            if mblur > 1:
                vf += [f"tmix=frames={mblur}", f"fps={fps}"]
            if grain:
                vf += [f"noise=alls={grain}:allf=t:all_seed=7"]
            log.write(f"\n$ ffmpeg -vf {','.join(vf)}\n"); log.flush()
            subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(raw), "-vf", ",".join(vf),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", str(silent)],
                           stdout=log, stderr=subprocess.STDOUT)
            raw.unlink(missing_ok=True)
        has_v, dur = probe(silent) if silent.exists() else (False, 0.0)
        log.write(f"\ngate: video={has_v} dur={dur:.3f} want={want:.3f}\n")
        if not has_v:
            return result(False, "no video stream in silent render")
        if abs(dur - want) > TOL:
            return result(False, f"duration {dur:.2f}s vs data-duration {want:.2f}s")
        # Mux into a temp file and swap it in only once it probes clean: the last good render
        # survives a failed one without keeping a .prev copy, and the silent intermediate is dropped.
        wav = sd / "audio" / "narration.wav"
        tmp = rd / f"{sid}.tmp.mp4"
        log.flush()
        if wav.exists():
            cmd = [FFMPEG, "-y", "-v", "error", "-i", str(silent), "-i", str(wav),
                   "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                   "-b:a", "192k", str(tmp)]
        else:
            cmd = [FFMPEG, "-y", "-v", "error", "-i", str(silent), "-c", "copy", str(tmp)]
        subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
        silent.unlink(missing_ok=True)
    has_v, dur = probe(tmp) if tmp.exists() else (False, 0.0)
    if not has_v:
        tmp.unlink(missing_ok=True)
        return result(False, "final mux missing video stream")
    os.replace(tmp, final)
    return result(True, f"{dur:.2f}s -> {final}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("film")
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--no-check", dest="check", action="store_false",
                    help="skip hyperframes lint+check (default: run them; a scene with no timeline renders fine without them)")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--expect", type=float, help="override expected duration (gate testing)")
    ap.add_argument("--sync-durations", action="store_true")
    ap.add_argument("--scaffold", action="store_true", help="create scenes/<id>/ from the kit template")
    a = ap.parse_args()
    film = Path(a.film).expanduser().resolve()
    if not (film / "film.json").exists():
        sys.exit(f"render: no film.json in {film}")
    if a.scaffold:
        scaffold(film, a.scenes)
        return
    if a.sync_durations:
        sync_durations(film, a.scenes)
        return
    if hf_cmd() is None:
        sys.exit(f"render: no renderer. Run `npm ci` in {HF_DIR}, or install Node so npx can fetch hyperframes@{HF_VERSION}")
    cfg, ids = scene_ids(film, a.scenes)
    if not ids:
        sys.exit("render: no scenes")
    write_film_js(film, cfg)
    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        futs = [ex.submit(render_scene, film, cfg, s, a.draft, a.check, a.expect) for s in ids]
        res = [f.result() for f in futs]
    bad = 0
    for sid, ok, msg, secs in res:
        print(f"  {'PASS' if ok else 'FAIL'} {sid} ({secs:.1f}s) {msg}")
        bad += 0 if ok else 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
