import re

import praw
import prawcore

from . import config, database, level, reply

### Globals ###

USER_AGENT = 'PointsBot (by u/GlipGlorp7)'

# The pattern that determines whether a post is marked as solved
# Could also just use re.IGNORECASE flag
SOLVED_PAT = re.compile('![Ss]olved')
MOD_SOLVED_PAT = re.compile('/[Ss]olved')

### Main Function ###


def run():
    cfg = config.load()
    levels = cfg.levels
    db = database.Database(cfg.database_path)

    # Run indefinitely, reconnecting any time a connection is lost
    while True:
        try:
            reddit = praw.Reddit(client_id=cfg.client_id,
                                 client_secret=cfg.client_secret,
                                 username=cfg.username,
                                 password=cfg.password,
                                 user_agent=USER_AGENT)
            subreddit = reddit.subreddit(cfg.subreddit)

            print_level(0, f'Connected to Reddit as {reddit.user.me()}')
            print_level(1, f'Read-only? {reddit.read_only}')
            print_level(0, f'Watching subreddit {subreddit.title}')
            is_mod = bool(subreddit.moderator(redditor=reddit.user.me()))
            print_level(1, f'Is mod? {is_mod}')

            monitor_comments(subreddit, db, levels)
        # Ignoring other potential exceptions for now, since we may not be able
        # to recover from them as well as from this one
        except prawcore.exceptions.RequestException as e:
            print('Unable to connect; attempting again....')
        except prawcore.exceptions.ServerError as e:
            print('Lost connection; attempting to reconnect....')


def monitor_comments(subreddit, db, levels):
    """Monitor new comments in the subreddit, looking for confirmed solutions."""
    # Passing pause_after=0 will bypass the internal exponential delay, but have
    # to check if any comments are returned with each query
    for comm in subreddit.stream.comments(skip_existing=True, pause_after=0):
        if comm is None:
            continue

        print_level(0, '\nFound comment')
        print_level(1, f'Comment text: "{comm.body}"')

        if not marks_as_solved(comm):
            print_level(1, 'Not a "![Ss]olved" comment')
            continue

        if is_mod_comment(comm):
            print_level(1, 'Mod comment')
        elif not is_first_solution(comm):
            # Skip this "!solved" comment and wait for the next
            print_level(1, 'Not the first solution')
            continue

        print_level(1, 'This is the first solution found')
        print_solution_info(comm)

        solver = find_solver(comm)
        db.add_point(solver)
        print_level(1, f'Added point for {solver.name}')

        points = db.get_points(solver)
        print_level(1, f'Total points for {solver.name}: {points}')
        level_info = level.user_level_info(points, levels)

        # Reply to the comment marking the submission as solved
        reply_body = reply.make(solver, points, level_info)
        try:
            comm.reply(reply_body)
            print_level(1, f'Replied to comment with: "{reply_body}"')
        except praw.exceptions.APIException as e:
            print_level(1, 'Unable to reply to comment')
            print_level(2, f'{e}')
            db.remove_point(solver)
            print_level(1, f'Removed point awarded to {solver.name}')
            print_level(1, 'Skipping comment')
            continue

        # Check if (non-mod) user flair should be updated to new level
        lvl = level_info.current
        if lvl and lvl.points == points:
            print_level(1, f'User reached level: {lvl.name}')
            if not subreddit.moderator(redditor=solver):
                print_level(2, 'Setting flair')
                print_level(3, f'Flair text: {lvl.name}')
                print_level(3, f'Flair template ID: {lvl.flair_template_id}')
                subreddit.flair.set(solver,
                                    text=lvl.name,
                                    flair_template_id=lvl.flair_template_id)
            else:
                print_level(2, 'Solver is mod; don\'t alter flair')


### Reddit Comment Functions ###


def marks_as_solved(comment):
    """Return True if the comment meets the criteria for marking the submission
    as solved, False otherwise.
    """
    op_resp_to_solver = (not comment.is_root
                         and comment.is_submitter
                         and not comment.parent().is_submitter
                         and SOLVED_PAT.search(comment.body))

    # Mod can only used MOD_SOLVED_PAT on any post, including their own
    mod_resp_to_solver = (not comment.is_root
                          and comment.subreddit.moderator(redditor=comment.author)
                          and MOD_SOLVED_PAT.search(comment.body))

    return op_resp_to_solver or mod_resp_to_solver


def is_mod_comment(comment):
    return comment.subreddit.moderator(redditor=comment.author)


def is_first_solution(solved_comment):
    """Return True if this solved comment is the first, False otherwise."""
    # Retrieve any comments hidden by "more comments" by passing limit=0
    submission = solved_comment.submission
    submission.comments.replace_more(limit=0)

    # Search the flattened comments tree
    for comment in submission.comments.list():
        if (comment.id != solved_comment.id
                and marks_as_solved(comment)
                and comment.created_utc < solved_comment.created_utc):
            # There is an earlier comment for the same submission
            # already marked as a solution by the OP
            return False
    return True


def find_solver(solved_comment):
    """Determine the redditor responsible for solving the question."""
    return solved_comment.parent().author


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


