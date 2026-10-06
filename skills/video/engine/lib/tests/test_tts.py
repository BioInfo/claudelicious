"""tts.py: Kokoro narration, lead/gap/tail layout, [[hold]]/[[tail]] markup, per-line caching.
Layout constants are written out here on purpose (contract values), not imported from tts.py."""
import json
import os
import re
import subprocess
import sys

import pytest

from conftest import LIB, needs_ffmpeg
import tts

LEAD, GAP, TAIL = 0.35, 0.7, 0.5
LINES = ["Every film starts with a single idea.",
         "Then the words get spoken aloud.",
         "Timing comes from the voice itself.",
         "Change one line and only that line moves."]


def test_speakable_versions():
    assert tts.speakable("Model-2.5 ships") == "Model 2 point 5 ships"
    assert tts.speakable("up 2.5% today") == "up 2.5% today"


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)], text=True))


def lufs(p):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])


def run_tts(scene):
    r = subprocess.run([sys.executable, str(LIB / "tts.py"), str(scene)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
    return r.stdout.strip()


def cues(scene):
    return json.loads((scene / "audio" / "cues.json").read_text())


@needs_ffmpeg
def test_layout_cache_and_edit(tmp_path, kokoro):
    scene = tmp_path / "scenes" / "s01"
    scene.mkdir(parents=True)
    (tmp_path / "film.json").write_text(json.dumps({"slug": "t", "voice": "af_heart", "speed": 1.0}))
    (scene / "narration.txt").write_text("\n\n".join(LINES) + "\n")
    a = scene / "audio"

    out = run_tts(scene)
    assert "4 lines" in out and "af_heart" in out
    c = cues(scene)
    assert abs(c["total"] - dur(a / "narration.wav")) < 0.05
    assert abs(c["lines"][0]["start"] - LEAD) < 1e-6
    for p, q in zip(c["lines"], c["lines"][1:]):
        assert abs(q["start"] - (p["start"] + p["dur"] + GAP)) < 0.002
    last = c["lines"][-1]
    assert abs(c["total"] - (last["start"] + last["dur"] + TAIL)) < 0.01
    for ln, text in zip(c["lines"], LINES):
        assert len(ln["words"]) == len(text.split()), (ln["words"], text)
        assert ln["words"][0]["start"] >= ln["start"] - 1e-6
    js = (a / "cues.js").read_text()
    assert js.startswith("window.CUES = ") and json.loads(js[len("window.CUES = "):].rstrip().rstrip(";")) == c
    info = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=sample_rate,channels",
                                    "-of", "csv=p=0", str(a / "narration.wav")], text=True).strip()
    assert info == "24000,1"
    assert abs(lufs(a / "narration.wav") + 16) < 1.0

    # unchanged re-run touches no line file
    mt = {n: os.path.getmtime(a / n) for n in os.listdir(a) if n.startswith("line_")}
    assert "resynth none" in run_tts(scene)
    assert mt == {n: os.path.getmtime(a / n) for n in mt}

    # edit one line: only it regenerates, later starts shift
    before = cues(scene)
    new = list(LINES)
    new[1] = "Then the words get spoken aloud, slowly and clearly, one at a time."
    (scene / "narration.txt").write_text("\n".join(new) + "\n")
    assert "resynth [2]" in run_tts(scene)
    after = cues(scene)
    assert os.path.getmtime(a / "line_01.wav") == mt["line_01.wav"]
    assert os.path.getmtime(a / "line_02.wav") != mt["line_02.wav"]
    assert after["lines"][0]["start"] == before["lines"][0]["start"]
    assert after["lines"][2]["start"] > before["lines"][2]["start"] + 0.5


@needs_ffmpeg
def test_hold_and_tail_markup(tmp_path, kokoro):
    scene = tmp_path / "scenes" / "s01"
    scene.mkdir(parents=True)
    (tmp_path / "film.json").write_text(json.dumps({"slug": "t"}))
    (scene / "narration.txt").write_text("First line here. [[hold 1.5]]\nSecond line here.\n[[tail 2.0]]\n")
    run_tts(scene)
    c = cues(scene)
    l1, l2 = c["lines"]
    assert l1["text"] == "First line here." and "[[" not in l2["text"]
    assert abs(l2["start"] - (l1["start"] + l1["dur"] + 1.5 + GAP)) < 0.002
    assert abs(c["total"] - (l2["start"] + l2["dur"] + 2.0)) < 0.01
