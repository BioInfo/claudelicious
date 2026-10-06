#!/usr/bin/env python3
"""assemble: scene renders -> master mp4 (xfade + acrossfade), music bed with ducking, loudnorm,
poster, optional word-highlight captions, extra formats.

Usage: assemble.py <film_dir> [--out PATH] [--captions]
       [--formats landscape,square,vertical,x,linkedin] [--music PATH|pad|none] [--version N]
Cuts land in <root>/out/<slug>/<slug>-v<N>.mp4, root = $MVID_ROOT or the current directory.
Never overwrites a prior version.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FFMPEG = os.environ.get("MVID_FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("MVID_FFPROBE") or shutil.which("ffprobe") or "ffprobe"
# The caption burn needs an ffmpeg built with libass. When the default one lacks the `ass` filter,
# point MVID_FFMPEG_ASS at one that has it (used ONLY for the caption burn).
FFMPEG_ASS = os.environ.get("MVID_FFMPEG_ASS", "")
ENGINE = Path(os.environ.get("MVID_HOME") or Path(__file__).resolve().parent.parent)


def work_root():
    return Path(os.environ.get("MVID_ROOT") or Path.cwd())
TOL = 0.25
SR = 48000
DUCK = "threshold=0.03:ratio=8:attack=20:release=400"
LOUDNORM = "I=-16:TP=-1.5:LRA=11"


class AssembleError(RuntimeError):
    pass


# Bitrate ceiling on the master: grain (film.json "grain") is incompressible, and CRF alone took a
# 2-minute film to 57 Mbps / 857 MB. 12 Mbps keeps 1080p30 clean and under every platform cap.
MASTER_CAP = ["-maxrate", "12M", "-bufsize", "24M"]


def run(cmd, **kw):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise AssembleError(f"command failed ({p.returncode}): {' '.join(map(str, cmd))[:400]}\n{p.stderr[-1500:]}")
    return p


def ffmpeg(*args):
    return run([FFMPEG, "-hide_banner", "-nostdin", "-y", *args])


def probe_duration(path):
    p = run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "json", path])
    return float(json.loads(p.stdout)["format"]["duration"])


def probe_video(path):
    p = run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height,codec_name,pix_fmt,profile", "-of", "json", path])
    return json.loads(p.stdout)["streams"][0]


def has_audio(path):
    p = run([FFPROBE, "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", path])
    return bool(p.stdout.strip())


def measure_loudness(path):
    """Integrated loudness (LUFS) and true peak of the file via ebur128."""
    p = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-i", str(path), "-vn", "-af",
                        "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    m = re.search(r"I:\s+(-?[\d.]+|-inf)\s+LUFS", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+|-inf)\s+dBFS", tail)
    if not m:
        raise AssembleError("could not parse ebur128 output:\n" + p.stderr[-800:])
    return float(m.group(1)), (float(tp.group(1)) if tp else None)


def expected_duration(durs, xfade):
    return sum(durs) - xfade * (len(durs) - 1)


def assert_duration(path, durs, xfade, tol=TOL):
    got = probe_duration(path)
    want = expected_duration(durs, xfade)
    if abs(got - want) > tol:
        raise AssembleError(f"duration mismatch on {path}: got {got:.3f}s, expected {want:.3f}s "
                            f"(sum {sum(durs):.3f} - {xfade}*{len(durs)-1}); tolerance {tol}s")
    return got, want


# ---------- film.json / paths ----------

def load_film(film_dir):
    film_dir = Path(film_dir).resolve()
    film = json.loads((film_dir / "film.json").read_text())
    scenes = film["scenes"]
    trans = film.get("transitions") or []
    if len(scenes) < 1:
        raise AssembleError("film.json has no scenes")
    if len(trans) != len(scenes) - 1:
        raise AssembleError(f"transitions has {len(trans)} entries, need {len(scenes)-1}")
    renders = []
    for s in scenes:
        r = film_dir / "renders" / f"{s}.mp4"
        if not r.exists():
            raise AssembleError(f"missing render {r}")
        renders.append(r)
    return film_dir, film, renders


def resolve_out(film, out, version, root=None):
    """Return (mp4 path, N). Never overwrites: explicit --out must not exist."""
    slug = film["slug"]
    root = Path(root) if root else work_root()
    if out:
        out = Path(out).expanduser().resolve()
        if out.exists():
            raise AssembleError(f"refusing to overwrite existing {out}")
        m = re.search(r"-v(\d+)$", out.stem)
        return out, int(m.group(1)) if m else (version or 1)
    d = root / "out" / slug
    d.mkdir(parents=True, exist_ok=True)
    if version:
        n = int(version)
    else:
        nums = [int(m.group(1)) for f in d.glob(f"{slug}-v*.mp4")
                if (m := re.fullmatch(re.escape(slug) + r"-v(\d+)", f.stem))]
        # critic/<slug>-vN packets outlive deleted cuts, so a version number is never reused
        crit = root / "films" / slug / "critic"
        nums += [int(m.group(1)) for f in crit.glob(f"{slug}-v*")
                 if (m := re.fullmatch(re.escape(slug) + r"-v(\d+)", f.name))]
        n = max(nums, default=0) + 1
    path = d / f"{slug}-v{n}.mp4"
    if path.exists():
        raise AssembleError(f"refusing to overwrite existing {path}")
    return path, n


def resolve_music(spec, film_dir):
    """-> None | 'pad' | Path"""
    if spec is None or str(spec).lower() in ("none", "null", ""):
        return None
    if str(spec) == "pad":
        return "pad"
    p = Path(str(spec)).expanduser()
    for cand in ([p] if p.is_absolute() else [film_dir / p, work_root() / p, Path.cwd() / p, ENGINE / p]):
        if cand.exists():
            return cand
    raise AssembleError(f"music bed not found: {spec}")


# ---------- video + narration chains ----------

def build_chains(n, durs, trans, xfade, fps, width, height):
    """filter_complex for n scenes: video xfade chain -> [v], narration acrossfade chain -> [a]."""
    parts = []
    for i in range(n):
        parts.append(f"[{i}:v]fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,"
                     f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
        # pad/trim narration to the scene's video length so the audio chain tracks the video chain
        parts.append(f"[{i}:a]aformat=sample_rates={SR}:channel_layouts=stereo,apad,atrim=0:{durs[i]:.6f},asetpts=PTS-STARTPTS[a{i}]")
    vprev, aprev = "v0", "a0"
    cum = durs[0]
    for i in range(1, n):
        off = cum - xfade
        parts.append(f"[{vprev}][v{i}]xfade=transition={trans[i-1]}:duration={xfade}:offset={off:.6f}[vx{i}]")
        parts.append(f"[{aprev}][a{i}]acrossfade=d={xfade}:c1=tri:c2=tri[ax{i}]")
        vprev, aprev = f"vx{i}", f"ax{i}"
        cum = cum + durs[i] - xfade
    parts.append(f"[{vprev}]null[v]")
    parts.append(f"[{aprev}]anull[a]")
    return ";".join(parts)


def render_video_and_narration(renders, durs, trans, xfade, fps, width, height, tmp):
    """Encode silent video (final quality) and raw narration wav from the scene chain."""
    fc = build_chains(len(renders), durs, trans, xfade, fps, width, height)
    vid, nar = tmp / "video.mp4", tmp / "narr_raw.wav"
    args = []
    for r in renders:
        args += ["-i", r]
    ffmpeg(*args, "-filter_complex", fc,
           "-map", "[v]", "-an", "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-crf", "17", "-preset", "medium", *MASTER_CAP, "-r", str(fps), vid,
           "-map", "[a]", "-c:a", "pcm_s16le", "-ar", str(SR), nar)
    return vid, nar


# ---------- loudness ----------

def loudnorm_wav(src, dst):
    """Two-pass loudnorm to -16 LUFS / TP -1.5 / LRA 11 (linear where possible)."""
    p = subprocess.run([FFMPEG, "-hide_banner", "-nostdin", "-i", str(src), "-af",
                        f"loudnorm={LOUDNORM}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.findall(r"\{[^{}]*\}", p.stderr)
    flt = f"loudnorm={LOUDNORM}"
    if m:
        try:
            j = json.loads(m[-1])
            if float(j["input_i"]) > -70:
                flt = (f"loudnorm={LOUDNORM}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
                       f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:"
                       f"offset={j['target_offset']}:linear=true")
        except (ValueError, KeyError):
            pass
    ffmpeg("-i", src, "-af", f"{flt},aresample={SR}", "-c:a", "pcm_s16le", "-ar", SR, dst)
    return dst


# ---------- music ----------

def prepare_bed(bed, total, tmp, xfade_loop=6.0):
    """Bed wav exactly `total`+pad seconds. 'pad' synthesizes; a file loops with crossfade."""
    need = total + 0.5
    out = tmp / "bed.wav"
    if bed == "pad":
        sys.path.insert(0, str(Path(__file__).parent))
        from pad import write_pad
        write_pad(str(out), need, SR)
        return out
    bd = probe_duration(bed)
    if bd >= need:
        ffmpeg("-i", bed, "-t", f"{need:.3f}", "-ar", SR, "-ac", 2, "-c:a", "pcm_s16le", out)
    else:
        # loop from the audible body: a bed's own fade-out tail leaves a hole at the crossfade seam
        bd = bed_body_end(bed)
        xf = min(3.0, bd / 3)  # a beat-aligned seam needs a shorter crossfade than xfade_loop
        sys.path.insert(0, str(Path(__file__).parent))
        from bedloop import loop_offset
        D, score = loop_offset(bed, bd, xf)
        bd = D + xf
        print(f"bed loop: seam at {D:.2f}s, rhythm match {score:.2f}" if score >= 0.3 else
              f"bed loop: no rhythm match ({score:.2f}), plain crossfade", file=sys.stderr)
        k = int(-(-(need - bd) // (bd - xf))) + 1  # copies needed so k*bd-(k-1)*xf >= need
        args, chain, prev = [], [], "b0"
        for i in range(k):
            args += ["-i", bed]
            chain.append(f"[{i}:a]atrim=0:{bd:.3f},asetpts=PTS-STARTPTS[b{i}]")
        for i in range(1, k):
            chain.append(f"[{prev}][b{i}]acrossfade=d={xf}:c1=tri:c2=tri[l{i}]")
            prev = f"l{i}"
        ffmpeg(*args, "-filter_complex", ";".join(chain), "-map", f"[{prev}]", "-t", f"{need:.3f}",
               "-ar", SR, "-ac", 2, "-c:a", "pcm_s16le", out)
    return out


def bed_body_end(bed, floor_db=-40):
    """End of the bed's audible body: the start of its trailing stretch below `floor_db`, else its full length."""
    L = probe_duration(bed)
    r = subprocess.run([FFMPEG, "-v", "info", "-i", str(bed), "-af", f"silencedetect=noise={floor_db}dB:d=0.5",
                        "-f", "null", "-"], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    if starts and (len(ends) < len(starts) or ends[-1] >= L - 0.05):
        return max(starts[-1], 1.0)
    return L


def duck_music(bed, narr, volume, total, dst, outro=0.0):
    """Music bed at `volume`, sidechain-ducked by the normalized narration; fades in/out. Writes dst wav.
    `outro` (film.json, seconds): the closing card. The bed swells +7 dB into it and resolves on a long fade,
    so the film ends on music rather than a cut."""
    fo = 1.5   # music carries to the last frame; a longer fade leaves the ending on dead air
    fc = (f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo,volume={volume},"
          f"afade=t=in:st=0:d=0.5,afade=t=out:st={max(total-fo,0):.3f}:d={fo}[m];"
          f"[1:a]aformat=sample_rates={SR}:channel_layouts=stereo[k];"
          f"[m][k]sidechaincompress={DUCK}[d];[d]atrim=0:{total:.6f},asetpts=PTS-STARTPTS[o0]")
    if outro > 0:
        t0, fl = total - outro - 0.4, max(fo, outro * 0.6)
        fc += (f";[o0]volume='if(gt(t,{t0:.3f}),min(2.24,1+1.24*(t-{t0:.3f})/1.2),1)':eval=frame,"
               f"afade=t=out:st={total-fl:.3f}:d={fl:.3f}[o]")
    else:
        fc += ";[o0]anull[o]"
    ffmpeg("-i", bed, "-i", narr, "-filter_complex", fc, "-map", "[o]", "-c:a", "pcm_s16le", "-ar", SR, dst)
    return dst


def mix_audio(narr, music, total, dst):
    if music is None:
        ffmpeg("-i", narr, "-af", f"atrim=0:{total:.6f}", "-c:a", "pcm_s16le", dst)
    else:
        ffmpeg("-i", narr, "-i", music, "-filter_complex",
               f"[0:a][1:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{total:.6f}[o]",
               "-map", "[o]", "-c:a", "pcm_s16le", dst)
    return dst


# ---------- captions ----------

def ass_time(t):
    t = max(t, 0)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_escape(w):
    return w.replace("\\", "").replace("{", "(").replace("}", ")")


def build_ass(words, width, height, group=4):
    """words: [(text, start, end)]. Per-word events: the group shows, the active word is highlighted."""
    portrait = height > width
    fs = int(height * (0.040 if portrait else 0.062))
    marginv = int(height * (0.24 if portrait else 0.11))  # vertical keeps clear of the bottom 20%
    hdr = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {width}\nPlayResY: {height}\nWrapStyle: 0\n\n"
           "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
           "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,"
           "MarginL,MarginR,MarginV,Encoding\n"
           f"Style: Cap,Helvetica Neue,{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,"
           f"{max(3, fs // 12)},2,2,{int(width*0.06)},{int(width*0.06)},{marginv},1\n\n"
           "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n")
    ev = []  # (start, end, text)
    for g in range(0, len(words), group):
        grp = words[g:g + group]
        for i, (w, s, e) in enumerate(grp):
            end = grp[i + 1][1] if i + 1 < len(grp) else e + 0.25
            end = max(end, s + 0.08)
            txt = " ".join(
                (f"{{\\c&H0000E5FF&\\fscx110\\fscy110}}{ass_escape(x[0].upper())}{{\\c&HFFFFFF&\\fscx100\\fscy100}}"
                 if j == i else ass_escape(x[0].upper())) for j, x in enumerate(grp))
            ev.append([s, end, txt])
    for i in range(len(ev) - 1):  # never overlap the next event
        ev[i][1] = max(min(ev[i][1], ev[i + 1][0]), ev[i][0] + 0.04)
    return hdr + "\n".join(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{t}" for a, b, t in ev) + "\n"


def narration_text(film_dir, scenes):
    chunks = []
    for s in scenes:
        p = film_dir / "scenes" / s / "narration.txt"
        if p.exists():
            # [[hold N]] / [[tail N]] are layout markup, never spoken
            chunks += [t for ln in p.read_text().splitlines() if (t := re.sub(r"\[\[[^\]]*\]\]", " ", ln).strip())]
    return " ".join(chunks)


def transcribe_words(audio_wav, text):
    """stable-ts forced alignment of `text` against the RENDERED mixed audio (local, CPU)."""
    try:
        import stable_whisper
    except ImportError:
        raise AssembleError("--captions needs a local aligner: install the asr extra (uv sync --extra asr)")
    model = stable_whisper.load_model("base")
    res = model.align(str(audio_wav), text, language="en")
    words = [(w.word.strip(), float(w.start), float(w.end)) for w in res.all_words() if w.word.strip()]
    if not words:
        raise AssembleError("caption alignment produced no words")
    return words


def burn_captions(master, out, film_dir, scenes, tmp):
    text = narration_text(film_dir, scenes)
    if not text:
        raise AssembleError("--captions needs scenes/*/narration.txt")
    wav = tmp / "rendered_audio.wav"
    ffmpeg("-i", master, "-vn", "-ac", 1, "-ar", 16000, wav)
    words = transcribe_words(wav, text)
    v = probe_video(master)
    ass = tmp / "caps.ass"
    ass.write_text(build_ass(words, int(v["width"]), int(v["height"])))
    if "ass" not in run([FFMPEG, "-hide_banner", "-filters"]).stdout.split():
        if not (FFMPEG_ASS and Path(FFMPEG_ASS).exists()):
            raise AssembleError("captions need an ffmpeg with libass (the `ass` filter); "
                                "set MVID_FFMPEG_ASS to one that has it")
        binary = FFMPEG_ASS
    else:
        binary = FFMPEG
    run([binary, "-hide_banner", "-nostdin", "-y", "-i", master, "-vf", f"ass=filename={ass}", "-c:v", "libx264", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-crf", "17", *MASTER_CAP, "-c:a", "copy", "-movflags", "+faststart", out])
    return out, len(words)


# ---------- formats ----------

BLUR_FILL = ("[0:v]split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
             "boxblur=40:6[bg];[b]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
             "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[o]")
ENC = ["-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "17",
       "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-movflags", "+faststart"]


def make_format(master, fmt, dst):
    if fmt == "square":
        ffmpeg("-i", master, "-filter_complex", BLUR_FILL.format(w=1080, h=1080), "-map", "[o]", "-map", "0:a", *ENC, dst)
    elif fmt == "vertical":
        ffmpeg("-i", master, "-filter_complex", BLUR_FILL.format(w=1080, h=1920), "-map", "[o]", "-map", "0:a", *ENC, dst)
    elif fmt in ("x", "linkedin"):
        w, h, mr = (1280, 720, "8M") if fmt == "x" else (1920, 1080, "10M")
        ffmpeg("-i", master, "-vf",
               f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1",
               *ENC, "-maxrate", mr, "-bufsize", f"{int(mr[:-1])*2}M", dst)
    else:
        raise AssembleError(f"unknown format {fmt}")
    return dst


# ---------- main ----------

def assemble(film_dir, out=None, captions=None, formats=("landscape",), music=..., version=None, root=None,
             xfade_override=None, quiet=False):
    film_dir, film, renders = load_film(film_dir)
    scenes, trans = film["scenes"], film.get("transitions") or []
    xfade = float(film.get("xfade", 0.4) if xfade_override is None else xfade_override)
    fps = int(film.get("fps", 30))
    captions = film.get("captions", False) if captions is None else captions
    mspec = film.get("music") if music is ... else music
    bed = resolve_music(mspec, film_dir)
    volume = float(film.get("music_volume", 0.16))
    for r in renders:
        if not has_audio(r):
            raise AssembleError(f"{r} has no audio stream (mvid render must mux narration)")
    durs = [probe_duration(r) for r in renders]
    v0 = probe_video(renders[0])
    width, height = int(film.get("width", v0["width"])), int(film.get("height", v0["height"]))
    master, n = resolve_out(film, out, version, root)
    master.parent.mkdir(parents=True, exist_ok=True)
    stem = master.with_suffix("")
    result = {"master": master, "version": n, "extras": {}}
    with tempfile.TemporaryDirectory(prefix="assemble-") as t:
        tmp = Path(t)
        vid, nar_raw = render_video_and_narration(renders, durs, trans, xfade, fps, width, height, tmp)
        vd = probe_duration(vid)
        want = expected_duration(durs, xfade)
        if abs(vd - want) > TOL:
            raise AssembleError(f"video chain duration {vd:.3f}s != expected {want:.3f}s (xfade {xfade})")
        total = want
        nar = loudnorm_wav(nar_raw, tmp / "narr.wav")
        music_wav = None
        if bed is not None:
            b = prepare_bed(bed, total, tmp)
            music_wav = duck_music(b, nar, volume, total, Path(str(stem) + "-music.wav"),
                                   outro=float(film.get("outro", 0)))
        mix = mix_audio(nar, music_wav, total, tmp / "mix_raw.wav")
        final = loudnorm_wav(mix, tmp / "mix.wav")
        tmp_out = tmp / "master.mp4"
        ffmpeg("-i", vid, "-i", final, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-ar", SR, "-t", f"{total:.6f}", "-movflags", "+faststart", tmp_out)
        got, want = assert_duration(tmp_out, durs, xfade)  # measured on the OUTPUT file
        if master.exists():
            raise AssembleError(f"refusing to overwrite {master}")
        tmp_out.replace(master) if tmp_out.parent.stat().st_dev == master.parent.stat().st_dev else \
            master.write_bytes(tmp_out.read_bytes())
        if bed is not None:
            result["extras"]["music"] = music_wav
        poster = master.parent / "poster.png"
        if not poster.exists():
            ffmpeg("-i", master, "-frames:v", 1, poster)
        result["extras"]["poster"] = poster
        if captions:
            cp = Path(str(stem) + "-captioned.mp4")
            if cp.exists():
                raise AssembleError(f"refusing to overwrite {cp}")
            _, nw = burn_captions(master, cp, film_dir, scenes, tmp)
            assert_duration(cp, durs, xfade)
            result["extras"]["captioned"] = cp
            result["caption_words"] = nw
        for fmt in formats:
            fmt = fmt.strip()
            if not fmt or fmt == "landscape":
                continue
            fp = Path(f"{stem}-{fmt}.mp4")
            if fp.exists():
                raise AssembleError(f"refusing to overwrite {fp}")
            make_format(master, fmt, fp)
            assert_duration(fp, durs, xfade)
            result["extras"][fmt] = fp
    lufs, tp = measure_loudness(master)
    result.update(duration=got, expected=want, lufs=lufs, true_peak=tp, scene_durations=durs, xfade=xfade)
    if not quiet:
        print(f"master     {master}\nduration   {got:.2f}s (expected {want:.2f}s = {sum(durs):.2f} - {xfade}*{len(durs)-1})")
        print(f"loudness   {lufs:.1f} LUFS, true peak {tp} dBFS")
        for k, v in result["extras"].items():
            print(f"{k:<10} {v}")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("film_dir")
    ap.add_argument("--out")
    ap.add_argument("--captions", action="store_true", default=None)
    ap.add_argument("--formats", default="landscape")
    ap.add_argument("--music", default=...)
    ap.add_argument("--version", type=int)
    ap.add_argument("--xfade", type=float, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    try:
        assemble(a.film_dir, a.out, a.captions, a.formats.split(","), a.music, a.version, xfade_override=a.xfade)
    except AssembleError as e:
        print(f"ASSEMBLE FAILED: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
