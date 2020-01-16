### Globals ###

FILLED_SYMBOL = '\u25AE'   # A small filled box character
EMPTY_SYMBOL  = '\u25AF'   # A same-sized empty box character
DIV_SYMBOL    = '|'

### Main Functions ###


def make(redditor, points, levels):
    body = (first_point(redditor) + '\n\n') if points == 1 else ''
    body += points_status(redditor, points, levels)
    return body


### Auxiliary Functions ###


def first_point(redditor):
    msg = (f'Congrats, u/{redditor.name}; you have received a point! Points '
           'help you "level up" to the next user flair!')
    return msg


def points_status(redditor, points, levels):
    '''Levels is an iterable of (level_name, points) pairs, sorted in ascending
    order by points.
    '''
    for next_level_name, next_level_points in levels:
        if next_level_points > points:
            break

    pointstext = 'points' if points > 1 else 'point'

    if points < next_level_points:
        lines = [
            f'Next level: "{next_level_name}"',
            f'You have {points} {pointstext}',
            f'You need {next_level_points} points',
        ]
    else:
        lines = [
            'MAXIMUM LEVEL ACHIEVED!!!',
            f'You have {points} {pointstext}',
        ]

    # 2 spaces are appended to each line to force a line break but not a
    # paragraph break
    # lines = [line + '  ' for line in lines]
    lines = list(map(lambda line: line + '  ', lines))

    """
    if points < next_level_points:
        lines = [
            f'Next level: "{next_level_name}"  ',
            f'You need {next_level_points} points  ',
        ]
    else:
        lines = ['MAXIMUM LEVEL ACHIEVED!!!  ']

    # TODO hacky and bad :(
    lines.insert(1, f'You have {points} points  ')
    """

    lines.append(progress_bar(points, levels))

    return '\n'.join(lines)


def progress_bar(points, levels):
    '''Assumes levels is sorted in ascending order.'''
    progbar = [FILLED_SYMBOL] * points
    ndx_shift = 0
    for levelndx, level in enumerate(levels):
        next_level_name, next_level_points = level
        if next_level_points > points:
            break
        ndx = next_level_points + ndx_shift
        progbar.insert(ndx, DIV_SYMBOL)
        ndx_shift += 1

    if next_level_points <= points:
        # If just reached max level, then an extra DIV_SYMBOL was appended
        progbar.pop()
    else:
        # Not max level, so fill slots left until next level with EMPTY_SYMBOL
        remaining = next_level_points - points
        progbar.extend([EMPTY_SYMBOL] * remaining)

    return '[' + ''.join(progbar) + ']'


