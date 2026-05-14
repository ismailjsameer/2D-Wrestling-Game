import pygame

import levels
import viewport

HOME = "home"
LEVEL_SELECT = "level_select"
BONUS_SELECT = "bonus_select"
HOW_TO = "how_to"
OPTIONS = "options"
PLAYING = "playing"
PAUSED = "paused"
ENDED = "ended"

MENU = HOME

PAUSE_KEYS = (pygame.K_ESCAPE, pygame.K_p)
EXIT_KEYS = (pygame.K_ESCAPE,)
RESTART_KEYS = (pygame.K_r,)


def _blend(a, b, t):
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def _draw_gradient(screen, width, height):
    top = (8, 10, 26)
    bot = (28, 14, 38)
    for y in range(height):
        t = y / max(1, height - 1)
        c = _blend(top, bot, t)
        pygame.draw.line(screen, c, (0, y), (width, y))


class MenuUI:
    def __init__(self, font_title, font_sub, font_btn, font_small):
        self.font_title = font_title
        self.font_sub = font_sub
        self.font_btn = font_btn
        self.font_small = font_small
        self._hovered = None
        self._last_rects = {}
        self._options_confirm_clear = False
        self._career_scroll = 0.0
        self._career_scroll_drag = False
        self._career_drag_grab_y = 0.0

    def reset_career_scroll(self):
        self._career_scroll = 0.0
        self._career_scroll_drag = False

    def reset_options_confirm(self):
        self._options_confirm_clear = False

    def set_options_clear_confirm(self, value):
        self._options_confirm_clear = bool(value)

    def _btn(self, screen, rect, text, hovered, locked=False):
        if locked:
            fill = (38, 40, 48)
            border = (90, 94, 108)
            fg = (130, 134, 148)
        else:
            fill = (58, 68, 96) if hovered else (42, 48, 68)
            border = (130, 160, 220) if hovered else (88, 98, 128)
            fg = (245, 248, 255)
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)
        surf = self.font_btn.render(text, True, fg)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))

    def handle_click(self, action_map, mouse_pos=None):
        if mouse_pos is not None:
            for label, rect in self._last_rects.items():
                if rect.collidepoint(mouse_pos):
                    if action_map is None:
                        return label
                    return action_map.get(label)
        if self._hovered is None:
            return None
        if action_map is None:
            return self._hovered
        return action_map.get(self._hovered)

    def handle_key(self, phase, event):
        if event.type != pygame.KEYDOWN:
            return None
        if phase == HOME and event.key in EXIT_KEYS:
            return "exit"
        if phase == LEVEL_SELECT and event.key == pygame.K_ESCAPE:
            return "goto_home"
        if phase == LEVEL_SELECT:
            if event.key == pygame.K_DOWN:
                self.career_scroll_key(
                    1,
                    viewport.VIEW_WIDTH,
                    viewport.VIEW_HEIGHT,
                    len(levels.MAIN_LEVELS),
                    page=False,
                )
                return None
            if event.key == pygame.K_PAGEDOWN:
                self.career_scroll_key(
                    1,
                    viewport.VIEW_WIDTH,
                    viewport.VIEW_HEIGHT,
                    len(levels.MAIN_LEVELS),
                    page=True,
                )
                return None
            if event.key == pygame.K_UP:
                self.career_scroll_key(
                    -1,
                    viewport.VIEW_WIDTH,
                    viewport.VIEW_HEIGHT,
                    len(levels.MAIN_LEVELS),
                    page=False,
                )
                return None
            if event.key == pygame.K_PAGEUP:
                self.career_scroll_key(
                    -1,
                    viewport.VIEW_WIDTH,
                    viewport.VIEW_HEIGHT,
                    len(levels.MAIN_LEVELS),
                    page=True,
                )
                return None
        if phase == BONUS_SELECT and event.key == pygame.K_ESCAPE:
            return "goto_home"
        if phase == HOW_TO and event.key == pygame.K_ESCAPE:
            return "goto_home"
        if phase == OPTIONS and event.key == pygame.K_ESCAPE:
            return "goto_home"
        if phase == PLAYING and event.key in PAUSE_KEYS:
            return "pause"
        if phase == PAUSED:
            if event.key == pygame.K_ESCAPE:
                return "goto_home"
            if event.key == pygame.K_p:
                return "resume"
        if phase in (PAUSED, ENDED) and event.key in RESTART_KEYS:
            return "restart_last"
        return None

    def draw_home(self, screen, width, height, mouse_pos, saved_progress, settings_dict):
        _draw_gradient(screen, width, height)
        self._hovered = None
        self._last_rects = {}

        title = self.font_title.render("Rumble League", True, (252, 252, 255))
        screen.blit(title, (width // 2 - title.get_width() // 2, 72))
        sub = self.font_sub.render("pin their head. protect yours.", True, (190, 198, 218))
        screen.blit(sub, (width // 2 - sub.get_width() // 2, 128))

        bx = width // 2 - 200
        y0 = 188
        gap = 46
        rows = [
            ("career", "Career (story levels)"),
            ("bonus_menu", "Bonus rings"),
            ("howto", "How to play"),
            ("options", "Options"),
            ("exit", "Quit"),
        ]
        for i, (key, label) in enumerate(rows):
            r = pygame.Rect(bx, y0 + i * gap, 400, 44)
            self._last_rects[key] = r
            hov = r.collidepoint(mouse_pos or (0, 0))
            if hov:
                self._hovered = key
            self._btn(screen, r, label, hov)

        tip = self.font_small.render(
            f"saved: main {saved_progress['main_unlocked']}/{len(levels.MAIN_LEVELS)}  bonus {saved_progress['bonus_unlocked']}/{len(levels.BONUS_LEVELS)}",
            True,
            (160, 168, 188),
        )
        screen.blit(tip, (width // 2 - tip.get_width() // 2, height - 70))
        dev_bits = []
        if settings_dict.get("dev_mode"):
            dev_bits.append("dev mode on  all unlocks in menus  wins do not write saves")
        if settings_dict.get("dev_invulnerable"):
            dev_bits.append("dev safe head on  mat does not knock you out")
        yd = height - 48
        for bit in dev_bits:
            d = self.font_small.render(bit, True, (255, 210, 120))
            screen.blit(d, (width // 2 - d.get_width() // 2, yd))
            yd += 20

    def _career_layout(self, width, height, n_levels):
        row_h = 54
        list_top = 96
        list_bottom = height - 88
        viewport_h = max(1, list_bottom - list_top)
        total_h = n_levels * row_h
        max_scroll = max(0.0, float(total_h - viewport_h))
        self._career_scroll = max(0.0, min(max_scroll, self._career_scroll))
        scroll = self._career_scroll
        bx = width // 2 - 268
        list_w = 508
        sb_x = bx + list_w + 12
        sb_w = 12
        track = pygame.Rect(sb_x, list_top, sb_w, viewport_h)
        need_scroll = max_scroll > 1e-6
        if need_scroll:
            thumb_h = max(24, int((viewport_h / total_h) * viewport_h))
        else:
            thumb_h = viewport_h
        ratio = scroll / max_scroll if max_scroll > 1e-6 else 0.0
        thumb_y = int(list_top + ratio * max(1, viewport_h - thumb_h))
        thumb = pygame.Rect(sb_x, thumb_y, sb_w, thumb_h)
        clip = pygame.Rect(bx - 2, list_top, list_w + 4, viewport_h)
        return {
            "row_h": row_h,
            "list_top": list_top,
            "list_bottom": list_bottom,
            "viewport_h": viewport_h,
            "total_h": total_h,
            "max_scroll": max_scroll,
            "scroll": scroll,
            "bx": bx,
            "list_w": list_w,
            "need_scroll": need_scroll,
            "track": track,
            "thumb": thumb,
            "clip": clip,
        }

    def career_scroll_wheel(self, dy, width, height, n_levels):
        L = self._career_layout(width, height, n_levels)
        if not L["need_scroll"]:
            return
        self._career_scroll -= float(dy) * 52.0
        self._career_scroll = max(0.0, min(L["max_scroll"], self._career_scroll))

    def career_scroll_key(self, direction, width, height, n_levels, page=False):
        L = self._career_layout(width, height, n_levels)
        if not L["need_scroll"]:
            return
        step = L["viewport_h"] * 0.55 if page else L["row_h"] * 0.95
        self._career_scroll += direction * step
        self._career_scroll = max(0.0, min(L["max_scroll"], self._career_scroll))

    def career_select_pointer_down(self, pos, width, height, n_levels):
        L = self._career_layout(width, height, n_levels)
        if not L["need_scroll"]:
            return False
        if L["thumb"].collidepoint(pos):
            self._career_scroll_drag = True
            self._career_drag_grab_y = pos[1] - L["thumb"].y
            return True
        if L["track"].collidepoint(pos):
            my = pos[1]
            mid = L["thumb"].y + L["thumb"].h // 2
            if my < mid:
                self._career_scroll -= L["viewport_h"] * 0.4
            else:
                self._career_scroll += L["viewport_h"] * 0.4
            self._career_scroll = max(0.0, min(L["max_scroll"], self._career_scroll))
            return True
        return False

    def career_select_pointer_move(self, pos, width, height, n_levels, left_down):
        if not self._career_scroll_drag or not left_down:
            return
        L = self._career_layout(width, height, n_levels)
        if not L["need_scroll"]:
            return
        thumb_h = L["thumb"].h
        vh = L["viewport_h"]
        span = max(1, vh - thumb_h)
        ty = pos[1] - self._career_drag_grab_y
        ty = max(L["list_top"], min(L["list_top"] + span, ty))
        self._career_scroll = ((ty - L["list_top"]) / span) * L["max_scroll"]

    def career_select_pointer_up(self):
        self._career_scroll_drag = False

    def draw_level_select(self, screen, width, height, mouse_pos, main_levels, progress):
        _draw_gradient(screen, width, height)
        self._hovered = None
        self._last_rects = {}

        n = len(main_levels)
        L = self._career_layout(width, height, n)

        t = self.font_title.render("Career", True, (248, 250, 255))
        screen.blit(t, (width // 2 - t.get_width() // 2, 48))

        unlocked = progress["main_unlocked"]
        prev_clip = screen.get_clip()
        screen.set_clip(L["clip"])
        try:
            for i, spec in enumerate(main_levels):
                locked = i >= unlocked
                label = f"{i + 1}.  {spec.title}"
                ry = L["list_top"] - L["scroll"] + i * L["row_h"]
                r = pygame.Rect(L["bx"], ry, L["list_w"], 44)
                if r.bottom < L["list_top"] or r.y > L["list_bottom"]:
                    continue
                key = f"main_{i}"
                if not locked:
                    self._last_rects[key] = r
                hov = not locked and r.collidepoint(mouse_pos or (0, 0))
                if hov:
                    self._hovered = key
                self._btn(screen, r, label, hov, locked=locked)
                if not locked:
                    tag = self.font_small.render(spec.tagline, True, (150, 158, 176))
                    tag_y = ry + 46
                    if L["list_top"] - 2 <= tag_y <= L["list_bottom"] - 10:
                        screen.blit(tag, (width // 2 - tag.get_width() // 2, tag_y))
        finally:
            screen.set_clip(prev_clip)

        if L["need_scroll"]:
            pygame.draw.rect(screen, (28, 30, 44), L["track"], border_radius=5)
            pygame.draw.rect(screen, (58, 64, 84), L["track"], 2, border_radius=5)
            pygame.draw.rect(screen, (88, 104, 148), L["thumb"], border_radius=5)
            pygame.draw.rect(screen, (130, 152, 208), L["thumb"], 2, border_radius=5)

        tip = self.font_small.render(
            "mouse wheel, keys up or down, or the bar on the right to scroll",
            True,
            (138, 146, 168),
        )
        screen.blit(tip, (width // 2 - tip.get_width() // 2, min(L["list_bottom"] + 4, height - 108)))

        back_r = pygame.Rect(width // 2 - 80, height - 72, 160, 40)
        self._last_rects["back"] = back_r
        bh = back_r.collidepoint(mouse_pos or (0, 0))
        if bh:
            self._hovered = "back"
        self._btn(screen, back_r, "Back", bh)

    def draw_bonus_select(self, screen, width, height, mouse_pos, bonus_levels, progress):
        _draw_gradient(screen, width, height)
        self._hovered = None
        self._last_rects = {}

        t = self.font_title.render("Bonus rings", True, (248, 250, 255))
        screen.blit(t, (width // 2 - t.get_width() // 2, 48))

        unlocked_bonus = progress["bonus_unlocked"]
        bx = width // 2 - 260
        y = 130
        for i, spec in enumerate(bonus_levels):
            locked = i >= unlocked_bonus
            label = f"{i + 1}.  {spec.title}"
            r = pygame.Rect(bx, y + i * 56, 520, 48)
            key = f"bonus_{i}"
            if not locked:
                self._last_rects[key] = r
            hov = not locked and r.collidepoint(mouse_pos or (0, 0))
            if hov:
                self._hovered = key
            self._btn(screen, r, label, hov, locked=locked)
            if not locked:
                tag = self.font_small.render(spec.tagline, True, (170, 178, 198))
                screen.blit(tag, (width // 2 - tag.get_width() // 2, y + i * 56 + 50))

        hint = self.font_small.render(
            "more bonus rings unlock as you climb the career ladder",
            True,
            (150, 158, 178),
        )
        screen.blit(hint, (width // 2 - hint.get_width() // 2, height - 118))

        back_r = pygame.Rect(width // 2 - 80, height - 72, 160, 40)
        self._last_rects["back"] = back_r
        bh = back_r.collidepoint(mouse_pos or (0, 0))
        if bh:
            self._hovered = "back"
        self._btn(screen, back_r, "Back", bh)

    def draw_how_to(self, screen, width, height, mouse_pos):
        _draw_gradient(screen, width, height)
        self._hovered = None
        self._last_rects = {}

        t = self.font_title.render("How to play", True, (248, 250, 255))
        screen.blit(t, (width // 2 - t.get_width() // 2, 44))

        lines = (
            "while your feet (or torso) touch mat or opponent you can aim a launch",
            "hold left mouse to charge toward cursor  release to fling from the hips",
            "                                                                           ",       
            "mat pin: 5 seconds with you on top while the rival touches the mat wins you the round",
            "the rival can win the same way when you touch the mat and they are on top",
            "                                                                           ", 
            "you lose if your head hits the mat",
            "                                                                           ", 
            "p pauses  esc backs out of menus  r restarts after a round",
            "                                                                           ", 
            "career floors get meaner  bonus rings change gravity and pacing",
            "options on the main menu has developer tools and clearing your save file",
        )
        y = 108
        for line in lines:
            surf = self.font_small.render(line, True, (200, 206, 220))
            screen.blit(surf, (width // 2 - surf.get_width() // 2, y))
            y += 28

        back_r = pygame.Rect(width // 2 - 80, height - 72, 160, 40)
        self._last_rects["back"] = back_r
        bh = back_r.collidepoint(mouse_pos or (0, 0))
        if bh:
            self._hovered = "back"
        self._btn(screen, back_r, "Back", bh)

    def draw_options(self, screen, width, height, mouse_pos, settings_dict):
        _draw_gradient(screen, width, height)
        self._hovered = None
        self._last_rects = {}

        t = self.font_title.render("Options", True, (248, 250, 255))
        screen.blit(t, (width // 2 - t.get_width() // 2, 36))

        bx = width // 2 - 220
        y = 92
        gap = 48

        mus_on = settings_dict.get("music_enabled", True)
        vol_pct = int(round(float(settings_dict.get("music_volume", 0.52)) * 100))

        r_m = pygame.Rect(bx, y, 440, 42)
        self._last_rects["toggle_music"] = r_m
        hm = r_m.collidepoint(mouse_pos or (0, 0))
        if hm:
            self._hovered = "toggle_music"
        self._btn(
            screen,
            r_m,
            f"Background music: {'ON' if mus_on else 'OFF'}",
            hm,
        )

        y += 50
        r_down = pygame.Rect(bx, y, 118, 40)
        r_up = pygame.Rect(bx + 322, y, 118, 40)
        self._last_rects["music_down"] = r_down
        self._last_rects["music_up"] = r_up
        hd = r_down.collidepoint(mouse_pos or (0, 0))
        hu = r_up.collidepoint(mouse_pos or (0, 0))
        if hd:
            self._hovered = "music_down"
        if hu:
            self._hovered = "music_up"
        self._btn(screen, r_down, "Quieter", hd)
        self._btn(screen, r_up, "Louder", hu)
        vol_lab = self.font_small.render(f"volume {vol_pct}%", True, (198, 204, 222))
        screen.blit(vol_lab, (width // 2 - vol_lab.get_width() // 2, y + 10))

        y += 54
        sec = self.font_small.render("developer", True, (150, 158, 180))
        screen.blit(sec, (bx, y))
        y += 26

        dm = settings_dict.get("dev_mode", False)
        inv = settings_dict.get("dev_invulnerable", False)
        r1 = pygame.Rect(bx, y, 440, 44)
        self._last_rects["toggle_dev"] = r1
        h1 = r1.collidepoint(mouse_pos or (0, 0))
        if h1:
            self._hovered = "toggle_dev"
        self._btn(
            screen,
            r1,
            f"Developer mode: {'ON' if dm else 'OFF'}",
            h1,
        )

        r2 = pygame.Rect(bx, y + gap, 440, 44)
        self._last_rects["toggle_invuln"] = r2
        h2 = r2.collidepoint(mouse_pos or (0, 0))
        if h2:
            self._hovered = "toggle_invuln"
        self._btn(
            screen,
            r2,
            f"Dev safe head (no mat KO): {'ON' if inv else 'OFF'}",
            h2,
        )

        explain = (
            "developer mode unlocks every floor in the menus for testing and skips writing",
            "progress when you win  safe head ignores your head hitting the mat",
        )
        ey = y + gap * 2 + 6
        for line in explain:
            es = self.font_small.render(line, True, (170, 178, 198))
            screen.blit(es, (width // 2 - es.get_width() // 2, ey))
            ey += 22

        if self._options_confirm_clear:
            warn = self.font_sub.render(
                "erase all saved unlocks on this machine?",
                True,
                (255, 200, 200),
            )
            screen.blit(warn, (width // 2 - warn.get_width() // 2, ey + 10))
            yc = ey + 48
            ry = pygame.Rect(width // 2 - 168, yc, 140, 40)
            rn = pygame.Rect(width // 2 + 28, yc, 140, 40)
            self._last_rects["clear_yes"] = ry
            self._last_rects["clear_no"] = rn
            hy = ry.collidepoint(mouse_pos or (0, 0))
            hn = rn.collidepoint(mouse_pos or (0, 0))
            if hy:
                self._hovered = "clear_yes"
            if hn:
                self._hovered = "clear_no"
            self._btn(screen, ry, "Yes erase", hy)
            self._btn(screen, rn, "Cancel", hn)
        else:
            r3 = pygame.Rect(bx, ey + 36, 440, 44)
            self._last_rects["clear_ask"] = r3
            h3 = r3.collidepoint(mouse_pos or (0, 0))
            if h3:
                self._hovered = "clear_ask"
            self._btn(screen, r3, "Clear saved career progress", h3)

        back_r = pygame.Rect(width // 2 - 80, height - 72, 160, 40)
        self._last_rects["back"] = back_r
        bh = back_r.collidepoint(mouse_pos or (0, 0))
        if bh:
            self._hovered = "back"
        self._btn(screen, back_r, "Back", bh)

    def draw_pause_menu(self, screen, width, height, mouse_pos=None):
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((6, 8, 16, 210))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (72, 82, 108), (0, 0, width, height), 1)

        t = self.font_title.render("Paused", True, (245, 248, 255))
        t_sh = self.font_title.render("Paused", True, (18, 20, 30))
        tx = width // 2 - t.get_width() // 2
        ty = height // 2 - 120
        screen.blit(t_sh, (tx + 2, ty + 2))
        screen.blit(t, (tx, ty))

        self._hovered = None
        self._last_rects = {}
        bx = width // 2 - 120
        for i, (key, lab) in enumerate((("resume", "Resume"), ("restart_last", "Restart round"))):
            r = pygame.Rect(bx, height // 2 - 40 + i * 54, 240, 44)
            self._last_rects[key] = r
            hov = r.collidepoint(mouse_pos or (0, 0))
            if hov:
                self._hovered = key
            self._btn(screen, r, lab, hov)

        tip = self.font_small.render("esc home  p resume", True, (170, 178, 198))
        screen.blit(tip, (width // 2 - tip.get_width() // 2, height // 2 + 88))

    def draw_end_menu(
        self,
        screen,
        width,
        height,
        player_won,
        mouse_pos,
        can_next_main,
        show_next_bonus,
    ):
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((6, 8, 16, 215))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (78, 88, 118), (0, 0, width, height), 1)

        title = "You win" if player_won else "You got pinned"
        t = self.font_title.render(title, True, (245, 248, 255))
        t_sh = self.font_title.render(title, True, (18, 20, 30))
        tx = width // 2 - t.get_width() // 2
        ty = height // 2 - 140
        screen.blit(t_sh, (tx + 2, ty + 2))
        screen.blit(t, (tx, ty))

        self._hovered = None
        self._last_rects = {}
        bx = width // 2 - 130
        y = height // 2 - 58
        buttons = [("restart_last", "Play again")]
        if player_won and can_next_main:
            buttons.append(("next_main", "Next floor"))
        if player_won and show_next_bonus:
            buttons.append(("goto_bonus_menu", "Bonus rings"))
        buttons.append(("goto_levels", "Floor select"))
        buttons.append(("goto_home", "Main menu"))

        for i, (key, lab) in enumerate(buttons):
            r = pygame.Rect(bx, y + i * 50, 260, 42)
            self._last_rects[key] = r
            hov = r.collidepoint(mouse_pos or (0, 0))
            if hov:
                self._hovered = key
            self._btn(screen, r, lab, hov)

        if not player_won:
            tip = self.font_small.render("r quick restart", True, (170, 178, 198))
            screen.blit(tip, (width // 2 - tip.get_width() // 2, height // 2 + 130))
