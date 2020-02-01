import re

import praw

from . import config, database, level, reply

### Main Function ###


def run():
    cfg = config.load()
    levels = cfg.levels

    # Connect to Reddit
    reddit = praw.Reddit(site_name=cfg.praw_site_name)
    subreddit = reddit.subreddit(cfg.subreddit_name)

    print_level(0, f'Connected to Reddit as {reddit.user.me()}')
    print_level(1, f'Read-only? {reddit.read_only}')
    print_level(0, f'Watching subreddit {subreddit.title}')
    is_mod = bool(subreddit.moderator(redditor=reddit.user.me()))
    print_level(1, f'Is mod? {is_mod}')

    db = database.Database(cfg.database_path)

    # The pattern that determines whether a post is marked as solved
    # Could also just use re.IGNORECASE flag
    solved_pat = re.compile('![Ss]olved')

    # Monitor new comments for confirmed solutions
    # Passing pause_after=0 will bypass the internal exponential delay, but have
    # to check if any comments are returned with each query
    for comm in subreddit.stream.comments(skip_existing=True, pause_after=0):
        if comm is None:
            continue

        print_level(0, '\nFound comment')
        print_level(1, f'Comment text: "{comm.body}"')

        if marks_as_solved(comm, solved_pat):
            if not is_first_solution(comm, solved_pat):
                # Skip this "!solved" comment and wait for the next
                print_level(1, 'Not the first solution')
                continue

            print_level(1, 'This is the first solution')
            print_solution_info(comm)

            solver = comm.parent().author
            print_level(1, f'Adding point for {solver.name}')
            db.add_point(solver)
            points = db.get_points(solver)
            print_level(1, f'Points for {solver.name}: {points}')

            level_info = level.user_level_info(points, levels)

            # TODO move comment to the end and use some things, e.g. whether
            # flair is set, when building comment (to avoid duplicate logic)

            # Reply to the comment marking the submission as solved
            reply_body = reply.make(solver, points, level_info)
            # reply_body = reply.make(solver, points, levels)
            print_level(1, f'Replying with: "{reply_body}"')
            comm.reply(reply_body)

            # Check if (non-mod) user flair should be updated to new level
            if level_info.current and level_info.current.points == points:
                print_level(1, f'User reached level: {level_info.current.name}')
                if not subreddit.moderator(redditor=solver):
                    print_level(2, 'Setting flair')
                    print_level(3, f'Flair text: {level_info.current.name}')
                    # TODO
                    # print_level(3, f'Flair template ID: {}')
                    subreddit.flair.set(solver, text=levelname)
                else:
                    print_level(2, 'Solver is mod; don\'t alter flair')
        else:
            print_level(1, 'Not a "!solved" comment')


### Reddit Comment Functions ###


def marks_as_solved(comment, solved_pattern):
    '''Return True if the comment meets the criteria for marking the submission
    as solved, False otherwise.
    '''
    return (not comment.is_root
            and comment.is_submitter
            and not comment.parent().is_submitter
            and solved_pattern.search(comment.body))


def is_first_solution(solved_comment, solved_pattern):
    # Retrieve any comments hidden by "more comments"
    # Passing limit=0 will replace all "more comments"
    submission = solved_comment.submission
    submission.comments.replace_more(limit=0)

    # Search the flattened comments tree
    for comment in submission.comments.list():
        if (comment.id != solved_comment.id
                and marks_as_solved(comment, solved_pattern)
                and comment.created_utc < solved_comment.created_utc):
            # There is an earlier comment for the same submission
            # already marked as a solution by the OP
            return False
    return True


def find_solver(comment):
    # TODO
    pass


def make_flair(points, levels):
    # TODO
    pass


### Debugging & Logging ###


def print_level(num_levels, string):
    print('\t' * num_levels + string)


def print_solution_info(comm):
    print_level(1, 'Submission solved')
    print_level(2, 'Solution comment:')
    print_level(3, f'Author: {comm.parent().author.name}')
    print_level(3, f'Body:   {comm.parent().body}')
    print_level(2, '"Solved" comment:')
    print_level(3, f'Author: {comm.author.name}')
    print_level(3, f'Body:   {comm.body}')


def make_comments():
    cfg = config.load()
    levels = cfg.levels

    # Connect to Reddit
    reddit = praw.Reddit(site_name=cfg.praw_site_name)
    subreddit = reddit.subreddit(cfg.subreddit_name)

    print_level(0, f'Connected to Reddit as {reddit.user.me()}')
    print_level(1, f'Read-only? {reddit.read_only}')
    print_level(0, f'Watching subreddit {subreddit.title}')
    is_mod = bool(subreddit.moderator(redditor=reddit.user.me()))
    print_level(1, f'Is mod? {is_mod}')

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


