from dataclasses import dataclass


@dataclass(frozen=True)
class LevelSpec:
    key: str
    title: str
    tagline: str
    is_bonus: bool
    gravity: tuple
    player_energy: tuple
    enemy_energy: tuple
    enemy_cooldown_scale: float
    enemy_charge_add: float
    arena_theme: str
    enemy_spawn_x: float
    player_spawn_x: float = 300.0
    second_enemy_spawn_x: float | None = None


def default_level():
    return MAIN_LEVELS[0]


MAIN_LEVELS = (
    LevelSpec(
        key="m1",
        title="Rookie Ramp",
        tagline="Where fresh faces learn to take a hit.",
        is_bonus=False,
        gravity=(0, 108),
        player_energy=(100, 20, 9, 16, 28),
        enemy_energy=(100, 14, 6, 14, 22),
        enemy_cooldown_scale=1.12,
        enemy_charge_add=-0.06,
        arena_theme="classic",
        enemy_spawn_x=500,
    ),
    LevelSpec(
        key="m2",
        title="Canvas Clash",
        tagline="The mat is soft… the opponents aren't.",
        is_bonus=False,
        gravity=(0, 108),
        player_energy=(100, 19, 8, 16, 28),
        enemy_energy=(100, 16, 7, 14, 23),
        enemy_cooldown_scale=1.02,
        enemy_charge_add=-0.03,
        arena_theme="classic",
        enemy_spawn_x=495,
    ),
    LevelSpec(
        key="m3",
        title="Turnbuckle Trial",
        tagline="Corners get dangerous real fast.",
        is_bonus=False,
        gravity=(0, 112),
        player_energy=(100, 18, 8, 16, 28),
        enemy_energy=(100, 18, 8, 14, 24),
        enemy_cooldown_scale=0.94,
        enemy_charge_add=0.02,
        arena_theme="dusk",
        enemy_spawn_x=488,
    ),
    LevelSpec(
        key="m4",
        title="Steel Chain Showdown",
        tagline="No escape. No excuses",
        is_bonus=False,
        gravity=(0, 115),
        player_energy=(95, 17, 7, 16, 28),
        enemy_energy=(100, 19, 9, 14, 25),
        enemy_cooldown_scale=0.86,
        enemy_charge_add=0.05,
        arena_theme="dusk",
        enemy_spawn_x=482,
    ),
    LevelSpec(
        key="m5",
        title="Titan Tunnel",
        tagline="Only true gaints survive.",
        is_bonus=False,
        gravity=(0, 118),
        player_energy=(90, 16, 7, 16, 28),
        enemy_energy=(100, 21, 10, 14, 26),
        enemy_cooldown_scale=0.78,
        enemy_charge_add=0.08,
        arena_theme="inferno",
        enemy_spawn_x=475,
    ),
    LevelSpec(
        key="m6",
        title="Suplex Station",
        tagline="Where every throw tests your balance and your bravery",
        is_bonus=False,
        gravity=(0, 120),
        player_energy=(88, 15, 7, 15, 28),
        enemy_energy=(100, 22, 10, 14, 27),
        enemy_cooldown_scale=0.72,
        enemy_charge_add=0.1,
        arena_theme="inferno",
        enemy_spawn_x=468,
    ),
    LevelSpec(
        key="m7",
        title="Rumble Road",
        tagline="Every step forward earns a bruise",
        is_bonus=False,
        gravity=(0, 122),
        player_energy=(85, 14, 6, 15, 28),
        enemy_energy=(100, 23, 11, 14, 28),
        enemy_cooldown_scale=0.66,
        enemy_charge_add=0.12,
        arena_theme="dusk",
        enemy_spawn_x=462,
    ),
    LevelSpec(
        key="m8",
        title="Lockdown Lair",
        tagline="Submission specialists own this place",
        is_bonus=False,
        gravity=(0, 125),
        player_energy=(82, 14, 6, 15, 27),
        enemy_energy=(100, 24, 11, 14, 29),
        enemy_cooldown_scale=0.6,
        enemy_charge_add=0.14,
        arena_theme="inferno",
        enemy_spawn_x=455,
    ),
    LevelSpec(
        key="m9",
        title="Brawler’s Balcony",
        tagline="High ground, higher stakes",
        is_bonus=False,
        gravity=(0, 126),
        player_energy=(80, 13, 6, 15, 27),
        enemy_energy=(100, 25, 12, 14, 30),
        enemy_cooldown_scale=0.56,
        enemy_charge_add=0.15,
        arena_theme="classic",
        enemy_spawn_x=448,
    ),
    LevelSpec(
        key="m10",
        title="Mayhem Mountain",
        tagline="Chaos climbs with you",
        is_bonus=False,
        gravity=(0, 128),
        player_energy=(78, 13, 6, 14, 26),
        enemy_energy=(100, 26, 12, 14, 30),
        enemy_cooldown_scale=0.52,
        enemy_charge_add=0.16,
        arena_theme="dusk",
        enemy_spawn_x=442,
    ),
    LevelSpec(
        key="m11",
        title="Champion’s Gauntlet",
        tagline="One ring. Many legends. Zero mercy",
        is_bonus=False,
        gravity=(0, 130),
        player_energy=(76, 12, 5, 14, 26),
        enemy_energy=(100, 27, 13, 14, 31),
        enemy_cooldown_scale=0.48,
        enemy_charge_add=0.17,
        arena_theme="inferno",
        enemy_spawn_x=436,
    ),
    LevelSpec(
        key="m12",
        title="The Apex Arena",
        tagline="The final bell decides everything",
        is_bonus=False,
        gravity=(0, 132),
        player_energy=(74, 12, 5, 14, 25),
        enemy_energy=(100, 28, 13, 14, 32),
        enemy_cooldown_scale=0.44,
        enemy_charge_add=0.18,
        arena_theme="ice",
        enemy_spawn_x=430,
    ),
)

BONUS_LEVELS = (
    LevelSpec(
        key="b1",
        title="Moon mat",
        tagline="Low gravity",
        is_bonus=True,
        gravity=(0, 62),
        player_energy=(110, 22, 14, 15, 26),
        enemy_energy=(100, 17, 11, 14, 24),
        enemy_cooldown_scale=0.98,
        enemy_charge_add=0.0,
        arena_theme="ice",
        enemy_spawn_x=500,
    ),
    LevelSpec(
        key="b2",
        title="Steel Rush",
        tagline="Fast rival",
        is_bonus=True,
        gravity=(0, 145),
        player_energy=(100, 18, 8, 16, 28),
        enemy_energy=(100, 20, 9, 14, 25),
        enemy_cooldown_scale=0.72,
        enemy_charge_add=0.06,
        arena_theme="inferno",
        enemy_spawn_x=468,
    ),
    LevelSpec(
        key="b3",
        title="Drift pit",
        tagline="Low gravity, slow regen",
        is_bonus=True,
        gravity=(0, 54),
        player_energy=(105, 20, 10, 15, 26),
        enemy_energy=(100, 18, 10, 14, 24),
        enemy_cooldown_scale=0.88,
        enemy_charge_add=0.02,
        arena_theme="ice",
        enemy_spawn_x=492,
    ),
    LevelSpec(
        key="b4",
        title="Thunder well",
        tagline="High gravity, greedy stamina",
        is_bonus=True,
        gravity=(0, 158),
        player_energy=(95, 17, 7, 16, 28),
        enemy_energy=(100, 21, 10, 14, 26),
        enemy_cooldown_scale=0.68,
        enemy_charge_add=0.08,
        arena_theme="dusk",
        enemy_spawn_x=460,
    ),
    LevelSpec(
        key="b5",
        title="Glass cannon ring",
        tagline="big launches, tiny stamina pools",
        is_bonus=True,
        gravity=(0, 102),
        player_energy=(88, 16, 6, 14, 22),
        enemy_energy=(100, 22, 9, 13, 24),
        enemy_cooldown_scale=0.62,
        enemy_charge_add=0.1,
        arena_theme="classic",
        enemy_spawn_x=478,
    ),
    LevelSpec(
        key="b6",
        title="Double drop",
        tagline="two rivals take them out one at a time mat ko or pin",
        is_bonus=True,
        gravity=(0, 118),
        player_energy=(100, 18, 8, 16, 28),
        enemy_energy=(100, 18, 9, 14, 25),
        enemy_cooldown_scale=0.72,
        enemy_charge_add=0.04,
        arena_theme="inferno",
        enemy_spawn_x=400,
        player_spawn_x=200,
        second_enemy_spawn_x=600,
    ),
)


def main_by_index(index):
    return MAIN_LEVELS[max(0, min(index, len(MAIN_LEVELS) - 1))]


def bonus_by_index(index):
    return BONUS_LEVELS[max(0, min(index, len(BONUS_LEVELS) - 1))]
