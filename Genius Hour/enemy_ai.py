import random

from movement import MovementIntent, RagdollController, enemy_movement_config


class EnemyAI:
    def __init__(self, level_spec=None):
        self.movement = RagdollController(enemy_movement_config())
        self.cooldown = 0.0
        self.plan_horizontal = 0
        self.plan_jump = False
        self.target_charge = 0.45
        self._cd_scale = 1.0
        self._charge_add = 0.0
        if level_spec is not None:
            self._cd_scale = max(0.55, min(1.35, level_spec.enemy_cooldown_scale))
            self._charge_add = max(-0.12, min(0.14, level_spec.enemy_charge_add))

    def _boost_charge(self, low, high):
        t = random.uniform(low, high) + self._charge_add
        return max(0.12, min(0.92, t))

    def _aim_point(self, player_head):
        return player_head.position + player_head.velocity * 0.18

    def _player_near_wall(self, player_head, arena_width):
        margin = 110
        if player_head.position.x < margin:
            return -1
        if player_head.position.x > arena_width - margin:
            return 1
        return 0

    def _clear_plan(self):
        self.plan_horizontal = 0
        self.plan_jump = False

    def _pick_plan(self, enemy_torso, player_head, player_torso, arena_width):
        target = self._aim_point(player_head)
        offset = target - enemy_torso.position
        distance = offset.length
        wall_side = self._player_near_wall(player_head, arena_width)
        pinned = distance < 190 and abs(offset.x) < 95

        if pinned and wall_side != 0:
            self.plan_horizontal = -wall_side
            self.plan_jump = False
            self.target_charge = self._boost_charge(0.35, 0.75)
            return

        if wall_side != 0 and distance < 280:
            self.plan_horizontal = -wall_side
            self.plan_jump = False
            self.target_charge = self._boost_charge(0.3, 0.65)
            return

        if distance > 130:
            if offset.x > 40:
                self.plan_horizontal = 1
            elif offset.x < -40:
                self.plan_horizontal = -1
            else:
                self.plan_horizontal = 0
            self.plan_jump = False
            self.target_charge = self._boost_charge(0.4, 0.9)
            return

        if offset.y < -35 or player_torso.position.y < enemy_torso.position.y - 24:
            self.plan_horizontal = 0
            self.plan_jump = True
            self.target_charge = self._boost_charge(0.35, 0.8)
            return

        if abs(offset.x) > 20:
            self.plan_horizontal = 1 if offset.x > 0 else -1
            self.plan_jump = False
            self.target_charge = self._boost_charge(0.3, 0.7)
            return

        self._clear_plan()
        self.target_charge = self._boost_charge(0.35, 0.65)

    def update(
        self,
        enemy_torso,
        player_head,
        player_torso,
        dt,
        supported,
        arena_width,
        energy,
        limbs,
    ):
        self.cooldown = max(0.0, self.cooldown - dt)

        intent = MovementIntent()
        if not supported:
            self._clear_plan()
            self.movement.apply(
                enemy_torso,
                supported,
                dt,
                intent,
                energy,
                limbs,
                player_torso,
            )
            return

        if self.cooldown <= 0.0 and self.movement.charge_mode is None:
            self._pick_plan(enemy_torso, player_head, player_torso, arena_width)

        release_horizontal = 0
        release_jump = False

        cap = energy.max_energy if energy is not None and energy.max_energy > 0 else 1.0
        charge_frac = self.movement.charge / cap

        if self.plan_jump:
            intent.hold_jump = True
            if charge_frac >= self.target_charge:
                release_jump = True
        elif self.plan_horizontal != 0:
            intent.hold_horizontal = self.plan_horizontal
            if charge_frac >= self.target_charge:
                release_horizontal = self.plan_horizontal

        intent.release_horizontal = release_horizontal
        intent.release_jump = release_jump

        self.movement.apply(
            enemy_torso,
            supported,
            dt,
            intent,
            energy,
            limbs,
            player_torso,
        )

        if release_horizontal != 0 or release_jump:
            self.cooldown = (
                (0.55 if release_jump else 0.42) * self._cd_scale
            )
            self._clear_plan()
