import random
import math
import enum

from damage_types import *

class StatblockBuilder():
    """Class to build Statblock instances

    """    
    core_stat_names = ['CR', 'Hp', 'AC', 'tohit', 'damage', 'strong_DC']

    def __init__(self, seed = None):
        pass

    def make_statblock_basic(self, CR, stats=dict(), offense_ratio=None, seed=None):
        """Makes a Statblock object based losely on the DMG p.274 table. 


        Args:
            CR (Int): Challenge rating of the monster, this is required.
            kwargs  : Optional conditions for the monster. The other stats
                        will be adjusted to fit the CR.

        Returns:
            Statblock: A Statblock object of the created monster.
        """ 
        random.seed(seed)

        for stat_name in StatblockBuilder.core_stat_names:
            stats.setdefault(stat_name, None)

        OCR, DCR = self.get_offensive_defensive_CR(CR, offense_ratio)
        HP, AC = self.get_defensive_stats(DCR, HP=stats['HP'], AC=stats['AC'])
        tohit, damage, DC = self.get_offensive_stats(OCR, tohit=stats['tohit'], damage=stats['damage'], strong_DC=stats['strong_DC'])

        stats['HP'] = HP
        stats['AC'] = AC
        stats['tohit'] = tohit
        stats['damage'] = damage
        stats['DC'] = DC

        damage_type = DamageType.BLUDGEONING
        attack = self.make_attack('Slam', damage_type, tohit, damage)
        stats['actions'] = [attack]
        stats['basic_attack'] = attack

        statblock = Statblock(stats=stats)

        return statblock

    def make_attack(self, name, damage_type, tohit, damage_target, die_size = None, n_attacks=None):
        if die_size is None:
            die_size = random.choice((4,6,8,12))
            if damage_target > 50 and die_size == 4:
                die_size = 8
        
        assert die_size in [1,2,4,6,8,12,20]
        die_avg_damage = die_size//2 + 0.5
        if n_attacks is None:
            n_dice = damage_target//die_avg_damage
            if n_dice > 8:
                n_attacks = math.ceil(n_dice/8)
                n_dice = (damage_target/n_attacks)//die_avg_damage
            else:
                n_attacks = 1
        else:
            n_dice = (damage_target/n_attacks)//die_avg_damage
        modifier = round(damage_target/n_attacks - n_dice*die_avg_damage)
        return Attack(name, tohit, n_dice, die_size, modifier, damage_type, n_attacks)

    def get_offensive_defensive_CR(self, CR, offense_ratio=None):
        """Splits CR in offensiveCR and defensiveCR based on some ratio

        Args:
            CR (float): challenge rating of the monster
            offense_ratio (float): number between 0 and 1.

        Returns:
            (OCR, DCF): Tuple of offensiveCR and defensiveCR
        """
        if offense_ratio is None:
            offense_ratio = random.random()/2 + 0.5
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
        a = [0.05376286, 0.30206772]
        CR = b + HP * a[0] * (1 + VRI_score/100) + AC * a[1]
        return CR

    def get_defensive_stats(self, CR, HP=None, AC=None, HP_to_AC_ratio=0.5, random_interval=0):
        """Computes defensive stats of the monster based in CR.

        Args:
            CR (float): CR  of the monster
            HP (float, optional): HP of the monster. Defaults to None.
            AC (float, optional): AC of the monster. Defaults to None.
            HP_to_AC_ratio (float, optional): Base ratio of the CR-budget that 
                                            will be used on HP as opposed to AC. 
                                            This is only used if no HP or AC are 
                                            given Defaults to 0.5.
            random_interval (float, optional): Determines how far the CR-budget is 
                                            allowed to randomly deviate. At one the 
                                            whole budget can randomly be used on 
                                            either AC or HP. At zero, there is
                                            no random deviating. Defaults to 0.

        Returns:
            (HP, AC): HP and AC that correspands to the given CR. If either or both 
            were given as arguments, they are passed back here.
        """
        if AC is None and HP is None:
            if random_interval:
                a = (random.random() - 0.5)*random_interval
                b = random_interval - a
            else:
                a, b = 0, 0
            HP_modifier = 2 * HP_to_AC_ratio     + a
            AC_modifier = 2 * (1-HP_to_AC_ratio) + b

            HP = self.HP_from_CR(CR * HP_modifier)
            AC = self.AC_from_CR(CR * AC_modifier)
        elif AC is None:
            CR_AC = self.CR_from_AC(AC)
            CR_HP = 2*CR - CR_AC

            HP = self.HP_from_CR(CR_HP)
        elif HP is None:
            CR_HP = self.CR_from_HP(HP)
            CR_AC = 2*CR - CR_HP

            AC = self.AC_from_CR(AC)
        
        return (HP, AC)

    def CR_from_tohit(self, tohit):
        if tohit >= 5:
            CR = (tohit-1)/2
        else:
            CR = 0.00335 * math.e**(1.33*tohit)
        return CR

    def CR_from_damage(self, damage):
        if damage >= 10:
            CR = (damage-1)/5
        else:
            CR = 0.043 * math.e**(0.32*damage)
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

    def get_offensive_stats(self, CR, tohit=None, damage=None, strong_DC=None, DC_ratio=0.25) -> tuple[float, float, float]:
        """Computes the offensive stats of a monster based on CR

        Args:
            CR (float): CR of the monster
            DC_ratio (float, optional): Ratio of DC to attack. Defaults to 0.25.

        Returns:
            (tohit, damage, strongDC): Tuple of offensive stats
        """
        if tohit is None and damage is None:
            a = random.random()
            b = 1-a
            tohit_ratio = 1 + (0.5-a)*0.8
            damage_ratio = 1 + (0.5-b)*0.8

            tohit = self.tohit_from_CR(CR * tohit_ratio)
            damage = self.damage_from_CR(CR * damage_ratio)
            strong_DC = self.strong_DC_from_CR(CR * tohit_ratio * DC_ratio)
        elif tohit is None:
            CR_tohit = self.CR_from_tohit(tohit)
            CR_damage = 2*CR - CR_tohit

            damage = self.damage_from_CR(CR_damage)
        elif damage is None:
            CR_damage = self.CR_from_damage(CR_damage)
            CR_tohit = 2*CR - CR_damage

            tohit = self.tohit_from_CR(CR_tohit)

        if strong_DC is None:
            strong_DC = self.strong_DC_from_CR(CR * tohit_ratio * DC_ratio)

        return tohit, damage, strong_DC

    def tohit_from_CR(self, CR):
        if CR >= 1:
            return (CR + 7)/2
        else:
            return 0.75 * math.log(300*CR)
    
    def damage_from_CR(self, CR):
        if CR >= 1:
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

    def __init__(self, stats):
        self.attributes = {}
        self.proficiencies = []
        self.actions = []
        self.abilities = []
        self.spellcasting = None
        self.senses = []
        self.basic_attack = None

        # Unpack kewword arguments
        for k, v in stats:
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
            elif k == 'basic_attack':
                self.basic_attack = v


    def __getitem__(self, key):
        try:
            return self.attributes[key]
        except:
            raise AttributeError(self + ' does not have attribute ' + key)

    def is_proficient(self, skill):
        return skill in self.proficiencies

    def get_basic_attack(self):
        if self.basic_attack:
            return self.basic_attack
        if isinstance(self.actions[0], Attack):
            return self.actions[0]
    
    def format_number(self, n, length, is_integer=True, fail_case='?') -> str:
        """Format number into a string of the appropriate length or shorter

        Args:
            n (int or float): The number to be formatted
            length (int): The max length of the returned string
            is_integer (bool, optional): Whether n should be treate as in int or float. Defaults to True.
            fail_case (str, optional): returned string if formatting is nor possible.. Defaults to '?'.

        Returns:
            str: The formatted number
        """
        n = str(n)
        if is_integer:
            if len(n) <= length:
                return n
            else:
                if len(n)-2 <= length:
                    return n[:-3] + 'k'
                else:
                    if len(fail_case) <= length:
                        return fail_case
                    else:
                        return '?'
        else:
            return fail_case

    def format(self, style='compact'):
        res = ''
        if style == 'compact':
            HP_max = self.attributes.get('HP_max', 0)
            HP_cur = self.attributes.get('HP_cur', 0)
            HP_max = self.format_number(HP_max, 4)
            HP_cur = self.format_number(HP_cur, 4)

            AC = self.attributes.get('AC', 10)
            AC = self.format_number(AC, 2)

            speed = self.attributes.get('Speed', 0)
            speed = self.format_number(speed, 2)

            strong_DC = self.attributes.get('strong_DC', 10)
            strong_DC = self.format_number(strong_DC, 2)

            weak_DC = self.attributes.get('weak_DC', 10)
            weak_DC = self.format_number(weak_DC, 2)

            ba = self.get_basic_attack()
            n_attacks = self.format_number(ba.n_attacks, 1)
            tohit = self.format_number(ba.tohit, 1)
            n_dice = self.format_number(ba.n_dice, 1)
            die_value = self.format_number(ba.die_value, 1)
            damage_modifier = self.format_number(ba.damage_modifier, 1)

            damage_type = ba.damage_type.abbr

            res += '+============+\n'
            res += '|HP {0:>4s}/{1:>4s}|\n'.format(HP_cur, HP_max)
            res += '|AC {0:>2s}|Spd {1:>2s}|\n'.format(AC, speed)
            res += '|Saves: {0:>2s}/{1:>2s}|\n'.format(strong_DC, weak_DC)
            res += '+============+\n'
            res += '|Atk: {0:1s}x {1:^4s}|\n'.format(n_attacks, damage_type)
            res += '|+{0:<2s}→{1:>2s}d{2:<2s}+{3:<2s}|\n'.format(tohit, n_dice, die_value, damage_modifier)
            res += '+============+'
            # Example:
            # '+============+'
            # '|HP  123/ 200|'
            # '|AC 13|Spd 30|'
            # '|Saves: 12/16|'
            # '+============+'
            # '|Atk: 2x Piec|'
            # '|+6 → 2d6 +3 |'
            # '+============+'
        
        return res

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