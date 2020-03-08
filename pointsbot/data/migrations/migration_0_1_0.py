SQL_STATEMENTS = [
    # Create initial database
    '''
    CREATE TABLE IF NOT EXISTS redditor_points(
        id TEXT UNIQUE NOT NULL,
        name TEXT UNIQUE NOT NULL,
        points INTEGER DEFAULT 0
    )
    ''',
]
