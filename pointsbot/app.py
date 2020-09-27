import logging

import praw
import prawcore

# from . import bot, config, newreply, newlevel
from . import newbot, newconfig, newreply, newlevel
from .data import database
from .models import model
# from .models import redditor, solved_submission


def run():
    cfg = newconfig.load()

    # TODO Set database path in model base class?
    level_factory = newlevel.get_factory(cfg.levels)
    reply_factory = newreply.get_factory(cfg.feedback_url, cfg.scoreboard_url)

    # Make bot w/ config values, level, and reply
    while True:
        try:
            reddit = praw.Reddit(client_id=cfg.client_id,
                                 client_secret=cfg.client_secret,
                                 username=cfg.username,
                                 password=cfg.password,
                                 user_agent=cfg.USER_AGENT)

            logging.info('Connected to Reddit as %s', reddit.user.me())
            access_type = 'read-only' if reddit.read_only else 'write'
            logging.info(f'Has {access_type} access to Reddit')

            subreddit = reddit.subreddit(cfg.subreddit)
            logging.info('Watching subreddit %s', subreddit.title)
            is_mod = subreddit.moderator(redditor=reddit.user.me())
            logging.info(f'Is {"" if is_mod else "NOT "} moderator for subreddit')

            bot = newbot.Bot(reddit, subreddit, level_factory, reply_factory)
            bot.run()
        except prawcore.exceptions.RequestException as e:
            logging.error('Unable to connect to Reddit')
            logging.error('Error message: %s', e)
            logging.error('Trying again')
        except prawcore.exceptions.ServerError as e:
            logging.error('Lost connection to Reddit')
            logging.error('Error message: %s', e)
            logging.error('Attempting to reconnect')


if __name__ == '__main__':
    run()
