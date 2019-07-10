from flask import Flask
from flask import request, render_template, Response
import os
import io
import base64
import json
from PIL import Image
import re
from jsonschema import validate, exceptions

app = Flask(__name__)
app._static_folder = os.path.abspath("templates/static/")

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string",
                 "maxLength": 24},
        "image": {"type": "object",
                  "properties": {
                      "data": {"type": "string"}
                  },
                  "required": ["data"]
                  },
        "metadata": {
            "type": "object",
            "properties": {
                "fields": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "point_1": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"}
                                },
                                "required": ["x", "y"]
                            },
                            "point_2": {
                                "type": "object",
                                "properties": {
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"}
                                },
                                "required": ["x", "y"]
                            }
                        },
                        "required": ["point_1", "point_2"]
                    },
                },
                "font": {"type": "string",
                         "enum": ["normal", "bold"]}
            },
            "required": ["fields", "font"]
        }
    },
    "required": ["name", "image", "metadata"]
}


@app.route('/create', methods=["GET"])
def return_create_page():
    title = 'Create a Meme Template'
    return render_template('layouts/create.html',
                           title=title)


@app.route('/create', methods=["POST"])
def process_create_request():
    json = request.get_json(force=True)
    try:
        validate(instance=json, schema=schema)
        print("Incoming request")
        base64_data = re.sub('^data:image/.+;base64,', '', json['image']['data'])
        byte_data = base64.b64decode(base64_data)
        image_data = io.BytesIO(byte_data)
        img = Image.open(image_data)
        verify_img_size(img)
        validate_metadata(json['metadata'])
        new_template(json['name'], img, json['metadata'])
        print("Template created")
        return Response("Template created", status=201)
    except FileExistsError as e:
        print(e)
        return Response("This template name is already in use", status=400)
    except exceptions.ValidationError as e:
        print(e)
        return Response("Invalid request.", status=400)


def verify_img_size(image):
    maxsize = 600
    if any(x > maxsize for x in image.size):
        raise exceptions.ValidationError('Image too big.')


def validate_metadata(metadata):
    for field in metadata['fields']:
        if field['point_1']['x'] > field['point_2']['x'] or field['point_1']['y'] > field['point_2']['y']:
            raise exceptions.ValidationError('Incorrect input')


def new_template(name, img, metadata):
    name = name.lower()
    path = os.path.normpath("../storage/memes/templates/" + name)
    os.mkdir(path)
    with open(path + "/template.png", "wb") as file:
        img.save(file)
    with open(path + "/metadata.json", "w") as file:
        json.dump(metadata, file)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
