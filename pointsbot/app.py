# from . import bot, config, reply_factory, level_factory
from . import newbot, newconfig, reply_factory, level_factory
# from . import bot, config
# from . import newbot, newconfig
from .data import database
from .models import model
# from .models import redditor, solved_submission


def run():
    cfg = newconfig.load()
    # Set database path
    level = level_factory.get_factory(cfg.levels)
    reply = reply_factory.get_factory(cfg.feedback_url, cfg.scoreboard_url)

    # Make bot w/ config values, level, and reply
    bot = newbot.Bot()
    bot.run()


if __name__ == '__main__':
    run()