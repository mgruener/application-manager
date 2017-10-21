# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from functools import wraps
from flask import Blueprint, render_template, flash, redirect, url_for, request, session, current_app
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape
from six.moves.urllib.parse import urlencode, urlparse
from six.moves.urllib.request import urlopen
from jose import jwt

from .forms import SignupForm
from .nav import nav
from .oauth import oauth

# eu.auth0.com uses a wildcard ssl certificate (*.eu.auth0.com)
# for the auth domains which causes trouble with urrlib
# temporarly disable ssl verification
# TODO: try to fix this
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

frontend = Blueprint('frontend', __name__)

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', Navbar(
    View('Application Manager', '.index'),
    View('Home', '.index'),
    View('Forms Example', '.example_form'),
    Subgroup(
        'Docs',
        Link('Flask-Bootstrap', 'http://pythonhosted.org/Flask-Bootstrap'),
        Link('Flask-AppConfig', 'https://github.com/mbr/flask-appconfig'),
        Separator(),
        Text('Bootstrap'),
        Link('Getting started', 'http://getbootstrap.com/getting-started/'),
        Link('CSS', 'http://getbootstrap.com/css/'),
        Link('Components', 'http://getbootstrap.com/components/'),
        Link('Javascript', 'http://getbootstrap.com/javascript/'),
        Link('Customize', 'http://getbootstrap.com/customize/'), ),
    View('Logout','.logout'),
    Text('Using Flask-Bootstrap {}'.format(FLASK_BOOTSTRAP_VERSION)), ))

# disable ssl verification because urllib somehow has problems with wildcard
# certificates
#ssl._create_default_https_context = ssl._create_unverified_context
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.
@frontend.route('/')
def index():
    return render_template('index.html')


# Shows a long signup form, demonstrating form rendering.
@frontend.route('/example-form/', methods=('GET', 'POST'))
@requires_auth
def example_form():
    form = SignupForm()

    if form.validate_on_submit():
        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        #
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
        flash('Hello, {}. You have successfully signed up'
              .format(escape(form.name.data)))

        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('.index'))

    return render_template('signup.html', form=form)

@frontend.route('/callback')
def callback_handling():
    resp = oauth.auth0.authorized_response()

    if resp is None:
        raise AuthError({'code': request.args['error'],
                         'description': request.args['error_description']}, 401)

    # Obtain JWT and the keys to validate the signature
    id_token = resp['id_token']
    jwks = urlopen("https://"+current_app.config['AUTH0_BASEURL']+"/.well-known/jwks.json")

    payload = jwt.decode(id_token, jwks.read(), algorithms=['RS256'],
                         audience=current_app.config['AUTH0_CONSUMER_KEY'], issuer="https://"+current_app.config['AUTH0_BASEURL']+"/")

    session['jwt_payload'] = payload

    session['profile'] = {
        'user_id': payload['sub'],
        'name': payload['name'],
        'picture': payload['picture']
    }

    return redirect('/example-form')

@frontend.route('/login')
def login():
    host = urlparse(request.url_root).netloc
    scheme = urlparse(request.url_root).scheme
    callback = scheme + '://' + host + '/callback'
    return oauth.auth0.authorize(callback=callback)

@frontend.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('frontend.index', _external=True), 'client_id': current_app.config['AUTH0_CONSUMER_KEY']}
    return redirect('https://' + current_app.config['AUTH0_BASEURL'] + '/v2/logout?' + urlencode(params))
