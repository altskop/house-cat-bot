import psycopg2
import psycopg2.extras
import json
import io
import base64
from PIL import Image
import re
import os
from .generator import MemeGenerator
from jsonschema import validate, exceptions

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string",
                 "maxLength": 21,
                 "minLength": 3,
                 "pattern": "^(?!.*(-)-*\1)[a-zA-Z][a-zA-Z0-9-]*$"},
        "image": {"type": "string"
                  },
        "guilds": {"type": "array",
                   "minItems": 1,
                   "maxItems": 100,
                   "items": {
                       "type": "string"
                    }
                   },
        "metadata": {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 20,
                    "items": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "type": "integer",
                                "minimum": 0
                            },
                            "y": {
                                "type": "integer",
                                "minimum": 0
                            },
                            "w": {
                                "type": "integer",
                                "minimum": 9
                            },
                            "h": {
                                "type": "integer",
                                "minimum": 9
                            },
                            "align": {
                                "type": "string",
                                "enum": ["center", "left", "right"]
                            },
                            "font": {
                                "type": "string",
                                "enum": ["normal", "bold"]
                            },
                            "color": {
                                "type": "string",
                                "pattern": "^#(?:[0-9a-fA-F]{3}){1,2}$"
                            }
                        },
                        "required": ["x", "y", "w", "h", "color", "align", "font"]
                    },
                }
            },
            "required": ["fields"]
        }
    },
    "required": ["name", "image", "metadata"]
}


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


class TemplateLoader:

    def __init__(self, author, guilds):
        self.img_blob = None
        self.name = None
        self.fields = None
        self.author = author['username']+author['discriminator']
        self.guilds = [x['id'] for x in guilds]
        self.connector = PostgresConnector()

    @staticmethod
    def _verify_img_size(image):
        maxsize = 600  # width
        if image.size[0] > maxsize:
            raise exceptions.ValidationError('Image too big.')

    def validate_metadata(self, sizes):
        for field in self.fields['fields']:
            if field['x']+field['w'] > sizes[0] or field['y']+field['h'] > sizes[1]:
                raise exceptions.ValidationError('Incorrect input')

    def validate_template(self, json):
        validate(instance=json, schema=schema)
        self._b64_to_img_blob(json['image'])
        if len(self.img_blob) > 3000000:
            raise ValueError("Image is too big, 3Mb limit")
        image_data = io.BytesIO(self.img_blob)
        img = Image.open(image_data)
        self._verify_img_size(img)
        self.fields = json['metadata']
        self.validate_metadata(img.size)
        self.verify_guilds(json)
        self.name = json['name'].lower()
        self.connector.verify_name_uniqueness(self.name, self.guilds)

    def verify_guilds(self, json):
        self.guilds = [x for x in json['guilds'] if x in self.guilds]
        if len(self.guilds) == 0:
            raise ValueError("No selected guilds with sufficient perms")

    def _b64_to_img_blob(self, image_data):
        base64_data = re.sub('^data:image/.+;base64,', '', image_data)
        self.img_blob = base64.b64decode(base64_data)

    def create_template(self, json):
        self.validate_template(json)
        self.connector.new_template()

    def preview_template(self, json):
        self.validate_template(json)
        text_list = ["sample text"] * len(self.fields)
        img = MemeGenerator(self.img_blob, self.fields, text_list)
        return img
