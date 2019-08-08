import io
import base64
from PIL import Image
import re

from .generator import MemeGenerator
from .postgres_connector import PostgresConnector
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


class TemplateLoader:

    def __init__(self):
        self.img_blob = None
        self.name = None
        self.fields = None
        self.author = None
        self.guilds = None
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
        self.name = json['name'].lower()

    def verify_guilds(self, json):
        self.guilds = [x for x in json['guilds'] if x in self.guilds]
        if len(self.guilds) == 0:
            raise ValueError("No selected guilds with sufficient perms")
        guilds_dicts = [{"id": x} for x in self.guilds]
        guilds_availability = self.connector.get_guilds_templates(guilds_dicts)
        self.guilds = [x['id'] for x in guilds_availability if x['full'] is False]
        if len(self.guilds) == 0:
            raise ValueError("Selected server is full.")

    def _b64_to_img_blob(self, image_data):
        base64_data = re.sub('^data:image/.+;base64,', '', image_data)
        self.img_blob = base64.b64decode(base64_data)

    def create_template(self, json, guilds, author):
        self.author = author['username'] + author['discriminator']
        self.guilds = [x['id'] for x in guilds]
        self.verify_guilds(json)
        self.validate_template(json)
        self.connector.verify_name_uniqueness(self.name, self.guilds)
        self.connector.new_template(self.img_blob, self.fields, self.name, self.author, self.guilds)

    def preview_template(self, json):
        text = json['text']
        del (json['text'])
        self.validate_template(json)
        text_list = []
        for entry in text:
            if len(entry) == 0:
                text_list.append("sample text")
            else:
                text_list.append(entry)
        img = MemeGenerator(self.img_blob, self.fields, text_list).generate()
        return img
