"""Note: With the exception of SQLite-specific fields like `rowid`, any `.*id`
fields refer to Reddit object ids.
"""
import datetime
import functools
import os.path
import sqlite3 as sqlite

from . import migrations

### Decorators ###


# The argument should be a method, not just any function.
# Apply this to any method that will need access to a cursor or conn object.
def transaction(func):
    @functools.wraps(func)
    def newfunc(self, *args, **kwargs):
        created_conn = False
        if not self.conn:
            self.conn = sqlite.connect(self.path)
            self.conn.row_factory = sqlite.Row
            self.cursor = self.conn.cursor()
            created_conn = True

        exc = None
        try:
            ret = func(self, *args, **kwargs)
        except Exception as e:
            exc = e

        if exc:
            self.conn.rollback()
        elif self.conn.in_transaction:
            self.conn.commit()

        # Don't check for exception here; if didn't create conn, then another
        # transaction method will catch this exception, do cleanup, and raise
        # the exception again.
        if created_conn:
            self.cursor.close()
            self.conn.close()
            self.cursor = self.conn = None

        if exc:
            raise exc

        return ret
    return newfunc


### Data Structures ###


class SchemaVersion:

    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'

    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)


class Database:

    #  SCHEMA_VERSION = '0.1.0'
#
    #  SCHEMA = '''
        #  CREATE TABLE IF NOT EXISTS redditor_points (
            #  id TEXT UNIQUE NOT NULL,
            #  name TEXT UNIQUE NOT NULL,
            #  points INTEGER DEFAULT 0
        #  )
    #  '''

    def __init__(self, dbpath):
        self.path = dbpath
        self.conn = None
        self.cursor = None
        self.schema_version = None

        if os.path.exists(self.path):
            # TODO make schema_version a read-only property instead?
            self._determine_schema_version()
        self._apply_any_migrations()

    # TODO make schema_version a read-only property instead
    @transaction
    def _determine_schema_version(self):
        try:
            self.cursor.execute('SELECT major, minor, patch FROM db_version')
            self.schema_version = SchemaVersion(*self.cursor.fetchone())
        except:
            # The database exists, but has no schema version; therefore, it must
            # be the first version
            self.schema_version = SchemaVersion(0, 1, 0)

    @transaction
    def _migrate(self, schema_version, sql_statements):
        # TODO only works if arg is a SchemaVersion
        #  if self.schema_version and self.schema_version >= schema_version:
            #  return

        for stmt in sql_statements:
            try:
                self.cursor.execute(stmt)
            except Exception as e:
                msg = f'Database migration failed on command: "{stmt}"'
                raise Exception(msg) from e

    @transaction
    def _apply_any_migrations(self):
        # Assume database doesn't exist; do all migrations
        #  if not self.schema_version:
        migrations_to_do = migrations.MIGRATIONS
        #  else:
        if self.schema_version:
            schema_string = str(self.schema_version)
            for ndx, migration in enumerate(migrations.MIGRATIONS):
                if migration[0] == schema_string:
                    #  migrations_to_do = migrations.MIGRATIONS[ndx+1:]
                    migrations_to_do = migrations_to_do[ndx+1:]
                    break

        if migrations_to_do:
            for schema_version, sql_statements in migrations_to_do:
                self._migrate(schema_version, sql_statements)

        #  migration_ndx = 0
        #  if self.schema_version:
            #  schema_string = str(self.schema_version)
            #  for ndx, migration in enumerate(migrations.MIGRATIONS):
                #  if migration[0] == schema_string:
                    #  # Add one to not repeat the migration for current schema
                    #  migration_ndx = ndx + 1
                    #  break

    ### Redditor Methods ###

    @transaction
    def add_redditor(self, redditor):
        insert_stmt = '''
            INSERT OR IGNORE INTO redditor (id, name)
            VALUES (:id, :name)
        '''
        self.cursor.execute(insert_stmt, {'id': redditor.id, 'name': redditor.name})
        return self.cursor.rowcount

    def add_points(self, redditor, points):
        return self._update_points(redditor, points)

    def remove_points(self, redditor, points):
        return self._update_points(redditor, points)

    @transaction
    def _update_points(self, redditor, points_modifier):
        """points_modifier is positive to add points, negative to subtract."""
        # points = self.get_points(redditor, add_if_none=True)
        cur_points_modifier = self.get_points_modifier(redditor)
        params = {
            'id': redditor.id,
            'name': redditor.name,
            # 'points': points + points_modifier,
            'points_modifier': cur_points_modifier + points_modifier,
        }
        update_stmt = '''
            UPDATE redditor
            SET points_modifier = :points_modifier
            WHERE id = :id AND name = :name
        '''
        self.cursor.execute(update_stmt, params)
        return self.cursor.rowcount

    @transaction
    def get_points(self, redditor):
        stmt = '''
            SELECT
                COUNT(solved_submission.id) as num_solutions,
                redditor.points_modifier as points_modifier
            FROM
                (redditor JOIN solved_submission ON (redditor.rowid = solved_submission.solver))
            WHERE
                redditor.id = :solver_id AND redditor.name = :solver_name
        '''
        params = {
            'solver_id': redditor.id,
            'solver_name': redditor.name,
        }
        self.cursor.execute(stmt, params)
        row = self.cursor.fetchone()
        if row:
            num_solutions, points_modifier = row['num_solutions'], row['points_modifier']
        else:
            num_solutions, points_modifier = 0, 0
        return num_solutions + points_modifier

        #  # Get redditor's rowid first
        #  params = {'id': redditor.id, 'name': redditor.name}
        #  stmt = '''
            #  SELECT rowid
            #  FROM redditor
            #  WHERE id = :id AND name = :name
        #  '''
        #  self.cursor.execute(stmt, params)
        #  redditor_rowid = self.cursor.fetchone()['rowid']
#
        #  params = {'solver': redditor_rowid}
        #  stmt = '''
            #  SELECT COUNT(id)
            #  FROM solved_submission
        #  '''

    #  @transaction
    #  def get_points(self, redditor, add_if_none=False):
        #  params = {'id': redditor.id, 'name': redditor.name}
        #  select_stmt = '''
            #  SELECT points
            #  FROM redditor
            #  WHERE id = :id AND name = :name
        #  '''
        #  self.cursor.execute(select_stmt, params)
        #  row = self.cursor.fetchone()
        #  if row:
            #  points = row['points']
        #  elif add_if_none:
            #  points = 0
            #  self.add_redditor(redditor)
#
        #  return points

    @transaction
    def get_points_modifier(self, redditor):
        params = {'id': redditor.id, 'name': redditor.name}
        select_stmt = '''
            SELECT points_modifier
            FROM redditor
            WHERE id = :id AND name = :name
        '''
        self.cursor.execute(select_stmt, params)
        row = self.cursor.fetchone()
        if row:
            points_modifier = row['points_modifier']
        else:
            msg = f'Redditor "{redditor.name}" ({redditor.id}) not found'
            raise Exception(msg)

        return points_modifier

    ### Solution Methods ###

    @transaction
    def add_solution(self, submission, solution_comment, solved_comment, solver):
        select_params = {'id': solver.id, 'name': solver.name}
        select_stmt = '''
            SELECT rowid
            FROM redditor
            WHERE id = :id AND name = :name
        '''
        self.cursor.execute(select_stmt, select_params)
        row = self.cursor.fetchone()

        if not row:
            # Add redditor to database
            insert_stmt = '''
                INSERT INTO redditor(id, name)
                VALUES (:id, :name)
            '''
            self.cursor.execute(insert_stmt, select_params)

            # Retrieve rowid for newly added redditor
            self.cursor.execute(select_stmt, select_params)
            row = self.cursor.fetchone()

        solver_id = row['rowid']

        # cur-debug
        print()
        print('Date')
        print(solved_comment.created_utc)
        print(type(solved_comment.created_utc))
        print()
        solved_datetime = datetime.datetime.utcfromtimestamp(solved_comment.created_utc)
        datetime_iso = solved_datetime.isoformat()

        insert_params = {
            'id': submission.id,
            'solution_comment_id': solution_comment.id,
            'solved_comment_id': solved_comment.id,
            'solver': solver_id,
            'datetime_iso': datetime_iso,
        }
        insert_stmt = '''
            INSERT INTO solved_submission(id, solution_comment_id,
                solved_comment_id, solver, datetime_iso)
            VALUES (:id, :solution_comment_id, :solved_comment_id, :solver,
                :datetime_iso)
        '''
        self.cursor.execute(insert_stmt, insert_params)
        return self.cursor.rowcount

    # def remove_solution(self, submission):
    @transaction
    def remove_solution(self, submission, solution_comment, solved_comment, solver):
        stmt = '''
            DELETE FROM solved_submission
            WHERE id = :submission_id
                AND solution_comment_id = :solution_comment_id
                AND solved_comment_id = :solved_comment_id
        '''
        params = {
            'submission_id': submission.id,
            'solution_comment_id': solution_comment.id,
            'solved_comment_id': solved_comment.id,
        }
        self.cursor.execute(stmt, params)
        return self.cursor.fetchone().rowcount


