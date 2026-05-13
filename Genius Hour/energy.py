class EnergyPool:
    def __init__(
        self,
        max_energy,
        regen_ground,
        regen_air,
        move_drain,
        jump_cost,
    ):
        self.max_energy = max_energy
        self.current = max_energy
        self.regen_ground = regen_ground
        self.regen_air = regen_air
        self.move_drain = move_drain
        self.jump_cost = jump_cost

    def ratio(self):
        if self.max_energy <= 0:
            return 0.0
        return max(0.0, min(1.0, self.current / self.max_energy))

    def regenerate(self, dt, grounded):
        rate = self.regen_ground if grounded else self.regen_air
        self.current = min(self.max_energy, self.current + rate * dt)

    def can_spend(self, amount):
        return self.current >= amount

    def spend(self, amount):
        if not self.can_spend(amount):
            return False
        self.current -= amount
        return True
