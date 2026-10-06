"""Shared fixtures. Tests that need a heavy tool (ffmpeg, Kokoro voices, a local transcriber, the
HyperFrames renderer) skip with the reason when it is missing; nothing reaches a remote host except
Kokoro's one-time model download on first use."""
import os
import shutil
import sys
from pathlib import Path

import pytest

LIB = Path(__file__).resolve().parent.parent
ENGINE = LIB.parent
sys.path.insert(0, str(LIB))

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
needs_ffmpeg = pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg/ffprobe not on PATH")


def kokoro_ok():
    """True when Kokoro can synthesize (package installed and model reachable)."""
    if os.environ.get("MVID_SKIP_KOKORO"):
        return False
    try:
        import tts
        wav, _ = tts.synth_kokoro("Test.", "af_heart", 1.0)
        return len(wav) > 0
    except Exception:
        return False


_kok = None


@pytest.fixture
def kokoro():
    global _kok
    if _kok is None:
        _kok = kokoro_ok()
    if not _kok:
        pytest.skip("Kokoro unavailable (package or model download)")
    import tts
    return tts


def speak(tts, text, out_wav, sr=44100):
    """Real speech for fixtures via Kokoro, resampled to sr."""
    import subprocess
    import soundfile as sf
    wav, _ = tts.synth_kokoro(text, "af_heart", 1.0)
    raw = str(out_wav) + ".24k.wav"
    sf.write(raw, wav, tts.SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-ac", "1", "-ar", str(sr), str(out_wav)], check=True)
    os.remove(raw)
