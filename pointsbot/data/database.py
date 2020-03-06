import functools
import os.path
import sqlite3 as sqlite

### Decorators ###


def transaction(func):
    @functools.wraps(func)
    def newfunc(self, *args, **kwargs):
        created_conn = False
        if not self.conn:
            self.conn = sqlite.connect(self.path)
            self.conn.row_factory = sqlite.Row
            self.cursor = self.conn.cursor()
            created_conn = True

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

    SCHEMA_VERSION = '0.1'

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

    def add_point(self, redditor):
        return self._update_points(redditor, 1)

    def remove_point(self, redditor):
        return self._update_points(redditor, -1)

    @transaction
    def _update_points(self, redditor, points_modifier):
        """points_modifier is positive to add points, negative to subtract."""
        points = self.get_points(redditor, add_if_none=True)
        params = {
            'id': redditor.id,
            'name': redditor.name,
            'points': points + points_modifier,
        }
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
        row = self.cursor.fetchone()
        if row:
            points = row['points']
        elif add_if_none:
            points = 0
            self.add_redditor(redditor)

        return points


