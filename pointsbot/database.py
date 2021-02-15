import datetime
import functools
import os.path
import sqlite3 as sqlite
from collections import namedtuple

### Decorators ###


def transaction(func):
    """Use this decorator on any methods that needs to query the database to
    ensure that connections are properly opened and closed.
    """
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

DatabaseVersion = namedtuple('DatabaseVersion', 'major minor patch pre_release_name pre_release_number')


class Database:

    VERSION = DatabaseVersion(0, 2, 0, None, None)

    SCHEMA = '''
        ---------------------------
        -- Schema version: 0.1.0 --
        ---------------------------

        CREATE TABLE IF NOT EXISTS redditor_points (
            id TEXT UNIQUE NOT NULL,
            name TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 0
        );

        ---------------------------
        -- Schema version: 0.2.0 --
        ---------------------------

        -- Tracking bot/db version for potential future use in migrations et al.
        CREATE TABLE IF NOT EXISTS bot_version (
            major INTEGER NOT NULL,
            minor INTEGER NOT NULL,
            patch INTEGER NOT NULL,
            pre_release_name TEXT,
            pre_release_number INTEGER
        );
        INSERT OR IGNORE INTO bot_version (major, minor, patch) VALUES (0, 2, 0);

        ALTER TABLE redditor_points RENAME TO redditor;
        -- TODO rename "id" columns to "reddit_id" for consistency/clarity?
        -- ALTER TABLE redditor RENAME COLUMN id TO reddit_id;

        CREATE TABLE IF NOT EXISTS submission (
            id TEXT UNIQUE NOT NULL,
            author_id TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS comment (
            id TEXT UNIQUE NOT NULL,
            author_id TEXT NOT NULL,
            author_rowid INTEGER,   -- May be NULL **for now**
            created_at_datetime TEXT NOT NULL,
            FOREIGN KEY (author_rowid) REFERENCES redditor (rowid) ON DELETE CASCADE
        );

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
            PRIMARY KEY (submission_rowid, author_rowid) ON DELETE CASCADE 
        );
    '''

    def __init__(self, dbpath):
        self.path = dbpath
        self.conn = None
        self.cursor = None

        if not os.path.exists(self.path):
            self._create()
        else:
            self._migrate_if_necessary()

    @transaction
    def _create(self):
        self.cursor.execute(self.SCHEMA)

    @transaction
    def _migrate_if_necessary(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'bot_version'")
        has_version_table = (self.cursor.rowcount == 1)
        has_outdated_version = False
        if has_version_table:
            self.cursor.execute('SELECT major, minor, patch, pre_release_name, pre_release_number FROM bot_version')
            row = self.cursor.fetchone()
            pre_release_number = int(row['pre_release_number']) if row['pre_release_number'] else None
            current_version = DatabaseVersion(int(row['major']), int(row['minor']), int(row['patch']), row['pre_release_name'], pre_release_number)
            has_outdated_version = (current_version == self.VERSION)

        if not has_version_table or has_outdated_version:
            self.cursor.execute(self.SCHEMA)

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
    # def has_already_solved_once(self, solver, submission):
    def has_already_solved_once(self, submission, solver):
        # author_id = self._get_rowid_from_reddit_id('redditor', solver)
        select_stmt = '''
            SELECT count(solution.rowid) AS num_solutions
            FROM solution
                JOIN submission ON (solution.submission_rowid = submission.rowid)
                JOIN redditor ON (solution.author_rowid = redditor.rowid)
                -- JOIN comment ON (solution.comment_rowid = comment.rowid)
            WHERE submission.id = :submission_id
                AND redditor.id = :author_id
                -- AND comment.author_id = :author_id
        '''
        self.cursor.execute(select_stmt, {'submission_id': submission.id, 'author_id': solver.id})
        row = self.cursor.fetchone()
        return row and row['num_solutions'] > 0
        
    def add_point_for_solution(self, submission, solver, solution_comment, chooser, chosen_by_comment):
        self._add_submission(submission)
        self._add_comment(solution_comment, solver)
        self._add_comment(chosen_by_comment, chooser)

        self._update_points(solver, 1)
        # rowcount = self._add_solution(submission, solution_comment, chosen_by_comment)
        rowcount = self._add_solution(submission, solver, solution_comment, chosen_by_comment)
        if rowcount == 0:
            # Was not able to add solution, probably because user has already solved this submission
            self._update_points(solver, -1)
        # if rowcount > 0:
        #     rowcount = self._update_points(solver, 1)
        #     # TODO update author_rowid for comment?
        return rowcount

    # def remove_point_for_solution(self, submission, solver, solution_comment, remover, removed_by_comment):
    # def remove_point_for_solution(self, submission, solver, remover, removed_by_comment):
    def soft_remove_point_for_solution(self, submission, solver, remover, removed_by_comment):
        # submission = removed_by_comment.submission
        self._add_comment(removed_by_comment, remover)
        # rowcount = self._soft_remove_solution(submission, solution_comment, removed_by_comment)
        rowcount = self._soft_remove_solution(submission, solver, removed_by_comment)
        if rowcount > 0:
            rowcount = self._update_points(solver, -1)
            # TODO move "remove redditor" logic here since it doesn't need to be considered when adding points?
        return rowcount

    @transaction
    def add_back_point_for_solution(self, submission, solver):
        self._update_points(solver, 1)
        # submission_rowid = self._get_submission_rowid(submission)
        submission_rowid = self._get_rowid_from_reddit_id('submission', submission)
        author_rowid = self._get_rowid_from_reddit_id('redditor', solver)
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
            'submission_rowid': self._get_rowid_from_reddit_id('submission', submission),
            'author_rowid': self._get_rowid_from_reddit_id('redditor', solver)
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

    @transaction
    def _get_rowid_from_reddit_id(self, table_name, reddit_object):
        params = {'table_name': table_name, 'reddit_id': reddit_object.id}
        self.cursor.execute('SELECT rowid FROM :table_name WHERE id = :reddit_id', params)
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

    # @transaction
    # def _get_comment_rowid(self, comment):
    #     self.cursor.execute('SELECT rowid FROM comment WHERE id = :id', {'id': comment.id})
    #     row = self.cursor.fetchone()
    #     return row['rowid'] if row else None

    @transaction
    def _add_submission(self, submission):
        insert_stmt = '''
            INSERT OR IGNORE INTO submission (id, author_id)
            VALUES (:id, :author_id)
        '''
        self.cursor.execute(insert_stmt, {'id': submission.id, 'author_id': submission.author.id})
        return self.cursor.rowcount

    # @transaction
    # def _get_submission_rowid(self, submission):
    #     self.cursor.execute('SELECT rowid FROM submission WHERE id = :id', {'id': submission.id})
    #     row = self.cursor.fetchone()
    #     return row['rowid'] if row else None

    @transaction
    def _add_solution(self, submission, solver, comment, chosen_by_comment):
        # submission_rowid = self._get_submission_rowid(submission)
        # comment_rowid = self._get_comment_rowid(comment)
        # chosen_by_comment_rowid = self._get_comment_rowid(chosen_by_comment)
        submission_rowid = self._get_rowid_from_reddit_id('submission', submission)
        author_rowid = self._get_rowid_from_reddit_id('redditor', solver)
        comment_rowid = self._get_rowid_from_reddit_id('comment', comment)
        chosen_by_comment_rowid = self._get_rowid_from_reddit_id('comment', chosen_by_comment)
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
    # def _soft_remove_solution(self, submission, comment, removed_by_comment):
    def _soft_remove_solution(self, submission, solver, removed_by_comment):
        # submission_rowid = self._get_submission_rowid(submission)
        # comment_rowid = self._get_comment_rowid(comment)
        # removed_by_comment_rowid = self._get_comment_rowid(removed_by_comment)
        submission_rowid = self._get_rowid_from_reddit_id('submission', submission)
        author_rowid = self._get_rowid_from_reddit_id('redditor', solver)
        # comment_rowid = self._get_rowid_from_reddit_id('comment', comment)
        removed_by_comment_rowid = self._get_rowid_from_reddit_id('comment', removed_by_comment)
        params = {
            'submission_rowid': submission_rowid,
            # 'comment_rowid': comment_rowid,
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

    # @transaction
    # def _get_redditor_rowid(self, redditor):
    #     self.cursor.execute('SELECT rowid FROM redditor WHERE id = :id', {'id': redditor.id})
    #     row = self.cursor.fetchone()
    #     return row['rowid'] if row else None

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


def reddit_datetime_to_iso(datetime):
    return datetime.datetime.utcfromtimestamp(datetime).isoformat()

