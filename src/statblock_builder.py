"""Contains StatblockBuilder and Statblock classes
"""
import random
import math

from damage_types import DamageType

class StatblockBuilder():
    """Class to build Statblock instances

    """    
    core_stat_names = ['cr', 'hp', 'ac', 'tohit', 'damage', 'save_DC', 'strong_save', 'weak_save']

    def __init__(self, seed = None):
        pass

    def make_statblock_basic(self, cr, stats=None, offense_ratio=None, seed=None):
        """Makes a Statblock object based losely on the DMG p.274 table. 


        Args:
            cr (Int): Challenge rating of the monster, this is required.
            kwargs  : Optional conditions for the monster. The other stats
                        will be adjusted to fit the cr.

        Returns:
            Statblock: A Statblock object of the created monster.
        """ 
        random.seed(seed)

        if stats is None:
            stats = dict()

        for stat_name in StatblockBuilder.core_stat_names:
            stats.setdefault(stat_name, None)

        Ocr, Dcr = self.get_offensive_defensive_cr(cr, offense_ratio)
        hp, ac, strong_save, weak_save = self.get_defensive_stats(Dcr, hp=stats['hp'], ac=stats['ac'])
        tohit, damage, save_DC = self.get_offensive_stats(Ocr, tohit=stats['tohit'], damage=stats['damage'], save_DC=stats['save_DC'])

        stats['cr'] = cr
        stats['hp_max'] = round(hp)
        stats['hp_cur'] = round(hp)
        stats['ac'] = round(ac)
        stats['tohit'] = round(tohit)
        stats['damage'] = round(damage)
        stats['save_DC'] = round(save_DC)
        stats['strong_save'] = round(strong_save)
        stats['weak_save'] = round(weak_save)

        stats['Speed'] = 30

        damage_type = DamageType.BLUDGEONING
        attack = self.make_attack('Slam', damage_type, round(tohit), round(damage))
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

    def get_offensive_defensive_cr(self, cr, offense_ratio=None):
        """Splits cr in offensivecr and defensivecr based on some ratio

        Args:
            cr (float): challenge rating of the monster
            offense_ratio (float): number between 0 and 1.

        Returns:
            (Ocr, DCF): Tuple of offensivecr and defensivecr
        """
        if offense_ratio is None:
            offense_ratio = random.random()/2 + 0.5
        return (cr * (1 + offense_ratio), cr * (1-offense_ratio))

    def PB_from_cr(self, cr):
        if cr < 5:
            return 2
        else:
            return (cr+7)//4
        
    def cr_from_PB(self, PB):
        return PB * 4 - 6
    
    def hp_from_cr(self, cr):
        return 10 + 15*cr

    def cr_from_hp(self, hp):
        return (hp - 10)/15
    
    def ac_from_cr(self, cr):
        if cr < 0.5:
            return 12
        elif cr <= 1:
            return 13
        else:
            return 13 + 0.35*cr

    def cr_from_ac(self, ac):
        if ac <= 12:
            return 0.25
        else:
            return (ac-12.5) * 3

    def defensive_cr(self, hp, ac, VRI_score):
        """Computes cr based on only the defensiv stats of the monster.
        The exact values are based on a reggression analysis of official
        DnD 5 monsters.

        Args:
            hp (Float): hp of the monster
            ac (Float): ac of the monster
            VRI_score (Float): A score based on the amount of vulnerabilites
                            resistances and immunities the monster has. Each
                            point equals 1% more expected damage taken.

        Returns:
            cr (Float): Defensive cr of the monster
        """
        b = -3.65
        a = [0.05376286, 0.30206772]
        cr = b + hp * a[0] * (1 + VRI_score/100) + ac * a[1]
        return cr

    def get_defensive_stats(self, cr, hp=None, ac=None, hp_to_ac_ratio=0.5, random_interval=0):
        """Computes defensive stats of the monster based in cr.

        Args:
            cr (float): cr  of the monster
            hp (float, optional): hp of the monster. Defaults to None.
            ac (float, optional): ac of the monster. Defaults to None.
            hp_to_ac_ratio (float, optional): Base ratio of the cr-budget that 
                                            will be used on hp as opposed to ac. 
                                            This is only used if no hp or ac are 
                                            given Defaults to 0.5.
            random_interval (float, optional): Determines how far the cr-budget is 
                                            allowed to randomly deviate. At one the 
                                            whole budget can randomly be used on 
                                            either ac or hp. At zero, there is
                                            no random deviating. Defaults to 0.

        Returns:
            (hp, ac): hp and ac that correspands to the given cr. If either or both 
            were given as arguments, they are passed back here.
        """
        if ac is None and hp is None:
            if random_interval:
                a = (random.random() - 0.5)*random_interval
                b = random_interval - a
            else:
                a, b = 0, 0
            hp_modifier = 2 * hp_to_ac_ratio     + a
            ac_modifier = 2 * (1-hp_to_ac_ratio) + b

            hp = self.hp_from_cr(cr * hp_modifier)
            ac = self.ac_from_cr(cr * ac_modifier)
        elif ac is None:
            cr_ac = self.cr_from_ac(ac)
            cr_hp = 2*cr - cr_ac

            hp = self.hp_from_cr(cr_hp)
        elif hp is None:
            cr_hp = self.cr_from_hp(hp)
            cr_ac = 2*cr - cr_hp

            ac = self.ac_from_cr(ac)
        
        strong_save = self.strong_save_from_cr(cr)

        if cr <= 2:
            weak_save = 10
        elif cr <= 8:
            weak_save = 12
        else:
            weak_save = 13
        
        return hp, ac, strong_save, weak_save

    def cr_from_tohit(self, tohit):
        if tohit >= 5:
            cr = (tohit-1)/2
        else:
            cr = 0.00335 * math.e**(1.33*tohit)
        return cr

    def cr_from_damage(self, damage):
        if damage >= 10:
            cr = (damage-1)/5
        else:
            cr = 0.043 * math.e**(0.32*damage)
        return cr

    def cr_from_strong_save(self, strong_save):
        return self.cr_from_tohit(strong_save-7)

    def offensive_cr(self, tohit, damage, strong_save=None, save_att_ratio=0.25):
        """Compute cr based only on the monsters offensive stats.

        Args:
            tohit (float): The monsters tohit stat (i.e. the bonus to attack rolls)
            damage (float): The monsters average damage per round assuming the attack, spell or ability hits.
            strong_save (float, optional): The monsters save DC for spells or abilities, if any. Defaults to None.
            save_att_ratio (float, optional): The ratio of damage the monster is expected to do from saving throws, and not attacks. Defaults to 0.25.

        Returns:
            float: Offensive cr
        """
        cr_tohit = self.cr_from_tohit(tohit)
        cr_damage = self.cr_from_damage(damage)

        cr_avg = (cr_damage + cr_tohit)/2

        if strong_save:
            cr_strong_save = self.cr_from_strong_save(strong_save)
            cr_avg = cr_avg*(1-save_att_ratio) + cr_strong_save*save_att_ratio

        return cr_avg

    def get_offensive_stats(self, cr, tohit=None, damage=None, save_DC=None, save_att_ratio=0.25) -> tuple[float, float, float]:
        """Computes the offensive stats of a monster based on cr

        Args:
            cr (float): cr of the monster
            save_att_ratio (float, optional): Ratio of DC to attack. Defaults to 0.25.

        Returns:
            (tohit, damage, save_DC): Tuple of offensive stats
        """
        if tohit is None and damage is None:
            a = random.random()
            b = 1-a
            tohit_ratio = 1 + (0.5-a)*0.8
            damage_ratio = 1 + (0.5-b)*0.8

            tohit = self.tohit_from_cr(cr * tohit_ratio)
            damage = self.damage_from_cr(cr * damage_ratio)
        elif tohit is None:
            cr_tohit = self.cr_from_tohit(tohit)
            cr_damage = 2*cr - cr_tohit

            damage = self.damage_from_cr(cr_damage)
        elif damage is None:
            cr_damage = self.cr_from_damage(cr_damage)
            cr_tohit = 2*cr - cr_damage

            tohit = self.tohit_from_cr(cr_tohit)

        if save_DC is None:
            save_DC = self.save_DC_from_cr(cr * tohit_ratio * save_att_ratio)

        return tohit, damage, save_DC

    def tohit_from_cr(self, cr):
        if cr >= 1:
            return (cr + 7)/2
        else:
            return 0.75 * math.log(300*cr)
    
    def damage_from_cr(self, cr):
        if cr >= 1:
            return (cr+1)*5
        else:
            return 3.125 * math.log(23.3 * cr)
    
    def save_DC_from_cr(self, cr):
        return self.tohit_from_cr(cr)+7
    
    def strong_save_from_cr(self, cr):
        return self.ac_from_cr(cr) -1

class Statblock():
    num_attributes = (
        'cr',
        'ac',
        'hp_max',
        'hp_cur',
        'Speed',
        'Str',
        'Dex',
        'Con',
        'Int',
        'Wis',
        'Cha',
        'PB',
        'save_DC',
        'strong_save',
        'weak_save'
    )
    str_attributes = (
        'Name',
        'Type',
        'Alignment',

    )
    skills = (
        'Athletics',
        'acrobatics',
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
        for k, v in stats.items():
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
        if key in self.attributes:
            return self.attributes[key]
        else:
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
            hp_max = self.attributes.get('hp_max', 0)
            hp_cur = self.attributes.get('hp_cur', 0)
            hp_max = self.format_number(hp_max, 4)
            hp_cur = self.format_number(hp_cur, 4)

            ac = self.attributes.get('ac', 10)
            ac = self.format_number(ac, 2)

            speed = self.attributes.get('Speed', 0)
            speed = self.format_number(speed, 2)

            strong_save = self.attributes.get('strong_save', 10)
            strong_save = self.format_number(strong_save, 2)

            weak_DC = self.attributes.get('weak_DC', 10)
            weak_DC = self.format_number(weak_DC, 2)

            ba = self.get_basic_attack()
            n_attacks = self.format_number(ba.n_attacks, 1)
            tohit = self.format_number(ba.tohit, 1)
            n_dice = self.format_number(ba.n_dice, 1)
            die_size = self.format_number(ba.die_size, 1)
            damage_modifier = self.format_number(ba.modifier, 1)

            damage_type = ba.damage_type.abbr

            res += '+============+\n'
            res += '|hp {0:>4s}/{1:>4s}|\n'.format(hp_cur, hp_max)
            res += '|ac {0:>2s}|Spd {1:>2s}|\n'.format(ac, speed)
            res += '|Saves: {0:>2s}/{1:>2s}|\n'.format(strong_save, weak_DC)
            res += '+============+\n'
            res += '|Atk: {0:1s}x {1:^4s}|\n'.format(n_attacks, damage_type)
            res += '|+{0:<2s}→{1:>2s}d{2:<2s}+{3:<2s}|\n'.format(tohit, n_dice, die_size, damage_modifier)
            res += '+============+'
            # Example:
            # '+============+'
            # '|hp  123/ 200|'
            # '|ac 13|Spd 30|'
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