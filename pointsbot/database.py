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
import functools
import os.path
import sqlite3 as sqlite

### Globals ###

# TODO put name/path in a config file?
DB_NAME = 'pointsbot.db'
DB_PATH = DB_NAME

DB_SCHEMA = '''
    CREATE TABLE IF NOT EXISTS redditor_points (
        id TEXT UNIQUE NOT NULL,
        name TEXT UNIQUE NOT NULL,
        points INTEGER DEFAULT 0
    )
'''

### Decorators ###


def transaction(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        conn = sqlite.connect(DB_PATH)
        conn.row_factory = sqlite.Row
        cursor = conn.cursor()

        ret = func(cursor, *args, **kwargs)

        cursor.close()
        if conn.in_transaction:
            conn.commit()
        conn.close()

        return ret
    return newfunc


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

