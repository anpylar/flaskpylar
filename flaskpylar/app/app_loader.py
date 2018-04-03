###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path
from urllib.parse import urlencode

from flask import (Blueprint, redirect, render_template, request,
                   send_from_directory, url_for, abort)

import flask_login
from flask_login import current_user

from . import app


def load_app(
        bpname,
        _login_required=False,  # holds callable to control access to view
        _login_to=False,  # if True and logged go to app.config['LOGIN_TO']
        _local_template=False,  # if True use local template bpname.index.html
        **kwargs):

    login_required = flask_login.login_required
    if not _login_required:
        # if no callable has been passed, create a nop decorator
        def login_required(x):
            return x

    # Set a url_prefix if not given
    url_prefix = kwargs.setdefault('url_prefix', '/' + bpname)
    if url_prefix.endswith('/'):  # avoid trailing / which ends up being //
        kwargs['url_prefix'] = url_prefix[:-1]

    # Convention: dev directory at same level as main static_folder
    # applicatins, right below it
    dev_f = os.path.join(app.static_folder, '..', app.config['FLASKPYLAR_DEV'])

    FAPPS = app.config['FLASKPYLAR_APPS']
    base_folder = os.path.join(dev_f, FAPPS)

    if app.config['TESTING']:
        static_folder = os.path.join(base_folder, bpname, 'static')
    else:
        static_folder = os.path.join(app.static_folder, FAPPS, bpname)

    temp_folder = None
    index_name = 'index.html'  # global template
    if _local_template:
        # Choose blueprint index.html
        index_name = bpname + '.' + index_name
        if app.config['TESTING']:
            temp_folder = os.path.join(base_folder, bpname, 'templates')
        else:
            temp_folder = os.path.join(app.template_folder, FAPPS, bpname)

    # Both templates and static files will be pulled from our apps directory
    mod = Blueprint(bpname, __name__,
                    template_folder=temp_folder,
                    static_folder=static_folder,
                    **kwargs)

    # During development and testing, serve an unoptimized anpylar.js from
    # dev's dir. This is in the template as '.bpstatic' (for Blueprint static)
    # The template switches to 'static' when not TESTING.
    # This allows to serve from the static root and blueprints can have an
    # independent static folder (same as with templates)
    if app.config['TESTING']:
        @mod.route('/bpstatic/<filename>')
        def bpstatic(filename):
            return send_from_directory(dev_f, filename)

    @mod.route('/')
    @mod.route('/<path:path>')
    @login_required
    def index(path=None):
        if _login_to and current_user.is_authenticated:
            login_to = app.config.get('LOGIN_TO', {}).copy()
            app.logger.debug('login_to: %s', str(login_to))
            next_to = login_to.pop('next', '')
            if not next_to:
                abort(404)

            if login_to:
                next_to = '?'.join(next_to, urlencode(list(login_to.items())))

            return redirect(next_to)

        app.logger.debug('mod.static_folder is: %s', static_folder)
        if path is None:  # simplest case, / called ... calling for index
            # use ".index.html" for custom template in blueprint folder
            app.logger.debug('kwargs is: %s', str(kwargs))
            return render_template(index_name, **kwargs)

        if not app.config['TESTING']:  # return imports only during testing
            abort(404)

        # brython imports look like this: xxx.py?v=1234567890
        isimport = len(request.args) == 1 and 'v' in request.args
        if not isimport:
            # not an import, it is a path. redirect to root with the path
            # as a "route" argument for the router in anpylar to use it
            return redirect(url_for('.index', route=path))

        # It is an import, return it, check format
        if path.startswith(app.config['FLASKPYLAR_APP_PKG'] + '/'):
            # inside app, add blueprint name
            # ppath = os.path.join(mod.static_folder, bpname)
            ppath = os.path.join(base_folder, bpname)
        else:  # outside app, return at static folder level
            # ppath = mod.static_folder
            ppath = base_folder

        return send_from_directory(ppath, path)  # simply return the file

    # Blueprint and routes created, register it and return it
    app.register_blueprint(mod)
    return mod
