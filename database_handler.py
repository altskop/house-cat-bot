import sqlite3
import time


class DBHandler:
    def __init__(self, db_file):
        self.db_file = db_file
        self.initialize_db()

    def initialize_db(self):
        # Connect to database. If the file doesn't exist, create it
        conn = sqlite3.connect(self.db_file)
        with conn:
            c = conn.cursor()
            try:
                c.execute("select * from users;")
            except sqlite3.OperationalError:
                # If the tables don't exist, create them
                c.execute("create table users("
                          "userid varchar(30) primary key not null,"
                          "pref_name text,"
                          "forward_mentions bool default false,"
                          "not_available bool default false,"
                          "dont_call bool default false,"
                          "last_seen text"
                          ");")
                c.execute("create table guilds("
                          "guildid varchar(30) primary key not null,"
                          "welcome_voice bool default true,"
                          "require_tts_permission bool default false"
                          ");")

    def is_in_timeframe(self, table, column, key, value, timeframe):
        conn = self.get_conn()
        with conn:
            entry = self.get_entry(conn, table, key, value)[column]
            if entry is not None:
                margin = timeframe * 60 * 1000
                if self.current_time() - int(entry) <= margin:
                    return True
            self.update_entry(conn, table, key, value, column, str(self.current_time()))
            return False

    def get_and_update(self, table, key, value, column, new_value):
        conn = self.get_conn()
        with conn:
            self.get_entry(conn, table, key, value)
            self.update_entry(conn, table, key, value, column, new_value)

    def get_boolean(self, table, column, key, value):
        conn = self.get_conn()
        with conn:
            return self.str2bool(self.get_entry(conn, table, key, value)[column])

    def get_value_by_key(self, table, column, key, value):
        conn = self.get_conn()
        with conn:
            return self.get_entry(conn, table, key, value)[column]

    # Will try to find an entry, or create it if doesn't exist
    def get_entry(self, conn, table, key, value):
        result = self.find_entry(conn, table, key, value)
        if len(result) == 0:
            self.insert_entry(conn, table, key, value)
            result = self.find_entry(conn, table, key, value)
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

    def find_entry(self, conn, table, key, value):
        c = conn.cursor()
        stmt = "select * from %s where %s=?" % (table, key)
        params = (value,)
        c.execute(stmt, params)
        return c.fetchall()

    def get_conn(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = self.dict_factory
        return conn

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def str2bool(self, v):
        return str(v).lower().lstrip() in ("true", "t", "1")

    def current_time(self):
        return int(round(time.time() * 1000))


if __name__ == "__main__":
    db = DBHandler("db/discord_data.db")
    print(db.is_in_timeframe("users","last_seen","userid","12345", 1))
    print(db.get_value_by_key("guilds", "welcome_voice", "guildid", "12345"))
    #print(db.get_value_by_key("users", "last_seen", "userid", "12345"))