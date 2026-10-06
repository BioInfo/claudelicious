"""assemble.py: xfade chain, music bed ducking, loudness, formats, versioning, captions.
Fixture scenes are ffmpeg test patterns with tone-burst 'narration', so most checks need only ffmpeg."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from conftest import needs_ffmpeg, speak
import assemble as A
from pad import make_pad

SR = 48000


def test_expected_duration_and_chain():
    assert A.expected_duration([5.0, 4.0, 3.0], 0.5) == pytest.approx(11.0)
    fc = A.build_chains(3, [5.0, 4.0, 3.0], ["fade", "wipeleft"], 0.5, 30, 1280, 720)
    assert "xfade=transition=fade:duration=0.5:offset=4.500000" in fc
    assert "xfade=transition=wipeleft:duration=0.5:offset=8.000000" in fc
    assert fc.count("acrossfade") == 2 and fc.endswith("[a]")


def test_ass_highlights_one_word_per_event():
    words = [("one", 0.0, 0.3), ("two", 0.3, 0.6), ("three", 0.6, 0.9), ("four", 0.9, 1.2), ("five", 1.2, 1.5)]
    ass = A.build_ass(words, 1920, 1080)
    ev = [l for l in ass.splitlines() if l.startswith("Dialogue:")]
    assert len(ev) == 5 and all(e.count("\\c&H0000E5FF&") == 1 for e in ev)
    starts = [e.split(",")[1] for e in ev]
    assert starts == sorted(starts)


def test_resolve_out_versions_and_refuses_overwrite(tmp_path):
    film = {"slug": "f"}
    p1, n1 = A.resolve_out(film, None, None, tmp_path)
    assert (p1.name, n1) == ("f-v1.mp4", 1) and p1.parent == tmp_path / "out" / "f"
    p1.write_bytes(b"x")
    p2, n2 = A.resolve_out(film, None, None, tmp_path)
    assert n2 == 2
    with pytest.raises(A.AssembleError):
        A.resolve_out(film, str(p1), None, tmp_path)


def sh(*cmd):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-800:]


def bursts(seconds, sr=SR):
    """Voice-like stand-in: 0.6s on (amplitude-modulated tone), 0.5s off, repeated, 0.4s lead."""
    t = np.arange(int(seconds * sr)) / sr
    on = ((t - 0.4) % 1.1 < 0.6) & (t > 0.4)
    sig = 0.3 * np.sin(2 * np.pi * 220 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * t))
    return (sig * on).astype(np.float32)


def build_fixture(root: Path, speech=None):
    (root / "renders").mkdir(parents=True, exist_ok=True)
    scenes, lines = [], ["Welcome to the film, this is the first scene of our test.",
                         "Now the second scene begins, it has more words to speak aloud.",
                         "Finally the third scene ends the story, thanks for watching."]
    for i, line in enumerate(lines, 1):
        sid = f"s0{i}"
        scenes.append(sid)
        d = root / "scenes" / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / "narration.txt").write_text(line + "\n")
        wav = root / f"{sid}.wav"
        if speech:
            speech(line, wav)
        else:
            sf.write(wav, bursts(4.0 + i * 0.5), SR)
        dur = A.probe_duration(wav) + 1.0
        sh(A.FFMPEG, "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc2=s=1280x720:r=30:d={dur:.2f}", "-i", wav,
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", SR, "-af", "apad", "-t", f"{dur:.2f}",
           root / "renders" / f"{sid}.mp4")
    film = {"slug": "assemble-test", "mode": "explainer", "width": 1280, "height": 720, "fps": 30,
            "scenes": scenes, "transitions": ["fade", "wipeleft"], "xfade": 0.6,
            "music": "pad", "music_volume": 0.16, "captions": False}
    (root / "film.json").write_text(json.dumps(film, indent=1))
    return film


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0


@needs_ffmpeg
def test_assemble_end_to_end(tmp_path):
    film_dir = tmp_path / "films" / "assemble-test"
    film = build_fixture(film_dir)
    r = A.assemble(film_dir, formats=["square", "vertical"], root=tmp_path, quiet=True)
    master, ex = r["master"], r["extras"]
    durs, xf = r["scene_durations"], r["xfade"]
    want = sum(durs) - xf * (len(durs) - 1)
    assert master == tmp_path / "out" / "assemble-test" / "assemble-test-v1.mp4"
    assert abs(A.probe_duration(master) - want) <= 0.25

    v = A.probe_video(master)
    assert v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p" and v["profile"] == "High", v
    a = A.run([A.FFPROBE, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate",
               "-of", "csv=p=0", master]).stdout.strip()
    assert a == "aac,48000"
    assert abs(r["lufs"] + 16) <= 1.0, r["lufs"]
    assert r["true_peak"] is None or r["true_peak"] <= -1.0, r["true_peak"]

    # music is ducked under the narration and recovers in the pauses
    mus, msr = sf.read(str(ex["music"]))
    assert msr == SR and abs(len(mus) / msr - want) < 0.1
    raw = make_pad(want + 0.5, SR)[: len(mus)] * film["music_volume"]
    nar, nsr = sf.read(str(film_dir / "s02.wav"))
    base = durs[0] - xf
    att_v, att_s = [], []
    for k in range(7, int((durs[1] - xf - 0.7) * 10)):
        w = nar[int(k * 0.1 * nsr): int((k + 1) * 0.1 * nsr)]
        sl = slice(int((base + k * 0.1) * msr), int((base + (k + 1) * 0.1) * msr))
        db = 20 * np.log10(rms(mus[sl]) / rms(raw[sl]))
        (att_v if rms(w) > 0.03 else att_s if rms(w) < 0.002 else []).append(db)
    assert len(att_v) >= 10 and len(att_s) >= 3, (len(att_v), len(att_s))
    att_db, open_db = float(np.median(att_v)), float(np.median(att_s))
    assert att_db < -8, f"music not ducked under speech: {att_db:.1f} dB"
    assert open_db > att_db + 6, f"bed never recovers in pauses: {open_db:.1f} dB"
    assert abs(mus[0]).max() < 0.01 and abs(mus[-1]).max() < 0.01

    assert (A.probe_video(ex["square"])["width"], A.probe_video(ex["square"])["height"]) == (1080, 1080)
    assert (A.probe_video(ex["vertical"])["width"], A.probe_video(ex["vertical"])["height"]) == (1080, 1920)
    assert ex["poster"].stat().st_size > 1000

    # never overwrite: a second run is v2 and v1 survives
    r2 = A.assemble(film_dir, root=tmp_path, music="none", quiet=True)
    assert r2["version"] == r["version"] + 1 and r2["master"].exists() and master.exists()
    # the duration gate fires on a wrong xfade
    with pytest.raises(A.AssembleError):
        A.assert_duration(master, durs, 0.0)


def _asr():
    try:
        import stable_whisper  # noqa: F401
        return True
    except Exception:
        return False


def _libass():
    if A.FFMPEG_ASS:
        return True
    p = subprocess.run([A.FFMPEG, "-hide_banner", "-filters"], capture_output=True, text=True)
    return "ass" in p.stdout.split()


@needs_ffmpeg
@pytest.mark.skipif(not _asr(), reason="captions need the asr extra (stable-ts)")
@pytest.mark.skipif(not _libass(), reason="captions need an ffmpeg with libass (or MVID_FFMPEG_ASS)")
def test_captions_burn_in_lower_third(tmp_path, kokoro):
    film_dir = tmp_path / "films" / "assemble-test"
    build_fixture(film_dir, speech=lambda text, out: speak(kokoro, text, out, SR))
    r = A.assemble(film_dir, captions=True, music="none", root=tmp_path, quiet=True)
    cap, master = r["extras"]["captioned"], r["master"]
    assert r["caption_words"] >= 15

    def gray(p):
        b = subprocess.run([A.FFMPEG, "-v", "error", "-ss", "1.5", "-i", str(p), "-frames:v", "1", "-vf", "format=gray",
                            "-f", "rawvideo", "-"], capture_output=True).stdout
        return np.frombuffer(b, dtype=np.uint8).reshape(720, 1280).astype(int)

    diff = np.abs(gray(cap) - gray(master))
    assert diff[: int(720 * 0.6)].max() < 40 and (diff[int(720 * 0.6):] > 60).sum() > 500


def test_caption_text_drops_markup(tmp_path):
    sd = tmp_path / "scenes" / "s01"
    sd.mkdir(parents=True)
    (sd / "narration.txt").write_text("First line. [[hold 0.8]]\n[[tail 3.0]]\nSecond line.\n")
    assert A.narration_text(tmp_path, ["s01"]) == "First line. Second line."
