import pygame

_THEMES = {
    "classic": {
        "canvas": (10, 12, 22),
        "crowd": (24, 26, 38),
        "curtain": (56, 22, 32),
        "mat": (108, 32, 42),
        "mat_dark": (72, 22, 30),
        "mat_edge": (130, 40, 48),
        "rope": (232, 216, 178),
        "rope_shadow": (100, 82, 64),
        "post": (218, 218, 228),
        "pad": (188, 48, 54),
    },
    "dusk": {
        "canvas": (8, 10, 28),
        "crowd": (28, 24, 48),
        "curtain": (48, 28, 62),
        "mat": (92, 36, 72),
        "mat_dark": (56, 24, 52),
        "mat_edge": (120, 52, 96),
        "rope": (210, 200, 230),
        "rope_shadow": (80, 70, 100),
        "post": (200, 198, 220),
        "pad": (140, 60, 120),
    },
    "inferno": {
        "canvas": (18, 6, 8),
        "crowd": (48, 18, 14),
        "curtain": (92, 24, 18),
        "mat": (140, 36, 28),
        "mat_dark": (88, 22, 18),
        "mat_edge": (180, 52, 36),
        "rope": (255, 200, 160),
        "rope_shadow": (120, 60, 40),
        "post": (220, 200, 190),
        "pad": (220, 80, 40),
    },
    "ice": {
        "canvas": (12, 18, 32),
        "crowd": (28, 40, 56),
        "curtain": (36, 52, 72),
        "mat": (72, 110, 140),
        "mat_dark": (48, 78, 108),
        "mat_edge": (90, 140, 170),
        "rope": (200, 230, 255),
        "rope_shadow": (60, 90, 120),
        "post": (210, 230, 245),
        "pad": (100, 170, 210),
    },
}


def draw_wrestling_ring(screen, width, height, theme="classic"):
    c = _THEMES.get(theme, _THEMES["classic"])
    canvas = c["canvas"]
    crowd = c["crowd"]
    curtain = c["curtain"]
    mat = c["mat"]
    mat_dark = c["mat_dark"]
    mat_edge = c["mat_edge"]
    rope = c["rope"]
    rope_shadow = c["rope_shadow"]
    post = c["post"]
    pad = c["pad"]

    screen.fill(canvas)

    floor_y = height
    mat_height = 220
    mat_top = floor_y - mat_height
    ring_left = 28
    ring_right = width - 28

    crowd_rect = pygame.Rect(0, 0, width, mat_top - 8)
    pygame.draw.rect(screen, crowd, crowd_rect)
    for i in range(0, width, 6):
        pygame.draw.line(screen, (min(255, crowd[0] + 12), crowd[1], crowd[2]), (i, 0), (i + 3, mat_top - 8), 1)
    pygame.draw.rect(screen, curtain, (0, mat_top - 72, width, 72))

    pygame.draw.rect(screen, mat_dark, (ring_left, mat_top, ring_right - ring_left, mat_height))
    pygame.draw.rect(
        screen,
        mat,
        (ring_left + 5, mat_top + 8, ring_right - ring_left - 10, mat_height - 14),
    )
    pygame.draw.rect(screen, mat_edge, (ring_left, mat_top, ring_right - ring_left, mat_height), 3)
    floor_edge = (
        max(0, min(255, (mat_dark[0] * 2 + crowd[0]) // 3 + 8)),
        max(0, min(255, (mat_dark[1] * 2 + crowd[1]) // 3 + 8)),
        max(0, min(255, (mat_dark[2] * 2 + crowd[2]) // 3 + 8)),
    )
    pygame.draw.line(screen, floor_edge, (ring_left, floor_y - 1), (ring_right, floor_y - 1), 2)

    center_y = mat_top + mat_height // 2
    pygame.draw.line(screen, mat_edge, (ring_left + 18, center_y), (ring_right - 18, center_y), 2)
    pygame.draw.circle(screen, mat_edge, (width // 2, center_y), 28, 2)

    rope_offsets = (42, 82, 122)
    for offset in rope_offsets:
        y = mat_top + offset
        pygame.draw.line(
            screen,
            rope_shadow,
            (ring_left + 10, y + 2),
            (ring_right - 10, y + 2),
            5,
        )
        pygame.draw.line(
            screen,
            rope,
            (ring_left + 10, y),
            (ring_right - 10, y),
            3,
        )

    for x in (ring_left, ring_right - 10):
        pygame.draw.rect(screen, post, (x, mat_top - 8, 10, mat_height + 8))
        pygame.draw.rect(screen, pad, (x - 2, mat_top - 10, 14, 18))
