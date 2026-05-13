import json
import os

_FILENAME = "game_settings.json"
_DEFAULT = {
    "dev_mode": False,
    "dev_invulnerable": False,
    "music_enabled": True,
    "music_volume": 0.52,
}


def _path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), _FILENAME)


def load():
    out = dict(_DEFAULT)
    try:
        with open(_path(), encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, ValueError, json.JSONDecodeError, TypeError):
        return out
    for k in _DEFAULT:
        if k not in raw:
            continue
        if k == "music_volume":
            out[k] = max(0.0, min(1.0, float(raw[k])))
        else:
            out[k] = bool(raw[k])
    return out


def save(data):
    try:
        merged = dict(_DEFAULT)
        merged.update(data)
        merged["music_volume"] = max(
            0.0, min(1.0, float(merged.get("music_volume", 0.52)))
        )
        merged["dev_mode"] = bool(merged.get("dev_mode"))
        merged["dev_invulnerable"] = bool(merged.get("dev_invulnerable"))
        merged["music_enabled"] = bool(merged.get("music_enabled", True))
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)
    except OSError:
        pass


def toggle(key):
    if key not in ("dev_mode", "dev_invulnerable", "music_enabled"):
        return load()
    s = load()
    s[key] = not bool(s.get(key, False))
    save(s)
    return s


def bump_music_volume(delta):
    s = load()
    s["music_volume"] = max(
        0.0, min(1.0, float(s.get("music_volume", 0.52)) + delta)
    )
    save(s)
    return s
