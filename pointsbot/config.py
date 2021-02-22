import os
import os.path
from collections import namedtuple
from copy import deepcopy

import toml

from .level import Level

### Globals ###

DATADIR = os.path.join(os.path.expanduser('~'), '.pointsbot')
CONFIGPATH = os.path.join(DATADIR, 'pointsbot.toml')

# Path to the sample config file
# Unused for now
# SAMPLEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
#                                           '..',
#                                           'pointsbot.sample.toml'))

### Primary Functions ###


def load(filepath=CONFIGPATH):
    # Prompt user for config values if file doesn't exist
    if not os.path.exists(filepath):
        datadir = os.path.dirname(filepath)
        if not os.path.exists(datadir):
            os.makedirs(datadir)
        interactive_config(filepath)

    return Config.from_toml(filepath)


### Classes ###


class Config:

    # Default config vals
    DEFAULT_DB_NAME = 'pointsbot.db'
    DEFAULT_LOG_NAME = 'pointsbot.log'

    def __init__(self, filepath, subreddit, client_id, client_secret, username,
                 password, levels, database_path=None, log_path=None,
                 feedback_url=None, scoreboard_url=None, tag_string=None):
        self._filepath = filepath
        self._dirname = os.path.dirname(filepath)

        if not log_path:
            log_path = os.path.join(self._dirname, self.DEFAULT_LOG_NAME)
        elif os.path.isdir(log_path):
            log_path = os.path.join(log_path, self.DEFAULT_LOG_NAME)
        self.log_path = log_path

        # TODO init logging here so it can be used immediately?

        if not database_path:
            database_path = os.path.join(self._dirname, self.DEFAULT_DB_NAME)
        elif os.path.isdir(database_path):
            database_path = os.path.join(database_path, self.DEFAULT_DB_NAME)
        self.database_path = database_path

        self.subreddit = subreddit
        self.feedback_url = feedback_url
        self.scoreboard_url = scoreboard_url

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        self.levels = levels
        if tag_string is None:
            self.tags = None
        else:
            self.tags = tag_string.lower().split(",")

    @classmethod
    def from_toml(cls, filepath):
        obj = toml.load(filepath)

        # Create list of level objects, in ascending order by point value
        levels = []
        for lvl in obj['levels']:
            flair_template_id = lvl.get('flair_template_id', None)
            if flair_template_id == '':
                flair_template_id = None
            levels.append(Level(lvl['name'], lvl['points'], flair_template_id))
        levels.sort(key=lambda l: l.points)

        dbpath = obj['filepaths']['database']
        if dbpath:
            dbpath = os.path.abspath(os.path.expandvars(os.path.expanduser(dbpath)))

        logpath = obj['filepaths']['log']
        if logpath:
            logpath = os.path.abspath(os.path.expandvars(os.path.expanduser(logpath)))

        return cls(
            filepath,
            obj['core']['subreddit'],
            obj['credentials']['client_id'],
            obj['credentials']['client_secret'],
            obj['credentials']['username'],
            obj['credentials']['password'],
            levels,
            database_path=dbpath,
            log_path=logpath,
            feedback_url=obj['links']['feedback'],
            scoreboard_url=obj['links']['scoreboard'],
            tag_string=obj['core']['valid_tags'],
        )

    def save(self):
        obj = deepcopy(vars(self))
        orig_levels, obj['levels'] = obj['levels'], []
        for level in orig_levels:
            obj['levels'].append({
                'name': level.name,
                'points': level.points,
                'flair_template_id': level.flair_template_id
            })

        obj['tags'] = ','.join(obj['tags'])

        with open(self._filepath, 'w') as f:
            toml.dump(obj, f)


### Interactive Config Editing ###


def interactive_config(dest):
    configvals = {
        'core': {},
        'links': {},
        'filepaths': {},
        'credentials': {},
        'levels': [],
    }

    print('\n' + ('#' * 80) + '\nCONFIGURING THE BOT\n' + ('#' * 80) + '\n')
    print('Type a value for each field, then press enter.')
    print('\nIf a field is specified as optional, then you can skip it by just pressing enter.')
    print("\nIt is recommended that you skip any fields that you aren't sure about")

    print('\n*** Core Configuration ***\n')
    configvals['core']['subreddit'] = input('name of subreddit to monitor? ')
    print()
    configvals['filepaths']['database'] = input('database filepath? (optional) ')
    configvals['filepaths']['log'] = input('log filepath? (optional) ')

    print('\n*** Website Links ***\n')
    print('These values should only be provided if you have valid URLs for websites that provide '
          'these services for your subreddit.\n')
    configvals['links']['feedback'] = input('feedback webpage URL? (optional) ')
    configvals['links']['scoreboard'] = input('scoreboard webpage URL? (optional) ')

    print('\n*** Bot account details ***\n')
    configvals['credentials']['client_id'] = input('client_id? ')
    configvals['credentials']['client_secret'] = input('client_secret? ')
    configvals['credentials']['username'] = input('bot username? ')
    configvals['credentials']['password'] = input('bot password? ')

    print('\n*** Flair Levels ***\n')
    print('These fields will determine the different levels that your subreddit users can achieve '
          'by earning points.')
    print('\nFor each level, you should provide...')
    print("\t- Level name:        the text that appears in the user's flair")
    print('\t- Level points:      the number of points needed to reach the level')
    print('\t- Flair template ID: (optional) the flair template ID in your')
    print('\t                     subreddit to be used for this level flair')
    print('\nThese may be provided in any order; the bot will sort them later.')
    print('\nDo not provide more than one level with the same number of points.')
    print('\nNote that at the moment, providing a level points value of zero will not set a '
          'default flair, because users must solve at least one issue before the bot will keep '
          'track of their points and set their flair for the first time.')
    print('\nFor any more questions, please refer to the README on the Github page.')

    response = 'y'
    while response.lower().startswith('y'):
        print('\n*** Adding a level ***\n')
        level = {}
        level['name'] = input('Level name? ')
        level['points'] = int(input('Level points? '))
        level['flair_template_id'] = input('Flair template ID? (optional) ')
        configvals['levels'].append(level)

        response = input('\nAdd another level? (y/n) ')

    with open(dest, 'w') as f:
        toml.dump(configvals, f)
    print('#' * 80 + f'\nConfig settings saved to {dest}\n' + '#' * 80)

