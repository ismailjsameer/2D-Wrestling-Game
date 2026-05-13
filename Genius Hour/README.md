# Rumble League

Physics-driven wrestling mini-game: fling your ragdoll, pin the rival on the mat, and keep your head off the floor. Built with Python, [Pygame](https://www.pygame.org/), and [Pymunk](https://www.pymunk.org/).

## Requirements

- Python 3.10 or newer (3.12 recommended)

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux use `source .venv/bin/activate` instead of the `Scripts` line.

## Run

```bash
python main.py
```

The game starts in **fullscreen**. From menus, **Escape** backs out or quits from the home screen; **P** pauses during a match.

## Controls (in match)

- **Mouse**: hold on the mat or on the rival to aim, release to launch from the hips
- **P**: pause
- **R**: quick restart (shown on some end screens)

## Optional music

Place 16-bit WAV loops in the `music` folder (see `audio.py` for filenames):

- `music/menu_loop.wav` for menus
- `music/fight_loop.wav` for matches

If those files are missing, built-in procedural music is used instead.

## Saves

`wrestle_progress.json` (unlocks) and `game_settings.json` (options) are created next to `main.py` when you play. They are listed in `.gitignore` so personal progress is not committed. Fresh clones start with default unlocks and settings.

## Project layout

| area        | modules |
|------------|---------|
| entry loop | `main.py` |
| physics match | `game_world.py`, `player.py`, `enemy.py`, `movement.py`, `ground_check.py` |
| AI | `enemy_ai.py` |
| levels | `levels.py`, `progress.py` |
| UI | `menu.py`, `hud.py`, `viewport.py` |
| polish | `arena_background.py`, `visual_polish.py`, `audio.py` |
