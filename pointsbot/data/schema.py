"""A schema class that allows for migrations from previous versions."""


class Schema:

    def __init__(self, version='', sql='', migrate=None):
        self.version = version
        # self.previous_version = previous_version

        # The SQL commands to create a new database
        self.sql = sql

        # A function to convert an existing instance of a previous database
        # version into a new instance with the new schema
        self._migrate = migrate

    def __lt__(self, other):
        """Return True if the version of self is earlier than other's, False
        otherwise.
        """
        ver1 = list(map(int, self.version.split('.')))
        ver2 = list(map(int, other.version.split('.')))
        return ver1 < ver2

    def __le__(self, other):
        return self < other or self == other

    def migrate(self):
        if self._migrate:
            self._migrate()


