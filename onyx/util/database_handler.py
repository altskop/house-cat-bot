import sqlite3
import time
from abc import ABC, abstractmethod


def str_to_bool(v):
    return str(v).lower().lstrip() in ("true", "t", "1")


def current_time():
    return int(round(time.time() * 1000))


class DBHandler(ABC):
    def __init__(self, db_file):
        self.db_file = db_file
        self.initialize_db()

    @abstractmethod
    def initialize_db(self):
        """
        Method that will be called in the constructor.
        Subclasses should implement this and perform
        their DB initialization and setup here if needed.
        """
        raise NotImplementedError

    def is_in_timeframe(self, table, column, key, value, timeframe):
        conn = self.conn()
        with conn:
            entry = self.get_entry(conn, table, key, value)[column]
            if entry is not None:
                margin = timeframe * 60 * 1000
                if current_time() - int(entry) <= margin:
                    return True
            self.update_entry(conn, table, key, value, column, str(current_time()))
            return False

    def get_and_update(self, table, key, value, column, new_value):
        conn = self.conn()
        with conn:
            self.get_entry(conn, table, key, value)
            self.update_entry(conn, table, key, value, column, new_value)

    def get_boolean(self, table, column, key, value):
        conn = self.conn()
        with conn:
            return str_to_bool(self.get_entry(conn, table, key, value)[column])

    def get_value_by_key(self, table, column, key, value):
        conn = self.conn()
        with conn:
            return self.get_entry(conn, table, key, value)[column]

    # Will try to find an entry, or create it if doesn't exist
    def get_entry(self, conn, table, key, value):
        result = self.select_entry(conn, table, key, value)
        if len(result) == 0:
            self.insert_entry(conn, table, key, value)
            result = self.select_entry(conn, table, key, value)
        return result[0]

    def insert_entry(self, conn, table, key, value):
        c = conn.cursor()
        stmt = "insert into %s (%s) values(?)" % (table, key)
        params = (value,)
        c.execute(stmt, params)

    def update_entry(self, conn, table, key, value, column, update_value):
        c = conn.cursor()
        stmt = "update %s set %s=? where %s=?" % (table, column, key)
        params = (update_value, value)
        c.execute(stmt, params)

    def select_entry(self, conn, table, key, value):
        c = conn.cursor()
        stmt = "select * from %s where %s=?" % (table, key)
        params = (value,)
        c.execute(stmt, params)
        return c.fetchall()

    @property
    def conn(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d