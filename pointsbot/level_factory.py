

def get_factory(config_levels):
    levels = [Level(*level) for level in config_levels]
    levels.sort(key=lambda l: l.points)

    def factory(points):
        """Return the user's previous (plural), current, and next levels.

        If the user has yet to reach the first level, return ([], None, <first level>).
        If the user has reached the max level, return ([previous levels], <max level>, None).

        Assumes levels are sorted in ascending order by points.
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

    return factory


class Level:

    def __init__(self, name, points, flair_template_id):
        self.name = name
        self.points = points
        self.flair_template_id = flair_template_id


class LevelInfo:

    def __init__(self, previous, current, next):
        self.previous = previous
        self.current = current
        self.next = next

    def has_level(self):
        return self.current

    def is_max_level(self):
        return self.has_level() and not self.next

