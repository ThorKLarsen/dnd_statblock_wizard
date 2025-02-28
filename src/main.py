from statblock_builder import StatblockBuilder

# Define the StatblockBuilder object
SBB = StatblockBuilder()

# Create a basic statblock with cr 5
sb = SBB.make_statblock_basic(5, {'hp': 20})

print(sb.format())

# Create a statblock using the optimization feature, this one has an AC of 17
sb = SBB.make_statblock_optimize(11, {'ac':17})

# This uses scipy's optimization library to make a suitable statblock.
# Tends to not make very balanced stats.

# print(sb)
# print(sb.attributes)
# print(sb.get_basic_attack().__dict__)
print(sb.format())


