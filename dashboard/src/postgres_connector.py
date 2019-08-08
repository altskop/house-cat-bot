import os
import psycopg2
import psycopg2.extras
import json


class PostgresConnector:

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ['PG_HOST'],
            port=os.environ['PG_PORT'],
            database='house_cat_db',
            user=os.environ['PG_USER'],
            password=os.environ['PG_PASSWORD']
        )
        self.conn.autocommit = True

    def new_template(self, img, metadata, name, author, guilds):
        with self.conn:
            cursor = self.conn.cursor()
            sql_string = "insert into memes (metadata, image, author) VALUES (%s,%s,%s) RETURNING id;"
            cursor.execute(sql_string, (json.dumps(metadata), img, author))
            meme_id = cursor.fetchone()[0]
            for guild in guilds:
                sql_string = "insert into guildMemes (name, guild, meme) VALUES (%s, %s, %s);"
                cursor.execute(sql_string, (name, guild, meme_id))

    def verify_name_uniqueness(self, name, guilds):
        with self.conn:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            guilds = tuple(guilds + ["global"])
            sql_string = "select count(*) from guildMemes where name=%s and guild in %s;"
            cursor.execute(sql_string, (name, guilds))
            result = cursor.fetchone()
            if result['count'] > 0:
                raise ValueError("This template name is already in use in one of the selected servers.")

    def get_guilds(self):
        conn = self.conn
        with conn:
            c = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute("select id from guilds;")
            return c.fetchall()

    def set_guilds(self, guilds: list):
        guilds_values = [(x,) for x in guilds]
        conn = self.conn
        with conn:
            c = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute("truncate guilds;")
            insert_query = 'insert into guilds (id) values %s'
            psycopg2.extras.execute_values(
                c, insert_query, guilds_values
            )
