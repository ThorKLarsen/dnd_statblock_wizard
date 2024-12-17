"""Damage type enum
"""
from enum import Enum

class DamageType(Enum):
    """Enum for the damage types of 5e
    """
    ACID        = 'Acd'
    BLUDGEONING= 'Bld'
    COLD        = 'Cld'
    FIRE        = 'Fir'
    FORCE       = 'Frc'
    LIGHTNING   = 'Lgt'
    NECROTIC    = 'Ncr'
    PIERCING    = 'Prc'
    POISON      = 'Psn'
    PSYCHIC     = 'Psy'
    RADIANT     = 'Rad'
    SLASHING    = 'Sla'
    THUNDER     = 'Thd'

    def __init__(self, abbr):
        super().__init__()
        self.abbr = abbr
