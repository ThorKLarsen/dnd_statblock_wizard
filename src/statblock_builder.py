
class Statblock_builder(): 
    def __init__(self):
        pass

    def make_statblock(self, CR, **kwargs) -> Statblock:
        """Makes a Statblock object based losely on the DMG p.274 table. 


        Args:
            CR (Int): Challenge rating of the monster, this is required.
            kwargs  : Optional conditions for the monster. The other stats
                        will be adjusted to fit the CR.

        Returns:
            Statblock: A Statblock object of the created monster.
        """ 
    
    def PB_from_CR(self, CR):
        if CR < 5:
            return 2
        else:
            return (CR+7)//4
    def CR_from_PB(self, PB):



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


        

            