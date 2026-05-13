import pygame

VIEW_WIDTH = 800
VIEW_HEIGHT = 600


def screen_to_game(pos, screen_size):
    screen_w, screen_h = screen_size
    scale = min(screen_w / VIEW_WIDTH, screen_h / VIEW_HEIGHT)
    dest_w = VIEW_WIDTH * scale
    dest_h = VIEW_HEIGHT * scale
    offset_x = (screen_w - dest_w) / 2
    offset_y = (screen_h - dest_h) / 2
    game_x = (pos[0] - offset_x) / scale
    game_y = (pos[1] - offset_y) / scale
    return game_x, game_y


def present_game_surface(screen, game_surface):
    screen_w, screen_h = screen.get_size()
    scale = min(screen_w / VIEW_WIDTH, screen_h / VIEW_HEIGHT)
    dest_w = max(1, int(VIEW_WIDTH * scale))
    dest_h = max(1, int(VIEW_HEIGHT * scale))
    offset_x = (screen_w - dest_w) // 2
    offset_y = (screen_h - dest_h) // 2
    screen.fill((10, 12, 18))
    scaled = pygame.transform.smoothscale(game_surface, (dest_w, dest_h))
    screen.blit(scaled, (offset_x, offset_y))
    frame = (52, 58, 74)
    pygame.draw.rect(screen, frame, (offset_x - 1, offset_y - 1, dest_w + 2, dest_h + 2), 1)
    vw, vh = screen.get_size()
    edge = max(28, min(100, vw // 14))
    vignette = pygame.Surface((vw, vh), pygame.SRCALPHA)
    for alpha, thick in ((38, edge), (22, edge // 2)):
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (0, 0, vw, thick))
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (0, vh - thick, vw, thick))
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (0, 0, thick, vh))
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (vw - thick, 0, thick, vh))
    screen.blit(vignette, (0, 0))
