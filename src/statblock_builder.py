import random
import math

class Statblock_builder():
    def __init__(self, seed = None):
        pass

    def make_statblock(self, CR, offense_ratio=None, seed=None, **kwargs) -> Statblock:
        """Makes a Statblock object based losely on the DMG p.274 table. 


        Args:
            CR (Int): Challenge rating of the monster, this is required.
            kwargs  : Optional conditions for the monster. The other stats
                        will be adjusted to fit the CR.

        Returns:
            Statblock: A Statblock object of the created monster.
        """ 
        random.seed(seed)
        stats = kwargs

        OCR, DCR = self.get_offensive_defensive_CR(CR, offense_ratio)
        HP, AC = self.get_defensive_stats(DCR)
        tohit, damage, DC = self.get_offensive_stats(OCR)

        stats['HP'] = HP
        stats['AC'] = AC
        stats['tohit'] = tohit
        stats['damage'] = damage
        stats['DC'] = DC



    def get_offensive_defensive_CR(self, CR, offense_ratio):
        if offense_ratio is None:
            offense_ratio = random.random/2 + 0.5
        return (CR * (1 + offense_ratio), CR * (1-offense_ratio))

    def PB_from_CR(self, CR):
        if CR < 5:
            return 2
        else:
            return (CR+7)//4
        
    def CR_from_PB(self, PB):
        return PB * 4 - 6
    
    def HP_from_CR(self, CR):
        return 10 + 15*CR

    def CR_from_HP(self, HP):
        return (HP - 10)/15
    
    def AC_from_CR(self, CR):
        if CR < 0.5:
            return 12
        elif CR <= 1:
            return 13
        else:
            return 13 + 0.35*CR

    def CR_from_AC(self, AC):
        if AC <= 12:
            return 0.25
        else:
            return (AC-12.5) * 3

    def defensive_CR(self, HP, AC, VRI_score):
        """Computes CR based on only the defensiv stats of the monster.
        The exact values are based on a reggression analysis of official
        DnD 5 monsters.

        Args:
            HP (Float): HP of the monster
            AC (Float): AC of the monster
            VRI_score (Float): A score based on the amount of vulnerabilites
                            resistances and immunities the monster has. Each
                            point equals 1% more expected damage taken.

        Returns:
            CR (Float): Defensive CR of the monster
        """
        b = -3.65
        a = [0.05376286 0.30206772]
        CR = b + HP * a[0] * (1 + VRI_score/100) + AC * a[1]
        return CR

    def get_defensive_stats(self, CR, HP=None, AC=None):
        if AC is None and HP is None:
            a = random.random()
            b = 1-a
            HP_ratio = 1 + (0.5-a)*0.8
            AC_ratio = 1 + (0.5-b)*0.8

            res = (
                self.HP_from_CR(CR * HP_ratio),
                self.AC_from_CR(CR * AC_ratio),
            )
        elif AC is None:
            CR_AC = self.CR
        return res

    def CR_from_tohit(self, tohit):
        if tohit >= 5:
            CR = (tohit-1)/2
        else:
            CR = 0.00335 * math.e**(1.33*x)
        return CR

    def CR_from_damage(self, damage):
        if damage >= 10:
            CR = (damage-1)/5
        else:
            CR = 0.043 * math.e**(0.32*x)
        return CR

    def CR_from_strong_DC(self, strong_DC):
        return self.CR_from_tohit(strong_DC-7)

    def offensive_CR(self, tohit, damage, strong_DC=None, DC_ratio=0.25):
        """Compute CR based only on the monsters offensive stats.

        Args:
            tohit (float): The monsters tohit stat (i.e. the bonus to attack rolls)
            damage (float): The monsters average damage per round assuming the attack, spell or ability hits.
            strong_DC (float, optional): The monsters save DC for spells or abilities, if any. Defaults to None.
            DC_ratio (float, optional): The ratio of damage the monster is expected to do from saving throws, and not attacks. Defaults to 0.25.

        Returns:
            float: Offensive CR
        """
        CR_tohit = self.CR_from_tohit(tohit)
        CR_damage = self.CR_from_damage(damage)

        CR_avg = (CR_damage + CR_tohit)/2

        if strong_DC:
            CR_strong_DC = self.CR_from_strong_DC(strong_DC)
            CR_avg = CR_avg*(1-DC_ratio) + CR_strong_DC*DC_ratio

        return CR_avg

    def get_offensive_stats(self, CR, DC_ratio=0.25) -> tuple[float, float, float]:
        """Computes the offensive stats of a monster based on CR

        Args:
            CR (float): CR of the monster
            DC_ratio (float, optional): Ratio of DC to attack. Defaults to 0.25.

        Returns:
            (tohit, damage, strongDC): Tuple of offensive stats
        """
        a = random.random()
        b = 1-a
        tohit_ratio = 1 + (0.5-a)*0.8
        damage_ratio = 1 + (0.5-b)*0.8

        res = (
            self.tohit_from_CR(CR * tohit_ratio),
            self.damage_from_CR(CR * damage_ratio),
            self.strong_DC_from_CR(CR * tohit_ratio * DC_ratio),
        )
        return res

    def tohit_from_CR(self, CR):
        if CR >= 1:
            return (CR + 7)/2
        else:
            return 0.75 * math.log(300*CR)
    
    def damage_from_CR(self, CR):
        if >= 1:
            return (CR+1)*5
        else:
            return 3.125 * math.log(23.3 * CR)
    
    def strong_DC_from_CR(self, CR):
        return self.tohit_from_CR(CR)+7

        

class Statblock():
    num_attributes = (
        'CR',
        'AC',
        'HP_max',
        'Speed',
        'Str',
        'Dex',
        'Con',
        'Int',
        'Wis',
        'Cha',
        'PB',        
    )
    str_attributes = (
        'Name',
        'Type',
        'Alignment',

    )
    skills = (
        'Athletics',
        'Acrobatics',
        'Sleight of Hand',
        'Stealth',
        'Arcana',
        'History',
        'Investigation',
        'Nature',
        'Religion',
        'Animal Handling',
        'Insight',
        'Medicine',
        'Perception',
        'Survival',
        'Deception',
        'Intimidation',
        'Performance',
        'Persuasion',
    )

    def __init__(self, **kwargs):
        self.attributes = {}
        self.proficiencies = []
        self.actions = []
        self.abilities = []
        self.spellcasting = None
        self.senses = []


        # Unpack kewword arguments
        for k, v in kwargs:
            if k in Statblock.num_attributes:
                self.attributes[k] = v
            elif k == 'actions':
                self.actions = v
            elif k == 'abilities':
                self.abilities = v
            elif k == 'spellcasting':
                self.spellcasting = v
            elif k == 'skills':
                self.proficiencies = v
            elif k == 'senses':
                self.senses = v


    def __index__(self, name):
        try:
            return self.attributes[name]
        except:
            raise AttributeError(self + ' does not have attribute ' + name)

    def is_proficient(self, skill):
        return skill in self.proficiencies

    def get_basic_attack(self):
        return self.actions[0]


        

            