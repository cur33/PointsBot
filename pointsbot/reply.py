from . import level

### Globals ###

EMPTY_SYMBOL  = '\u25AF'   # A same-sized empty box character
FILLED_SYMBOL = '\u25AE'   # A small filled box character
EXCESS_SYMBOL = '\u2B51'   # A star character
DIV_SYMBOL    = '|'

# Number of "excess" points should be greater than max level points
EXCESS_POINTS = 100   # TODO move this to level?

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
        if level_info.current and points == level_info.current.points:
            paras.append(level_up(redditor, level_info.current.name))
        elif not level_info.next and points > 0 and points % EXCESS_POINTS == 0:
            first_star = (points == EXCESS_POINTS)
            paras.append(new_star(redditor, first_star))
        else:
            paras.append(normal_greeting(redditor))

    paras.append(points_status(redditor, points, level_info))
    paras.append(footer())
    return '\n\n'.join(paras)


### Comment Section Functions ###


def header():
    return 'Thanks! Post marked as Solved!'


def first_greeting(redditor):
    msg = (f'Congrats, u/{redditor.name}, you have received a point! Points '
           'help you "level up" to the next user flair!')
    return msg


def normal_greeting(redditor):
    return f'u/{redditor.name}, here is your points status:'


def level_up(redditor, level_name, tag_user=True):
    start = f'Congrats u/{redditor.name}, y' if tag_user else 'Y'
    return (f'{start}ou have leveled up to "{level_name}"! Your flair has been '
            'updated accordingly.')
    # return (f'Congrats u/{redditor.name}, y
    # return (f'Congrats u/{redditor.name}, you have leveled up to "{level_name}"! '
            # 'Your flair has been updated accordingly.')


def new_star(redditor, first_star):
    num_stars_msg = '' if first_star else 'another '
    return (f'Congrats u/{redditor.name} on getting '
            '{num_stars_msg}{EXCESS_POINTS} points! They are shown as a star '
            'in your progress bar.')


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
    # ^(This bot is written and maintained by u/GlipGlorp7 | Learn more and view the source code on [Github](https://github.com/cur33/PointsBot))
    # ^([Learn more]() | [View source code](https://github.com/cur33/PointsBot) | [Contacts mods]())


