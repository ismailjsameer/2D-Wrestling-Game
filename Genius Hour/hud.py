import math

import pygame


def draw_energy_bar(screen, x, y, width, height, ratio, fill_color, label, font):
    ratio = max(0.0, min(1.0, ratio))
    bg = (16, 18, 26)
    edge = (56, 62, 82)
    fill_inner = (
        min(255, fill_color[0] + 28),
        min(255, fill_color[1] + 28),
        min(255, fill_color[2] + 20),
    )
    pygame.draw.rect(screen, bg, (x, y, width, height), border_radius=6)
    pygame.draw.rect(screen, edge, (x, y, width, height), 2, border_radius=6)
    pygame.draw.line(screen, (44, 48, 64), (x + 3, y + 3), (x + width - 4, y + 3), 1)
    if ratio > 0:
        inner_w = max(0, int((width - 8) * ratio))
        pygame.draw.rect(
            screen,
            fill_color,
            (x + 4, y + 4, inner_w, height - 8),
            border_radius=4,
        )
        if inner_w > 10:
            pygame.draw.rect(
                screen,
                fill_inner,
                (x + 4, y + 4, inner_w // 3, height - 8),
                border_radius=4,
            )
        hi = (
            min(255, fill_color[0] + 55),
            min(255, fill_color[1] + 55),
            min(255, fill_color[2] + 45),
        )
        pygame.draw.line(
            screen,
            hi,
            (x + 5, y + 5),
            (x + 4 + max(1, inner_w - 2), y + 5),
            1,
        )
    if label:
        label_surf = font.render(label, True, (236, 238, 246))
        shadow = font.render(label, True, (0, 0, 0))
        lx = x
        ly = y + height + 4
        screen.blit(shadow, (lx + 1, ly + 1))
        screen.blit(label_surf, (lx, ly))


def draw_level_banner(screen, width, title, subtitle, font_title, font_sub):
    pad_x = 14
    tw = max(font_title.size(title)[0], font_sub.size(subtitle)[0]) + pad_x * 2
    bw = min(width - 24, tw + 20)
    bh = 62
    box = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for yy in range(bh):
        t = yy / max(1, bh - 1)
        r = int(14 + (5 - 14) * t)
        g = int(16 + (7 - 16) * t)
        b = int(30 + (16 - 30) * t)
        a = int(228 + (188 - 228) * t)
        pygame.draw.line(box, (r, g, b, a), (0, yy), (bw, yy))
    pygame.draw.rect(box, (96, 108, 142, 210), (0, 0, bw, bh), 1)
    bx = (width - bw) // 2
    screen.blit(box, (bx, 52))
    cx = bx + bw // 2
    ty = 56
    st = font_sub.render(subtitle, True, (188, 194, 208))
    tt = font_title.render(title, True, (248, 250, 255))
    st_sh = font_sub.render(subtitle, True, (22, 24, 32))
    tt_sh = font_title.render(title, True, (16, 18, 26))
    tx = cx - tt.get_width() // 2
    sx = cx - st.get_width() // 2
    sy = ty + tt.get_height() - 2
    screen.blit(tt_sh, (tx + 1, ty + 1))
    screen.blit(st_sh, (sx + 1, sy + 1))
    screen.blit(tt, (tx, ty))
    screen.blit(st, (sx, sy))


def draw_dev_corner(screen, width, font, settings_dict):
    y = 6
    if settings_dict.get("dev_mode"):
        s = font.render("DEV MODE", True, (255, 220, 100))
        screen.blit(font.render("DEV MODE", True, (40, 30, 8)), (width - s.get_width() - 9, y + 1))
        screen.blit(s, (width - s.get_width() - 10, y))
        y += 20
    if settings_dict.get("dev_invulnerable"):
        s = font.render("SAFE HEAD", True, (180, 255, 180))
        screen.blit(font.render("SAFE HEAD", True, (12, 40, 12)), (width - s.get_width() - 9, y + 1))
        screen.blit(s, (width - s.get_width() - 10, y))


def _draw_mat_pin_bar(screen, width, y, bar_w, ratio, font, label, fill_rgb):
    ratio = max(0.0, min(1.0, ratio))
    h = 14
    x = width // 2 - bar_w // 2
    pygame.draw.rect(screen, (16, 18, 26), (x, y, bar_w, h), border_radius=6)
    pygame.draw.rect(screen, (58, 64, 84), (x, y, bar_w, h), 2, border_radius=6)
    pygame.draw.line(screen, (42, 46, 62), (x + 3, y + 3), (x + bar_w - 4, y + 3), 1)
    if ratio > 0:
        iw = max(0, int((bar_w - 8) * ratio))
        pygame.draw.rect(
            screen,
            fill_rgb,
            (x + 4, y + 4, iw, h - 8),
            border_radius=4,
        )
        br, bg, bb = fill_rgb
        edge = (min(255, br + 40), min(255, bg + 40), min(255, bb + 35))
        pygame.draw.line(screen, edge, (x + 5, y + 5), (x + 4 + max(1, iw - 2), y + 5), 1)
    lab = font.render(label, True, (218, 222, 234))
    sh = font.render(label, True, (8, 10, 16))
    lx = width // 2 - lab.get_width() // 2
    ly = y - lab.get_height() - 4
    screen.blit(sh, (lx + 1, ly + 1))
    screen.blit(lab, (lx, ly))


def draw_pin_hold(screen, width, y, bar_w, ratio, font):
    _draw_mat_pin_bar(
        screen,
        width,
        y,
        bar_w,
        ratio,
        font,
        "mat pin (rival on mat, you on top)",
        (92, 200, 120),
    )


def draw_rival_mat_pin_hold(screen, width, y, bar_w, ratio, font):
    _draw_mat_pin_bar(
        screen,
        width,
        y,
        bar_w,
        ratio,
        font,
        "rival mat pin (you on mat, them on top)",
        (220, 96, 78),
    )


def draw_aim_charge(screen, hip_pos, aim_pos, charge, max_charge, color):
    if charge <= 0.0:
        return

    hip_x, hip_y = hip_pos
    aim_x, aim_y = aim_pos
    dx = aim_x - hip_x
    dy = aim_y - hip_y
    distance = math.hypot(dx, dy)
    if distance < 8.0:
        return

    length = 28.0 + 92.0 * min(1.0, charge / max_charge)
    end_x = hip_x + dx / distance * length
    end_y = hip_y + dy / distance * length
    hx, hy = int(hip_x), int(hip_y)
    ex, ey = int(end_x), int(end_y)
    mid = (
        min(255, (color[0] + 255) // 2),
        min(255, (color[1] + 255) // 2),
        min(255, (color[2] + 255) // 2),
    )
    pygame.draw.line(screen, (0, 0, 0), (hx + 2, hy + 2), (ex + 2, ey + 2), 7)
    pygame.draw.line(screen, (28, 32, 48), (hx + 1, hy + 1), (ex + 1, ey + 1), 5)
    pygame.draw.line(screen, color, (hx, hy), (ex, ey), 3)
    pygame.draw.line(screen, mid, (hx, hy), (ex, ey), 1)
