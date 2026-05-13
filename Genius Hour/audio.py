import io
import math
import os
import random
import struct

import pygame

import menu

_BASE = os.path.dirname(os.path.abspath(__file__))
_MENU_FILE = os.path.join(_BASE, "music", "menu_loop.wav")
_FIGHT_FILE = os.path.join(_BASE, "music", "fight_loop.wav")

_kind = None
_menu_buf = None
_fight_buf = None

_SR = 22050


def _soft_clip(x, drive=1.25):
    return math.tanh(x * drive) / math.tanh(drive)


def _pack_wav16_stereo(sr, samples_l, samples_r):
    chunks = [struct.pack("<hh", a, b) for a, b in zip(samples_l, samples_r)]
    pairs = b"".join(chunks)
    riff_size = 36 + len(pairs)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        riff_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        2,
        sr,
        sr * 4,
        4,
        16,
        b"data",
        len(pairs),
    )
    return header + pairs


def _lp_step(z, x, coef=0.86):
    return z * coef + x * (1.0 - coef)


def _menu_track():
    """warm d minor pad, slow motion, stereo width."""
    sr = _SR
    dur = 8.2
    n = int(sr * dur)
    d3, f3, a3, d4 = 146.83, 174.61, 220.0, 293.66
    sub = d3 * 0.5
    dt_r = 1.0 / sr
    zl = zr = 0.0
    out_l = []
    out_r = []
    rng = random.Random(42)
    for i in range(n):
        t = i * dt_r
        tr = t + 0.00019
        breathe = 0.45 + 0.55 * math.sin(2 * math.pi * 0.09 * t)
        sway = 0.08 * math.sin(2 * math.pi * 0.037 * t + 0.3)
        s = (
            math.sin(2 * math.pi * d3 * t) * (0.30 + sway)
            + math.sin(2 * math.pi * f3 * t + 0.85) * 0.26
            + math.sin(2 * math.pi * a3 * t + 1.55) * 0.22
            + math.sin(2 * math.pi * d4 * t + 0.4) * 0.07
            + math.sin(2 * math.pi * sub * t + 0.2) * 0.36
        )
        s *= breathe
        s += (
            math.sin(2 * math.pi * a3 * 3 * t) * 0.028
            * (0.5 + 0.5 * math.sin(2 * math.pi * 3.1 * t))
        )
        s_r = (
            math.sin(2 * math.pi * d3 * tr * 1.0012) * (0.30 + sway)
            + math.sin(2 * math.pi * f3 * tr * 1.0008 + 0.85) * 0.26
            + math.sin(2 * math.pi * a3 * tr * 1.0015 + 1.55) * 0.22
            + math.sin(2 * math.pi * d4 * tr + 0.4) * 0.07
            + math.sin(2 * math.pi * sub * tr + 0.2) * 0.36
        )
        s_r *= breathe
        s_r += (
            math.sin(2 * math.pi * a3 * 3 * tr) * 0.028
            * (0.5 + 0.5 * math.sin(2 * math.pi * 3.1 * tr))
        )
        grain = (rng.random() - 0.5) * 0.012 * breathe
        s = _soft_clip((s + grain) * 0.88, 1.12)
        s_r = _soft_clip((s_r + grain) * 0.88, 1.12)
        zl = _lp_step(zl, s, 0.82)
        zr = _lp_step(zr, s_r, 0.82)
        amp = 9200
        out_l.append(int(max(-32767, min(32767, zl * amp))))
        out_r.append(int(max(-32767, min(32767, zr * amp))))
    return _pack_wav16_stereo(sr, out_l, out_r)


def _fight_track():
    """driving pulse, kick on beat, bass + gritty mid layer."""
    sr = _SR
    dur = 6.8
    n = int(sr * dur)
    bpm = 116.0
    beat = 60.0 / bpm
    dt = 1.0 / sr
    zl = zr = 0.0
    out_l = []
    out_r = []
    for i in range(n):
        t = i * dt
        tr = t + 0.00014
        ph = (t % beat) / beat
        env_k = math.exp(-ph * 9.0)
        kick = math.sin(2 * math.pi * 58.0 * t) * env_k * 0.62
        t_off = t + beat * 0.5
        ph_s = (t_off % beat) / beat
        env_s = math.exp(-ph_s * 22.0)
        sn = math.sin(2 * math.pi * 205.0 * t_off) * env_s * 0.16
        pulse = 0.38 + 0.62 * (0.5 + 0.5 * math.sin(2 * math.pi * 1.85 * t)) ** 2
        root = 73.42
        bass = (
            math.sin(2 * math.pi * root * t) * 0.22
            + math.sin(2 * math.pi * root * 0.5 * t) * 0.28
        ) * pulse
        mid = (
            math.sin(2 * math.pi * root * 2.02 * t + 0.4) * 0.12
            + math.sin(2 * math.pi * root * 3.01 * t + 1.1) * 0.08
        ) * pulse
        grit = _soft_clip(
            math.sin(2 * math.pi * root * 5.5 * t) * 0.11
            + math.sin(2 * math.pi * root * 7.1 * t + 0.7) * 0.07,
            1.4,
        ) * pulse * 0.55
        s = kick + sn + bass + mid + grit
        s_r = (
            math.sin(2 * math.pi * 58.0 * tr) * env_k * 0.62
            + math.sin(2 * math.pi * 210.0 * tr) * env_s * 0.14
            + (
                math.sin(2 * math.pi * root * tr) * 0.22
                + math.sin(2 * math.pi * root * 0.5 * tr) * 0.28
            )
            * pulse
            + (
                math.sin(2 * math.pi * root * 2.02 * tr + 0.4) * 0.12
                + math.sin(2 * math.pi * root * 3.01 * tr + 1.1) * 0.08
            )
            * pulse
            + grit * 0.92
        )
        s = _soft_clip(s * 0.9, 1.18)
        s_r = _soft_clip(s_r * 0.9, 1.18)
        zl = _lp_step(zl, s, 0.78)
        zr = _lp_step(zr, s_r, 0.78)
        amp = 9800
        out_l.append(int(max(-32767, min(32767, zl * amp))))
        out_r.append(int(max(-32767, min(32767, zr * amp))))
    return _pack_wav16_stereo(sr, out_l, out_r)


def _menu_fallback():
    global _menu_buf
    if _menu_buf is None:
        _menu_buf = _menu_track()
    return _menu_buf


def _fight_fallback():
    global _fight_buf
    if _fight_buf is None:
        _fight_buf = _fight_track()
    return _fight_buf


def init():
    if pygame.mixer.get_init() is None:
        pygame.mixer.init(frequency=_SR, size=-16, channels=2, buffer=4096)


def stop():
    global _kind
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass
    _kind = None


def tick(phase, settings_dict):
    global _kind
    vol = max(0.0, min(1.0, float(settings_dict.get("music_volume", 0.52))))
    pygame.mixer.music.set_volume(vol)
    if not settings_dict.get("music_enabled", True):
        if _kind is not None:
            stop()
        return
    if phase == menu.PLAYING:
        want = "fight"
    else:
        want = "menu"
    if _kind == want:
        if pygame.mixer.music.get_busy():
            return
    path = _FIGHT_FILE if want == "fight" else _MENU_FILE
    try:
        if os.path.isfile(path):
            pygame.mixer.music.load(path)
        else:
            buf = _fight_fallback() if want == "fight" else _menu_fallback()
            pygame.mixer.music.load(io.BytesIO(buf))
        pygame.mixer.music.play(-1)
        _kind = want
    except pygame.error:
        _kind = None
