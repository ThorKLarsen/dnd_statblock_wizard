from abilities import Attack, Ability

class Statblock():
    num_attributes = (
        'cr',
        'ac',
        'hp_max',
        'hp_cur',
        'speed',
        'Str',
        'Dex',
        'Con',
        'Int',
        'Wis',
        'Cha',
        'pb',
        'save_dc',
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
        """Returns a formatted string of the statblock.
        Supported styles are:
        * compact - Displays on the minimum information to run the monsters.

        Args:
            style (str, optional): Display style. Defaults to 'compact'.

        Returns:
            str: Statblock string
        """
        res = ''
        if style == 'compact':
            hp_max = self.attributes.get('hp_max', 0)
            hp_cur = self.attributes.get('hp_cur', 0)
            hp_max = self.format_number(hp_max, 4)
            hp_cur = self.format_number(hp_cur, 4)

            ac = self.attributes.get('ac', 10)
            ac = self.format_number(ac, 2)

            speed = self.attributes.get('speed', 0)
            speed = self.format_number(speed, 2)

            strong_save = self.attributes.get('strong_save', 10)
            strong_save = self.format_number(strong_save, 2)

            weak_save = self.attributes.get('weak_save', 10)
            weak_save = self.format_number(weak_save, 2)

            ba = self.get_basic_attack()
            n_attacks = self.format_number(ba.n_attacks, 1)
            tohit = self.format_number(ba.tohit, 2)
            n_dice = self.format_number(ba.n_dice, 2)
            die_size = self.format_number(ba.die_size, 2)
            damage_modifier = self.format_number(ba.modifier, 2)
            
            damage_type = ba.damage_type.abbr

            res += '+============+\n'
            res += '|hp {0:>4s}/{1:>4s}|\n'.format(hp_cur, hp_max)
            res += '|ac {0:>2s}|Spd {1:>2s}|\n'.format(ac, speed)
            res += '|Sav. +{0:<2s}/+{1:<2s}|\n'.format(strong_save, weak_save)
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