import math

from dataclasses import dataclass


@dataclass
class MovementConfig:
    charge_rate: float = 5.2
    min_charge: float = 0.05
    max_charge: float = 1.0
    charge_decay: float = 2.4
    horizontal_impulse: float = 5200
    jump_impulse: float = 8200
    upright_torque: float = 22000
    upright_damping: float = 380
    move_cost: float = 22
    jump_cost: float = 28
    hip_offset_y: float = 39
    aim_min_distance: float = 22


@dataclass
class MovementIntent:
    hold_horizontal: int = 0
    release_horizontal: int = 0
    hold_jump: bool = False
    release_jump: bool = False
    hold_aim: bool = False
    release_aim: bool = False
    aim_x: float = 0.0
    aim_y: float = 0.0


@dataclass
class RagdollLimbs:
    l_upper_arm: object
    l_lower_arm: object
    r_upper_arm: object
    r_lower_arm: object
    l_upper_leg: object
    l_lower_leg: object
    r_upper_leg: object
    r_lower_leg: object


class RagdollController:
    def __init__(self, config=None):
        self.config = config or MovementConfig()
        self._charge = 0.0
        self._charge_mode = None

    @property
    def charge(self):
        return self._charge

    @property
    def charge_mode(self):
        return self._charge_mode

    def _hip_point(self, torso):
        return torso.local_to_world((0, self.config.hip_offset_y))

    def hip_world(self, torso):
        return self._hip_point(torso)

    def _reset_charge(self):
        self._charge = 0.0
        self._charge_mode = None

    def _charge_cap(self, energy):
        if energy is not None and energy.max_energy > 0:
            return float(energy.max_energy)
        return self.config.max_charge

    def _charge_key(self, mode, direction=0):
        if mode == "horizontal":
            return ("horizontal", direction)
        if mode == "aim":
            return ("aim",)
        return ("jump",)

    def _matches_charge(self, mode, direction=0):
        if self._charge_mode is None:
            return False
        return self._charge_mode == self._charge_key(mode, direction)

    def _begin_charge(self, dt, mode, direction=0, energy=None):
        cap = self._charge_cap(energy)
        key = self._charge_key(mode, direction)
        if self._charge_mode != key:
            self._charge = 0.0
            self._charge_mode = key
        self._charge = min(
            cap,
            self._charge + self.config.charge_rate * cap * dt,
        )

    def _release_charge(self, torso, energy, mode, direction=0):
        if not self._matches_charge(mode, direction):
            self._reset_charge()
            return

        cap = self._charge_cap(energy)
        min_build = self.config.min_charge * cap
        if self._charge < min_build:
            self._reset_charge()
            return

        frac = self._charge / cap

        if mode == "horizontal":
            cost = self.config.move_cost * frac
            impulse = direction * self.config.horizontal_impulse * frac
            impulse_point = (impulse, 0)
        else:
            cost = self.config.jump_cost * frac
            impulse = -self.config.jump_impulse * frac
            impulse_point = (0, impulse)

        if energy is not None and not energy.can_spend(cost):
            self._reset_charge()
            return

        torso.apply_impulse_at_world_point(impulse_point, self._hip_point(torso))
        if energy is not None:
            energy.spend(cost)
        self._reset_charge()

    def _release_aim_charge(self, torso, energy, aim_x, aim_y):
        if not self._matches_charge("aim"):
            self._reset_charge()
            return

        cap = self._charge_cap(energy)
        min_build = self.config.min_charge * cap
        if self._charge < min_build:
            self._reset_charge()
            return

        hip = self._hip_point(torso)
        dx = aim_x - hip.x
        dy = aim_y - hip.y
        distance = math.hypot(dx, dy)
        if distance < self.config.aim_min_distance:
            self._reset_charge()
            return

        direction_x = dx / distance
        direction_y = dy / distance
        frac = self._charge / cap
        impulse_x = direction_x * self.config.horizontal_impulse * frac
        impulse_y = direction_y * self.config.jump_impulse * frac

        horizontal_weight = abs(direction_x)
        upward_weight = max(0.0, -direction_y)
        weight_sum = horizontal_weight + upward_weight
        if weight_sum < 0.001:
            cost = self.config.move_cost * frac
        else:
            cost = frac * (
                self.config.move_cost * horizontal_weight
                + self.config.jump_cost * upward_weight
            ) / weight_sum

        if energy is not None and not energy.can_spend(cost):
            self._reset_charge()
            return

        torso.apply_impulse_at_world_point(
            (impulse_x, impulse_y),
            hip,
        )
        if energy is not None:
            energy.spend(cost)
        self._reset_charge()

    def _decay_charge(self, dt, energy=None):
        if self._charge_mode is None:
            return
        cap = self._charge_cap(energy)
        self._charge = max(0.0, self._charge - self.config.charge_decay * cap * dt)
        if self._charge <= 0.0:
            self._reset_charge()

    def _apply_upright(self, torso, supported):
        if not supported:
            return
        torso.torque += (
            -torso.angle * self.config.upright_torque
            - torso.angular_velocity * self.config.upright_damping
        )

    def apply(self, torso, supported, dt, intent, energy=None, limbs=None, opponent_torso=None):
        if energy is not None:
            energy.regenerate(dt, supported)

        if not supported:
            self._reset_charge()
            self._apply_upright(torso, supported)
            return

        acted = False
        if intent.hold_aim:
            self._begin_charge(dt, "aim", energy=energy)
            acted = True
        if intent.hold_horizontal != 0:
            self._begin_charge(
                dt, "horizontal", intent.hold_horizontal, energy=energy
            )
            acted = True
        if intent.hold_jump:
            self._begin_charge(dt, "jump", energy=energy)
            acted = True

        if intent.release_aim:
            self._release_aim_charge(torso, energy, intent.aim_x, intent.aim_y)
            acted = True
        if intent.release_horizontal != 0:
            self._release_charge(torso, energy, "horizontal", intent.release_horizontal)
            acted = True
        if intent.release_jump:
            self._release_charge(torso, energy, "jump")
            acted = True

        if not acted:
            self._decay_charge(dt, energy)

        self._apply_upright(torso, supported)


def player_movement_config():
    return MovementConfig()


def enemy_movement_config():
    return MovementConfig(
        charge_rate=4.6,
        min_charge=0.07,
        horizontal_impulse=4400,
        jump_impulse=7000,
        upright_torque=19500,
        upright_damping=360,
        move_cost=18,
        jump_cost=24,
    )


def stand_torso_y(arena_height):
    return arena_height - 165
