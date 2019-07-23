from flask import request, render_template, Response, Flask, session, redirect, url_for, jsonify
from requests_oauthlib import OAuth2Session
import os
import io
import base64
import json
from PIL import Image
import re
from jsonschema import validate, exceptions

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

OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__, static_url_path="", static_folder="templates/static")
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


@app.route('/login')
def login():
    scope = request.args.get(
        'scope',
        'identify guilds guilds.join')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/logout')
def logout():
    session.pop('oauth2_token')
    session['logged_in'] = False
    return redirect(url_for('index'))


@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    session['logged_in'] = True
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    session['user'] = user
    return redirect(url_for('.me'))


@app.route('/me')
def me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    return jsonify(user=user, guilds=guilds)


@app.route('/')
def index():
    return render_template('layouts/index.html')


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
        base64_data = re.sub('^data:image/.+;base64,', '', json['image']['data'])
        byte_data = base64.b64decode(base64_data)
        image_data = io.BytesIO(byte_data)
        img = Image.open(image_data)
        verify_img_size(img)
        validate_metadata(json['metadata'])
        new_template(json['name'], img, json['metadata'])
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
