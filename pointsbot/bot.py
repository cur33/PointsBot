import configparser
import re

import praw

from . import comment, database

### Globals ###

CONFIGPATH = 'pointsbot.ini'

### Main Function ###


def run():
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)

    # Get the user flair levels in ascending order by point value
    # TODO Make levels a dict instead
    # TODO Could also make a Level class or namedtuple that contains more info, e.g.
    # flair css or template id
    levels = [(o, config.getint('Levels', o)) for o in config.options('Levels')]
    levels.sort(key=lambda pair: pair[1])

    # levels = []
    # for opt in config.options('Levels'):
        # levels.append((opt, config.getint('Levels', opt)))
    # levels.sort(key=lambda pair: pair[1])

    # Connect to Reddit
    reddit = praw.Reddit(site_name=config['Core']['praw_site_name'])
    subreddit = reddit.subreddit(config['Core']['subreddit_name'])

    print(f'Connected to Reddit as {reddit.user.me()}')
    print(f'Read-only? {reddit.read_only}')
    print(f'Watching subreddit {subreddit.title}')
    print(f'Is mod? {bool(subreddit.moderator(redditor=reddit.user.me()))}')

    # TODO pass database path instead of setting global variable
    db = database.Database(config['Core']['database_name'])

    # The pattern to look for in comments when determining whether to award a point
    # solved_pat = re.compile('!solved', re.IGNORECASE)
    solved_pat = re.compile('![Ss]olved')

    # Monitor new comments for confirmed solutions
    for comm in subreddit.stream.comments(skip_existing=True):
        print('Found comment')
        print(f'Comment text: "{comm.body}"')

        if marks_as_solved(comm, solved_pat):
            # Ensure that this is the first "!solved" comment in the thread
            submission = comm.submission
            # Retrieve any comments hidden by "more comments"
            submission.comments.replace_more(limit=0)

            # Search the flattened comments tree
            is_first_solution = True
            for subcomm in submission.comments.list():
                if (subcomm.id != comm.id
                        and marks_as_solved(subcomm, solved_pat)
                        and subcomm.created_utc < comm.created_utc):
                    # There is an earlier comment for the same submission
                    # already marked as a solution by the OP
                    is_first_solution = False
                    break

            if not is_first_solution:
                # Skip this "!solved" comment and wait for the next
                print('This is not the first solution')
                continue

            print('This is the first solution')
            print_solution_info(comm)

            solution = comm.parent()
            solver = solution.author
            print(f'Adding point for {solver.name}')
            db.add_point(solver)
            points = db.get_points(solver)
            print(f'Points for {solver.name}: {points}')

            # Reply to the comment containing the solution
            reply_body = comment.make(solver, points, levels)
            print(f'Replying with: "{reply_body}"')
            solution.reply(reply_body)

            # Check if (non-mod) user flair should be updated to new level
            for levelname, levelpoints in levels:
                # If the redditor's points total is equal to one of the levels,
                # that means they just reached that level
                if points == levelpoints:
                    print('User reached new level')
                    if not subreddit.moderator(redditor=solver):
                        # TODO can also use the keyword arg css_class *or*
                        # flair_template_id to style the flair
                        print(f'Setting flair text to {levelname}')
                        subreddit.flair.set(solver, text=levelname)
                    else:
                        print('Don\'t update flair b/c user is mod')

                    # Don't need to check the rest of the levels
                    break
        else:
            print('Not a "!solved" comment')


### Auxiliary Functions ###


def marks_as_solved(comment, solved_pattern):
    '''Return True if  not top-level comment, from OP, contains "!Solved"; False
    otherwise.
    '''
    #comment.refresh()   # probably not needed, but the docs are a tad unclear
    return (not comment.is_root
            and comment.is_submitter
            and not comment.parent().is_submitter
            and solved_pattern.search(comment.body))


### Debugging ###


def print_solution_info(comm):
    print('Submission solved')
    print('\tSolution comment:')
    print(f'\t\tAuthor: {comm.parent().author.name}')
    print(f'\t\tBody:   {comm.parent().body}')
    print('\t"Solved" comment:')
    print(f'\t\tAuthor: {comm.author.name}')
    print(f'\t\tBody:   {comm.body}')


