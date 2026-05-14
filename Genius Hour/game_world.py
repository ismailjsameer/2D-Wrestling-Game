import pymunk
import pymunk.pygame_util

import enemy
import enemy_ai
import energy
import ground_check
import levels
import movement
import player
import visual_polish
from ragdoll_tuning import damp_limb_spin

COLLISION_FLOOR = 1
COLLISION_PLAYER_HEAD = 2
COLLISION_ENEMY_HEAD = 3
COLLISION_ENEMY_SURFACE = 4
COLLISION_PLAYER_SURFACE = 5
COLLISION_ENEMY_HEAD_B = 6
COLLISION_ENEMY_SURFACE_B = 7
COLLISION_CORPSE = 10

MAX_HORIZONTAL_SPEED = 2600
MAX_VERTICAL_SPEED = 5200
PIN_WIN_SECONDS = 5.0
START_GRACE_SECONDS = 0.22


def _all_enemy_surface_bodies(
    torso,
    lua,
    lla,
    rua,
    rla,
    lul,
    lll,
    rul,
    rll,
):
    return (
        torso,
        lua,
        lla,
        rua,
        rla,
        lul,
        lll,
        rul,
        rll,
    )


class Match:
    def __init__(
        self,
        screen,
        width,
        height,
        level_spec=None,
        dev_invulnerable=False,
    ):
        self.width = width
        self.height = height
        self.level_spec = level_spec or levels.default_level()
        self.dev_invulnerable = dev_invulnerable
        self.player_lost = False
        self.player_won = False
        self._pin_time = 0.0
        self._enemy_pin_time = 0.0
        self._match_age = 0.0
        self._aim_input_primed = False
        self._aim_seen_play_mousedown = False
        self._rival1_eliminated = False
        self._rival2_eliminated = False
        self.enemy_energy_secondary = None
        self.enemy_controller_secondary = None
        self.enemy_limbs_secondary = None
        self._enemy_b_joints = None
        self._enemy_b_head = None
        self._enemy_b_torso = None
        self._enemy2_shadow_parts = ()

        self.space = pymunk.Space()
        self.space.damping = 0.978
        self.space.gravity = self.level_spec.gravity
        self.space.iterations = 42

        static_body = self.space.static_body
        wall_thickness = 10
        self.floor = pymunk.Segment(
            static_body,
            (0, height),
            (width, height),
            wall_thickness,
        )
        self.floor.friction = 0.52
        self.floor.elasticity = 0.22
        self.floor.collision_type = COLLISION_FLOOR

        self.walls = [
            pymunk.Segment(static_body, (0, 0), (width, 0), wall_thickness),
            pymunk.Segment(static_body, (width, 0), (width, height), wall_thickness),
            pymunk.Segment(static_body, (0, height), (0, 0), wall_thickness),
        ]
        for wall in self.walls:
            wall.elasticity = 0.2
            wall.friction = 0.95

        spawn_torso_y = movement.stand_torso_y(height)
        (
            self.ragdoll_joints,
            self.torso,
            self.head,
            self.l_upper_arm,
            self.l_lower_arm,
            self.r_upper_arm,
            self.r_lower_arm,
            self.l_upper_leg,
            self.l_lower_leg,
            self.r_upper_leg,
            self.r_lower_leg,
        ) = player.make_player(
            space=self.space,
            x=self.level_spec.player_spawn_x,
            y=spawn_torso_y,
            group=0,
        )

        head_shape = next(iter(self.head.shapes))
        head_shape.collision_type = COLLISION_PLAYER_HEAD

        (
            self.enemy_joints,
            self.enemy_torso,
            self.enemy_head,
            self.enemy_l_upper_arm,
            self.enemy_l_lower_arm,
            self.enemy_r_upper_arm,
            self.enemy_r_lower_arm,
            self.enemy_l_upper_leg,
            self.enemy_l_lower_leg,
            self.enemy_r_upper_leg,
            self.enemy_r_lower_leg,
        ) = enemy.make_enemy(
            space=self.space,
            x=self.level_spec.enemy_spawn_x,
            y=spawn_torso_y,
            group=0,
        )

        next(iter(self.enemy_head.shapes)).collision_type = COLLISION_ENEMY_HEAD

        for body in _all_enemy_surface_bodies(
            self.enemy_torso,
            self.enemy_l_upper_arm,
            self.enemy_l_lower_arm,
            self.enemy_r_upper_arm,
            self.enemy_r_lower_arm,
            self.enemy_l_upper_leg,
            self.enemy_l_lower_leg,
            self.enemy_r_upper_leg,
            self.enemy_r_lower_leg,
        ):
            ground_check._set_shape_collision_type(body, COLLISION_ENEMY_SURFACE)

        for body in (
            self.torso,
            self.l_upper_arm,
            self.l_lower_arm,
            self.r_upper_arm,
            self.r_lower_arm,
            self.l_upper_leg,
            self.l_lower_leg,
            self.r_upper_leg,
            self.r_lower_leg,
        ):
            ground_check._set_shape_collision_type(body, COLLISION_PLAYER_SURFACE)

        self._enemy1_ground_bodies = [
            self.enemy_torso,
            self.enemy_l_upper_leg,
            self.enemy_l_lower_leg,
            self.enemy_r_upper_leg,
            self.enemy_r_lower_leg,
        ]
        self._enemy1_all_bodies = (
            self.enemy_torso,
            self.enemy_head,
            self.enemy_l_upper_arm,
            self.enemy_l_lower_arm,
            self.enemy_r_upper_arm,
            self.enemy_r_lower_arm,
            self.enemy_l_upper_leg,
            self.enemy_l_lower_leg,
            self.enemy_r_upper_leg,
            self.enemy_r_lower_leg,
        )

        self._enemy2_ground_bodies = None
        self._enemy2_all_bodies = ()
        bx = self.level_spec.second_enemy_spawn_x
        if bx is not None:
            (
                self._enemy_b_joints,
                self._enemy_b_torso,
                self._enemy_b_head,
                eb_lua,
                eb_lla,
                eb_rua,
                eb_rla,
                eb_lul,
                eb_lll,
                eb_rul,
                eb_rll,
            ) = enemy.make_enemy(
                space=self.space,
                x=bx,
                y=spawn_torso_y,
                group=0,
            )
            next(iter(self._enemy_b_head.shapes)).collision_type = COLLISION_ENEMY_HEAD_B
            for body in _all_enemy_surface_bodies(
                self._enemy_b_torso,
                eb_lua,
                eb_lla,
                eb_rua,
                eb_rla,
                eb_lul,
                eb_lll,
                eb_rul,
                eb_rll,
            ):
                ground_check._set_shape_collision_type(body, COLLISION_ENEMY_SURFACE_B)

            self._enemy2_ground_bodies = [
                self._enemy_b_torso,
                eb_lul,
                eb_lll,
                eb_rul,
                eb_rll,
            ]
            self._enemy2_all_bodies = (
                self._enemy_b_torso,
                self._enemy_b_head,
                eb_lua,
                eb_lla,
                eb_rua,
                eb_rla,
                eb_lul,
                eb_lll,
                eb_rul,
                eb_rll,
            )
            self._enemy2_shadow_parts = self._enemy2_all_bodies
            self.enemy_limbs_secondary = movement.RagdollLimbs(
                eb_lua,
                eb_lla,
                eb_rua,
                eb_rla,
                eb_lul,
                eb_lll,
                eb_rul,
                eb_rll,
            )
            ee = self.level_spec.enemy_energy
            self.enemy_energy_secondary = energy.EnergyPool(
                ee[0], ee[1], ee[2], ee[3], ee[4]
            )
            self.enemy_controller_secondary = enemy_ai.EnemyAI(self.level_spec)

        self._enemy_heads_remaining = {self.enemy_head}
        if bx is not None:
            self._enemy_heads_remaining.add(self._enemy_b_head)

        self.space.add(*self.walls)
        self.space.add(self.floor)
        self.space.add(*self.ragdoll_joints)
        self.space.add(*self.enemy_joints)
        if self._enemy_b_joints is not None:
            self.space.add(*self._enemy_b_joints)

        self.ground_tracker = ground_check.GroundTracker(self.space, COLLISION_FLOOR)
        self._player_ground_bodies = [
            self.torso,
            self.l_upper_leg,
            self.l_lower_leg,
            self.r_upper_leg,
            self.r_lower_leg,
        ]

        ct = COLLISION_CORPSE
        self._player_on_e1 = ground_check.RagdollSurfaceContacts(
            self.space,
            (COLLISION_ENEMY_SURFACE, COLLISION_ENEMY_HEAD),
            self._player_ground_bodies,
            corpse_collision_type=ct,
        )
        self._player_on_e2 = None
        if bx is not None:
            self._player_on_e2 = ground_check.RagdollSurfaceContacts(
                self.space,
                (COLLISION_ENEMY_SURFACE_B, COLLISION_ENEMY_HEAD_B),
                self._player_ground_bodies,
                corpse_collision_type=ct,
            )

        self._enemy_on_player_e1 = ground_check.RagdollSurfaceContacts(
            self.space,
            (COLLISION_PLAYER_SURFACE, COLLISION_PLAYER_HEAD),
            self._enemy1_ground_bodies,
            corpse_collision_type=ct,
        )
        self._enemy_on_player_e2 = None
        if bx is not None:
            self._enemy_on_player_e2 = ground_check.RagdollSurfaceContacts(
                self.space,
                (COLLISION_PLAYER_SURFACE, COLLISION_PLAYER_HEAD),
                self._enemy2_ground_bodies,
                corpse_collision_type=ct,
            )

        self.draw_options = pymunk.pygame_util.DrawOptions(screen)

        self.space.on_collision(
            COLLISION_PLAYER_HEAD,
            COLLISION_FLOOR,
            begin=self._on_player_head_floor,
            data=self,
        )
        self.space.on_collision(
            COLLISION_ENEMY_HEAD,
            COLLISION_FLOOR,
            begin=self._on_enemy_head_floor,
            data=self,
        )
        self.space.on_collision(
            COLLISION_ENEMY_HEAD_B,
            COLLISION_FLOOR,
            begin=self._on_enemy_head_floor,
            data=self,
        )

        speed_roots = [self.torso, self.head, self.enemy_torso, self.enemy_head]
        spin_extra = list(self._enemy1_all_bodies[2:])
        if self._enemy_b_torso is not None:
            speed_roots.extend((self._enemy_b_torso, self._enemy_b_head))
            spin_extra.extend(self._enemy2_all_bodies[2:])

        for body in speed_roots:
            body.velocity_func = self._limit_speed
        for body in (
            self.l_upper_arm,
            self.l_lower_arm,
            self.r_upper_arm,
            self.r_lower_arm,
            self.l_upper_leg,
            self.l_lower_leg,
            self.r_upper_leg,
            self.r_lower_leg,
            *spin_extra,
        ):
            body.velocity_func = damp_limb_spin

        self.player_controller = movement.RagdollController(movement.player_movement_config())
        self.enemy_controller = enemy_ai.EnemyAI(self.level_spec)
        self.player_limbs = movement.RagdollLimbs(
            self.l_upper_arm,
            self.l_lower_arm,
            self.r_upper_arm,
            self.r_lower_arm,
            self.l_upper_leg,
            self.l_lower_leg,
            self.r_upper_leg,
            self.r_lower_leg,
        )
        self.enemy_limbs = movement.RagdollLimbs(
            self.enemy_l_upper_arm,
            self.enemy_l_lower_arm,
            self.enemy_r_upper_arm,
            self.enemy_r_lower_arm,
            self.enemy_l_upper_leg,
            self.enemy_l_lower_leg,
            self.enemy_r_upper_leg,
            self.enemy_r_lower_leg,
        )
        pe = self.level_spec.player_energy
        ee = self.level_spec.enemy_energy
        self.player_energy = energy.EnergyPool(pe[0], pe[1], pe[2], pe[3], pe[4])
        self.enemy_energy = energy.EnergyPool(ee[0], ee[1], ee[2], ee[3], ee[4])

    def _strip_ragdoll_to_corpse(self, bodies):
        for body in bodies:
            for shape in body.shapes:
                shape.collision_type = COLLISION_CORPSE

    @staticmethod
    def _on_player_head_floor(arbiter, space_, data):
        if data.dev_invulnerable:
            return True
        if data._match_age < START_GRACE_SECONDS:
            return True
        data.player_lost = True
        return True

    @staticmethod
    def _on_enemy_head_floor(arbiter, space_, data):
        if data._match_age < START_GRACE_SECONDS:
            return True
        head_body = None
        for shape in arbiter.shapes:
            if shape is None or shape.body is None:
                continue
            if shape.body in data._enemy_heads_remaining:
                head_body = shape.body
                break
        if head_body is None:
            return True
        data._enemy_heads_remaining.discard(head_body)
        if head_body is data.enemy_head:
            data._rival1_eliminated = True
            data._strip_ragdoll_to_corpse(data._enemy1_all_bodies)
        elif data._enemy_b_head is not None and head_body is data._enemy_b_head:
            data._rival2_eliminated = True
            data._strip_ragdoll_to_corpse(data._enemy2_all_bodies)
        if not data._enemy_heads_remaining:
            data.player_won = True
        return True

    def _limit_speed(self, body, gravity, damping, dt):
        pymunk.Body.update_velocity(body, gravity, damping, dt)
        vx, vy = body.velocity
        if abs(vx) > MAX_HORIZONTAL_SPEED:
            vx = MAX_HORIZONTAL_SPEED if vx > 0 else -MAX_HORIZONTAL_SPEED
        if abs(vy) > MAX_VERTICAL_SPEED:
            vy = MAX_VERTICAL_SPEED if vy > 0 else -MAX_VERTICAL_SPEED
        body.velocity = vx, vy

    def _alive_e1_on_mat(self):
        if self._rival1_eliminated:
            return False
        return self.ground_tracker.ragdoll_on_floor(self._enemy1_ground_bodies)

    def _alive_e2_on_mat(self):
        if self._enemy2_ground_bodies is None or self._rival2_eliminated:
            return False
        return self.ground_tracker.ragdoll_on_floor(self._enemy2_ground_bodies)

    def pinning_opponent(self):
        rival_on_mat = self._alive_e1_on_mat() or self._alive_e2_on_mat()
        if not rival_on_mat:
            return False
        on_rival = False
        if not self._rival1_eliminated:
            on_rival |= self._player_on_e1.any_supported(self._player_ground_bodies)
        if self._player_on_e2 is not None and not self._rival2_eliminated:
            on_rival |= self._player_on_e2.any_supported(self._player_ground_bodies)
        return on_rival

    def enemy_pinning_player(self):
        you_on_mat = self.ground_tracker.ragdoll_on_floor(self._player_ground_bodies)
        rival_on_you = False
        if not self._rival1_eliminated:
            rival_on_you |= self._enemy_on_player_e1.any_supported(self._enemy1_ground_bodies)
        if self._enemy_on_player_e2 is not None and not self._rival2_eliminated:
            rival_on_you |= self._enemy_on_player_e2.any_supported(self._enemy2_ground_bodies)
        return you_on_mat and rival_on_you

    def pin_ratio(self):
        if self.match_over():
            return 0.0
        return max(0.0, min(1.0, self._pin_time / PIN_WIN_SECONDS))

    def enemy_pin_ratio(self):
        if self.match_over():
            return 0.0
        return max(0.0, min(1.0, self._enemy_pin_time / PIN_WIN_SECONDS))

    def _update_pin_win(self, dt):
        if self.match_over():
            return
        if self._match_age < START_GRACE_SECONDS:
            return
        if self.pinning_opponent():
            self._pin_time += dt
            if self._pin_time >= PIN_WIN_SECONDS:
                self.player_won = True
        else:
            self._pin_time = 0.0

        if self.match_over():
            return

        if self.enemy_pinning_player():
            self._enemy_pin_time += dt
            if self._enemy_pin_time >= PIN_WIN_SECONDS:
                self.player_lost = True
        else:
            self._enemy_pin_time = 0.0

    def player_supported(self):
        on_floor = self.ground_tracker.ragdoll_on_floor(self._player_ground_bodies)
        on_e1 = self._player_on_e1.any_supported(self._player_ground_bodies)
        if self._player_on_e2 is not None:
            on_e2 = self._player_on_e2.any_supported(self._player_ground_bodies)
            return on_floor or on_e1 or on_e2
        return on_floor or on_e1

    def enemy_supported(self):
        if self._rival1_eliminated:
            return False
        on_floor = self.ground_tracker.ragdoll_on_floor(self._enemy1_ground_bodies)
        on_player = self._enemy_on_player_e1.any_supported(self._enemy1_ground_bodies)
        return on_floor or on_player

    def _enemy_b_supported(self):
        if self._enemy2_ground_bodies is None or self._rival2_eliminated:
            return False
        on_floor = self.ground_tracker.ragdoll_on_floor(self._enemy2_ground_bodies)
        on_player = self._enemy_on_player_e2.any_supported(self._enemy2_ground_bodies)
        return on_floor or on_player

    def match_over(self):
        return self.player_lost or self.player_won

    def set_draw_surface(self, screen):
        self.draw_options = pymunk.pygame_util.DrawOptions(screen)

    def step(self, dt, player_intent):
        self._match_age += dt
        if not self.match_over():
            self.player_controller.apply(
                self.torso,
                self.player_supported(),
                dt,
                player_intent,
                self.player_energy,
                self.player_limbs,
                self.enemy_torso,
            )
            if not self._rival1_eliminated:
                self.enemy_controller.update(
                    self.enemy_torso,
                    self.head,
                    self.torso,
                    dt,
                    self.enemy_supported(),
                    self.width,
                    self.enemy_energy,
                    self.enemy_limbs,
                )
            if self.enemy_controller_secondary is not None and not self._rival2_eliminated:
                self.enemy_controller_secondary.update(
                    self._enemy_b_torso,
                    self.head,
                    self.torso,
                    dt,
                    self._enemy_b_supported(),
                    self.width,
                    self.enemy_energy_secondary,
                    self.enemy_limbs_secondary,
                )
        self.space.step(dt)
        if not self.match_over():
            self._update_pin_win(dt)

    def draw(self, screen):
        self.set_draw_surface(screen)
        base_shadow = (
            self.torso,
            self.head,
            self.l_upper_arm,
            self.l_lower_arm,
            self.r_upper_arm,
            self.r_lower_arm,
            self.l_upper_leg,
            self.l_lower_leg,
            self.r_upper_leg,
            self.r_lower_leg,
            self.enemy_torso,
            self.enemy_head,
            self.enemy_l_upper_arm,
            self.enemy_l_lower_arm,
            self.enemy_r_upper_arm,
            self.enemy_r_lower_arm,
            self.enemy_l_upper_leg,
            self.enemy_l_lower_leg,
            self.enemy_r_upper_leg,
            self.enemy_r_lower_leg,
        )
        visual_polish.draw_ragdoll_shadows(
            screen,
            self.height - 10,
            base_shadow + self._enemy2_shadow_parts,
        )
        self.space.debug_draw(self.draw_options)
