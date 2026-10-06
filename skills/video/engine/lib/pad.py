#!/usr/bin/env python3
"""Synthesize a warm ambient chord pad sized to a given duration.

Numpy sines with slow LFO amplitude/detune drift, gentle fade in/out (no clicks).
Usage: pad.py <seconds> <out.wav> [--sr 48000]
"""
import argparse
import numpy as np
import soundfile as sf

# Fmaj9-ish warm voicing, then Am7 / Dm9 drift: (freq Hz) lists per chord
CHORDS = [
    [87.31, 130.81, 174.61, 220.00, 329.63],   # F2 C3 F3 A3 E4
    [110.00, 164.81, 220.00, 261.63, 392.00],  # A2 E3 A3 C4 G4
    [73.42, 146.83, 220.00, 293.66, 349.23],   # D2 D3 A3 D4 F4
    [98.00, 146.83, 196.00, 246.94, 329.63],   # G2 D3 G3 B3 E4
]


def make_pad(seconds, sr=48000, seed=7, chord_len=12.0, fade=3.0):
    rng = np.random.default_rng(seed)
    n = int(round(seconds * sr))
    t = np.arange(n) / sr
    out = np.zeros((2, n))
    nchords = max(1, int(np.ceil(seconds / chord_len)) + 1)
    for ci in range(nchords):
        chord = CHORDS[ci % len(CHORDS)]
        c0 = ci * chord_len
        # chord envelope: raised-cosine crossfade of one chord_len overlap
        env = np.zeros(n)
        a, b = c0 - chord_len / 2, c0 + chord_len * 1.5
        m = (t >= a) & (t < b)
        env[m] = 0.5 - 0.5 * np.cos(2 * np.pi * (t[m] - a) / (b - a))
        if not m.any():
            continue
        for f in chord:
            for ch in range(2):
                for det in (-0.12 * (1 + ch), 0.12 * (1 + ch)):  # slow beating detune (Hz)
                    ph = rng.uniform(0, 2 * np.pi)
                    lfo_rate = rng.uniform(0.05, 0.16)
                    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * lfo_rate * t + rng.uniform(0, 6.28))
                    sig = np.sin(2 * np.pi * (f + det) * t + ph)
                    sig += 0.25 * np.sin(2 * np.pi * 2 * (f + det) * t + ph * 1.3)  # warm 2nd partial
                    out[ch] += env * lfo * sig / (1 + f / 400)
    peak = np.abs(out).max() or 1.0
    out = out / peak * 0.5
    fade = min(fade, seconds / 2)
    fn = int(fade * sr)
    if fn > 0:
        ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fn))
        out[:, :fn] *= ramp
        out[:, -fn:] *= ramp[::-1]
    return out.T.astype(np.float32)


def write_pad(path, seconds, sr=48000):
    data = make_pad(seconds, sr)
    sf.write(path, data, sr, subtype="PCM_16")
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("seconds", type=float)
    ap.add_argument("out")
    ap.add_argument("--sr", type=int, default=48000)
    a = ap.parse_args()
    write_pad(a.out, a.seconds, a.sr)
    print(a.out)
