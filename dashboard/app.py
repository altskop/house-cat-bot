from flask import request, render_template, Response, Flask, session, redirect, url_for, jsonify, abort
from requests_oauthlib import OAuth2Session
import os
from jsonschema import exceptions
from flask_misaka import Misaka
from src import bot_client
from src import template_loader
from functools import wraps


OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__, static_url_path="", static_folder="templates/static")
app.debug = True
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


@app.route('/me')
@login_required
def me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    return jsonify(user=user, guilds=guilds)


@app.route('/guilds-create', methods=["GET"])
@login_required
def guilds_create():
    discord = make_session(token=session.get('oauth2_token'))
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    return jsonify(house_cat_client.get_common_guilds_to_create_template(guilds))


@app.route('/guilds-manage', methods=["GET"])
@login_required
def guilds_manage():
    discord = make_session(token=session.get('oauth2_token'))
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    return jsonify(house_cat_client.get_common_guilds_to_manage(guilds))


@app.route('/')
def index():
    return render_template('layouts/index.html')


@app.route('/editor') # TODO remove after tests
def editor():
    return render_template('layouts/editor.html')


@app.route('/changelog')
def changelog():
    # TODO verify if this is the best way of doing this? Maybe I could just have a regular page instead
    with open("../CHANGELOG.md", "r") as file:
        changelog = file.read()
        return render_template('layouts/changelog.html', changelog=changelog)


@app.route('/commands', methods=["GET"])
def commands():
    return render_template('layouts/commands.html')


@app.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    return render_template('layouts/dashboard.html')


@app.route('/create', methods=["GET"])
def return_create_page():
    title = 'Create a Meme Template'
    return render_template('layouts/create.html',
                           title=title)


@app.route('/create', methods=["POST"])
def process_create_request():
    json = request.get_json(force=True)
    try:
        template_loader.create_template(json)
        return Response("Template created", status=201)
    except FileExistsError as e:
        print(e)
        return Response("This template name is already in use", status=400)
    except exceptions.ValidationError as e:
        print(e)
        return Response("Invalid request.", status=400)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
