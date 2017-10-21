from flask import Flask
from flask_bootstrap import Bootstrap

from .frontend import frontend
from .nav import nav
from .oauth import oauth

import json
import os

class Config(object):
    with open(os.environ['APPMAN_SETTINGS']) as data_file:
        data = json.load(data_file)
    for key in data:
        locals()[key] = data[key]

def create_app():
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__)

    #app.config.from_envvar('APPMAN_SETTINGS')
    app.config.from_object('application_manager.Config')

    # Install our Bootstrap extension
    Bootstrap(app)

    # Our application uses blueprints as well; these go well with the
    # application factory. We already imported the blueprint, now we just need
    # to register it:
    app.register_blueprint(frontend)

    # Because we're security-conscious developers, we also hard-code disabling
    # the CDN support (this might become a default in later versions):
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # We initialize the navigation as well
    nav.init_app(app)

    oauth.init_app(app)

    oauth.remote_app(
        'auth0',
        consumer_key=app.config['AUTH0_CONSUMER_KEY'],
        consumer_secret=app.config['AUTH0_CONSUMER_SECRET'],
        request_token_params={
            'scope': 'openid profile',
            'audience': 'https://' + app.config['AUTH0_BASEURL'] + '/userinfo'
        },
        base_url='https://%s' % app.config['AUTH0_BASEURL'],
        access_token_method='POST',
        access_token_url='/oauth/token',
        authorize_url='/authorize',
    )


    return app
