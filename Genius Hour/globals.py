ENEMY_BODY_RGB = (220, 72, 82)

PLAYER_SKIN = {
    "torso": (58, 168, 232),
    "head": (108, 200, 255),
    "upper_arm": (38, 128, 198),
    "lower_arm": (32, 112, 176),
    "upper_leg": (34, 118, 182),
    "lower_leg": (28, 98, 158),
}

PLAYER_BODY_RGB = PLAYER_SKIN["torso"]

ENEMY_SKIN = {
    "torso": (210, 58, 68),
    "head": (255, 168, 152),
    "upper_arm": (185, 44, 56),
    "lower_arm": (165, 36, 48),
    "upper_leg": (155, 32, 44),
    "lower_leg": (135, 28, 40),
}

ENEMY_BODY_RGB = ENEMY_SKIN["torso"]


def shape_color_rgba(color):
    if len(color) == 3:
        return (*color, 255)

    r, g, b, a = color
    if a == 0:
        a = 255
    return (r, g, b, a)
