from statblock_builder import *

SBB = StatblockBuilder()



sb = SBB.make_statblock_basic(4)

print(sb.attributes)
print(sb.format())
