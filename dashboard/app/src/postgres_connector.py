import os
import psycopg2
import psycopg2.extras
import json


class PostgresConnector:

    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ['PG_HOST'],
            port=os.environ['PG_PORT'],
            database=os.environ['PG_DATABASE'],
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
            guilds_values = [(name, guild, meme_id) for guild in guilds]
            sql_string = "insert into guildMemes (name, guild, meme) VALUES %s;"
            psycopg2.extras.execute_values(cursor, sql_string, guilds_values)

    def get_meme_template(self, name, guild):
        conn = self.conn
        with conn:
            c = self.cursor
            if guild is not None:
                guilds = tuple([str(guild)] + ["global"])
            else:
                guilds = ("global",)
            sql_string = "select image, metadata from guildMemes join memes on (meme=id) where name=%s and guild in %s;"
            c.execute(sql_string, (name, guilds))
            return c.fetchone()

    def delete_meme_template(self, name, guild):
        conn = self.conn
        with conn:
            c = self.cursor
            sql_string = "delete from guildMemes where name=%s and guild=%s returning meme;"
            c.execute(sql_string, (name, guild))
            meme_id = c.fetchone()['meme']
            try:
                sql_string = "delete from memes where id=%s;"
                c.execute(sql_string, (meme_id,))
            except Exception as e:
                print(e)

    def list_guild_memes(self, guild):
        conn = self.conn
        with conn:
            c = self.cursor
            sql_string = "select name, author from guildMemes join memes on (meme=id) where guild=%s order by name;"
            c.execute(sql_string, (str(guild),))
            return c.fetchall()

    def verify_name_uniqueness(self, name, guilds):
        with self.conn:
            cursor = self.cursor
            guilds = tuple(guilds + ["global"])
            sql_string = "select count(*) from guildMemes where name=%s and guild in %s;"
            cursor.execute(sql_string, (name, guilds))
            result = cursor.fetchone()
            if result['count'] > 0:
                raise ValueError("This template name is already in use in one of the selected servers.")

    def get_guilds_templates(self, guilds: list):
        guilds_values = [(x['id'],) for x in guilds]
        with self.conn:
            cursor = self.cursor
            sql_string = "select guild, count(*) from guildMemes where guild in %s group by guild;"
            cursor.execute(sql_string, (tuple(guilds_values),))
            result = cursor.fetchall()
            guilds_templates = {guild['guild']: guild['count'] for guild in result}
            for guild in guilds:
                entry = guilds_templates.get(guild['id'])
                if entry is None:
                    guild['full'] = False
                elif entry >= 15 and guild['id'] != "global":
                    guild['full'] = True
                else:
                    guild['full'] = False
            return guilds

    def get_author(self, name, guild):
        conn = self.conn
        with conn:
            c = self.cursor
            guilds = tuple(guild)
            sql_string = "select author from guildMemes join memes on (meme=id) where name=%s and guild in %s;"
            c.execute(sql_string, (name, guilds))
            return c.fetchone()['author']

    def get_guilds(self):
        conn = self.conn
        with conn:
            c = self.cursor
            c.execute("select id from guilds;")
            return c.fetchall()

    def set_guilds(self, guilds: list):
        guilds_values = [(x,) for x in guilds]
        conn = self.conn
        with conn:
            c = self.cursor
            c.execute("truncate guilds;")
            insert_query = 'insert into guilds (id) values %s'
            psycopg2.extras.execute_values(
                c, insert_query, guilds_values
            )

    @property
    def cursor(self):
        return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
