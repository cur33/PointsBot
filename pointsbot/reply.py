from . import level

### Globals ###

# Progress bar symbols
DIV_SYMBOL    = '|'
FILLED_SYMBOL = '\u25AE'   # A small filled box character
EMPTY_SYMBOL  = '\u25AF'   # A same-sized empty box character

# Number of "excess" points should be greater than max level points
EXCESS_POINTS = 100              # TODO move this to level?
EXCESS_SYMBOL = '\u2605'         # A star character
EXCESS_SYMBOL_TITLE = 'a star'   # Used in comment body

### Main Functions ###


def make(redditor, points, level_info):
    paras = [header()]

    if points == 1:
        paras.append(first_greeting(redditor))
        if level_info.current and points == level_info.current.points:
            paras.append(level_up(redditor,
                                  level_info.current.name,
                                  tag_user=False))
    elif points > 1:
        user_already_tagged = False

        if level_info.current and points == level_info.current.points:
            paras.append(level_up(redditor,
                                  level_info.current.name,
                                  tag_user=(not user_already_tagged)))
            user_already_tagged = True

        if points % EXCESS_POINTS == 0:
            first_excess = (points == EXCESS_POINTS)
            paras.append(new_excess_symbol(redditor,
                                           first_excess=first_excess,
                                           tag_user=(not user_already_tagged)))
            user_already_tagged = True

        if not user_already_tagged:
            paras.append(normal_greeting(redditor))

    paras.append(points_status(redditor, points, level_info))
    paras.append(footer())
    return '\n\n'.join(paras)


### Comment Section Functions ###


def header():
    return 'Thanks! Post marked as Solved!'


def first_greeting(redditor):
    return (f'Congrats, u/{redditor.name}, you have received a point! Points '
           'help you "level up" to the next user flair!')


def normal_greeting(redditor):
    return f'u/{redditor.name}, here is your points status:'


def level_up(redditor, level_name, tag_user=True):
    start = f'Congrats u/{redditor.name}, y' if tag_user else 'Y'
    return (f'{start}ou have leveled up to "{level_name}"! Your flair has been '
            'updated accordingly.')


def new_excess_symbol(redditor, first_excess=True, tag_user=True):
    # Surrounding spaces for simplicity
    tag = f' u/{redditor.name} ' if tag_user else ' '
    num_stars_prefix = ' another ' if not first_excess else ' '
    return (f'Congrats{tag}on getting{num_stars_prefix}{EXCESS_POINTS} points! '
            f'They are shown as {EXCESS_SYMBOL_TITLE} in your progress bar.')


def points_status(redditor, points, level_info):
    pointstext = 'points' if points > 1 else 'point'

    if level_info.next:
        lines = [
            f'Next level: "{level_info.next.name}"',
            f'You have {points} {pointstext}',
            f'You need {level_info.next.points} points',
        ]
    else:
        lines = [
            'MAXIMUM LEVEL ACHIEVED!!!',
            f'You have {points} {pointstext}',
        ]

    # 2 spaces are appended to each line to force a Markdown line break
    lines = [line + '  ' for line in lines]
    lines.append(progress_bar(points, level_info))

    return '\n'.join(lines)


def progress_bar(points, level_info):
    if points < EXCESS_POINTS:
        past, cur, nxt = level_info
        allpoints = [lvl.points for lvl in [*past, cur]]
        diffs = [a - b for a, b in zip(allpoints, [0] + allpoints)]
        bar = [FILLED_SYMBOL * diff for diff in diffs]

        if nxt:
            have = points if not cur else points - cur.points
            need = nxt.points - points
            bar.append((FILLED_SYMBOL * have) + (EMPTY_SYMBOL * need))

        bar = DIV_SYMBOL.join(bar)
    else:
        num_excess, num_leftover = divmod(points, EXCESS_POINTS)
        bar = [DIV_SYMBOL.join(EXCESS_SYMBOL * num_excess)]
        if num_leftover > 0:
            bar.append(DIV_SYMBOL)
            bar.append(FILLED_SYMBOL * num_leftover)
        bar = ''.join(bar)

    return f'[{bar}]'


def footer():
    return ('^(This bot is written and maintained by GlipGlorp7 '
            '| Learn more and view the source code on '
            '[Github](https://github.com/cur33/PointsBot))')


