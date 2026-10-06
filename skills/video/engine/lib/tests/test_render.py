"""render.py (stdlib) and the mvid CLI's film/scene verbs. The render gate runs only when a HyperFrames
binary is installed locally (<engine>/hf/node_modules or $MVID_HYPERFRAMES); it never fetches one."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import ENGINE, needs_ffmpeg
import render

MVID = ENGINE / "bin" / "mvid"


def mvid(root, *args, check=True):
    env = dict(os.environ, MVID_ROOT=str(root))
    env.pop("MVID_HOME", None)
    p = subprocess.run(["bash", str(MVID), *args], capture_output=True, text=True, env=env)
    if check:
        assert p.returncode == 0, p.stdout + p.stderr
    return p


def test_help_lists_only_kept_verbs(tmp_path):
    out = mvid(tmp_path, "--help").stdout
    for verb in ("new", "scene", "voice", "render", "critic", "assemble"):
        assert f"mvid {verb}" in out
    p = mvid(tmp_path, "publish", "x", check=False)
    assert p.returncode != 0 and "unknown command" in p.stderr


def test_new_and_scene(tmp_path):
    mvid(tmp_path, "new", "demo", "--title", 'A "quoted" title')
    film = tmp_path / "films" / "demo"
    cfg = json.loads((film / "film.json").read_text())
    assert cfg["title"] == 'A "quoted" title' and cfg["mode"] == "explainer" and cfg["voice"] == "af_heart"
    assert (film / "_kit" / "harness.js").is_file() and (film / "KIT.md").is_file()
    # refuses an existing film and an unknown mode
    assert mvid(tmp_path, "new", "demo", check=False).returncode != 0
    assert mvid(tmp_path, "new", "other", "--mode", "nope", check=False).returncode != 0
    assert not (tmp_path / "films" / "other").exists()

    mvid(tmp_path, "scene", "demo", "s01-hook", "s02-body")
    cfg = json.loads((film / "film.json").read_text())
    assert cfg["scenes"] == ["s01-hook", "s02-body"] and cfg["transitions"] == ["slideleft"]
    html = (film / "scenes" / "s01-hook" / "index.html").read_text()
    assert 'data-composition-id="s01-hook"' in html and "_kit/theme.css" in html
    assert (film / "scenes" / "s01-hook" / "_kit" / "harness.js").is_file()
    assert (film / "scenes" / "s01-hook" / "film.js").read_text().startswith("window.MV_FILM")
    # re-scaffolding leaves an edited scene alone
    (film / "scenes" / "s01-hook" / "index.html").write_text(html + "<!-- edited -->")
    mvid(tmp_path, "scene", "demo", "s01-hook")
    assert (film / "scenes" / "s01-hook" / "index.html").read_text().endswith("<!-- edited -->")
    assert json.loads((film / "film.json").read_text())["scenes"] == ["s01-hook", "s02-body"]


def test_loop_mode_is_square_and_unvoiced(tmp_path):
    mvid(tmp_path, "new", "lp", "--mode", "loop")
    cfg = json.loads((tmp_path / "films" / "lp" / "film.json").read_text())
    assert (cfg["width"], cfg["height"], cfg["fps"], cfg["voice"]) == (1080, 1080, 60, None)


def test_sync_durations_and_root_duration(tmp_path):
    mvid(tmp_path, "new", "d")
    mvid(tmp_path, "scene", "d", "s01")
    film = tmp_path / "films" / "d"
    sd = film / "scenes" / "s01"
    (sd / "audio").mkdir()
    (sd / "audio" / "cues.json").write_text(json.dumps({"total": 7.25, "lines": []}))
    render.sync_durations(film, [])
    assert render.root_duration(sd / "index.html") == 7.25


def test_kit_link_must_reach_the_kit(tmp_path):
    sd = tmp_path / "film" / "scenes" / "s01"
    sd.mkdir(parents=True)
    (tmp_path / "film" / "_kit").mkdir()      # an empty kit: no harness.js
    with pytest.raises(SystemExit):
        render.ensure_kit_link(sd)


def _local_renderer():
    if os.environ.get("MVID_HYPERFRAMES"):
        return True
    return (ENGINE / "hf" / "node_modules" / ".bin" / "hyperframes").exists()


@needs_ffmpeg
@pytest.mark.skipif(not _local_renderer(), reason="no local hyperframes (npm ci in engine/hf, or set MVID_HYPERFRAMES)")
def test_render_gate_both_directions(tmp_path):
    mvid(tmp_path, "new", "t1", "--mode", "loop")
    mvid(tmp_path, "scene", "t1", "s01")
    film = tmp_path / "films" / "t1"
    sd = film / "scenes" / "s01"
    html = (sd / "index.html").read_text()
    html = html.replace('<script src="audio/cues.js"></script>\n', "").replace('data-duration="6"', 'data-duration="3"')
    (sd / "index.html").write_text(html)
    final = film / "renders" / "s01.mp4"
    p = mvid(tmp_path, "render", "t1", "--draft", check=False)
    assert final.exists(), p.stdout + p.stderr
    _, dur = render.probe(final)
    assert abs(dur - 3.0) <= 0.1
    before = hashlib.md5(final.read_bytes()).hexdigest()
    # direction 2: a wrong expected duration fails and leaves the good render in place
    assert mvid(tmp_path, "render", "t1", "--draft", "--expect", "5", check=False).returncode != 0
    assert hashlib.md5(final.read_bytes()).hexdigest() == before
