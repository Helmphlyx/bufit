from typing import Optional

from db.utilities.db_utilities import DatabaseUtilities
import sqlite3

import os
import mysql.connector
from settings import settings


class SqliteUtilites(DatabaseUtilities):
    """DB utilities for SQLite DB."""

    def __init__(self, db_name: str):
        super().__init__(db_name)

    def _get_db_connection(self):
        """Return DB connection."""
        if settings.MYSQL_CREDENTIALS["NAME"]:
            conn = mysql.connector.connect(
                host=settings.MYSQL_CREDENTIALS.get('HOST'),
                user=settings.MYSQL_CREDENTIALS.get('USER'),
                password=settings.MYSQL_CREDENTIALS.get('PASSWORD'),
                database=settings.MYSQL_CREDENTIALS.get('PORT')
            )
        else:
            conn = sqlite3.connect(self.db_name, isolation_level=None)  # defaults auto-commit mode
            conn.row_factory = sqlite3.Row
        return conn

    def execute(
            self,
            sql: str,
            params: Optional[tuple] = None,
            fetch_all: bool = False,
            commit: bool = False,
            row_id: bool = False,
    ):
        """
        Execute passed SQL on db.
        :param sql: the sql to be executed
        :param params: parameters to pass to the sql
        :param fetch_all: flag to fetch all results, default is fetch one row
        :param commit: flag to commit query changes to db
        :return:
        """
        conn = self._get_db_connection()
        sql = f"""{sql}"""
        if fetch_all:
            if params:
                result = conn.execute(sql, params).fetchall()
            else:
                result = conn.execute(sql).fetchall()
        else:
            if params:
                result = conn.execute(sql, params).fetchone()
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
