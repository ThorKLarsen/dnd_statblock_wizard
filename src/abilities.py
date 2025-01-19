class Ability:
    """Base class for all abilities
    """
    def __init__(self, name):
        self.name = name

class Attack(Ability):
    """Class to hold an attack ability
    """
    def __init__(self, name, tohit, n_dice, die_size, modifier, damage_type, n_attacks=1):
        super().__init__(name)

        self.tohit = tohit
        self.n_dice = n_dice
        self.die_size = die_size
        self.modifier = modifier
        self.damage_type = damage_type
        self.n_attacks = n_attacks

    def get_avg_damage(self):
        return self.n_attacks * (self.n_dice * (self.die_size/2 + 0.5) + self.modifier)