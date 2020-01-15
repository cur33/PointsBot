'''
    A bot for Reddit to award points to helpful subreddit members.
    Copyright (C) 2020  Collin U. Rapp

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import re

import praw

from . import comment, database

### Globals ###

# SUBREDDIT_NAME = 'MinecraftHelp'
SUBREDDIT_NAME = 'GlipGlorp7BotTests'
PRAW_SITE_NAME = 'testbot'

# TODO Make LEVELS a dict instead
# TODO Could also make a Level class or namedtuple that contains more info, e.g.
# flair css or template id
LEVELS = [
    ('Helper', 5),
    ('Trusted Helper', 15),
    ('Super Helper', 40),
]

### Main Function ###


def run():
    # Connect to Reddit
    reddit = praw.Reddit(site_name=PRAW_SITE_NAME)
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    # xdebugx
    print(f'Connected to reddit as {reddit.user.me()}')
    print(f'Read-only? {reddit.read_only}')
    print(f'Watching subreddit {subreddit.title}')
    print(f'Mod? {bool(subreddit.moderator(redditor=reddit.user.me()))}')

    database.init()

    # Initialize database
    #if not database.exists():
        #database.create()

    # The pattern to look for in comments when determining whether to award a point
    # solved_pat = re.compile('!solved', re.IGNORECASE)
    solved_pat = re.compile('![Ss]olved')

    # Monitor new comments for confirmed solutions
    for comm in subreddit.stream.comments(skip_existing=True):
        # xdebugx
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
                # if (subcomm.is_submitter
                        # and subcomm.id != comm.id
                        # and not subcomm.is_root
                        # and solved_pat.search(subcomm.body)
                        # and subcomm.created_utc < comm.created_utc):
                if (subcomm.id != comm.id
                        and marks_as_solved(subcomm, solved_pat)
                        and subcomm.created_utc < comm.created_utc):
                    # There is an earlier comment for the same submission
                    # already marked as a solution by the OP
                    is_first_solution = False
                    break

            if not is_first_solution:
                # Skip this "!solved" comment and wait for the next
                # xdebugx
                print('This is not the first solution')
                continue

            # xdebugx
            print('This is the first solution')
            print_solution_info(comm)

            solution = comm.parent()
            solver = solution.author
            print(f'Adding point for {solver.name}')
            database.add_point(solver)
            points = database.get_redditor_points(solver)
            print(f'Points for {solver.name}: {points}')

            # Reply to the comment containing the solution
            reply_body = comment.make(solver, points, LEVELS)
            print(f'Replying with: "{reply_body}"')
            solution.reply(reply_body)

            # Check if (non-mod) user flair should be updated to new level
            for levelname, levelpoints in LEVELS:
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
                        # xdebugx
                        print('Don\'t update flair b/c user is mod')

                    # Don't need to check the rest of the levels
                    break
        else:
            # xdebugx
            print('Not a "!solved" comment')


### Auxiliary Functions ###


def marks_as_solved(comment, solved_pattern):
    '''Return True if  not top-level comment, from OP, contains "!Solved"; False
    otherwise.
    '''
    #comment.refresh()
    return (not comment.is_root
            and comment.is_submitter
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


