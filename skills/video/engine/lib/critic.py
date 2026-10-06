#!/usr/bin/env python
"""critic.py: build the evidence packet a FRESH critic agent reads to judge a rendered film.

    critic.py <film_dir> [--video PATH] [--scene <id>] [--strict] [--skip-transcript]

Writes <film_dir>/critic/<video-stem>/ : sheet_NN.jpg, transitions/, cues/, frame0.png,
transcript.txt/.json, packet.md, packet.json. Measurements only, no opinions.

Tooling: frames are extracted with ffmpeg and timestamped + tiled with ImageMagick (`magick`),
because many ffmpeg builds lack drawtext. Without magick or a font the sheets fall back to unlabelled
ffmpeg tiles and the packet lists every tile time.

Transcript: local only. Uses stable-ts (the `asr` extra) or faster-whisper when either is installed,
model from $MVID_WHISPER_MODEL (default "base"). With neither, the transcript and WER check are
skipped and the packet says so. Nothing is sent to a remote host.
"""
import argparse, json, math, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

FFMPEG = os.environ.get("MVID_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("MVID_FFPROBE") or shutil.which("ffprobe") or "ffprobe"
MAGICK = shutil.which("magick") or ""
FONTS = [os.environ.get("MVID_LABEL_FONT", ""),
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]
WHISPER_MODEL = os.environ.get("MVID_WHISPER_MODEL", "base")

# thresholds (spec)
T_FROZEN_PER30 = 1.0
T_MAX_FREEZE = 0.5
T_LUFS, T_LUFS_TOL = -16.0, 1.0
T_TP = -1.0
T_SILENT_DB = -45.0
T_WER = 0.10
T_DUR = 0.25
SILENT_RUN_MIN = 1.0      # seconds of consecutive sub-threshold audio that counts as a silent window
CUE_OFFSET = 0.5          # cue frame is taken this long after the line start so the visual response has landed


def run(cmd, check=False, capture=True):
    p = subprocess.run([str(c) for c in cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed rc={p.returncode}: {p.stderr[-600:]}")
    return p


def probe(path):
    p = run([FFPROBE, "-v", "error", "-show_entries", "format=duration:stream=index,codec_type,width,height,r_frame_rate,duration",
             "-of", "json", path])
    try:
        j = json.loads(p.stdout)
    except Exception:
        raise RuntimeError(f"ffprobe could not read {path}: {p.stderr[-300:]}")
    info = {"duration": float(j["format"].get("duration", 0) or 0), "has_audio": False, "audio_duration": None}
    for s in j.get("streams", []):
        if s["codec_type"] == "video" and "width" not in info:
            n, _, d = s.get("r_frame_rate", "0/1").partition("/")
            info.update(width=s["width"], height=s["height"], fps=(float(n) / float(d or 1)) if float(d or 1) else 0)
        elif s["codec_type"] == "audio":
            info["has_audio"] = True
            try:
                info["audio_duration"] = float(s.get("duration"))
            except Exception:
                pass
    return info


def fmt_t(t):
    m, s = divmod(max(t, 0), 60)
    return f"{int(m)}:{s:04.1f}"


# ------------------------------------------------------------------ film model
def load_film(film_dir, scene_only=None):
    fj = film_dir / "film.json"
    film = json.loads(fj.read_text()) if fj.exists() else {}
    slug = film.get("slug") or film_dir.name
    mode = film.get("mode", "explainer")
    xfade = float(film.get("xfade", 0) or 0)
    ids = [scene_only] if scene_only else list(film.get("scenes", []))
    scenes, off = [], 0.0
    for i, sid in enumerate(ids):
        sd = film_dir / "scenes" / sid
        cues = None
        cj = sd / "audio" / "cues.json"
        if cj.exists():
            cues = json.loads(cj.read_text())
        dur = None
        src = None
        if cues and cues.get("total"):
            dur, src = float(cues["total"]), "cues.total"
        if dur is None:
            ih = sd / "index.html"
            if ih.exists():
                m = re.search(r'data-duration="([\d.]+)"', ih.read_text(errors="replace"))
                if m:
                    dur, src = float(m.group(1)), "data-duration"
        if dur is None:
            rp = film_dir / "renders" / f"{sid}.mp4"
            if rp.exists():
                dur, src = probe(rp)["duration"], "renders probe"
        nt = sd / "narration.txt"
        if nt.exists():   # [[hold N]] / [[tail N]] are layout markup, never spoken
            ref = " ".join(re.sub(r"\[\[[^\]]*\]\]", " ", l).strip() for l in nt.read_text().splitlines())
            ref = " ".join(ref.split())
        elif cues:
            ref = " ".join(l["text"] for l in cues.get("lines", []))
        else:
            ref = ""
        scenes.append({"id": sid, "dur": dur, "dur_src": src, "offset": off, "lines": (cues or {}).get("lines", []),
                       "narration": ref})
        if dur is not None:
            off += dur - (xfade if not scene_only else 0)
    return {"slug": slug, "mode": mode, "xfade": 0.0 if scene_only else xfade, "scenes": scenes, "film": film,
            "scene_only": bool(scene_only)}


def expected_duration(m):
    if any(s["dur"] is None for s in m["scenes"]) or not m["scenes"]:
        return None
    return sum(s["dur"] for s in m["scenes"]) - m["xfade"] * (len(m["scenes"]) - 1)


def pick_video(film_dir, slug):
    cands = []
    for od in (film_dir / "out" / slug, film_dir.parent.parent / "out" / slug):
        if od.is_dir():
            for f in od.iterdir():
                mm = re.fullmatch(re.escape(slug) + r"-v(\d+)\.mp4", f.name)
                if mm:
                    cands.append((int(mm.group(1)), f.stat().st_mtime, f))
    if not cands:
        return None
    return sorted(cands)[-1][2]


# ------------------------------------------------------------------ images
def grab(video, t, out, width=None, dur=None):
    """One frame at time t (seconds), clamped inside the file."""
    if dur:
        t = min(max(t, 0), max(dur - 0.05, 0))
    cmd = [FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1"]
    if width:
        cmd += ["-vf", f"scale={width}:-2"]
    if str(out).endswith(".jpg"):
        cmd += ["-q:v", "2"]
    run(cmd + [out])
    return Path(out).exists()


def font_path():
    return next((f for f in FONTS if f and os.path.exists(f)), None)


def labelled_montage(frames, labels, cols, out, tile_w):
    """Tile frames cols-wide with a timestamp burned into each. Returns True if labelled."""
    frames = [str(f) for f in frames]
    rows = math.ceil(len(frames) / cols)
    font = font_path()
    if font and MAGICK:
        lab = []
        for f, l in zip(frames, labels):
            o = f + ".lab.png"
            r = run([MAGICK, f, "-font", font, "-pointsize", str(max(16, tile_w // 16)), "-gravity", "northwest",
                     "-undercolor", "#000000CC", "-fill", "white", "-annotate", "+6+6", f" {l} ", o])
            lab.append(o if r.returncode == 0 and os.path.exists(o) else f)
        r = run([MAGICK, "montage", "-font", font, *lab, "-tile", f"{cols}x{rows}", "-geometry", "+3+3", "-background", "black",
                 "-quality", "88", out])
        if r.returncode == 0 and os.path.exists(out):
            return all(x.endswith(".lab.png") for x in lab)
    # fallback: unlabelled ffmpeg tile over a numbered copy
    d = Path(tempfile.mkdtemp(prefix="critic_tile_"))
    for i, f in enumerate(frames):
        shutil.copy(f, d / f"t_{i:03d}.png")
    run([FFMPEG, "-v", "error", "-y", "-framerate", "1", "-i", str(d / "t_%03d.png"),
         "-vf", f"tile={cols}x{rows}", "-frames:v", "1", "-q:v", "3", out])
    shutil.rmtree(d, ignore_errors=True)
    return False


def build_sheets(video, dur, outdir, tmp):
    n_sheets = max(1, math.ceil(dur / 18.0))   # 9 tiles per sheet, about 1 frame per 2s
    span = dur / n_sheets
    sheets = []
    for s in range(n_sheets):
        start = s * span
        times = [start + (k + 0.5) * span / 9 for k in range(9)]
        frames, labels = [], []
        for k, t in enumerate(times):
            fp = tmp / f"sh{s}_{k}.png"
            if grab(video, t, fp, width=640, dur=dur):
                frames.append(fp), labels.append(fmt_t(t))
        out = outdir / f"sheet_{s + 1:02d}.jpg"
        labelled = labelled_montage(frames, labels, 3, str(out), 640)
        sheets.append({"path": str(out), "start": start, "end": start + span, "fps": 9.0 / span, "times": times,
                       "labelled": labelled})
    return sheets


def build_transitions(video, dur, m, outdir, tmp):
    res = []
    outdir.mkdir(exist_ok=True)
    for i in range(1, len(m["scenes"])):
        sc = m["scenes"][i]
        center = sc["offset"] + m["xfade"] / 2
        t0 = min(max(center - 0.5, 0), max(dur - 1.0, 0))
        frames, labels = [], []
        for k in range(10):
            t = t0 + k * 0.1
            fp = tmp / f"tr{i}_{k}.png"
            if grab(video, t, fp, width=384, dur=dur):
                frames.append(fp), labels.append(f"{t:.1f}s")
        out = outdir / f"{m['scenes'][i - 1]['id']}__{sc['id']}.jpg"
        labelled_montage(frames, labels, 5, str(out), 384)
        res.append({"path": str(out), "from": m["scenes"][i - 1]["id"], "to": sc["id"], "join_at": sc["offset"],
                    "xfade": m["xfade"], "window": [t0, t0 + 1.0]})
    return res


def build_cues(video, dur, m, outdir):
    outdir.mkdir(exist_ok=True)
    res = []
    for sc in m["scenes"]:
        for ln in sc["lines"]:
            t_start = sc["offset"] + float(ln["start"])
            t = t_start + min(CUE_OFFSET, float(ln.get("dur", 1)) / 2)
            p = outdir / f"{sc['id']}_L{int(ln['i']):02d}_t{t_start:07.2f}.jpg"
            if grab(video, t, p, dur=dur):
                res.append({"path": str(p), "scene": sc["id"], "line": ln["i"], "line_start": t_start, "frame_at": t,
                            "text": ln["text"]})
    return res


# ------------------------------------------------------------------ measurements
FREEZE_N, FREEZE_D = 0.003, 0.5   # freezedetect noise and minimum duration, used by measure_frozen and the report


def measure_frozen(video, dur):
    # Downscale + blur before freezedetect: temporal film grain (film.json "grain") makes every frame differ,
    # so a full-frame check reports 0 freezes on a frozen picture. With this filter a still under grain is
    # caught and a slow 20px/s pan is not flagged.
    p = run([FFMPEG, "-hide_banner", "-nostats", "-i", video, "-an", "-vf", f"scale=160:-2,gblur=sigma=1.5,freezedetect=n={FREEZE_N}:d={FREEZE_D}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"freeze_start:\s*([\d.]+)", p.stderr)]
    durs = [float(x) for x in re.findall(r"freeze_duration:\s*([\d.]+)", p.stderr)]
    freezes = []
    for i, s in enumerate(starts):
        d = durs[i] if i < len(durs) else max(dur - s, 0)   # a freeze that runs to EOF has no end line
        freezes.append({"start": s, "dur": d})
    total = sum(f["dur"] for f in freezes)
    return {"freezes": freezes, "total": total, "longest": max([f["dur"] for f in freezes], default=0.0),
            "per30": total / dur * 30 if dur else 0.0, "ok_run": p.returncode == 0}


def measure_black(video, dur):
    # Blank frames in transitions. Same downscale + blur as freezedetect so film grain does not lift a black
    # frame over pix_th. pix_th 0.03: dark navy backgrounds sit near 0.08 of the luma range and would read as
    # black at 0.10. A run that ends at EOF is a fade-out, allowed.
    p = run([FFMPEG, "-hide_banner", "-nostats", "-i", video, "-an", "-vf",
             "scale=160:-2,gblur=sigma=1.5,blackdetect=d=0.08:pic_th=0.98:pix_th=0.03", "-f", "null", "-"])
    runs = [{"start": float(a), "end": float(b)} for a, b in
            re.findall(r"black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)", p.stderr)]
    for r in runs:
        r["at_end"] = r["start"] > 0.5 and r["end"] >= dur - 0.1
    return {"runs": runs, "ok_run": p.returncode == 0}


def measure_readtime(film_dir, m):
    """lib/readcheck.mjs over each scene's HTML: text blocks held shorter than letters/15 + 1.5 s. Times are film times.
    Returns None when it could not run, with the reason, never an empty pass."""
    rc = Path(__file__).resolve().parent / "readcheck.mjs"
    dirs = [film_dir / "scenes" / s["id"] for s in m["scenes"]]
    missing = [d.name for d in dirs if not (d / "index.html").exists()]
    if missing:
        return {"error": f"no index.html for {', '.join(missing)}"}
    p = run(["node", str(rc), *map(str, dirs), "--json"])
    try:
        res = json.loads(p.stdout)
    except ValueError:
        return {"error": f"readcheck exit {p.returncode}: {(p.stderr or p.stdout)[-300:]}"}
    off = {s["id"]: s["offset"] for s in m["scenes"]}
    for sc in res["scenes"]:
        for b in sc["blocks"]:
            b["film_t"] = off.get(sc["scene"], 0.0) + b["start"]
    res["short"] = [dict(b, scene=sc["scene"]) for sc in res["scenes"] for b in sc["blocks"] if b["status"] == "short"]
    res["total"] = sum(len(sc["blocks"]) for sc in res["scenes"])
    res["errors"] = [f"{sc['scene']}: {sc['error']}" for sc in res["scenes"] if sc["error"]]
    return res


def check_extra(black, read):
    """Checks and packet sections for blackdetect and readcheck, appended after evaluate()."""
    chk, L = [], []
    if black is None or not black["ok_run"]:
        chk.append(("black frames", "N/A", "blackdetect did not run"))
    else:
        mid = [r for r in black["runs"] if not r["at_end"]]
        det = ", ".join(f"{fmt_t(r['start'])}-{fmt_t(r['end'])}" for r in mid) or "none"
        tail = [r for r in black["runs"] if r["at_end"]]
        chk.append(("black frames", "FAIL" if mid else "PASS",
                    f"runs >= 0.08s before the end: {det}" + (f"; fade to black at {fmt_t(tail[0]['start'])} (end, allowed)" if tail else "")))
    # Read time is INFO, not FAIL: its precision is not yet known across many films, and a gate that
    # over-fires gets muted.
    if read is None:
        chk.append(("text read time", "N/A", "skipped"))
    elif read.get("error") or read.get("errors"):
        chk.append(("text read time", "N/A", "not checked: " + (read.get("error") or "; ".join(read["errors"]))))
    else:
        n = len(read["short"])
        chk.append(("text read time", "INFO" if n else "PASS",
                    f"{n} of {read['total']} text blocks held under letters/15 + 1.5s (min 1.5s)"))
        if n:
            L += ["## Text read time (readcheck)", "",
                  "Each block below left the screen before a viewer could finish reading it. Judge each: P1 when it carries a",
                  "number, name or claim the viewer needs; P2 when it is decoration. Times are film times.", "",
                  "| at | scene | held | needs | text |", "|---|---|---|---|---|"]
            for b in sorted(read["short"], key=lambda b: b["film_t"]):
                L.append(f"| {fmt_t(b['film_t'])} | {b['scene']} | {b['held']:.1f}s | {b['need']:.1f}s | {b['text'][:80].replace('|', '/')} |")
            L.append("")
    return chk, L


def measure_loudness(video):
    p = run([FFMPEG, "-hide_banner", "-nostats", "-i", video, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = p.stderr.split("Summary:")[-1]
    def g(pat):
        m = re.search(pat, tail)
        return float(m.group(1)) if m else None
    return {"lufs": g(r"I:\s*(-?[\d.]+)\s*LUFS"), "lra": g(r"LRA:\s*(-?[\d.]+)\s*LU"), "tp": g(r"Peak:\s*(-?[\d.]+)\s*dBFS")}


def window_volume(video, t0, t1):
    p = run([FFMPEG, "-hide_banner", "-nostats", "-ss", f"{t0:.3f}", "-t", f"{max(t1 - t0, 0.05):.3f}", "-i", video, "-vn",
             "-af", "volumedetect", "-f", "null", "-"])
    mean = re.search(r"mean_volume:\s*(-?[\d.]+|-inf)", p.stderr)
    mx = re.search(r"max_volume:\s*(-?[\d.]+|-inf)", p.stderr)
    f = lambda m: (float("-inf") if m and m.group(1) == "-inf" else float(m.group(1))) if m else None
    return {"mean": f(mean), "max": f(mx)}


def decode_mono(video, sr=16000):
    import numpy as np
    p = subprocess.run([FFMPEG, "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return np.frombuffer(p.stdout, dtype="<i2").astype("float64") / 32768.0, sr


def silent_runs(video, win=0.25):
    """Runs of consecutive windows whose mean level (dBFS, same quantity volumedetect reports) is under -45 dB."""
    import numpy as np
    x, sr = decode_mono(video)
    n = int(sr * win)
    if len(x) < n:
        return [], 0.0
    k = len(x) // n
    rms = np.sqrt((x[: k * n].reshape(k, n) ** 2).mean(axis=1))
    db = 20 * np.log10(np.maximum(rms, 1e-9))
    quiet = db < T_SILENT_DB
    runs, i = [], 0
    while i < k:
        if quiet[i]:
            j = i
            while j < k and quiet[j]:
                j += 1
            runs.append((i * win, j * win))
            i = j
        else:
            i += 1
    return runs, len(x) / sr


def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def measure_audio_windows(video, dur, m):
    """Per-scene volumedetect plus silent-window detection against where narration should be."""
    per_scene = []
    for sc in m["scenes"]:
        if sc["dur"] is None:
            continue
        t0, t1 = sc["offset"], min(sc["offset"] + sc["dur"], dur)
        v = window_volume(video, t0, t1)
        per_scene.append({"scene": sc["id"], "t0": t0, "t1": t1, **v,
                          "silent": v["mean"] is not None and v["mean"] < T_SILENT_DB})
    runs, _ = silent_runs(video)
    defects = []
    for r0, r1 in runs:
        if r1 - r0 < SILENT_RUN_MIN - 1e-6:
            continue
        for sc in m["scenes"]:
            if sc["dur"] is None:
                continue
            s0, s1 = sc["offset"], sc["offset"] + sc["dur"]
            if overlap(r0, r1, s0, s1) <= 0:
                continue
            # Speech spans come from the word timings when present: a line's dur includes the TTS's own
            # trailing silence, so line bounds flag the natural tail before the next line as a dropout.
            speech = []
            for l in sc["lines"]:
                ws = l.get("words") or []
                a = float(ws[0]["start"]) if ws else float(l["start"])
                b = float(ws[-1]["end"]) if ws else float(l["start"]) + float(l["dur"])
                speech.append((sc["offset"] + a + 0.15, sc["offset"] + b - 0.15))
            hit = sum(overlap(r0, r1, a, b) for a, b in speech)
            if (speech and hit > 0.3) or (not speech and overlap(r0, r1, s0, s1) >= SILENT_RUN_MIN):
                defects.append({"scene": sc["id"], "t0": max(r0, s0), "t1": min(r1, s1),
                                "why": "silent during narration line" if speech else "silent scene with no narration"})
    return {"per_scene": per_scene, "runs": [{"t0": a, "t1": b} for a, b in runs if b - a >= SILENT_RUN_MIN - 1e-6],
            "defects": defects}


# ------------------------------------------------------------------ transcript / WER
def norm_words(text):
    text = text.lower().replace("%", " percent ").replace("&", " and ")
    text = re.sub(r"(?<=\d),(?=\d)", "", text)
    try:
        from num2words import num2words
        text = re.sub(r"\d+(?:\.\d+)?", lambda mo: " " + num2words(float(mo.group()) if "." in mo.group() else int(mo.group())) + " ", text)
    except Exception:
        pass
    text = re.sub(r"[-‐-―]", " ", text)
    text = re.sub(r"[^a-z' ]+", " ", text).replace("'", "")
    return text.split()


def align(ref, hyp):
    """Levenshtein alignment. Returns ops list of (op, ref_idx|None, hyp_idx|None), op in match/sub/del/ins."""
    n, k = len(ref), len(hyp)
    d = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(k + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            d[i][j] = min(d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]), d[i - 1][j] + 1, d[i][j - 1] + 1)
    ops, i, j = [], n, k
    while i > 0 or j > 0:
        if i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]):
            ops.append(("match" if ref[i - 1] == hyp[j - 1] else "sub", i - 1, j - 1)); i -= 1; j -= 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append(("del", i - 1, None)); i -= 1
        else:
            ops.append(("ins", None, j - 1)); j -= 1
    return ops[::-1]


def asr_backend():
    """Name of the local transcriber available, or None. Never a remote service."""
    for mod in ("stable_whisper", "faster_whisper"):
        try:
            __import__(mod)
            return mod
        except Exception:
            continue
    return None


_asr_model = {}


def asr_words(wav, prompt=None):
    """Transcribe a 16 kHz mono wav locally. Returns (segments [(start, text)], words [{w,start,end}])."""
    be = asr_backend()
    if be == "stable_whisper":
        import stable_whisper
        m = _asr_model.get(be) or _asr_model.setdefault(be, stable_whisper.load_model(WHISPER_MODEL, device="cpu"))
        res = m.transcribe(str(wav), language="en", fp16=False, condition_on_previous_text=False, verbose=None,
                           initial_prompt=prompt)
        segs = [(s.start, s.text) for s in res.segments]
        words = [{"w": w.word.strip(), "start": float(w.start), "end": float(w.end)} for s in res.segments for w in s.words]
        return segs, words
    if be == "faster_whisper":
        from faster_whisper import WhisperModel
        m = _asr_model.get(be) or _asr_model.setdefault(be, WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8"))
        it, _ = m.transcribe(str(wav), language="en", word_timestamps=True, condition_on_previous_text=False,
                             initial_prompt=prompt)
        segs, words = [], []
        for s in it:
            segs.append((s.start, s.text))
            words += [{"w": w.word.strip(), "start": float(w.start), "end": float(w.end)} for w in (s.words or [])]
        return segs, words
    raise RuntimeError("no local transcriber installed")


def transcribe(video, outdir, tmp, prompt=None):
    wav = tmp / "audio16k.wav"
    run([FFMPEG, "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav])
    # film.json "asr_prompt": proper names, so names don't read as misspeaks
    segs, words = asr_words(wav, prompt)
    (outdir / "transcript.json").write_text(json.dumps(words, indent=1))
    (outdir / "transcript.txt").write_text("\n".join(f"[{fmt_t(a)}] {t.strip()}" for a, t in segs) + "\n")
    return words


def recheck_failed_scenes(video, m, dur, wer, tmp, prompt=None):
    """Whisper on a whole film can silently drop a long stretch, which reads as a huge misspeak rate.
    Re-transcribe each failing scene's own window and keep the lower WER; the entry records that it was
    rechecked and both numbers."""
    bad = [p for p in wer["scenes"] if p["wer"] is not None and p["wer"] > T_WER]
    if not bad:
        return wer
    by_id = {sc["id"]: sc for sc in m["scenes"]}
    for p in bad:
        sc = by_id[p["scene"]]
        if sc["dur"] is None:
            continue
        wav = tmp / f"recheck-{sc['id']}.wav"
        run([FFMPEG, "-v", "error", "-y", "-ss", f"{max(0.0, sc['offset']):.3f}", "-t", f"{sc['dur']:.3f}",
             "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav])
        # both with and without the name prompt: the prompt fixes names but can also make whisper skip a stretch
        best = None
        for pr in dict.fromkeys([prompt, None]):
            _, words = asr_words(wav, pr)
            solo = {"mode": m["mode"], "xfade": 0.0, "film": m["film"], "scenes": [dict(sc, offset=0.0)]}
            r = measure_wer(words, solo, sc["dur"])["scenes"][0]
            if r["wer"] is not None and (best is None or r["wer"] < best["wer"]):
                best = r
        if best is not None and best["wer"] < p["wer"]:
            best["rechecked_from"] = p["wer"]
            p.clear(); p.update(best)
    return wer


def merge_compounds(ref, ref_scene, hyp, hyp_t, hyp_raw):
    """Spelling, not speech: "re check"/"recheck", "data set"/"dataset", "set up"/"setup"
    are one spoken word written two ways. Join an adjacent pair on either side when the joined form is a
    single word on the other side. A spoken URL's "dot" never reaches the transcript as a word; drop it."""
    keep = [i for i, w in enumerate(ref) if w != "dot"]
    ref, ref_scene = [ref[i] for i in keep], [ref_scene[i] for i in keep]
    keep = [i for i, w in enumerate(hyp) if w != "dot"]
    hyp, hyp_t, hyp_raw = [hyp[i] for i in keep], [hyp_t[i] for i in keep], [hyp_raw[i] for i in keep]

    def join(words, other, *side):
        vocab, i, out = set(other), 0, [[] for _ in range(1 + len(side))]
        while i < len(words):
            if i + 1 < len(words) and words[i] + words[i + 1] in vocab and words[i] not in vocab:
                out[0].append(words[i] + words[i + 1])
                for k, s in enumerate(side): out[k + 1].append(s[i])
                i += 2
            else:
                out[0].append(words[i])
                for k, s in enumerate(side): out[k + 1].append(s[i])
                i += 1
        return out
    ref, ref_scene = join(ref, hyp, ref_scene)
    hyp, hyp_t, hyp_raw = join(hyp, ref, hyp_t, hyp_raw)
    return ref, ref_scene, hyp, hyp_t, hyp_raw


def measure_wer(words, m, dur):
    """Whole-film alignment of narration vs what the output audio says; errors attributed to scenes
    (del/sub by reference position, insertions by the time the extra word was spoken)."""
    ref, ref_scene = [], []
    for sc in m["scenes"]:
        for w in norm_words(sc["narration"]):
            ref.append(w); ref_scene.append(sc["id"])
    hyp, hyp_t, hyp_raw = [], [], []
    for w in words:
        for t in norm_words(w["w"]):
            hyp.append(t); hyp_t.append(w["start"]); hyp_raw.append(w["w"])
    ref, ref_scene, hyp, hyp_t, hyp_raw = merge_compounds(ref, ref_scene, hyp, hyp_t, hyp_raw)
    ops = align(ref, hyp)
    bounds = []
    for i, sc in enumerate(m["scenes"]):
        if sc["dur"] is None:
            bounds.append((sc["id"], 0, dur)); continue
        lo = 0.0 if i == 0 else sc["offset"] + m["xfade"] / 2
        hi = (m["scenes"][i + 1]["offset"] + m["xfade"] / 2) if i + 1 < len(m["scenes"]) else dur + 1
        bounds.append((sc["id"], lo, hi))
    def scene_at(t):
        for sid, lo, hi in bounds:
            if lo <= t < hi:
                return sid
        return bounds[-1][0]
    per = {sc["id"]: {"scene": sc["id"], "ref_words": 0, "sub": 0, "del": 0, "ins": 0, "missing": [], "extra": [], "swapped": []}
           for sc in m["scenes"]}
    for sid in ref_scene:
        per[sid]["ref_words"] += 1
    for op, ri, hj in ops:
        if op == "del":
            p = per[ref_scene[ri]]; p["del"] += 1; p["missing"].append(ref[ri])
        elif op == "sub":
            p = per[ref_scene[ri]]; p["sub"] += 1; p["swapped"].append(f"{ref[ri]} -> {hyp[hj]}")
        elif op == "ins":
            p = per[scene_at(hyp_t[hj])]; p["ins"] += 1; p["extra"].append(f"{hyp[hj]} @{fmt_t(hyp_t[hj])}")
    for p in per.values():
        p["wer"] = (p["sub"] + p["del"] + p["ins"]) / p["ref_words"] if p["ref_words"] else None
    tot_err = sum(p["sub"] + p["del"] + p["ins"] for p in per.values())
    return {"scenes": list(per.values()), "total_wer": tot_err / len(ref) if ref else None, "ref_words": len(ref),
            "hyp_words": len(hyp)}


# ------------------------------------------------------------------ checks + packet
def scene_of(m, t):
    hit = "?"
    for sc in m["scenes"]:
        if sc["dur"] is not None and sc["offset"] <= t + 1e-6:
            hit = sc["id"]
    return hit


def evaluate(m, info, expected, frozen, loud, aud, wer, wer_note="transcript skipped or unavailable"):
    """Returns list of (name, status, detail) with status PASS / FAIL / INFO / N/A."""
    mode = m["mode"]
    chk = []
    # frozen
    if frozen is None:
        chk.append(("frozen time per 30s", "N/A", "not measured"))
    elif mode == "explainer":
        chk.append(("frozen time per 30s", "INFO", f"{frozen['per30']:.2f}s per 30s (holds are intentional in explainers; reported only)"))
    else:
        ok = frozen["per30"] < T_FROZEN_PER30
        chk.append(("frozen time per 30s", "PASS" if ok else "FAIL", f"{frozen['per30']:.2f}s per 30s, threshold < {T_FROZEN_PER30}s"))
    if frozen is not None and mode in ("reel", "loop"):
        ok = frozen["longest"] <= T_MAX_FREEZE + 0.05
        chk.append(("max freeze (reel/loop)", "PASS" if ok else "FAIL", f"longest {frozen['longest']:.2f}s, threshold <= {T_MAX_FREEZE}s"))
    elif frozen is not None:
        chk.append(("max freeze", "INFO", f"longest {frozen['longest']:.2f}s (limit applies to reel/loop only)"))
    # loudness
    if not info["has_audio"]:
        for n in ("loudness LUFS", "true peak", "silent windows", "transcript WER"):
            chk.append((n, "N/A", "output has no audio stream"))
    else:
        if loud and loud["lufs"] is not None:
            ok = abs(loud["lufs"] - T_LUFS) <= T_LUFS_TOL
            chk.append(("loudness LUFS", "PASS" if ok else "FAIL", f"{loud['lufs']:.1f} LUFS integrated, target {T_LUFS:.0f} +/- {T_LUFS_TOL:.0f} (LRA {loud['lra']} LU)"))
        else:
            chk.append(("loudness LUFS", "FAIL", "ebur128 produced no integrated value"))
        if loud and loud["tp"] is not None:
            if m.get("scene_only") and loud["tp"] > T_TP:
                # a scene render carries the raw narration; the limiter runs in `mvid assemble`, so a scene's
                # peak says nothing about the film. The film-level packet holds the gate.
                chk.append(("true peak", "INFO", f"{loud['tp']:.1f} dBTP before the assemble limiter (gated on the film)"))
            else:
                chk.append(("true peak", "PASS" if loud["tp"] <= T_TP else "FAIL", f"{loud['tp']:.1f} dBTP, threshold <= {T_TP}"))
        else:
            chk.append(("true peak", "FAIL", "ebur128 produced no true-peak value"))
        bad = [w for w in aud["per_scene"] if w["silent"]]
        d = aud["defects"]
        detail = f"{len(aud['per_scene'])} scene windows measured (volumedetect mean, silent < {T_SILENT_DB:.0f} dB)"
        if bad:
            detail += "; SILENT scenes: " + ", ".join(f"{w['scene']} ({w['mean']:.1f} dB)" for w in bad)
        if d:
            detail += "; SILENT windows: " + ", ".join(f"{x['scene']} {fmt_t(x['t0'])}-{fmt_t(x['t1'])} ({x['why']})" for x in d)
        chk.append(("silent windows", "FAIL" if (bad or d) else "PASS", detail))
        if wer is None:
            chk.append(("transcript WER", "N/A", wer_note))
        else:
            badw = [p for p in wer["scenes"] if p["wer"] is not None and p["wer"] > T_WER]
            det = "; ".join(f"{p['scene']} {p['wer'] * 100:.0f}%" if p["wer"] is not None else f"{p['scene']} n/a" for p in wer["scenes"])
            chk.append(("transcript WER", "FAIL" if badw else "PASS", f"per scene: {det}; threshold <= {T_WER * 100:.0f}% each"))
    # duration
    if expected is None:
        chk.append(("duration", "N/A", f"expected duration unknown; output {info['duration']:.2f}s"))
    else:
        diff = info["duration"] - expected
        chk.append(("duration", "PASS" if abs(diff) <= T_DUR else "FAIL",
                    f"output {info['duration']:.2f}s vs expected {expected:.2f}s (diff {diff:+.2f}s, tolerance {T_DUR}s)"))
    return chk


INSTRUCTIONS = """\
## Critic instructions

You are a fresh critic. You did not build this film and you have not been told what was fixed. Judge rendered pixels and
measured audio only. Everything above this block is measurement; nothing above is an opinion.

**Look at every image listed in "Images to look at": every contact sheet, every transition strip, every cue frame and frame0.**
Do not sample. Crop or zoom into anything you cannot read.

Order of judgment:

1. **Template look, yes or no, FIRST.** Does it read as a template (centered text on a gradient, fade-ins, the same layout
   repeated scene after scene)? Answer `template look: yes` or `template look: no` and give the evidence frames before anything else.
2. **Text readability and collisions.** Text at phone size, anything clipped, any title over another title, text flying through
   other text, especially inside the transition strips. Text under y = 993 at 1080p is a defect.
   Rule on every row of the "Text read time" table: it lists text that left the screen too soon to read, which a still cannot show.
3. **Contrast.** Settled text against its background (aim for 4.5:1). Note the frame.
4. **Focus follows the narration.** For each cue frame, say whether what is on screen is what the line at that time is talking about.
   Cue frames are taken 0.5s after the line starts; the "narration line" text is given beside each one.
5. **Numbers and names match KIT.md.** Open `KIT.md` in the film dir. Every on-screen number, name and claim must appear there.
   Anything on screen that is not in KIT.md is a P0.
6. **Frame 0 is a finished picture.** No half-entered word, no blank frame.
7. **Empty frames, unequal spacing, misaligned left edges, transitions with no carried object.**

Return:

- A ranked P0/P1/P2 list of defects, **P0** blocks shipping, **P1** fix in the next pass, **P2** polish, each with a
  timestamp (m:ss.s) and the scene id.
- Then a section **Measured** (facts you confirmed from the packet or the images) kept separate from a section
  **Human must still watch or listen** (pacing, music fit, voice quality, sound effects, anything the stills and numbers cannot show).
  Do not claim you watched or heard the film.
- End with exactly one line: `SHIP` or `ONE MORE PASS` (list at most 3 fixes for the pass). If any measured check above is FAIL,
  the verdict cannot be SHIP.
"""


def write_packet(outdir, video, info, m, expected, checks, frozen, loud, aud, wer, sheets, strips, cues, frame0, scene_only,
                 extra=()):
    L = []
    allp = all(c[1] != "FAIL" for c in checks)
    L += [f"# Critic packet: {Path(video).name}", "",
          f"- film: `{m['slug']}`   mode: `{m['mode']}`   scenes: {', '.join(s['id'] for s in m['scenes']) or '(none)'}",
          f"- video: `{video}`", f"- stream: {info.get('width')}x{info.get('height')} @ {info.get('fps', 0):.2f}fps, "
          f"{info['duration']:.2f}s, audio {'yes' if info['has_audio'] else 'NO'}" +
          (f" ({info['audio_duration']:.2f}s)" if info.get("audio_duration") else ""),
          f"- xfade: {m['xfade']}s" + ("   (single-scene critique)" if scene_only else ""), "",
          f"## Measured checks: {'PASS' if allp else 'FAIL'}", "", "| check | result | measurement |", "|---|---|---|"]
    for n, s, d in checks:
        L.append(f"| {n} | **{s}** | {d} |")
    L += ["", "Thresholds: frozen < 1s per 30s (explainer: report only); max freeze 0.5s (reel/loop); LUFS -16 +/- 1; true peak <= -1.0;",
          "no silent scene windows; WER <= 10% per scene; duration within 0.25s. PASS on every line does not mean the film is good.", ""]
    L += ["## Scene timeline", "", "| scene | film start | dur | dur source | lines |", "|---|---|---|---|---|"]
    for sc in m["scenes"]:
        L.append(f"| {sc['id']} | {sc['offset']:.2f}s | {sc['dur'] if sc['dur'] is None else round(sc['dur'], 2)} | {sc['dur_src']} | {len(sc['lines'])} |")
    L.append("")
    if frozen is not None:
        L += ["## Frozen time", "", f"total frozen {frozen['total']:.2f}s = {frozen['per30']:.2f}s per 30s; longest {frozen['longest']:.2f}s "
              f"(freezedetect n={FREEZE_N} d={FREEZE_D}, after scale=160 + gblur)", ""]
        for f in frozen["freezes"]:
            L.append(f"- {fmt_t(f['start'])} to {fmt_t(f['start'] + f['dur'])} ({f['dur']:.2f}s) in {scene_of(m, f['start'])}")
        if not frozen["freezes"]:
            L.append(f"- no freeze of {FREEZE_D}s or longer")
        L.append("")
    if loud:
        L += ["## Loudness", "", f"- integrated {loud['lufs']} LUFS, LRA {loud['lra']} LU, true peak {loud['tp']} dBTP (ebur128)", ""]
    if aud:
        L += ["## Audio windows (volumedetect)", "", "| scene | window | mean dB | max dB | silent |", "|---|---|---|---|---|"]
        for w in aud["per_scene"]:
            L.append(f"| {w['scene']} | {fmt_t(w['t0'])}-{fmt_t(w['t1'])} | {w['mean']} | {w['max']} | {'YES' if w['silent'] else 'no'} |")
        L.append("")
        L.append(f"Silent runs of {SILENT_RUN_MIN:.0f}s or longer (0.25s windows under {T_SILENT_DB:.0f} dB): " +
                 (", ".join(f"{fmt_t(r['t0'])}-{fmt_t(r['t1'])}" for r in aud["runs"]) or "none"))
        L += ["", "Runs that fall in the natural lead/gap/tail silence of a narrated scene are not defects; only runs over a narration line "
              "or inside a scene with no narration are flagged above.", ""]
    if wer is not None:
        L += [f"## Transcript vs narration.txt (local {asr_backend()} on the output audio)", "",
              f"total WER {wer['total_wer'] * 100:.1f}% over {wer['ref_words']} reference words ({wer['hyp_words']} heard). "
              "Numbers are spelled out on both sides before comparing.", "",
              "| scene | ref words | WER | sub | missing | extra |", "|---|---|---|---|---|---|"]
        for p in wer["scenes"]:
            w = "n/a" if p["wer"] is None else f"{p['wer'] * 100:.0f}%"
            L.append(f"| {p['scene']} | {p['ref_words']} | {w} | {p['sub']} | {p['del']} | {p['ins']} |")
        for p in wer["scenes"]:
            if p["missing"] or p["extra"] or p["swapped"]:
                L += ["", f"**{p['scene']}**", f"- missing words: {' '.join(p['missing']) or 'none'}",
                      f"- extra words: {', '.join(p['extra']) or 'none'}",
                      f"- swapped: {', '.join(p['swapped']) or 'none'}"]
        L += ["", f"Transcript with timings: `{outdir / 'transcript.txt'}`", ""]
    L += list(extra)
    L += ["## Images to look at", "", f"- frame 0: `{frame0}`" if frame0 else "- frame 0: MISSING"]
    for s in sheets:
        tag = "" if s["labelled"] else "  (UNLABELLED, tile times: " + ", ".join(fmt_t(t) for t in s["times"]) + ")"
        L.append(f"- contact sheet {fmt_t(s['start'])}-{fmt_t(s['end'])}, 3x3 row-major, each tile timestamped: `{s['path']}`{tag}")
    for t in strips:
        L.append(f"- transition {t['from']} to {t['to']}, join at {fmt_t(t['join_at'])}, 10 frames at 10fps "
                 f"{fmt_t(t['window'][0])}-{fmt_t(t['window'][1])}, 5x2: `{t['path']}`")
    for c in cues:
        L.append(f"- cue frame {c['scene']} line {c['line']}, line starts {fmt_t(c['line_start'])}, frame at {fmt_t(c['frame_at'])}: "
                 f"`{c['path']}`  narration line: \"{c['text']}\"")
    L += ["", f"KIT.md (numbers source of truth): `{Path(outdir).parent.parent / 'KIT.md'}`", "", INSTRUCTIONS]
    (outdir / "packet.md").write_text("\n".join(L))
    return allp


# ------------------------------------------------------------------ main
def build(film_dir, video=None, scene=None, skip_transcript=False, skip_readcheck=False):
    film_dir = Path(film_dir).resolve()
    m = load_film(film_dir, scene)
    if scene:
        video = film_dir / "renders" / f"{scene}.mp4"
    elif video is None:
        video = pick_video(film_dir, m["slug"])
    if video is None or not Path(video).exists():
        raise SystemExit(f"critic: no video found (looked for out/{m['slug']}/{m['slug']}-v*.mp4 under {film_dir} and its root); pass --video")
    video = Path(video).resolve()
    outdir = film_dir / "critic" / video.stem
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    info = probe(video)
    dur = info["duration"]
    expected = expected_duration(m)
    tmp = Path(tempfile.mkdtemp(prefix="critic_"))
    try:
        sheets = build_sheets(video, dur, outdir, tmp)
        strips = build_transitions(video, dur, m, outdir / "transitions", tmp)
        cues = build_cues(video, dur, m, outdir / "cues")
        f0 = outdir / "frame0.png"
        grab(video, 0, f0)
        frozen = measure_frozen(video, dur)
        loud = aud = wer = None
        wer_note = "transcript skipped (--skip-transcript)" if skip_transcript else "no narration to compare"
        if info["has_audio"]:
            loud = measure_loudness(video)
            aud = measure_audio_windows(video, dur, m)
            if not skip_transcript and any(s["narration"] for s in m["scenes"]):
                if asr_backend() is None:
                    wer_note = ("not checked: no local transcriber installed "
                                "(uv sync --extra asr, or pip install faster-whisper)")
                    print(f"critic: {wer_note}", file=sys.stderr)
                else:
                    words = transcribe(video, outdir, tmp, m["film"].get("asr_prompt"))
                    wer = measure_wer(words, m, dur)
                    wer = recheck_failed_scenes(video, m, dur, wer, tmp, m["film"].get("asr_prompt"))
        black = measure_black(video, dur)
        read = None if skip_readcheck else measure_readtime(film_dir, m)
        checks = evaluate(m, info, expected, frozen, loud, aud, wer, wer_note)
        more, extra = check_extra(black, read)
        checks += more
        ok = write_packet(outdir, video, info, m, expected, checks, frozen, loud, aud, wer, sheets, strips, cues,
                          f0 if f0.exists() else None, bool(scene), extra)
        (outdir / "packet.json").write_text(json.dumps(
            {"video": str(video), "ok": ok, "checks": [{"name": n, "status": s, "detail": d} for n, s, d in checks],
             "frozen": frozen, "black": black, "readtime": read,
             "loudness": loud, "audio": aud, "wer": wer, "expected_duration": expected, "duration": dur,
             "images": {"frame0": str(f0), "sheets": [s["path"] for s in sheets], "transitions": [t["path"] for t in strips],
                        "cues": [c["path"] for c in cues]}}, indent=1, default=str))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return outdir, ok, checks


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the critic evidence packet for a rendered film.")
    ap.add_argument("film_dir")
    ap.add_argument("--video")
    ap.add_argument("--scene")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any measured check fails")
    ap.add_argument("--skip-transcript", action="store_true")
    ap.add_argument("--skip-readcheck", action="store_true", help="skip the per-scene text read-time check (headless Chrome)")
    a = ap.parse_args(argv)
    outdir, ok, checks = build(a.film_dir, a.video, a.scene, a.skip_transcript, a.skip_readcheck)
    for n, s, d in checks:
        print(f"{s:5} {n}: {d}")
    print(f"MEASURED: {'PASS' if ok else 'FAIL'}\npacket: {outdir / 'packet.md'}")
    return 1 if (a.strict and not ok) else 0


if __name__ == "__main__":
    sys.exit(main())
