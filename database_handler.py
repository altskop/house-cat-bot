import sqlite3


class DBHandler:
    def __init__(self, db_file):
        self.db_file = db_file

    def initialize_db(self):
        # Will occur if there is no db file
        pass

    def insert(self, table, column, value):
        conn = sqlite3.connect(self.db_file)
        with conn:
            c = conn.cursor()
            # params = (self.input, str(datetime.now()), reason, None)
            # c.execute("INSERT INTO JOURNAL VALUES (?,?,?,?)", params)

    def get_value(self, table, column):
        conn = sqlite3.connect(self.db_file)
        with conn:
            c = conn.cursor()
            # params = (self.input,)
            # c.execute(
            #     "SELECT * FROM JOURNAL WHERE ID=? AND SignIn>=datetime('now', 'localtime', 'start of day') AND SignIn<datetime('now', '+1 day','localtime','start of day') AND SignOut IS NULL",
            #     params)
            # return c.fetchall()


db = DBHandler("discord_data.db")