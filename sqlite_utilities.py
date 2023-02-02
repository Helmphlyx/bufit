from db.utilities.db_utilities import DatabaseUtilities
import sqlite3


class SqliteUtilites(DatabaseUtilities):
    """DB utilities for SQLite DB."""

    def __init__(self, db_name: str):
        super().__init__(db_name)

    def _get_db_connection(self):
        """Return DB connection."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(
        self,
        sql: str,
        fetch_all: bool = False,
        commit: bool = False,
        row_id: bool = False,
    ):
        """
        Execute passed SQL on db.
        :param sql: the sql to be executed
        :param fetch_all: flag to fetch all results, default is fetch one row
        :param commit: flag to commit query changes to db
        :return:
        """
        conn = self._get_db_connection()
        if fetch_all:
            result = conn.execute(sql).fetchall()
        else:
            result = conn.execute(sql).fetchone()

        if commit:
            conn.commit()

        if row_id:
            result = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.close()
        return result

    def execute_from_file(self, path: str):
        """Execute sql from file."""
        conn = self._get_db_connection()
        with open(path) as f:
            results = conn.executescript(f.read())

        conn.commit()
        conn.close()
        return results

    def cursor(self):
        return self._get_db_connection().cursor()
