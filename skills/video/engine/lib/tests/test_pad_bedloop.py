import numpy as np
import pytest

from conftest import needs_ffmpeg
import pad
import bedloop


def test_pad_length_and_fades():
    x = pad.make_pad(10.0, sr=8000)
    assert x.shape == (80000, 2)
    assert np.abs(x).max() <= 0.5 + 1e-6
    assert np.abs(x[:10]).max() < 1e-3 and np.abs(x[-10:]).max() < 1e-3   # no click at either end
    assert np.abs(x[40000:40100]).max() > 0.01                             # audible in the middle


def test_pad_is_deterministic():
    assert np.array_equal(pad.make_pad(3.0, sr=8000), pad.make_pad(3.0, sr=8000))


@needs_ffmpeg
def test_bedloop_selftest():
    # both directions: a rhythmic bed finds a bar-aligned seam, a rhythm-free one falls back
    assert bedloop.selftest()
