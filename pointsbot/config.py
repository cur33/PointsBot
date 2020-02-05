import os
import os.path
# from os.path import abspath, dirname, expanduser, join

import toml

from .level import Level

### Globals ###

# ROOTPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

### Classes ###


class Config:

    DATADIR = os.path.join(os.path.expanduser('~'), '.pointsbot')
    PATH = os.path.join(DATADIR, 'pointsbot.toml')

    # Default config vals
    DEFAULT_DBPATH = os.path.join(DATADIR, 'pointsbot.db')

    def __init__(self, subreddit, client_id, client_secret, username, password,
                 levels, database_path=DEFAULT_DBPATH):
        self.subreddit = subreddit
        self.database_path = database_path

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        self.levels = levels

    @classmethod
    def load(cls, filepath=PATH):
        obj = toml.load(filepath)

        # Create list of level objects, in ascending order by point value
        levels = []
        for lvl in obj['levels']:
            flair_template_id = lvl['flair_template_id']
            if flair_template_id == "":
                flair_template_id = None
            levels.append(Level(lvl['name'], lvl['points'], flair_template_id))
        levels.sort(key=lambda l: l.points)

        database_path = os.path.join(cls.DATADIR, obj['filepaths']['database'])

        return cls(
            obj['core']['subreddit'],
            obj['credentials']['client_id'],
            obj['credentials']['client_secret'],
            obj['credentials']['username'],
            obj['credentials']['password'],
            levels,
            database_path=database_path,
        )

    @classmethod
    def dump(cls, obj, filepath=PATH):
        pass


