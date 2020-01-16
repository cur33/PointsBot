import functools
import os.path
import sqlite3 as sqlite

### Globals ###

# TODO put name/path in a config file?
# DB_NAME = 'pointsbot.db'
# DB_PATH = DB_NAME

"""
DB_SCHEMA = '''
    CREATE TABLE IF NOT EXISTS redditor_points (
        id TEXT UNIQUE NOT NULL,
        name TEXT UNIQUE NOT NULL,
        points INTEGER DEFAULT 0
    )
'''
"""

### Decorators ###

# TODO read config here and create a closure instead of using DB_PATH?
# or could do it in the init function somehow?
# It seems like the only alternatives would be an OO aproach or global variable


"""
def transaction(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        conn = sqlite.connect(DB_PATH)
        conn.row_factory = sqlite.Row
        cursor = conn.cursor()

        ret = func(cursor, *args, **kwargs)

        if conn.in_transaction:
            conn.commit()
        cursor.close()
        conn.close()

        return ret
    return newfunc
"""


# TODO create a method decorator for Database methods

def transaction(func):
    @functools.wraps(func)
    def newfunc(self, *args, **kwargs):
        created_conn = False
        if not self.conn:
            self.conn = sqlite.connect(self.path)
            self.conn.row_factory = sqlite.Row
            self.cursor = self.conn.cursor()
            created_conn = True

        # ret = func(cursor, *args, **kwargs)
        ret = func(self, *args, **kwargs)

        if self.conn.in_transaction:
            self.conn.commit()

        if created_conn:
            self.cursor.close()
            self.conn.close()
            self.cursor = self.conn = None

        return ret
    return newfunc


### Classes ###


class Database:

    SCHEMA = '''
        CREATE TABLE IF NOT EXISTS redditor_points (
            id TEXT UNIQUE NOT NULL,
            name TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 0
        )
        '''

    def __init__(self, dbpath):
        self.path = dbpath
        self.conn = None
        self.cursor = None

        if not os.path.exists(self.path):
            self._create()

    @transaction
    def _create(self):
        self.cursor.execute(self.SCHEMA)

    @transaction
    def add_redditor(self, redditor):
        insert_stmt = '''
            INSERT OR IGNORE INTO redditor_points (id, name)
            VALUES (:id, :name)
            '''
        self.cursor.execute(insert_stmt, {'id': redditor.id, 'name': redditor.name})
        return self.cursor.rowcount

    @transaction
    def add_point(self, redditor):
        points = self.get_points(redditor, add_if_none=True)
        params = {'id': redditor.id, 'name': redditor.name, 'points': points + 1}
        update_stmt = '''
            UPDATE redditor_points
            SET points = :points
            WHERE id = :id AND name = :name
            '''
        self.cursor.execute(update_stmt, params)
        return self.cursor.rowcount

    @transaction
    def get_points(self, redditor, add_if_none=False):
        params = {'id': redditor.id, 'name': redditor.name}
        select_stmt = '''
            SELECT points
            FROM redditor_points
            WHERE id = :id AND name = :name
            '''
        self.cursor.execute(select_stmt, params)
        row = self.cursor.fetchone()   # TODO check if more than one row
        if row:
            points = row['points']
        elif add_if_none:
            points = 0
            self.add_redditor(redditor)

        return points

"""

### Private Functions ###

# These functions are intended for internal use, since they need to be explicity
# passed a database cursor. The public methods below are wrapped with the
# transaction decorator to remove the need for keeping a connection or cursor
# opened for the entire life of the program.


def _init(cursor):
    if not exists():
        cursor.execute(DB_SCHEMA)


def _add_redditor(cursor, redditor):
    insert_stmt = '''
        INSERT OR IGNORE INTO redditor_points (id, name)
        VALUES (:id, :name)
        '''
    cursor.execute(insert_stmt, {'id': redditor.id, 'name': redditor.name})
    return cursor.rowcount


def _add_point(cursor, redditor):
    points = _get_redditor_points(cursor, redditor, add_if_none=True)
    params = {'id': redditor.id, 'name': redditor.name, 'points': points + 1}
    update_stmt = '''
        UPDATE redditor_points
        SET points = :points
        WHERE id = :id AND name = :name
        '''
    cursor.execute(update_stmt, params)
    return cursor.rowcount


def _get_redditor_points(cursor, redditor, add_if_none=False):
    params = {'id': redditor.id, 'name': redditor.name}
    select_stmt = '''
        SELECT points
        FROM redditor_points
        WHERE id = :id AND name = :name
        '''
    cursor.execute(select_stmt, params)
    row = cursor.fetchone()   # TODO check if more than one row
    if row:
        points = row['points']
    elif add_if_none:
        points = 0
        _add_redditor(cursor, redditor)

    return points


### Public Functions ###


def exists():
    return os.path.exists(DB_PATH)


# Public wrappers for the database access functions
init                = transaction(_init)
add_redditor        = transaction(_add_redditor)
add_point           = transaction(_add_point)
get_redditor_points = transaction(_get_redditor_points)

"""

