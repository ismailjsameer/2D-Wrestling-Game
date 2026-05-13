import pygame


def draw_ragdoll_shadows(game_surface, floor_y, bodies):
    w, h = game_surface.get_size()
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    for b in bodies:
        x = int(b.position.x)
        y = int(b.position.y)
        if y < floor_y - 420:
            continue
        sw = max(26, min(78, int(20 + b.mass * 1.15)))
        shh = max(7, sw // 5)
        cy = floor_y - shh // 2
        pygame.draw.ellipse(
            sh,
            (0, 0, 0, 28),
            (x - sw // 2 - 4, cy - shh // 2 - 2, sw + 8, shh + 6),
        )
        pygame.draw.ellipse(
            sh,
            (0, 0, 0, 48),
            (x - sw // 2, cy - shh // 2, sw, shh),
        )
    game_surface.blit(sh, (0, 0))
