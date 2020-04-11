import context

# import unittest

# TODO???
# from pointsbot import level
import pointsbot.level as level

levels = [
    ('Helper', 5),
    ('Trusted Helper', 15),
    ('Super Helper', 45),
]

### Test user_level_info ###


pastlvls, curlvl, nextlvl = user_level_info(1, levels)
assert (pastlevels == [] and curlvl is None and nextlvl == levels[0])

pastlvls, curlvl, nextlvl = user_level_info(5, levels)
assert (pastlevels == [] and curlvl == levels[0] and nextlvl == levels[1])

pastlvls, curlvl, nextlvl = user_level_info(15, levels)
assert (pastlvls == levels[:1] and curlvl == levels[1] and nextlvl == levels[2])

pastlvls, curlvl, nextlvl = user_level_info(45, levels)
assert (pastlvls == levels[:2] and curlvl == levels[2] and nextlvl is None)


### Test is_max_level ###


# TODO I mean, this could be tested exhaustively with positive numbers, even if
# the number of points for the max level is decently large
assert not level.is_max_level(-1, levels)
assert not level.is_max_level(0, levels)
assert not level.is_max_level(4, levels)
assert not level.is_max_level(5, levels)
assert not level.is_max_level(14, levels)
assert not level.is_max_level(15, levels)
assert not level.is_max_level(16, levels)
assert not level.is_max_level(44, levels)
assert level.is_max_level(45, levels)
assert level.is_max_level(46, levels)
