"""Common methods across test suites.

Since many tests need a praw.Reddit instance, they therefore also need access to
config, unfortunately. It would be better if insted of using config, this would
just access the config file directly and extract only the needed info, the same
way config does.
"""
import praw

import context
import pointsbot.bot as bot
import pointsbot.config as config


def get_reddit_instance():
    cfg = config.load()
    return praw.Reddit(client_id=cfg.client_id,
                       client_secret=cfg.client_secret,
                       user_agent=bot.USER_AGENT)


'''
class MockSubreddit:
    pass


class MockRedditor:
    pass


class MockSubmission:
    pass


class MockComment:

    def __init__(self, author, body, submission, subreddit, is_root=True,
                 is_submitter=False, parent_comment=None):
        self.author = author
        self.body = body
        self.submission = submission
        self.subreddit = subreddit
        self.is_root = is_root
        self.is_submitter = is_submitter
        self.parent_comment = parent_comment

    def parent(self):
        return self.parent_comment
'''
