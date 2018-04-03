###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import uuid

from flask import Flask, abort, redirect
import jinja2


class Flask(Flask):

    # http://fewstreet.com/2015/01/16/flask-blueprint-templates.html
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.jinja_loader = jinja2.ChoiceLoader([
            self.jinja_loader,
            jinja2.PrefixLoader({}, delimiter='.')
        ])

    def create_global_jinja_loader(self):
        return self.jinja_loader

    def register_blueprint(self, bp, *args, **kwargs):
        super().register_blueprint(bp, *args, **kwargs)
        self.jinja_loader.loaders[1].mapping[bp.name] = bp.jinja_loader

    # Doing things just before run, allows us to have app declared at module
    # level and modifiy the config (TESTING True/False) with the definitions in
    # the blueprints and routes here having access to the modified
    # configuration (from run.py)
    def run(self, *args, **kwargs):
        # Avoid this pestering browser request from getting to the blueprints
        # should actually be handled by web-server
        @app.route('/favicon.ico')
        def favicon():
            abort(404)

        # Go to default blueprint below
        @app.route('/')
        @app.route('/<path:path>')
        def index(path=None):
            return redirect('/pyroes')

        # Load modules which define routes
        from . import api
        from . import app_loader

        # Set our default login view
        from . user_management import login_manager
        login_manager.login_view = '/users'

        app_loader.load_app('users',
                            _login_to=True,
                            url_prefix='/users')

        # Hint where to go after login
        app.config['LOGIN_TO'] = {'next': '/pyroes'}

        # Content blueprint
        app_loader.load_app('pyroes',
                            _login_required=True,
                            _local_template=True)

        # Now delegate to original Flask.run
        super().run(*args, **kwargs)


# Create an configure the app
app = Flask(__name__)
app.config.from_object('config_flaskpylar')
app.config.from_object('config')


# Define a CSRF Token Generator for Forms
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = uuid.uuid4().hex
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token
