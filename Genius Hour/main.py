import pygame

import arena_background
import audio
import game_world
import hud
import levels
import menu
import movement
import progress
import settings
import viewport
from globals import ENEMY_BODY_RGB, PLAYER_BODY_RGB


def _font(name, size, bold=False):
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except (OSError, ValueError, TypeError):
        return pygame.font.Font(None, size)


pygame.init()
audio.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Rumble League")
game_surface = pygame.Surface((viewport.VIEW_WIDTH, viewport.VIEW_HEIGHT))
clock = pygame.time.Clock()

font_title = _font("Segoe UI", 46, bold=True)
font_sub = _font("Segoe UI", 22)
font_btn = _font("Segoe UI", 22)
font_small = _font("Segoe UI", 17)
font_banner = _font("Segoe UI", 19, bold=True)
menu_ui = menu.MenuUI(font_title, font_sub, font_btn, font_small)

energy_bar_width = 220
energy_bar_height = 18

phase = menu.HOME
match = None
last_level_spec = levels.default_level()
active_main_index = 0
active_is_bonus = False
app_running = True

while app_running:
    frame_dt = clock.get_time() / 1000
    if frame_dt <= 0:
        frame_dt = 1 / 60
    frame_dt = min(frame_dt, 0.05)

    screen_size = screen.get_size()
    menu_action = None
    released_aim = False
    game_mouse = viewport.screen_to_game(pygame.mouse.get_pos(), screen_size)
    aim_x, aim_y = game_mouse
    st = settings.load()
    saved_prog = progress.load_state()
    prog = progress.menu_unlock_display(st, saved_prog)
    audio.tick(phase, st)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_running = False
            break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_pos = viewport.screen_to_game(event.pos, screen_size)
            if phase == menu.PLAYING and match is not None:
                match._aim_seen_play_mousedown = True
            if phase == menu.HOME:
                menu_action = menu_ui.handle_click(
                    {
                        "career": "goto_levels",
                        "bonus_menu": "goto_bonus",
                        "howto": "goto_howto",
                        "options": "goto_options",
                        "exit": "exit",
                    },
                    click_pos,
                )
            elif phase == menu.LEVEL_SELECT:
                consumed = menu_ui.career_select_pointer_down(
                    click_pos,
                    viewport.VIEW_WIDTH,
                    viewport.VIEW_HEIGHT,
                    len(levels.MAIN_LEVELS),
                )
                if not consumed:
                    act = menu_ui.handle_click(None, click_pos)
                    if act == "back":
                        menu_action = "goto_home"
                    elif act and act.startswith("main_"):
                        idx = int(act.split("_")[1])
                        if st.get("dev_mode") or idx < saved_prog["main_unlocked"]:
                            menu_action = "start_main"
                            active_main_index = idx
            elif phase == menu.BONUS_SELECT:
                act = menu_ui.handle_click(None, click_pos)
                if act == "back":
                    menu_action = "goto_home"
                elif act and act.startswith("bonus_"):
                    idx = int(act.split("_")[1])
                    if st.get("dev_mode") or idx < saved_prog["bonus_unlocked"]:
                        menu_action = "start_bonus"
                        active_main_index = idx
            elif phase == menu.HOW_TO:
                menu_action = menu_ui.handle_click({"back": "goto_home"}, click_pos)
            elif phase == menu.OPTIONS:
                act = menu_ui.handle_click(None, click_pos)
                if act == "back":
                    menu_action = "goto_home"
                elif act == "toggle_music":
                    settings.toggle("music_enabled")
                elif act == "music_down":
                    settings.bump_music_volume(-0.08)
                elif act == "music_up":
                    settings.bump_music_volume(0.08)
                elif act == "toggle_dev":
                    settings.toggle("dev_mode")
                elif act == "toggle_invuln":
                    settings.toggle("dev_invulnerable")
                elif act == "clear_ask":
                    menu_ui.set_options_clear_confirm(True)
                elif act == "clear_yes":
                    progress.clear_progress()
                    menu_ui.reset_options_confirm()
                elif act == "clear_no":
                    menu_ui.reset_options_confirm()
            elif phase == menu.PAUSED:
                menu_action = menu_ui.handle_click(
                    {"resume": "resume", "restart_last": "restart_last"},
                    click_pos,
                )
            elif phase == menu.ENDED:
                menu_action = menu_ui.handle_click(
                    {
                        "restart_last": "restart_last",
                        "next_main": "next_main",
                        "goto_bonus_menu": "goto_bonus",
                        "goto_levels": "goto_levels",
                        "goto_home": "goto_home",
                    },
                    click_pos,
                )

        if event.type == pygame.MOUSEWHEEL and phase == menu.LEVEL_SELECT:
            menu_ui.career_scroll_wheel(
                event.y,
                viewport.VIEW_WIDTH,
                viewport.VIEW_HEIGHT,
                len(levels.MAIN_LEVELS),
            )

        if event.type == pygame.MOUSEMOTION and phase == menu.LEVEL_SELECT:
            gm = viewport.screen_to_game(event.pos, screen_size)
            menu_ui.career_select_pointer_move(
                gm,
                viewport.VIEW_WIDTH,
                viewport.VIEW_HEIGHT,
                len(levels.MAIN_LEVELS),
                event.buttons[0],
            )

        if event.type == pygame.KEYDOWN:
            menu_action = menu_action or menu_ui.handle_key(phase, event)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            menu_ui.career_select_pointer_up()
            if phase == menu.PLAYING and match is not None:
                if not match._aim_input_primed:
                    match._aim_input_primed = True
                elif match.player_supported():
                    released_aim = True
                    aim_x, aim_y = viewport.screen_to_game(event.pos, screen_size)

    if menu_action == "goto_home":
        phase = menu.HOME
        match = None
        menu_ui.reset_options_confirm()
    elif menu_action == "goto_levels":
        phase = menu.LEVEL_SELECT
        match = None
        menu_ui.reset_career_scroll()
    elif menu_action == "goto_bonus":
        phase = menu.BONUS_SELECT
        match = None
    elif menu_action == "goto_howto":
        phase = menu.HOW_TO
        match = None
    elif menu_action == "goto_options":
        phase = menu.OPTIONS
        match = None
        menu_ui.reset_options_confirm()
    elif menu_action == "start_main":
        spec = levels.main_by_index(active_main_index)
        last_level_spec = spec
        active_is_bonus = False
        match = game_world.Match(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            spec,
            dev_invulnerable=st.get("dev_invulnerable", False),
        )
        phase = menu.PLAYING
    elif menu_action == "start_bonus":
        spec = levels.bonus_by_index(active_main_index)
        last_level_spec = spec
        active_is_bonus = True
        match = game_world.Match(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            spec,
            dev_invulnerable=st.get("dev_invulnerable", False),
        )
        phase = menu.PLAYING
    elif menu_action == "pause":
        phase = menu.PAUSED
    elif menu_action == "resume":
        phase = menu.PLAYING
    elif menu_action == "restart_last":
        phase = menu.PLAYING
        match = game_world.Match(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            last_level_spec,
            dev_invulnerable=st.get("dev_invulnerable", False),
        )
    elif menu_action == "next_main":
        if not active_is_bonus and active_main_index < len(levels.MAIN_LEVELS) - 1:
            active_main_index += 1
            spec = levels.main_by_index(active_main_index)
            last_level_spec = spec
            match = game_world.Match(
                game_surface,
                viewport.VIEW_WIDTH,
                viewport.VIEW_HEIGHT,
                spec,
                dev_invulnerable=st.get("dev_invulnerable", False),
            )
            phase = menu.PLAYING
    elif menu_action == "exit":
        app_running = False

    theme = "classic"
    if match is not None:
        theme = match.level_spec.arena_theme
    arena_background.draw_wrestling_ring(
        game_surface,
        viewport.VIEW_WIDTH,
        viewport.VIEW_HEIGHT,
        theme,
    )

    if phase in (menu.PLAYING, menu.PAUSED, menu.ENDED) and match is not None:
        player_supported = match.player_supported()
        mouse_held = pygame.mouse.get_pressed()[0]
        hold_aim = False
        if (
            phase == menu.PLAYING
            and player_supported
            and mouse_held
            and match._aim_input_primed
            and match._aim_seen_play_mousedown
        ):
            hold_aim = True
            aim_x, aim_y = viewport.screen_to_game(pygame.mouse.get_pos(), screen_size)

        player_intent = movement.MovementIntent(
            hold_aim=hold_aim,
            release_aim=released_aim,
            aim_x=aim_x,
            aim_y=aim_y,
        )

        dt = frame_dt / 3
        for _ in range(3):
            if phase == menu.PLAYING and not match.match_over():
                match.step(dt, player_intent)
            else:
                match.space.step(dt)

        match.draw(game_surface)
        spec = match.level_spec
        hud.draw_energy_bar(
            game_surface,
            18,
            96,
            energy_bar_width,
            energy_bar_height,
            match.player_energy.ratio(),
            PLAYER_BODY_RGB,
            "your stamina",
            font_small,
        )
        hud.draw_energy_bar(
            game_surface,
            viewport.VIEW_WIDTH - energy_bar_width - 18,
            96,
            energy_bar_width,
            energy_bar_height,
            match.enemy_energy.ratio(),
            ENEMY_BODY_RGB,
            "rival stamina"
            if match.enemy_energy_secondary is None
            else "rival 1 stamina",
            font_small,
        )
        if match.enemy_energy_secondary is not None:
            hud.draw_energy_bar(
                game_surface,
                viewport.VIEW_WIDTH - energy_bar_width - 18,
                128,
                energy_bar_width,
                energy_bar_height,
                match.enemy_energy_secondary.ratio(),
                ENEMY_BODY_RGB,
                "rival 2 stamina",
                font_small,
            )
        hud.draw_level_banner(
            game_surface,
            viewport.VIEW_WIDTH,
            spec.title,
            spec.tagline,
            font_banner,
            font_small,
        )
        if phase == menu.PLAYING and hold_aim:
            hip = match.player_controller.hip_world(match.torso)
            hud.draw_aim_charge(
                game_surface,
                (hip.x, hip.y),
                (aim_x, aim_y),
                match.player_controller.charge,
                match.player_energy.max_energy,
                PLAYER_BODY_RGB,
            )
        if phase == menu.PLAYING and (
            st.get("dev_mode") or st.get("dev_invulnerable")
        ):
            hud.draw_dev_corner(game_surface, viewport.VIEW_WIDTH, font_small, st)
        if phase == menu.PLAYING and (
            match.pinning_opponent() or match.pin_ratio() > 0.001
        ):
            hud.draw_pin_hold(
                game_surface,
                viewport.VIEW_WIDTH,
                140,
                200,
                match.pin_ratio(),
                font_small,
            )
        if phase == menu.PLAYING and (
            match.enemy_pinning_player() or match.enemy_pin_ratio() > 0.001
        ):
            hud.draw_rival_mat_pin_hold(
                game_surface,
                viewport.VIEW_WIDTH,
                190,
                200,
                match.enemy_pin_ratio(),
                font_small,
            )

        if phase == menu.PLAYING and match.match_over():
            if (
                match.player_won
                and not active_is_bonus
                and not st.get("dev_mode", False)
            ):
                progress.register_main_win(active_main_index)
            phase = menu.ENDED

    if phase == menu.HOME:
        menu_ui.draw_home(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            game_mouse,
            saved_prog,
            st,
        )
    elif phase == menu.LEVEL_SELECT:
        menu_ui.draw_level_select(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            game_mouse,
            levels.MAIN_LEVELS,
            prog,
        )
    elif phase == menu.BONUS_SELECT:
        menu_ui.draw_bonus_select(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            game_mouse,
            levels.BONUS_LEVELS,
            prog,
        )
    elif phase == menu.HOW_TO:
        menu_ui.draw_how_to(game_surface, viewport.VIEW_WIDTH, viewport.VIEW_HEIGHT, game_mouse)
    elif phase == menu.OPTIONS:
        menu_ui.draw_options(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            game_mouse,
            settings.load(),
        )
    elif phase == menu.PAUSED:
        menu_ui.draw_pause_menu(game_surface, viewport.VIEW_WIDTH, viewport.VIEW_HEIGHT, game_mouse)
    elif phase == menu.ENDED and match is not None:
        can_next = (
            match.player_won
            and not active_is_bonus
            and active_main_index < len(levels.MAIN_LEVELS) - 1
        )
        show_bonus_btn = match.player_won and prog["bonus_unlocked"] >= 1
        menu_ui.draw_end_menu(
            game_surface,
            viewport.VIEW_WIDTH,
            viewport.VIEW_HEIGHT,
            match.player_won,
            game_mouse,
            can_next,
            show_bonus_btn,
        )

    viewport.present_game_surface(screen, game_surface)
    pygame.display.flip()
    clock.tick(60)

audio.stop()
pygame.quit()
