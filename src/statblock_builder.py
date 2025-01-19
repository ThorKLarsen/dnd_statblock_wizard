"""Contains StatblockBuilder and Statblock classes
"""
import random
import math

from scipy import optimize

from damage_types import DamageType
from statblock import Statblock
from abilities import Attack

class StatblockBuilder():
    """Class to build Statblock instances
    """
    core_stat_names = ['cr', 'hp', 'ac', 'tohit', 'damage', 'save_dc', 'strong_save', 'weak_save']

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

        off_cr, def_cr = self.split_cr(cr, offense_ratio)
        hp, ac, strong_save, weak_save = self.get_defensive_stats(def_cr, hp=stats['hp'], ac=stats['ac'])
        tohit, damage, save_dc = self.get_offensive_stats(off_cr, tohit=stats['tohit'], damage=stats['damage'], save_dc=stats['save_dc'])

        stats['cr'] = cr
        stats['hp_max'] = round(hp)
        stats['hp_cur'] = round(hp)
        stats['ac'] = round(ac)
        stats['tohit'] = round(tohit)
        stats['damage'] = round(damage)
        stats['save_dc'] = round(save_dc)
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
        """Makes an Attack object based on the given arguments.
        Die size (e.i. d4, d6, etc.) and number of attacks can be fixed.
        The other attrubutes will be computed from 'damage_target'.
        The to hit bonus is not factored into any damage calculations.

        Args:
            name (string): Name of the attack 'Slam, Longsword, Firebolt, etc.
            damage_type (enum): The damage type of the attack. Should be an instance of DamageTypes. 
            tohit (int): To hit bonus of the attack.
            damage_target (float): The damage of the attack assuming it hits.
            die_size (int, optional): The die size used, i.e. d4, d6, etc. Defaults to None.
            n_attacks (int, optional): Number of attacks. Defaults to None.

        Returns:
            attack: Attack object with apprx. the desired damage.
        """
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
        n_dice = round(n_dice)
        modifier = round(damage_target/n_attacks - n_dice*die_avg_damage)
        return Attack(name, tohit, n_dice, die_size, modifier, damage_type, n_attacks)

    def split_cr(self, cr, offense_ratio=None):
        """Splits cr in offensive_cr and defensive_cr based on some ratio

        Args:
            cr (float): challenge rating of the monster
            offense_ratio (float): number between 0 and 1.

        Returns:
            (off_cr, def_cr): Tuple of offensive_cr and defensive_cr
        """
        if offense_ratio is None:
            offense_ratio = random.random()/2 - 0.5
        return (cr * (1 + offense_ratio), cr * (1-offense_ratio))

    def defensive_cr(self, hp, ac, vri_score):
        """Computes cr based on only the defensiv stats of the monster.
        The exact values are based on a reggression analysis of official
        DnD 5 monsters.

        Args:
            hp (Float): hp of the monster
            ac (Float): ac of the monster
            vri_score (Float): A score based on the amount of vulnerabilites
                            resistances and immunities the monster has. Each
                            point equals 1% more expected damage taken.

        Returns:
            cr (Float): Defensive cr of the monster
        """
        b = -3.65
        a = [0.05376286, 0.30206772]
        cr = b + hp * a[0] * (1 + vri_score/100) + ac * a[1]
        return cr

    def get_defensive_stats(
            self,
            cr,
            hp=None,
            ac=None,
            hp_to_ac_ratio=0.5,
            random_interval=0.2
        ):
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
        elif hp is None:
            cr_ac = self.cr_from_ac(ac)
            cr_hp = 2*cr - cr_ac

            hp = self.hp_from_cr(cr_hp)
        elif ac is None:
            cr_hp = self.cr_from_hp(hp)
            cr_ac = 2*cr - cr_hp

            ac = self.ac_from_cr(cr_ac)
        
        strong_save = self.strong_save_from_cr(cr)

        if cr <= 2:
            weak_save = 0
        elif cr <= 8:
            weak_save = 2
        else:
            weak_save = 3
        
        return hp, ac, strong_save, weak_save

    def offensive_cr(self, tohit, damage, strong_save=None, save_att_ratio=0.25):
        """Compute cr based only on the monsters offensive stats.

        Args:
            tohit (float): The monsters tohit stat (i.e. the bonus to attack rolls)
            damage (float): The monsters average damage per round assuming the attack, 
                            spell or ability hits.
            strong_save (float, optional): The monsters save dc for spells or abilities, 
                            if any. Defaults to None.
            save_att_ratio (float, optional): The ratio of damage the monster is expected 
                            to do from saving throws, and not attacks. Defaults to 0.25.

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

    def get_offensive_stats(
            self,
            cr,
            tohit=None,
            damage=None,
            save_dc=None,
            save_att_ratio=0.25
        ) -> tuple[float, float, float]:
        """Computes the offensive stats of a monster based on cr

        Args:
            cr (float): cr of the monster
            save_att_ratio (float, optional): Ratio of dc to attack. Defaults to 0.25.

        Returns:
            (tohit, damage, save_dc): Tuple of offensive stats
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

        if save_dc is None:
            save_dc = self.save_dc_from_cr(cr * tohit_ratio * save_att_ratio)

        return tohit, damage, save_dc
    
    #region cr_from_x
    def cr_from_pb(self, pb):
        """Challenge rating computed from proficiency bonus

        Args:
            pb (float): proficiency bonus

        Returns:
            float: Challenge rating
        """
        return pb * 4 - 6

    def cr_from_hp(self, hp):
        """Challenge rating computed from HP

        Args:
            hp (float): health points

        Returns:
            float: challenge rating
        """
        return (hp - 10)/15

    def cr_from_ac(self, ac):
        """Challeneg rating from armor class

        Args:
            ac (float): armor class

        Returns:
            float: challeneg rating
        """
        if ac <= 12:
            return 0.25
        else:
            return (ac-12.5) * 3

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
    
    def cr_from_save_dc(self, save_dc):
        return self.cr_from_ac(save_dc+2)
    #endregion

    #region x_from_cr
    def pb_from_cr(self, cr):
        """Proficiency bonus computed from CR

        Args:
            cr (float): Challnenge rating of the monster

        Returns:
            float: proficiency bonus
        """
        if cr < 5:
            return 2
        else:
            return (cr+7)/4

    def hp_from_cr(self, cr):
        """HP computed from challenge rating

        Args:
            cr (float): challenge rating

        Returns:
            float: HP of the monster
        """
        return 10 + 15*cr

    def ac_from_cr(self, cr):
        """Armor class computed from challenge rating

        Args:
            cr (float): challenge rating

        Returns:
            float: armor class
        """
        if cr < 0.5:
            return 12
        elif cr <= 1:
            return 13
        else:
            return 13 + 0.35*cr

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
    
    def save_dc_from_cr(self, cr):
        return self.tohit_from_cr(cr)+7
    
    def strong_save_from_cr(self, cr):
        return self.ac_from_cr(cr) -11
    #endregion

    #region bounds
    def _hp_bound(self, hp, cr):
        if hp < cr:
            return cr
        elif hp > 50*cr:
            return 50*cr
        return hp
    
    def _ac_bound(self, ac, cr):
        if ac < 0:
            return 0
        elif cr < 2 and ac > 18:
            return 18
        elif ac > 30:
            return 30
        return ac
    #endregion

    #region optimize
    def make_statblock_optimize(self, cr, stats=None, offense_ratio=None, seed=None):
        # ['cr', 'hp', 'ac', 'tohit', 'damage', 'save_dc', 'strong_save', 'weak_save']
        random.seed(seed)
        fixed_index = []
        fixed_value = []

        x = self._optimize_guess(cr)
        if stats is None:
            stats = {'cr': cr}
        else:
            stats['cr'] = cr
        for i, name in enumerate(self.core_stat_names):
            if name in stats:
                fixed_index.append(i)
                fixed_value.append(stats[name])

        for i in sorted(fixed_index, reverse=True):
            del x[i]

        sol = optimize.minimize(
            self._optimize_objective_function, 
            x,
            (fixed_index, fixed_value),
            bounds=self._optimize_bounds(fixed_index),
            tol=0.0001  
        )
        # print(sol)
        sol = list(sol.x)
        for i, v in zip(fixed_index, fixed_value):
            sol.insert(i, v)

        return sol

    def _optimize_guess(self, cr):
        hp, ac, strong_save, weak_save = self.get_defensive_stats(cr)
        tohit, damage, save_dc = self.get_offensive_stats(cr)
        return [cr, hp, ac, tohit, damage, save_dc, strong_save, weak_save]
    
    def _optimize_bounds(self, fixed_index):
        bounds = [
            (None, None), # cr
            (0, None), # hp
            (1, 29), # ac
            (-5, 29), # tohit
            (0, None), # damage
            (7, 29), # save dc
            (-5, 29), # strong save
            (-5, 29), # weak save
        ]
        for i in sorted(fixed_index, reverse=True):
            del bounds[i]
        return bounds

    def _optimize_objective_function(self, x_var, fixed_index, fixed_value):
        x = list(x_var.copy())
        for i, v in zip(fixed_index, fixed_value):
            x.insert(i, v)

        target_cr = x[0]
        cr = []

        cr.append(self.cr_from_hp(x[1]))
        cr.append(self.cr_from_ac(x[2]))
        cr.append(self.cr_from_tohit(x[3]))
        cr.append(self.cr_from_damage(x[4]))
        cr.append(self.cr_from_save_dc(x[5]))
        cr.append(self.cr_from_strong_save(x[6]))

        weights = [
            1.0,
            0.6,
            1.0,
            1.0,
            0.2,
            0.2,
        ]

        computed_cr = sum(c*w for c, w in zip(cr, weights))/sum(weights)
        return abs(target_cr - computed_cr)
    #endregion
