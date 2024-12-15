import random

class Statblock_builder():
    def __init__(self, seed = None):
        pass

    def make_statblock(self, CR, offense_ratio=None, seed=None **kwargs) -> Statblock:
        """Makes a Statblock object based losely on the DMG p.274 table. 


        Args:
            CR (Int): Challenge rating of the monster, this is required.
            kwargs  : Optional conditions for the monster. The other stats
                        will be adjusted to fit the CR.

        Returns:
            Statblock: A Statblock object of the created monster.
        """ 
        random.seed(seed)

        OCR, DCR = self.get_offensive_defensive_CR(CR, offense_ratio)

    def get_offensive_defensive_CR(self, CR, offense_ratio)
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


        

            