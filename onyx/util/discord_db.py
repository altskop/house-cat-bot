from . import database_handler
import sqlite3


class DiscordDb(database_handler.DBHandler):
    def __init__(self):
        database_handler.DBHandler.__init__(self, "/storage/db/discord_data.db")

    def initialize_db(self):
        # Connect to database. If the file doesn't exist, create it
        conn = self.conn
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
