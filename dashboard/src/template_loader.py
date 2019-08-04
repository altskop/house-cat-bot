import json
import io
import base64
from PIL import Image
import re
import os
from jsonschema import validate, exceptions

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string",
                 "maxLength": 21,
                 "minLength": 3,
                 "pattern": "^(?!.*(-)-*\1)[a-zA-Z][a-zA-Z0-9-]*$"},
        "image": {"type": "string",
                  "maxLength": 3000000
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


def verify_img_size(image):
    maxsize = 600  # width
    if image.size[0] > maxsize:
        raise exceptions.ValidationError('Image too big.')


def validate_metadata(metadata, sizes):
    for field in metadata['fields']:
        if field['x']+field['w'] > sizes[0] or field['y']+field['h'] > sizes[1]:
            raise exceptions.ValidationError('Incorrect input')


def new_template(name, img, metadata):
    name = name.lower()
    path = os.path.normpath("../storage/memes/templates/" + name)
    os.mkdir(path)
    with open(path + "/template.png", "wb") as file:
        img.save(file)
    with open(path + "/metadata.json", "w") as file:
        json.dump(metadata, file)


def create_template(json):
    print(len(json["image"]))
    validate(instance=json, schema=schema)
    base64_data = re.sub('^data:image/.+;base64,', '', json['image'])
    byte_data = base64.b64decode(base64_data)
    image_data = io.BytesIO(byte_data)
    img = Image.open(image_data)
    verify_img_size(img)
    validate_metadata(json['metadata'], img.size)
    new_template(json['name'], img, json['metadata'])