import configparser
import os.path
# from os.path import abspath, dirname, join

from .level import Level

### Globals ###

ROOTPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIGPATH = os.path.join(ROOTPATH, 'pointsbot.ini')
# CONFIGPATH = abspath(join(dirname(__file__), '..', 'pointsbot.ini'))

# TODO add default config values to pass to configparser

### Classes ###


class Config:

    def __init__(self, praw_site_name='', subreddit_name='', database_path='',
                 levels=None):
        self.praw_site_name = praw_site_name
        self.subreddit_name = subreddit_name
        self.database_path = database_path
        self.levels = levels if levels is not None else []

    @classmethod
    def from_configparser(cls, config):
        database_path = os.path.join(ROOTPATH, config['Core']['database_name'])

        # Get the user flair levels in ascending order by point value
        # TODO Make levels a dict instead
        levels = []
        for opt in config.options('Levels'):
            name, points = opt.title(), config.getint('Levels', opt)
            levels.append(Level(name, points))
        levels.sort(key=lambda lvl: lvl.points)

        return cls(
            praw_site_name=config['Core']['praw_site_name'],
            subreddit_name=config['Core']['subreddit_name'],
            database_path=database_path,
            levels=levels,
        )


### Functions ###


def load():
    config = configparser.ConfigParser()
    config.read(CONFIGPATH)
    return Config.from_configparser(config)


