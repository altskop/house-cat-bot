from . import database_handler
import psycopg2


class DiscordDb(database_handler.DBHandler):

    def list_guild_memes(self, guild):
        conn = self.conn
        with conn:
            c = self.cursor
            sql_string = "select name, author from guildMemes join memes on (meme=id) where guild=%s;"
            c.execute(sql_string, (str(guild),))
            return c.fetchall()

    def list_global_memes(self):
        conn = self.conn
        with conn:
            c = self.cursor
            sql_string = "select name, metadata from guildMemes join memes on (meme=id) where guild='global';"
            c.execute(sql_string)
            return c.fetchall()

    def get_meme_template(self, name, guild):
        conn = self.conn
        with conn:
            c = self.cursor
            guilds = tuple([str(guild)] + ["global"])
            sql_string = "select image, metadata from guildMemes join memes on (meme=id) where name=%s and guild in %s;"
            c.execute(sql_string, (name, guilds))
            return c.fetchone()

    def initialize_db(self):
        # Connect to database. If the file doesn't exist, create it
        conn = self.conn
        with conn:
            c = conn.cursor()
            try:
                c.execute("select id, metadata, image, author from memes;")
                c.execute("select name, guild, meme from guildMemes;")
                c.execute("select command, arg1, arg2, args, author, guild, datetime, success from queries;")
            except psycopg2.ProgrammingError:
                # If the tables don't exist, create them
                c.execute("create table memes("
                          "id SERIAL primary key not null,"
                          "metadata json not null,"
                          "image bytea not null,"
                          "author varchar(21) not null"
                          ");")
                c.execute("create table guildMemes("
                          "name varchar(21) not null,"
                          "guild varchar(20) not null,"
                          "meme integer references memes(id) not null,"
                          "PRIMARY KEY (name, guild)"
                          ");")
                c.execute("create table queries("
                          "command varchar(60) not null,"
                          "arg1 varchar(50) not null,"
                          "arg2 varchar(50) not null,"
                          "args varchar(200) not null,"
                          "author varchar(20) not null,"
                          "guild varchar(20) not null,"
                          "datetime timestamp not null,"
                          "success bool default false"
                          ");")
                c.execute("create table guilds("
                          "id varchar(20) not null primary key"
                          ");")
