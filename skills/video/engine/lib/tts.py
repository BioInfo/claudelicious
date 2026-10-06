#!/usr/bin/env python
"""tts.py <scene_dir> [--voice af_heart] [--speed 1.0] [--force]

Narration step of mvid (local Kokoro TTS). Reads <scene_dir>/narration.txt (one cue per line,
blanks ignored) and writes <scene_dir>/audio/{line_NN.wav, narration.wav, cues.json, cues.js, .hashes.json}.
Voice/speed default to ../../film.json when the flags are absent. Only changed lines are re-synthesized.

Markup in narration.txt (never spoken):
  a line ending in [[hold 1.5]]   adds 1.5s of silence after that line (a reveal beat)
  a line [[tail 4.0]] on its own  sets this scene's closing silence (film.json "tail" otherwise)
"""
import os, sys, json, argparse, hashlib, re, subprocess, shutil, tempfile, time

# Kokoro's English G2P falls back to espeak-ng; point it at a Homebrew install when one is present.
for _var, _path in (("ESPEAK_DATA_PATH", "/opt/homebrew/share/espeak-ng-data"),
                    ("PHONEMIZER_ESPEAK_LIBRARY", "/opt/homebrew/lib/libespeak-ng.dylib")):
    if os.path.exists(_path):
        os.environ.setdefault(_var, _path)

import numpy as np
import soundfile as sf

SR = 24000
# Scene-edge silence. A cut costs tail + next lead - xfade of dead air, so keep the edges short
# (about 1s audible per cut). film.json "lead"/"tail" override.
LEAD, GAP, TAIL = 0.35, 0.7, 0.5
FADE_IN, FADE_OUT = 0.010, 0.025
TARGET_LUFS = -16.0
FFMPEG = os.environ.get("MVID_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


# ---------- helpers ----------
def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


_VERSION = re.compile(r"(?<=[A-Za-z])-(\d+)\.(\d+)(?![\d.%])")


def speakable(text):
    """Spoken form for the TTS only (on-screen text and cues keep the written form).
    Kokoro reads a hyphenated version like "Model-2.5" as "Model two, five"; this says "Model 2 point 5"."""
    return _VERSION.sub(lambda m: f" {m.group(1)} point {m.group(2)}", text)


def line_hash(text, voice, speed, backend):
    return hashlib.sha256(f"{backend}|{voice}|{speed}|{speakable(text)}".encode()).hexdigest()[:16]


def apply_fades(wav, sr=SR):
    wav = wav.astype(np.float32).copy()
    n_in, n_out = int(FADE_IN * sr), int(FADE_OUT * sr)
    if len(wav) > n_in + n_out:
        wav[:n_in] *= np.linspace(0, 1, n_in, dtype=np.float32)
        wav[-n_out:] *= np.linspace(1, 0, n_out, dtype=np.float32)
    return wav


def measure_lufs(path):
    """Integrated loudness via ffmpeg loudnorm pass 1 (json)."""
    p = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path), "-af",
                        f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = p.stderr
    j = json.loads(txt[txt.rindex("{"):txt.rindex("}") + 1])
    return float(j["input_i"])


def master(full, tmpdir):
    """Pure gain to -16 LUFS integrated (no tempo change, timings stay valid). Peak-safe via soft ceiling."""
    tmp = os.path.join(tmpdir, "pre.wav")
    sf.write(tmp, full, SR)
    cur = measure_lufs(tmp)
    if cur < -70:  # silence
        return full
    gain = 10 ** ((TARGET_LUFS - cur) / 20)
    out = full * gain
    peak = float(np.max(np.abs(out)))
    if peak > 0.89:  # -1 dBFS ceiling: compress the overshoot rather than lower loudness
        out = np.where(np.abs(out) > 0.89, np.sign(out) * (0.89 + 0.1 * np.tanh((np.abs(out) - 0.89) / 0.1)), out)
    return out.astype(np.float32)


# ---------- backend: returns (wav float32 @24k, words relative to line start) ----------
_kpipes = {}


def synth_kokoro(text, voice, speed, **_):
    from kokoro import KPipeline
    if voice[0] not in _kpipes:
        _kpipes[voice[0]] = KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M", device="cpu")
    pipe = _kpipes[voice[0]]
    parts, ws, off = [], [], 0.0
    for r in pipe(speakable(text), voice=voice, speed=speed):
        audio = r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)
        for t in (r.tokens or []):
            if getattr(t, "start_ts", None) is not None and getattr(t, "end_ts", None) is not None \
                    and any(ch.isalnum() for ch in t.text):
                ws.append({"w": t.text, "start": off + t.start_ts, "end": off + t.end_ts})
        parts.append(audio)
        off += len(audio) / SR
    return np.concatenate(parts).astype(np.float32), ws


BACKENDS = {"kokoro": synth_kokoro}


# ---------- main ----------
def run(scene_dir, voice=None, speed=None, backend="kokoro", force=False):
    scene_dir = os.path.abspath(scene_dir)
    film = {}
    fj = os.path.join(scene_dir, "..", "..", "film.json")
    if os.path.exists(fj):
        film = json.load(open(fj))
    voice = voice or film.get("voice") or "af_heart"
    speed = speed if speed is not None else film.get("speed", 1.0)
    lines = read_lines(os.path.join(scene_dir, "narration.txt"))
    # "[[tail 0.8]]" on its own line = this scene's closing silence (a hard ending), overriding film.json "tail".
    tail = float(film.get("tail", TAIL))
    lead = float(film.get("lead", LEAD))
    for k in range(len(lines) - 1, -1, -1):
        m = re.fullmatch(r"\s*\[\[tail\s+([0-9.]+)\]\]\s*", lines[k])
        if m:
            tail = float(m.group(1)); del lines[k]
    # "[[hold 1.5]]" at the end of a line = extra silence after it (a reveal beat). Not spoken, not hashed.
    holds = []
    for k, ln in enumerate(lines):
        m = re.search(r"\s*\[\[hold\s+([0-9.]+)\]\]\s*$", ln)
        holds.append(float(m.group(1)) if m else 0.0)
        if m:
            lines[k] = ln[:m.start()].rstrip()
    audio = os.path.join(scene_dir, "audio")
    os.makedirs(audio, exist_ok=True)
    hpath = os.path.join(audio, ".hashes.json")
    old = {}
    if os.path.exists(hpath) and not force:
        try:
            old = json.load(open(hpath))
        except Exception:
            old = {}
    new, clips, resynth = {}, [], []
    tmpdir = tempfile.mkdtemp(prefix="mvtts-")
    try:
        for n, text in enumerate(lines, 1):
            key = f"{n:02d}"
            h = line_hash(text, voice, speed, backend)
            wp = os.path.join(audio, f"line_{key}.wav")
            ent = old.get(key)
            if ent and ent.get("hash") == h and os.path.exists(wp):
                wav, _ = sf.read(wp, dtype="float32")
                words = ent["words"]
            else:
                wav, words = BACKENDS[backend](text, voice, speed, idx=n, tmpdir=tmpdir)
                wav = apply_fades(wav)
                sf.write(wp, wav, SR)
                words = [{"w": w["w"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words]
                resynth.append(n)
            new[key] = {"hash": h, "words": words}
            clips.append((wav, words))
        # drop stale line files beyond current count
        for f in os.listdir(audio):
            if f.startswith("line_") and f.endswith(".wav") and int(f[5:-4]) > len(lines):
                os.remove(os.path.join(audio, f))
        json.dump(new, open(hpath, "w"), indent=1)

        pad = lambda s: np.zeros(int(round(s * SR)), np.float32)
        out, cues, t = [pad(lead)], [], lead
        for i, (text, (wav, words)) in enumerate(zip(lines, clips)):
            d = len(wav) / SR
            cues.append({"i": i + 1, "text": text, "start": round(t, 3), "dur": round(d, 3),
                         "words": [{"w": w["w"], "start": round(t + w["start"], 3), "end": round(t + w["end"], 3)}
                                   for w in words]})
            out.append(wav)
            t += d
            if holds[i]:
                out.append(pad(holds[i]))
                t += holds[i]
            if i < len(clips) - 1:
                out.append(pad(GAP))
                t += GAP
        out.append(pad(tail))  # film.json "tail" or a scene's [[tail N]]: the end card scene sets [[tail 4.0]]
        full = master(np.concatenate(out), tmpdir)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    sf.write(os.path.join(audio, "narration.wav"), full, SR, subtype="PCM_16")
    total = round(len(full) / SR, 3)
    obj = {"voice": voice, "speed": speed, "total": total, "lines": cues}
    with open(os.path.join(audio, "cues.json"), "w") as f:
        json.dump(obj, f, indent=1)
    with open(os.path.join(audio, "cues.js"), "w") as f:
        f.write("window.CUES = " + json.dumps(obj) + ";\n")
    return {"lines": len(lines), "total": total, "voice": voice, "resynth": resynth}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene_dir")
    ap.add_argument("--voice", default=None)
    ap.add_argument("--speed", type=float, default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    r = run(a.scene_dir, a.voice, a.speed, force=a.force)
    print(f"{os.path.basename(os.path.abspath(a.scene_dir))}: {r['lines']} lines, {r['total']:.1f}s, "
          f"voice {r['voice']} (resynth {r['resynth'] or 'none'}, {time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
