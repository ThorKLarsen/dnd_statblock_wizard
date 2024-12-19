from statblock_builder import StatblockBuilder

SBB = StatblockBuilder()

# sb = SBB.make_statblock_basic(1, {'ac': 18})


# print(sb.attributes)
# print(sb.get_basic_attack().__dict__)
# print(sb.format())

sb = SBB.make_statblock_optimize(4, {'ac':17})

print(sb)
