import json
import os

import levels

_FILENAME = "wrestle_progress.json"


def _path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), _FILENAME)


def _nm():
    return len(levels.MAIN_LEVELS)


def _nb():
    return len(levels.BONUS_LEVELS)


def load_state():
    try:
        with open(_path(), encoding="utf-8") as f:
            data = json.load(f)
        main_u = int(data.get("main_unlocked", 1))
        bonus_u = int(data.get("bonus_unlocked", 0))
        return {
            "main_unlocked": max(1, min(_nm(), main_u)),
            "bonus_unlocked": max(0, min(_nb(), bonus_u)),
        }
    except (OSError, ValueError, json.JSONDecodeError, TypeError):
        return {"main_unlocked": 1, "bonus_unlocked": 0}


def save_state(state):
    try:
        with open(_path(), "w", encoding="utf-8") as f:
            json.dump(state, f, indent=0)
    except OSError:
        pass


def register_main_win(level_index):
    s = load_state()
    s["main_unlocked"] = min(_nm(), max(s["main_unlocked"], level_index + 2))
    m = s["main_unlocked"]
    b = s["bonus_unlocked"]
    if m >= 3:
        b = max(b, 1)
    if m >= 5:
        b = max(b, min(2, _nb()))
    if m >= 7:
        b = max(b, min(3, _nb()))
    if m >= 9:
        b = max(b, min(4, _nb()))
    if m >= 11:
        b = max(b, min(5, _nb()))
    if m >= _nm():
        b = max(b, _nb())
    s["bonus_unlocked"] = b
    save_state(s)


def clear_progress():
    save_state({"main_unlocked": 1, "bonus_unlocked": 0})


def menu_unlock_display(settings_dict, saved_dict):
    if settings_dict.get("dev_mode"):
        return {"main_unlocked": _nm(), "bonus_unlocked": _nb()}
    return dict(saved_dict)
