"""critic.py: builds a synthetic 2-scene film, plants a 2s freeze and a 1.5s silence, and checks the packet
FAILS on both, then PASSES on the clean film. Narration is tone bursts, so these run with ffmpeg alone;
the transcript/WER test needs Kokoro speech and a local transcriber and skips without them."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from conftest import needs_ffmpeg, speak
import critic

SCENES = {
    "s01-hook": ["Every film starts with a measurement, not an opinion.", "The critic reads numbers and looks at pictures."],
    "s02-check": ["Frozen frames and silent gaps are caught by the machine.", "A human still has to watch and listen at the end."],
}
XFADE = 0.5
LEAD, GAP, TAIL = 0.8, 0.7, 1.0
SR = 44100


def sh(cmd):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    assert p.returncode == 0, f"{cmd[0]} failed: {p.stderr[-500:]}"


def tone_line(text, out):
    """A voiced stand-in about as long as the line would be spoken (about 15 characters a second)."""
    n = int(max(1.5, len(text) / 15) * SR)
    t = np.arange(n) / SR
    sf.write(out, (0.3 * np.sin(2 * np.pi * 200 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 4 * t))).astype(np.float32), SR)


def build_scene(film, sid, lines, line_wav):
    sd = film / "scenes" / sid
    (sd / "audio").mkdir(parents=True, exist_ok=True)
    (film / "renders").mkdir(exist_ok=True)
    (sd / "narration.txt").write_text("\n\n".join(lines) + "\n")
    parts, cue_lines, t = [np.zeros(int(LEAD * SR))], [], LEAD
    for i, text in enumerate(lines, 1):
        w = sd / "audio" / f"line_{i:02d}.wav"
        line_wav(text, w)
        x, fsr = sf.read(w)
        assert fsr == SR
        cue_lines.append({"i": i, "text": text, "start": round(t, 3), "dur": round(len(x) / SR, 3), "words": []})
        parts += [x, np.zeros(int(GAP * SR))]
        t += len(x) / SR + GAP
    parts[-1] = np.zeros(int(TAIL * SR))
    audio = np.concatenate(parts)
    total = round(len(audio) / SR, 3)
    sf.write(sd / "audio" / "narration.wav", audio, SR)
    (sd / "audio" / "cues.json").write_text(json.dumps({"voice": "t", "speed": 1.0, "total": total, "lines": cue_lines}))
    sh([critic.FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=size=640x360:rate=30:duration={total}",
        "-i", sd / "audio" / "narration.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
        film / "renders" / f"{sid}.mp4"])
    return total, cue_lines


def build_film(root, version, line_wav=tone_line, frozen=False, silent=False):
    film = root / "films" / "fx"
    film.mkdir(parents=True, exist_ok=True)
    totals, cues = {}, {}
    for sid, lines in SCENES.items():
        totals[sid], cues[sid] = build_scene(film, sid, lines, line_wav)
    ids = list(SCENES)
    (film / "film.json").write_text(json.dumps({"slug": "fx", "mode": "demo", "width": 640, "height": 360, "fps": 30,
                                                "scenes": ids, "transitions": ["fade"], "xfade": XFADE}))
    (film / "KIT.md").write_text("# KIT\n- synthetic fixture, no numbers\n")
    a, b = (film / "renders" / f"{i}.mp4" for i in ids)
    vf = f"[0:v][1:v]xfade=transition=fade:duration={XFADE}:offset={totals[ids[0]] - XFADE}[v]"
    if frozen:   # freeze frames 60..119 (2.0s) of the joined video onto frame 60
        vf += ";[v]split[a][b];[a][b]freezeframes=first=60:last=119:replace=61[v]"
    af = f"[0:a][1:a]acrossfade=d={XFADE}[a]"
    if silent:   # zero 1.5s in the middle of s02 line 1
        t0 = totals[ids[0]] - XFADE + cues[ids[1]][0]["start"] + 0.5
        af += f";[a]volume=enable='between(t,{t0:.3f},{t0 + 1.5:.3f})':volume=0[a]"
    out_dir = root / "out" / "fx"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / f"tmp-{version}.mp4"
    sh([critic.FFMPEG, "-v", "error", "-y", "-i", a, "-i", b, "-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", tmp])
    final = out_dir / f"fx-v{version}.mp4"
    gain = -16.0 - critic.measure_loudness(tmp)["lufs"]
    for _ in range(6):   # master to -16 LUFS / TP <= -1.5 by iterating the gain under a hard limiter
        sh([critic.FFMPEG, "-v", "error", "-y", "-i", tmp, "-c:v", "copy", "-af",
            f"volume={gain:.2f}dB,alimiter=limit=0.66:level=disabled:attack=2:release=50", "-c:a", "aac", "-b:a", "256k", final])
        m = critic.measure_loudness(final)
        if abs(m["lufs"] + 16.0) <= 0.4 and m["tp"] <= -1.5:
            break
        gain += -16.0 - m["lufs"]
    tmp.unlink()
    return film, final


def status(checks, name):
    return next(s for n, s, d in checks if n == name)


def test_wer_alignment():
    ref = critic.norm_words("There are 31 cats, and 50% sleep.")
    hyp = critic.norm_words("There are thirty-one cats and fifty percent sleep sleep")
    ops = critic.align(ref, hyp)
    assert [o for o, _, _ in ops].count("ins") == 1 and all(o != "del" for o, _, _ in ops)
    assert [o for o, _, _ in critic.align(["a", "b", "c"], ["a", "c"])].count("del") == 1


def test_measure_wer_attributes_errors_to_scenes():
    m = {"mode": "demo", "xfade": 0.0, "film": {}, "scenes": [
        {"id": "a", "dur": 2.0, "offset": 0.0, "lines": [], "narration": "one two three"},
        {"id": "b", "dur": 2.0, "offset": 2.0, "lines": [], "narration": "four five six"}]}
    words = [{"w": w, "start": t, "end": t + 0.2} for w, t in
             (("one", 0.1), ("two", 0.5), ("three", 0.9), ("four", 2.1), ("six", 2.9))]
    w = critic.measure_wer(words, m, 4.0)
    per = {p["scene"]: p for p in w["scenes"]}
    assert per["a"]["wer"] == 0 and per["b"]["del"] == 1 and per["b"]["missing"] == ["five"]


@needs_ffmpeg
def test_defective_fails_then_fixed_passes(tmp_path):
    film, bad = build_film(tmp_path, 1, frozen=True, silent=True)
    _, ok, checks = critic.build(film, video=bad, skip_transcript=True, skip_readcheck=True)
    assert not ok
    assert status(checks, "frozen time per 30s") == "FAIL", "planted 2s freeze not caught"
    assert status(checks, "silent windows") == "FAIL", "planted 1.5s silence not caught"
    bad_dir = film / "critic" / "fx-v1"
    assert "Measured checks: FAIL" in (bad_dir / "packet.md").read_text()
    fr = json.loads((bad_dir / "packet.json").read_text())["frozen"]
    assert any(1.8 <= f["start"] <= 2.2 and f["dur"] >= 1.8 for f in fr["freezes"]), fr

    _, good = build_film(tmp_path, 2)
    (tmp_path / "out" / "fx" / "fx-v3-vertical.mp4").write_bytes(good.read_bytes())   # a variant is never picked
    assert critic.pick_video(film, "fx").name == "fx-v2.mp4"
    outdir, ok, checks = critic.build(film, skip_transcript=True, skip_readcheck=True)
    assert outdir.name == "fx-v2"
    assert ok, [c for c in checks if c[1] == "FAIL"]
    for n in ("frozen time per 30s", "loudness LUFS", "true peak", "silent windows", "duration", "black frames"):
        assert status(checks, n) == "PASS", n
    assert status(checks, "transcript WER") == "N/A"

    d = outdir
    assert (d / "frame0.png").stat().st_size > 1000
    sheets = sorted(d.glob("sheet_*.jpg"))
    assert sheets and len(list((d / "transitions").glob("*.jpg"))) == 1 and len(list((d / "cues").glob("*.jpg"))) == 4
    p = (d / "packet.md").read_text()
    for needle in ("template look", "P0/P1/P2", "SHIP", "ONE MORE PASS", "KIT.md", "Images to look at", "Human must still"):
        assert needle.lower() in p.lower(), needle
    assert all(str(s) in p for s in sheets)

    outdir, ok, checks = critic.build(film, scene="s01-hook", skip_transcript=True, skip_readcheck=True)
    assert outdir.name == "s01-hook" and status(checks, "duration") == "PASS"
    assert len(list((outdir / "cues").glob("*.jpg"))) == 2 and not list((outdir / "transitions").glob("*.jpg"))


def test_missing_transcriber_is_reported_not_passed(tmp_path, monkeypatch):
    monkeypatch.setattr(critic, "asr_backend", lambda: None)
    m = {"mode": "demo", "scenes": [], "xfade": 0}
    info = {"has_audio": True, "duration": 1.0}
    chk = critic.evaluate(m, info, None, None, {"lufs": -16.0, "tp": -2.0, "lra": 1},
                          {"per_scene": [], "defects": [], "runs": []}, None, "not checked: no local transcriber")
    assert ("transcript WER", "N/A", "not checked: no local transcriber") in chk


@needs_ffmpeg
@pytest.mark.skipif(critic.asr_backend() is None, reason="no local transcriber (asr extra or faster-whisper)")
def test_transcript_wer_passes_on_real_speech(tmp_path, kokoro):
    film, good = build_film(tmp_path, 1, line_wav=lambda text, out: speak(kokoro, text, out, SR))
    _, ok, checks = critic.build(film, video=good, skip_readcheck=True)
    assert status(checks, "transcript WER") == "PASS", [c for c in checks if c[0] == "transcript WER"]
    assert (film / "critic" / "fx-v1" / "transcript.txt").read_text().strip()


def test_narration_markup_is_not_reference_text(tmp_path):
    sd = tmp_path / "scenes" / "s01"
    sd.mkdir(parents=True)
    (tmp_path / "film.json").write_text(json.dumps({"slug": "m", "scenes": ["s01"]}))
    (sd / "narration.txt").write_text("First line. [[hold 0.8]]\n[[tail 3.0]]\nSecond line.\n")
    m = critic.load_film(tmp_path)
    assert m["scenes"][0]["narration"] == "First line. Second line."
