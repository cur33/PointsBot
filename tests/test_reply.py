from collections import namedtuple

from context import pointsbot

### Data Structures ###

MockRedditor = namedtuple('MockRedditor', 'id name')

### Functions ###


def leftpad(msg, num_indents=1):
    return '\n'.join([('\t' * num_indents + l) for l in msg.split('\n')])


def make_comments(subreddit, levels):
    testpoints = [1, 3, 5, 10, 15, 30, 45, 75] + list(range(100, 551, 50))

    for sub in subreddit.new():
        if sub.title == 'Testing comment scenarios':
            redditor = sub.author
            for points in testpoints:
                body = f'Solver: {redditor}\n\nTotal points after solving: {points}'
                print_level(0, body)
                comm = sub.reply(body)
                if comm:
                    level_info = level.user_level_info(points, levels)
                    body = reply.make(redditor, points, level_info)
                    comm.reply(body)
                else:
                    print_level(1, 'ERROR: Unable to comment')
            break


### Tests ###

levels = [
    pointsbot.level.Level('Novice', 1, ''),
    pointsbot.level.Level('Apprentice', 5, ''),
    pointsbot.level.Level('Journeyman', 15, ''),
    pointsbot.level.Level('Expert', 45, ''),
    pointsbot.level.Level('Master I', 100, ''),
    pointsbot.level.Level('Master II', 200, ''),
    pointsbot.level.Level('Master III', 300, ''),
    pointsbot.level.Level('Master IV', 400, ''),
    pointsbot.level.Level('Master V', 500, ''),
]

testredditors = [MockRedditor('1', 'Tim_the_Sorcerer')]
testpoints = [1, 3, 5, 10, 15, 30, 45, 75] + list(range(100, 551, 50))

for redditor in testredditors:
    for points in testpoints:
        level_info = pointsbot.level.user_level_info(points, levels)
        body = pointsbot.reply.make(redditor, points, level_info)
        print('*' * 80)
        print()
        print(f'Name:   {redditor.name}')
        print(f'Points: {points}')
        print(f'Body:')
        print(leftpad(body, num_indents=1))
        print()
print('*' * 80)
