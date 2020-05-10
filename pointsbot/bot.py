import logging
import os
import os.path
import re

import praw
import prawcore

from . import config, database, level, reply

### Globals ###

USER_AGENT = 'PointsBot (by u/GlipGlorp7)'

# TODO put this in config
LOG_FILEPATH = os.path.abspath(os.path.join(os.path.expanduser('~'),
                                            '.pointsbot',
                                            'pointsbot.log.txt'))

# The pattern that determines whether a post is marked as solved
# Could also use re.IGNORECASE flag instead
SOLVED_PAT = re.compile('![Ss]olved')
MOD_SOLVED_PAT = re.compile('/[Ss]olved')

### Main Function ###


def run():
    logging.basicConfig(filename=LOG_FILEPATH,
                        level=logging.DEBUG,
                        format='%(asctime)s %(module)s:%(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    print_welcome_message()

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
            logging.info('Connected to Reddit as %s', reddit.user.me())
            if not reddit.read_only:
                logging.info('Has write access to Reddit')
            else:
                logging.info('Has read-only access to Reddit')

            subreddit = reddit.subreddit(cfg.subreddit)
            logging.info('Watching subreddit %s', subreddit.title)
            if subreddit.moderator(redditor=reddit.user.me()):
                logging.info('Is moderator for monitored subreddit')
            else:
                logging.warning('Is NOT moderator for monitored subreddit')

            monitor_comments(subreddit, db, levels)
        # Ignoring other potential exceptions for now, since we may not be able
        # to recover from them as well as from this one
        except prawcore.exceptions.RequestException as e:
            log.error('Unable to connect; attempting again....')
        except prawcore.exceptions.ServerError as e:
            log.error('Lost connection to Reddit; attempting to reconnect....')


def monitor_comments(subreddit, db, levels):
    """Monitor new comments in the subreddit, looking for confirmed solutions."""
    # Passing pause_after=0 will bypass the internal exponential delay, but have
    # to check if any comments are returned with each query
    for comm in subreddit.stream.comments(skip_existing=True, pause_after=0):
        if comm is None:
            continue

        logging.info('Received comment')
        # TODO more debug info about comment, eg author
        logging.debug('Comment text: "%s"', comm.body)
        # print_level(0, '\nFound comment')
        # print_level(1, f'Comment text: "{comm.body}"')

        if not marks_as_solved(comm):
            logging.info('Comment does not mark issue as solved')
            # print_level(1, 'Not a "![Ss]olved" comment')
            continue

        logging.info('Comment marks issues as solved')

        if is_mod_comment(comm):
            logging.info('Comment was submitted by mod')
            # print_level(1, 'Mod comment')
        elif not is_first_solution(comm):
            # Skip this "!solved" comment
            logging.info('Comment is NOT the first to mark the issue as solved')
            # print_level(1, 'Not the first solution')
            continue

        logging.info('Comment is the first to mark the issue as solved')
        # print_level(1, 'This is the first solution found')
        log_solution_info(comm)

        solver = find_solver(comm)
        db.add_point(solver)
        logging.info('Added point for user "%s"', solver.name)
        # print_level(1, f'Added point for {solver.name}')

        points = db.get_points(solver)
        logging.info('Total points for user "%s": %d', solver.name, points)
        # print_level(1, f'Total points for {solver.name}: {points}')
        level_info = level.user_level_info(points, levels)

        # Reply to the comment marking the submission as solved
        reply_body = reply.make(solver, points, level_info)
        try:
            comm.reply(reply_body)
            logging.info('Replied to the comment')
            logging.debug('Reply body: %s', reply_body)
            # print_level(1, f'Replied to comment with: "{reply_body}"')
        except praw.exceptions.APIException as e:
            logging.error('Unable to reply to comment: %s', e)
            db.remove_point(solver)
            logging.error('Removed point that was just awarded to user "%s"', solver.name)
            logging.error('Skipping comment')
            continue

        # Check if (non-mod) user flair should be updated to new level
        lvl = level_info.current
        if lvl and lvl.points == points:
            logging.info('User reached level: %s', lvl.name)
            if not subreddit.moderator(redditor=solver):
                # print_level(2, 'Setting flair')
                logging.info('User is not mod; setting flair')
                logging.info('Flair text: %s', lvl.name)
                logging.info('Flair template ID: %s', lvl.flair_template_id)
                subreddit.flair.set(solver,
                                    text=lvl.name,
                                    flair_template_id=lvl.flair_template_id)
            else:
                logging.info('Solver is mod; don\'t alter flair')


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


### Print Functions ###


def print_separator_line():
    print('#' * 80)


def print_welcome_message():
    print_separator_line()
    print('\n*** Welcome to PointsBot! ***\n')
    print_separator_line()
    print('\nThis bot will monitor the subreddit specified in the '
          'configuration file as long as this program is running.')
    print('\nAny Reddit activity that occurs while this program is not running '
          'will be missed. You can work around this by using features '
          'mentioned in the README.')
    print('\nThe output from this program can be referenced if any issues are '
          'to occur, and the relevant error message or crash report can be '
          'sent to the developer by reporting an issue on the Github page.')
    print('\nFuture updates will hopefully resolve these issues, but for the '
          "moment, this is what we've got to work with! :)\n")


def print_level(num_levels, string):
    print('\t' * num_levels + string)


def log_solution_info(comm):
    logging.info('Submission solved')
    logging.debug('Solution comment:')
    logging.debug('Author: %s', comm.parent().author.name)
    logging.debug('Body:   %s', comm.parent().body)
    logging.debug('"Solved" comment:')
    logging.debug('Author: %s', comm.author.name)
    logging.debug('Body:   %s', comm.body)


