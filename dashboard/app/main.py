from flask import request, render_template, Response, Flask, session, redirect, url_for, jsonify, abort, send_file
from requests_oauthlib import OAuth2Session
import os
import json
import urllib.parse
import base64
from jsonschema import exceptions
from flask_misaka import Misaka
from src import bot_client
from src import template_loader
from src import postgres_connector
from src.generator import MemeGenerator
from functools import wraps


OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
OAUTH2_REDIRECT_URI = 'http://housecat.altskop.com/callback'
OWNER_ID = os.environ['OWNER_ID']

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__, static_url_path="", static_folder="templates/static")
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET
Misaka(app)
house_cat_client = bot_client.HouseCatClient(ACCESS_TOKEN)


if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


@app.context_processor
def utility_processor():
    def modulo(x, y):
        return int(x) % int(y)
    return dict(modulo=modulo)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and 'oauth2_state' in session \
                and 'oauth2_token' in session and 'user' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


def require_referrer(referrer):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if request.referrer == referrer:
                return f(*args, **kwargs)
            else:
                abort(412)
        return wrap
    return decorator


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


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


@app.route('/login')
def login():
    scope = request.args.get(
        'scope',
        'identify guilds guilds.join')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    session['referrer'] = request.referrer or "/"
    return redirect(authorization_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(redirect_url())


@app.route('/callback')
def callback():
    if request.values.get('error'):
        session.clear()
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
    url = session['referrer']
    session.pop('referrer')
    return redirect(url)


def get_user_guilds():
    discord = make_session(token=session.get('oauth2_token'))
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    if type(guilds) == list:
        session['guilds'] = guilds
        return guilds
    elif "guilds" in session:
        # TODO verify that this is not a security concern because it very well could be
        print("Error: response from API is null, falling back to session cache:")
        print(session['guilds'])
        return session['guilds']
    else:
        abort(500)


def get_common_guilds_with_create_perms():
    guilds = get_user_guilds()
    result = house_cat_client.get_common_guilds_to_create_template(guilds)
    if session['user']['id'] == OWNER_ID:
        result.append({"name": "global", "id": "global"})
    return result


@app.route('/check-template-name', methods=["GET"])
@login_required
def check_template_name():
    try:
        data = json.loads(urllib.parse.unquote(request.query_string.decode("utf-8")))
        name = data.get('name')
        guilds = data.get('guilds')  # TODO security concern
        connector = postgres_connector.PostgresConnector()
        connector.verify_name_uniqueness(name, guilds)
        return Response("Name available", status=200)
    except ValueError:
        abort(400)


@app.route('/guilds-create', methods=["GET"])
@login_required
def guilds_create():
    guilds = get_common_guilds_with_create_perms()
    guilds_templates = postgres_connector.PostgresConnector().get_guilds_templates(guilds)
    return jsonify(guilds_templates)


def get_common_guilds_with_manage_perms():
    guilds = get_user_guilds()
    result = house_cat_client.get_common_guilds_to_manage(guilds)
    if session['user']['id'] == OWNER_ID:
        result.append({"name": "global", "id": "global"})
    return result


@app.route('/guilds-manage', methods=["GET"])
@login_required
def guilds_manage():
    return jsonify(get_common_guilds_with_manage_perms())


@app.route('/guild-templates', methods=["GET"])
@login_required
def guild_templates():
    guild = request.args.get('id')
    if guild in [x['id'] for x in get_common_guilds_with_manage_perms()]:
        templates = postgres_connector.PostgresConnector().list_guild_memes(guild)
        return jsonify(templates)


@app.route('/')
def index():
    return render_template('layouts/index.html')


@app.route('/changelog')
def changelog():
    # TODO verify if this is the best way of doing this? Maybe I could just have a regular page instead
    with open("/CHANGELOG.md", "r") as file:
        changelog = file.read()
        return render_template('layouts/changelog.html', changelog=changelog)


@app.route('/commands', methods=["GET"])
def commands():
    return render_template('layouts/commands.html')


@app.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    return render_template('layouts/dashboard.html')


@app.route('/preview', methods=["POST"])
@login_required
def preview():
    json = request.get_json(force=True)
    try:
        loader = template_loader.TemplateLoader()
        preview = loader.preview_template(json)
        base64string = base64.b64encode(preview.read())
        return Response(base64string, status=200)
    except ValueError as e:
        return Response(str(e), status=400)


@app.route('/template', methods=["GET"])
@login_required
def template():
    try:
        name = request.args.get("name")
        guild = request.args.get("guild")
        if guild in [x['id'] for x in get_common_guilds_with_manage_perms()]:
            connector = postgres_connector.PostgresConnector()
            template = connector.get_meme_template(name, guild)
            base64string = base64.b64encode(template['image']).decode('UTF-8')
            return jsonify(image=base64string, metadata=template['metadata'])
        else:
            abort(403)
    except ValueError as e:
        return Response(str(e), status=400)


@app.route('/delete', methods=["GET"])
@login_required
def delete():
    try:
        name = request.args.get("name")
        guild = request.args.get("guild")
        print(name, guild)
        if guild in [x['id'] for x in get_common_guilds_with_manage_perms()]:
            connector = postgres_connector.PostgresConnector()
            connector.delete_meme_template(name, guild)
            return Response(status=200)
        else:
            abort(403)
    except ValueError as e:
        return Response(str(e), status=400)


@app.route('/preview', methods=["GET"])
@login_required
def preview_get():
    try:
        name = request.args.get("name")
        guild = request.args.get("guild")
        if guild in [x['id'] for x in get_common_guilds_with_manage_perms()]:
            connector = postgres_connector.PostgresConnector()
            template = connector.get_meme_template(name, guild)
            preview = MemeGenerator(bytes(template['image']), template['metadata'], []).generate()
            base64string = base64.b64encode(preview.read())
            return Response(base64string, status=200)
        else:
            abort(403)
    except ValueError as e:
        return Response(str(e), status=400)


@app.route('/create', methods=["POST"])
@login_required
def process_create_request():
    json = request.get_json(force=True)
    try:
        author = session['user']
        guilds = get_common_guilds_with_create_perms()
        loader = template_loader.TemplateLoader()
        loader.create_template(json, guilds, author)
        return Response("Template created", status=201)
    except ValueError as e:
        return Response(str(e), status=400)
    except exceptions.ValidationError as e:
        print(e)
        return Response("Invalid request.", status=400)


@app.route('/update', methods=["POST"])
@login_required
def update():
    json = request.get_json(force=True)
    try:
        guilds = get_common_guilds_with_manage_perms()
        loader = template_loader.TemplateLoader()
        loader.update_template(json, guilds)
        return Response("Template created", status=201)
    except ValueError as e:
        return Response(str(e), status=400)
    except exceptions.ValidationError as e:
        print(e)
        return Response("Invalid request.", status=400)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
