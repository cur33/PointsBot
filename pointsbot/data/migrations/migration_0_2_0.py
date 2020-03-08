# TODO provide a description string for each action

SQL_STATEMENTS = [
    # Store current database version
    # TODO could probably just be a string, esp if versions are more than just
    # integers.
    # TODO could also just store version in db schema name.
    '''
    CREATE TABLE IF NOT EXISTS db_version(
        major INTEGER NOT NULL,
        minor INTEGER NOT NULL,
        patch INTEGER NOT NULL
    )
    ''',
    '''
    DELETE FROM db_version
    ''',
    '''
    INSERT INTO db_version(major, minor, patch)
    VALUES (0, 2, 0)
    ''',

    # 1. Rename table to redditor
    # 2. Remove now-unnecessary points field
    # 3. Add points_modifier field to allow admins to adjust points manually
    '''
    CREATE TABLE IF NOT EXISTS redditor(
        id TEXT UNIQUE NOT NULL,
        name TEXT UNIQUE NOT NULL,
        points_modifier INTEGER DEFAULT 0
    )
    ''',
    '''
    INSERT INTO redditor(id, name)
        SELECT id, name
        FROM redditor_points
    ''',
    '''
    DROP TABLE redditor_points
    ''',

    # Store a reference to each solved post and the comment that solved it
    #
    # TODO could make id non-unique to allow storing multiple solution comments,
    # in the event that one gets deleted. This would allow admin to take action
    # based on that knowledge. If so, should also store datetime of comment.
    #
    # TODO If needed, eg if start to store more data about submission and/or
    # comments as suggested above, could split this table into several tables:
    #     - submission
    #     - comment
    #     - submission_solution (name?)
    # TODO also add OP field? If so, may want to add OP to redditor table. In
    # that event, may also want to add a field to redditor like 'has_solved' to
    # avoid checking for points for a redditor who hasn't solved anything.
    '''
    CREATE TABLE IF NOT EXISTS solved_submission(
        id TEXT UNIQUE NOT NULL,
        solution_comment_id TEXT UNIQUE NOT NULL,
        solved_comment_id TEXT UNIQUE NOT NULL,
        solver INTEGER NOT NULL,
        datetime_iso TEXT NOT NULL,
        FOREIGN KEY(solver) REFERENCES redditor(rowid)
    )
    ''',
]
