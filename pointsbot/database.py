import datetime
import functools
import logging
import os.path
import re
import sqlite3 as sqlite

### Decorators ###


def transaction(func):
    """Use this decorator on any methods that needs to query the database to ensure that connections
    are properly opened and closed, without being left open unnecessarily.
    """
    @functools.wraps(func)
    def newfunc(self, *args, **kwargs):
        created_conn = False
        if not self.conn:
            self.conn = sqlite.connect(self.path)
            self.conn.row_factory = sqlite.Row
            self.cursor = self.conn.cursor()
            created_conn = True

        return_value = func(self, *args, **kwargs)
        # try:
        #     return_value = func(self, *args, **kwargs)
        # except Exception as e:
        #     if self.conn.in_transaction:
        #         self.conn.rollback()
        #     if created_conn:
        #         self.cursor.close()
        #         self.conn.close()
        #         self.cursor = self.conn = None
        #     raise e

        if self.conn.in_transaction:
            self.conn.commit()

        if created_conn:
            self.cursor.close()
            self.conn.close()
            self.cursor = self.conn = None

        return return_value

    return newfunc


### Classes ###


# @functools.total_ordering
class DatabaseVersion:

    PRE_RELEASE_NAME_ORDER_NUMBER = {
        None: 0,
        'alpha': 1,
        'beta': 2,
        'rc': 3
    }

    def __init__(self, major, minor, patch, pre_release_name=None, pre_release_number=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre_release_name = pre_release_name
        self.pre_release_number = pre_release_number

    def __lt__(self, other):
        # self_tuple = (self.major, self.minor, self.patch, self.PRE_RELEASE_NAME_ORDER_NUMBER[self.pre_release_name], self.pre_release_number)
        # other_tuple = (other.major, other.minor, other.patch, self.PRE_RELEASE_NAME_ORDER_NUMBER[other.pre_release_name], other.pre_release_number)
        return self._to_tuple() < other._to_tuple()

    def __eq__(self, other):
        # self_tuple = (self.major, self.minor, self.patch, self.PRE_RELEASE_NAME_ORDER_NUMBER[self.pre_release_name], self.pre_release_number)
        # other_tuple = (other.major, other.minor, other.patch, self.PRE_RELEASE_NAME_ORDER_NUMBER[other.pre_release_name], other.pre_release_number)
        return self._to_tuple() == other._to_tuple()

    def __hash__(self):
        # self_tuple = (self.major, self.minor, self.patch, self.PRE_RELEASE_NAME_ORDER_NUMBER[self.pre_release_name], self.pre_release_number)
        return hash(self._to_tuple())

    def _to_tuple(self):
        return (self.major, self.minor, self.patch, self.PRE_RELEASE_NAME_ORDER_NUMBER[self.pre_release_name], self.pre_release_number)

    def __str__(self):
        version_string = f'{self.major}.{self.minor}.{self.patch}'
        if self.pre_release_name is not None:
            version_string += f'-{self.pre_release_name}'
            if self.pre_release_number is not None:
                version_string += f'.{self.pre_release_number}'
        return version_string

    @classmethod
    def from_string(cls, version_string):
        match = re.match(r'(\d+).(\d+).(\d+)(?:-([:alpha:]+)(?:.(\d+))?)?', version_string)
        if not match:
            return None
        groups = match.groups()
        return cls(int(groups[0]), int(groups[1]), int(groups[2]), groups[3], int(groups[4]))


class Database:

    LATEST_VERSION = DatabaseVersion(0, 2, 0)

    # TODO now that I'm separating these statements by version, I could probably make these
    # scripts instead of lists of individual statements...
    SCHEMA_VERSION_STATEMENTS = {
        DatabaseVersion(0, 1, 0): [
            '''
            CREATE TABLE IF NOT EXISTS redditor_points (
                id TEXT UNIQUE NOT NULL,
                name TEXT UNIQUE NOT NULL,
                points INTEGER DEFAULT 0
            )
            '''
        ],
        DatabaseVersion(0, 2, 0): [
            '''
            CREATE TABLE IF NOT EXISTS bot_version (
                major INTEGER NOT NULL,
                minor INTEGER NOT NULL,
                patch INTEGER NOT NULL,
                pre_release_name TEXT,
                pre_release_number INTEGER
            )
            ''',
            '''
            ALTER TABLE redditor_points RENAME TO redditor
            ''',
            '''
            CREATE TABLE IF NOT EXISTS submission (
                id TEXT UNIQUE NOT NULL,
                author_id TEXT UNIQUE NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS comment (
                id TEXT UNIQUE NOT NULL,
                author_id TEXT NOT NULL,
                author_rowid INTEGER,   -- May be NULL **for now**
                created_at_datetime TEXT NOT NULL,
                FOREIGN KEY (author_rowid) REFERENCES redditor (rowid) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS solution (
                submission_rowid INTEGER NOT NULL,
                author_rowid INTEGER NOT NULL,
                comment_rowid INTEGER NOT NULL,
                chosen_by_comment_rowid INTEGER NOT NULL,
                removed_by_comment_rowid INTEGER,
                FOREIGN KEY (submission_rowid) REFERENCES submission (rowid) ON DELETE CASCADE,
                FOREIGN KEY (author_rowid) REFERENCES redditor (rowid) ON DELETE CASCADE,
                FOREIGN KEY (comment_rowid) REFERENCES comment (rowid) ON DELETE CASCADE,
                FOREIGN KEY (chosen_by_comment_rowid) REFERENCES comment (rowid) ON DELETE SET NULL,
                FOREIGN KEY (removed_by_comment_rowid) REFERENCES comment (rowid) ON DELETE SET NULL,
                PRIMARY KEY (submission_rowid, author_rowid)
            )
            '''
        ]
    }

    def __init__(self, dbpath):
        self.path = dbpath
        self.conn = None
        self.cursor = None

        if not os.path.exists(self.path):
            logging.info('No database found; creating...')
            self._run_migrations()
            logging.info('Successfully created database')
        else:
            logging.info(f'Using existing database: {self.path}')
            current_version = self._get_current_version()
            if current_version != self.LATEST_VERSION:
                logging.info('Newer database version exists; migrating...')
                self._run_migrations(current_version)
                logging.info('Successfully completed all migrations')

    @transaction
    def _run_migrations(self, current_version=None):
        if not current_version:
            current_version = DatabaseVersion(0, 0, 0)
        logging.info(f'Current database version: {current_version}')

        versions = sorted(v for v in self.SCHEMA_VERSION_STATEMENTS if current_version < v)
        for v in versions:
            logging.info(f'Beginning migration to version: {v}...')
            for sql_stmt in self.SCHEMA_VERSION_STATEMENTS[v]:
                self.cursor.execute(sql_stmt)
            if DatabaseVersion(0, 1, 0) < v:
                # Only update bot_version table starting at version 0.2.0
                self.cursor.execute('DELETE FROM bot_version')
                params = {
                   'major': v.major,
                   'minor': v.minor,
                   'patch': v.patch,
                   'pre_release_name': v.pre_release_name,
                   'pre_release_number': v.pre_release_number
                }
                insert_stmt = '''
                    INSERT INTO bot_version (major, minor, patch, pre_release_name, pre_release_number)
                    VALUES (:major, :minor, :patch, :pre_release_name, :pre_release_number)
                '''
                self.cursor.execute(insert_stmt, params)
            logging.info(f'Successfully completed migration')

    @transaction
    def _get_current_version(self):
        # self.cursor.execute('select * from sqlite_master')
        # for row in self.cursor.fetchmany():
        #     logging.info(tuple(row))
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'bot_version'")
        has_version_table = self.cursor.fetchone()
        if not has_version_table:
            current_version = DatabaseVersion(0, 1, 0)
        else:
            self.cursor.execute('SELECT major, minor, patch, pre_release_name, pre_release_number FROM bot_version')
            row = self.cursor.fetchone()
            pre_release_number = int(row['pre_release_number']) if row['pre_release_number'] else None
            current_version = DatabaseVersion(int(row['major']), int(row['minor']), int(row['patch']), row['pre_release_name'], pre_release_number)

        return current_version

    ### Public Methods ###

    @transaction
    def add_redditor(self, redditor):
        insert_stmt = '''
            INSERT OR IGNORE INTO redditor (id, name)
            VALUES (:id, :name)
        '''
        self.cursor.execute(insert_stmt, {'id': redditor.id, 'name': redditor.name})
        return self.cursor.rowcount

    @transaction
    def remove_redditor(self, redditor):
        insert_stmt = '''
            DELETE FROM redditor
            WHERE id = :id
                AND name = :name
        '''
        self.cursor.execute(insert_stmt, {'id': redditor.id, 'name': redditor.name})
        return self.cursor.rowcount

    @transaction
    def has_already_solved_once(self, submission, solver):
        select_stmt = '''
            SELECT count(solution.rowid) AS num_solutions
            FROM solution
                JOIN submission ON (solution.submission_rowid = submission.rowid)
                JOIN redditor ON (solution.author_rowid = redditor.rowid)
            WHERE submission.id = :submission_id
                AND redditor.id = :author_id
        '''
        self.cursor.execute(select_stmt, {'submission_id': submission.id, 'author_id': solver.id})
        row = self.cursor.fetchone()
        return row and row['num_solutions'] > 0

    def add_point_for_solution(self, submission, solver, solution_comment, chooser, chosen_by_comment):
        self._add_submission(submission)
        self._add_comment(solution_comment, solver)
        self._add_comment(chosen_by_comment, chooser)

        self._update_points(solver, 1)
        rowcount = self._add_solution(submission, solver, solution_comment, chosen_by_comment)
        if rowcount == 0:
            # Was not able to add solution, probably because user has already solved this submission
            self._update_points(solver, -1)
        # if rowcount > 0:
        #     # TODO update author_rowid for comment?
        return rowcount

    def soft_remove_point_for_solution(self, submission, solver, remover, removed_by_comment):
        self._add_comment(removed_by_comment, remover)
        rowcount = self._soft_remove_solution(submission, solver, removed_by_comment)
        if rowcount > 0:
            rowcount = self._update_points(solver, -1)
        return rowcount

    @transaction
    def add_back_point_for_solution(self, submission, solver):
        self._update_points(solver, 1)
        # submission_rowid = self._get_rowid_from_reddit_id('submission', submission)
        # author_rowid = self._get_rowid_from_reddit_id('redditor', solver)
        submission_rowid = self._get_submission_rowid(submission)
        author_rowid = self._get_redditor_rowid(solver)
        params = {'submission_rowid': submission_rowid, 'author_rowid': author_rowid}
        update_stmt = '''
            UPDATE solution
            SET removed_by_comment_rowid = NULL
            WHERE submission_rowid = :submission_rowid
                AND author_rowid = :author_rowid
        '''
        return self.cursor.execute(update_stmt, params)

    @transaction
    def remove_point_and_delete_solution(self, submission, solver):
        params = {
            # 'submission_rowid': self._get_rowid_from_reddit_id('submission', submission),
            # 'author_rowid': self._get_rowid_from_reddit_id('redditor', solver)
            'submission_rowid': self._get_submission_rowid(submission),
            'author_rowid': self._get_redditor_rowid(solver)
        }
        delete_stmt = '''
            DELETE FROM solution
            WHERE submission_rowid = :submission_rowid
                AND author_rowid = :author_rowid
        '''
        self.cursor.execute(delete_stmt, params)
        return self._update_points(solver, -1)

    @transaction
    def get_points(self, redditor, add_if_none=False):
        params = {'id': redditor.id, 'name': redditor.name}
        select_stmt = '''
            SELECT points
            FROM redditor
            WHERE id = :id AND name = :name
        '''
        self.cursor.execute(select_stmt, params)
        row = self.cursor.fetchone()
        points = 0
        if row:
            points = row['points']
        elif add_if_none:
            self.add_redditor(redditor)

        return points

    ### Private Methods ###

    # @transaction
    # def _get_rowid_from_reddit_id(self, table_name, reddit_object):
    #     params = {'table_name': table_name, 'reddit_id': reddit_object.id}
    #     self.cursor.execute('SELECT rowid FROM :table_name WHERE id = :reddit_id', params)
    #     row = self.cursor.fetchone()
    #     return row['rowid'] if row else None

    # @transaction
    def _get_submission_rowid(self, submission):
        return self._get_rowid_from_reddit_id('SELECT rowid FROM submission WHERE id = :reddit_id', {'reddit_id': submission.id})
        # self.cursor.execute('SELECT rowid FROM submission WHERE id = :reddit_id', {'reddit_id': submission.id})
        # row = self.cursor.fetchone()
        # return row['rowid'] if row else None

    def _get_comment_rowid(self, comment):
        return self._get_rowid_from_reddit_id('SELECT rowid FROM comment WHERE id = :reddit_id', {'reddit_id': comment.id})

    def _get_redditor_rowid(self, redditor):
        return self._get_rowid_from_reddit_id('SELECT rowid FROM redditor WHERE id = :reddit_id', {'reddit_id': redditor.id})

    @transaction
    def _get_rowid_from_reddit_id(self, stmt, params):
        self.cursor.execute(stmt, params)
        row = self.cursor.fetchone()
        return row['rowid'] if row else None

    @transaction
    def _add_comment(self, comment, author):
        params = {
            'id': comment.id,
            'author_id': author.id,
            'created_at_datetime': reddit_datetime_to_iso(comment.created_utc)
        }
        insert_stmt = '''
            INSERT INTO comment (id, author_id, created_at_datetime)
            VALUES (:id, :author_id, :created_at_datetime)
        '''
        self.cursor.execute(insert_stmt, params)
        return self.cursor.rowcount

    @transaction
    def _add_submission(self, submission):
        insert_stmt = '''
            INSERT OR IGNORE INTO submission (id, author_id)
            VALUES (:id, :author_id)
        '''
        self.cursor.execute(insert_stmt, {'id': submission.id, 'author_id': submission.author.id})
        return self.cursor.rowcount

    @transaction
    def _add_solution(self, submission, solver, comment, chosen_by_comment):
        submission_rowid = self._get_submission_rowid(submission)
        author_rowid = self._get_redditor_rowid(solver)
        comment_rowid = self._get_comment_rowid(comment)
        chosen_by_comment_rowid = self._get_comment_rowid(chosen_by_comment)
        params = {
            'submission_rowid': submission_rowid,
            'author_rowid': author_rowid,
            'comment_rowid': comment_rowid,
            'chosen_by_comment_rowid': chosen_by_comment_rowid
        }
        insert_stmt = '''
            INSERT INTO solution (submission_rowid, author_rowid, comment_rowid, chosen_by_comment_rowid)
            VALUES (:submission_rowid, :author_rowid, :comment_rowid, :chosen_by_comment_rowid)
        '''
        self.cursor.execute(insert_stmt, params)
        return self.cursor.rowcount

    @transaction
    def _soft_remove_solution(self, submission, solver, removed_by_comment):
        submission_rowid = self._get_submission_rowid(submission)
        author_rowid = self._get_redditor_rowid(solver)
        removed_by_comment_rowid = self._get_comment_rowid(removed_by_comment)
        params = {
            'submission_rowid': submission_rowid,
            'author_rowid': author_rowid,
            'removed_by_comment_rowid': removed_by_comment_rowid,
        }
        update_stmt = '''
            UPDATE solution
            SET removed_by_comment_rowid = :removed_by_comment_rowid
            WHERE submission_rowid = :submission_rowid AND author_rowid = :author_rowid
        '''
        self.cursor.execute(update_stmt, params)
        return self.cursor.rowcount

    @transaction
    def _update_points(self, redditor, points_modifier):
        """points_modifier is positive to add points, negative to subtract."""
        points = self.get_points(redditor, add_if_none=True)
        if points + points_modifier <= 0:
            return self.remove_redditor(redditor)
        else:
            params = {
                'id': redditor.id,
                'name': redditor.name,
                'points': points + points_modifier,
            }
            update_stmt = '''
                UPDATE redditor
                SET points = :points
                WHERE id = :id AND name = :name
            '''
            self.cursor.execute(update_stmt, params)
            return self.cursor.rowcount


### Utility ###


def reddit_datetime_to_iso(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).isoformat()

