from collections import namedtuple

### Data Structures ###

# A (string, int) tuple
Level = namedtuple('Level', 'name points flair_template_id')

# A ([Level], Level, Level) tuple
# previous can be empty, and exactly one of current and next can be None
LevelInfo = namedtuple('LevelInfo', 'previous current next')

### Functions ###


def user_level_info(points, levels):
    """Return a tuple the user's previous (plural), current, and next levels.

    If the user has yet to reach the first level, return ([], None, <first
    level>).
    If the user has reached the max level, return ([previous], <max level>,
    None).

    Assume levels is sorted in ascending order by points.
    """
    past_levels, cur_level, next_level = [], None, None

    for level in levels:
        if points < level.points:
            next_level = level
            break
        if cur_level:
            past_levels.append(cur_level)
        cur_level = level
    else:
        next_level = None

    return LevelInfo(past_levels, cur_level, next_level)


def is_max_level(level_info):
    return not level_info.next

