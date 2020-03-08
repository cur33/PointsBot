# from . import *
from . import migration_0_1_0, migration_0_2_0

# TODO use ..database.SchemaVersion

# Guaranteed to be sorted in ascending order by version
MIGRATIONS = (
    ('0.1.0', migration_0_1_0.SQL_STATEMENTS),
    ('0.2.0', migration_0_2_0.SQL_STATEMENTS),
)
