import logging
import os
import os.path
import re
import sys
from collections import namedtuple

import praw
import prawcore

from . import config, level, reply
from .data import database

### Globals ###

USER_AGENT = 'PointsBot (by u/GlipGlorp7)'

# The pattern that determines whether a post is marked as solved
SOLVED_PATTERN = re.compile('![Ss]olved')
MOD_SOLVED_PATTERN = re.compile('/[Ss]olved')

### Main Function ###


def run():
    print_welcome_message()

    cfg = config.load()
    file_handler = logging.FileHandler(cfg.log_path, 'w', 'utf-8')
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)

    logging.basicConfig(handlers=[file_handler, console_handler],
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(module)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    # TODO instead of letting config access level module, create a level
    # function to take the values from cfg and convert them into the proper
    # levels
    levels = cfg.levels

    try:
        db = database.Database(cfg.database_path)
    except Exception as e:
        print('Unable to set up database connection for the following reason:\n')
        print(e)
        print('\nPlease contact the bot creator/maintainer with the issue details')
        sys.exit(1)

    # Run indefinitely, reconnecting any time a connection is lost
    while True:
        try:
            reddit = praw.Reddit(client_id=cfg.client_id,
                                 client_secret=cfg.client_secret,
                                 username=cfg.username,
                                 password=cfg.password,
                                 user_agent=USER_AGENT)
            logging.info('Connected to Reddit as %s', reddit.user.me())
            access_type = 'read-only' if reddit.read_only else 'write'
            logging.info(f'Has {access_type} access to Reddit')

            subreddit = reddit.subreddit(cfg.subreddit)
            logging.info('Watching subreddit %s', subreddit.title)
            is_mod = subreddit.moderator(redditor=reddit.user.me())
            logging.info(f'Is {"" if is_mod else "NOT "} moderator for subreddit')

            monitor_comments(reddit, subreddit, db, levels, cfg)

        # Ignoring other potential exceptions for now, since we may not be able
        # to recover from them as well as from these ones
        except prawcore.exceptions.RequestException as e:
            logging.error('Unable to connect to Reddit')
            logging.error('Error message: %s', e)
            logging.error('Trying again')
        except prawcore.exceptions.ServerError as e:
            logging.error('Lost connection to Reddit')
            logging.error('Error message: %s', e)
            logging.error('Attempting to reconnect')


def monitor_comments(reddit, subreddit, db, levels, cfg):
    """Monitor new comments in the subreddit, looking for confirmed solutions."""
    # Passing pause_after=0 will bypass the internal exponential delay, but have
    # to check if any comments are returned after each query
    for comm in subreddit.stream.comments(skip_existing=True, pause_after=0):
        if comm is None:
            continue
        if comm.author == reddit.user.me():
            logging.info('Comment was posted by this bot')
            continue
        if comm.author.name == reddit.user.me().name:
            logging.info('Comment was posted by this bot name')
            continue

        logging.info('Found comment')

        # TODO more debug info about comment
        logging.debug('Comment author: "%s"', comm.author.name)
        logging.debug('Comment text: "%s"', comm.body)

        if not marks_as_solved(comm):
            # Skip this "!solved" comment
            logging.info('Comment does not mark issue as solved')
            continue
        logging.info('Comment marks issue as solved')

        if is_mod_comment(comm):
            logging.info('Comment was submitted by mod')
        elif is_first_solution(comm):
            logging.info('Comment is the first to mark the issue as solved')
        else:
            # Skip this "!solved" comment
            logging.info('Comment is NOT the first to mark the issue as solved')
            continue
        log_solution_info(comm)

        solver = find_solver(comm)
        db.add_solution(comm.submission, comm.parent(), comm, solver)
        logging.info('Added point for user "%s"', solver.name)

        points = db.get_points(solver)
        logging.info('Total points for user "%s": %d', solver.name, points)
        level_info = level.user_level_info(points, levels)

        # Reply to the comment marking the submission as solved
        reply_body = reply.make(solver,
                                points,
                                level_info,
                                feedback_url=cfg.feedback_url,
                                scoreboard_url=cfg.scoreboard_url)
        try:
            comm.reply(reply_body)
            logging.info('Replied to the comment')
            logging.debug('Reply body: %s', reply_body)
        except praw.exceptions.APIException as e:
            logging.error('Unable to reply to comment: %s', e)
            db.remove_solution(comm.submission, comm.parent(), comm, solver)
            logging.error('Removed point that was just awarded to user "%s"', solver.name)
            logging.error('Skipping comment')
            continue

        # Check if (non-mod) user flair should be updated to new level
        lvl = level_info.current
        if lvl and lvl.points == points:
            logging.info('User reached level: %s', lvl.name)
            if not subreddit.moderator(redditor=solver):
                logging.info('User is not mod; setting flair')
                logging.info('Flair text: %s', lvl.name)
                logging.info('Flair template ID: %s', lvl.flair_template_id)
                subreddit.flair.set(solver,
                                    text=lvl.name,
                                    flair_template_id=lvl.flair_template_id)
            else:
                logging.info('Solver is mod; don\'t alter flair')


### Reddit Comment Functions ###

SolutionResponseRule = namedtuple('SolutionResponseRule',
                                  'description success_msg failure_msg check')

OP_RESPONSE_RULES = [
    SolutionResponseRule(
        'user "solved" pattern',
        'Comment contains user "solved" pattern',
        'Comment does not contain user "solved" pattern',
        lambda c: SOLVED_PATTERN.search(c.body),
    ),
    SolutionResponseRule(
        'is a reply (not top-level)',
        'Comment is a reply to another comment',
        'Comment is a top-level comment',
        lambda c: not c.is_root,
    ),
    SolutionResponseRule(
        'author is OP',
        'Comment author is submission OP',
        'Comment author is not submission OP',
        lambda c: c.is_submitter,
    ),
    SolutionResponseRule(
        "OP can't solve own problem",
        'Submission OP is different from solution author',
        'Submission OP is marking own comment as solution',
        lambda c: not c.is_root and not c.parent().is_submitter,
    ),
]

MOD_RESPONSE_RULES = [
    SolutionResponseRule(
        'contains mod "solved" pattern',
        'Comment contains mod "solved" pattern',
        'Comment does not contain mod "solved" pattern',
        lambda c: MOD_SOLVED_PATTERN.search(c.body),
    ),
    SolutionResponseRule(
        'is a reply (not top-level)',
        'Comment is a reply to another comment',
        'Comment is a top-level comment',
        lambda c: not c.is_root,
    ),
    SolutionResponseRule(
        'author is mod',
        'Comment author is a mod',
        'Comment author is not a mod',
        # TODO Initialize rules in a function so that they can include other
        # functions
        lambda c: is_mod_comment(c),
    ),
]

# GENERAL_RESPONSE_RULES = []


def check_rules(rules, comment):
    all_rules_passed = True
    for rule in rules:
        rule_passed = rule.check(comment)
        logging.info(rule.success_msg if rule_passed else rule.failure_msg)
        all_rules_passed = all_rules_passed and rule_passed
    return all_rules_passed


def marks_as_solved(comment):
    """Return True if the comment meets the criteria for marking the submission
    as solved, False otherwise.
    """
    # TODO should enforce that only one or the other can pass?
    op_rules_pass = check_rules(OP_RESPONSE_RULES, comment)
    if op_rules_pass:
        logging.info('OP marking submission as solved')

    mod_rules_pass = check_rules(MOD_RESPONSE_RULES, comment)
    if mod_rules_pass:
        logging.info('Mod marking submission as solved')

    return op_rules_pass or mod_rules_pass


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
    # TODO plz make this better someday
    return solved_comment.parent().author


### Print & Logging Functions ###


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
    print_separator_line()


def log_solution_info(comm):
    logging.info('Submission solved')
    logging.debug('Solution comment:')
    logging.debug('Author: %s', comm.parent().author.name)
    logging.debug('Body:   %s', comm.parent().body)

