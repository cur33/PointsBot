from .schema import Schema

### Migration Function ###


def _migrate():
    pass


### Export ###

SCHEMA = Schema(
    version='0.1.0',
    sql='''
        CREATE TABLE IF NOT EXISTS redditor_points (
            id TEXT UNIQUE NOT NULL,
            name TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 0
        );
    ''',
    migrate=_migrate,
)
