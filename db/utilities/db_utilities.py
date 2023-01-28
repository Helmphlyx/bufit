from abc import ABC


class DatabaseUtilities(ABC):
    """Abstract class for defining DB utilities."""

    def __init__(self, db_name: str):
        self.db_name = db_name

    def _get_db_connection(self):
        """Return DB connection."""
        pass

    def execute(self, sql: str, fetch_all: bool, commit: bool):
        """
        Execute passed SQL on db.
        :param sql: the sql to be executed
        :param fetch_all: flag to fetch all results, default is fetch one row
        :param commit: flag to commit query changes to db
        :return:
        """
        pass
