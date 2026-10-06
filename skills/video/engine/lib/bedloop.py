#!/usr/bin/env python3
"""Beat-aligned loop point for a music bed: tempo-free, pure numpy.

loop_offset() picks where a second copy of the bed should start on the first copy's timeline so the
rhythm at the seam matches the bed's own opening (the seam lands on the same point of the bar).
Usage: bedloop.py --selftest
"""
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

FFMPEG = os.environ.get("MVID_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
SR = 22050
N_FFT, HOP = 2048, 512


def _decode(path):
    r = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True)
    if r.returncode or not r.stdout:
        raise RuntimeError(f"decode failed: {path}: {r.stderr.decode()[-200:]}")
    return np.frombuffer(r.stdout, dtype=np.float32)


def onset_envelope(y):
    """Positive spectral flux of the log-magnitude STFT, one value per hop, normalized to max 1."""
    y = np.pad(y, (N_FFT // 2, N_FFT // 2))
    n = 1 + (len(y) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    mag = np.abs(np.fft.rfft(y[idx] * np.hanning(N_FFT), axis=1))
    flux = np.maximum(np.diff(np.log1p(mag), axis=0, prepend=np.log1p(mag[:1])), 0).sum(axis=1)
    return flux / (flux.max() or 1.0)


def loop_offset(path, body_end, xf, search=16.0):
    """(D, score): D = start of copy 2 on copy 1's timeline (so the trimmed body is D + xf long)."""
    env = onset_envelope(_decode(path))
    fps = SR / HOP
    lo = max(xf, body_end - xf - search)
    hi = body_end - xf
    W = int(max(xf, 4.0) * fps)
    W = min(W, len(env))
    ref = env[:W]
    best_d, best = hi, -2.0
    for f in range(int(round(lo * fps)), int(round(hi * fps)) + 1):
        seg = env[f:f + W]
        if len(seg) < W:
            break
        if seg.std() < 1e-9 or ref.std() < 1e-9:
            continue
        c = float(np.corrcoef(seg, ref)[0, 1])
        if c > best:
            best_d, best = f / fps, c
    if best < 0.3:
        return hi, best
    return best_d, best


def _write_wav(path, y):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())


def _synth_rhythm(dur=30.0, bpm=100, fade=3.0):
    rng = np.random.default_rng(1)
    t = np.arange(int(dur * SR)) / SR
    y = 0.05 * np.sin(2 * np.pi * 220 * t)
    beat = 60.0 / bpm
    k = np.arange(int(0.08 * SR)) / SR
    click = np.exp(-k * 60) * rng.standard_normal(len(k))
    for i in range(int(dur / beat)):
        s = int(i * beat * SR)
        amp = 0.8 if i % 4 == 0 else 0.3
        y[s:s + len(click)] += amp * click[:len(y) - s]
    y *= np.clip((dur - t) / fade, 0, 1)
    return y


def selftest():
    ok = True
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "rhythm.wav"
        _write_wav(p, _synth_rhythm())
        D, s = loop_offset(p, 26.5, 3.0)
        bar = 2.4
        err = abs(D - round(D / bar) * bar)
        good = err <= 0.03 and s >= 0.3
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} rhythm: D={D:.3f}s score={s:.2f} off-grid by {err:.3f}s (bar {bar}s)")
        p = Path(d) / "pad.wav"
        rng = np.random.default_rng(2)
        t = np.arange(30 * SR) / SR
        _write_wav(p, 0.1 * rng.standard_normal(len(t)) + 0.1 * np.sin(2 * np.pi * 110 * t))
        D, s = loop_offset(p, 26.5, 3.0)
        good = s < 0.3 and abs(D - 23.5) < 1e-6
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} no-rhythm fallback: D={D:.3f}s score={s:.2f}")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    print(__doc__)
