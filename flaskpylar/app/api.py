###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from urllib.parse import urlencode

from flask import abort, jsonify, request, Blueprint
from flask_login import current_user, login_required, login_user, logout_user


from passlib.apps import custom_app_context as pwd_context

from . import app
from . user_management import User
from . import pyroes_management

mod = Blueprint(
    'api',
    __name__,
    url_prefix='/api',
)


@mod.route('/login', methods=['POST'])
def login():
    app.logger.debug('LOGINTO is: %s', str(app.config.get('LOGIN_TO', {})))
    if current_user.is_authenticated:
        l_to = app.config.get('LOGIN_TO', {}).copy()
        return urlencode(list(l_to.items()))

    fdata = request.form
    app.logger.debug('fdata is: %s', fdata)
    username = fdata.get('username', '')
    if not username:
        return abort(401)  # cannot authenticate without username

    user = User.get_by_name(username=username)
    if not user:
        return abort(401)  # username doesn't exist

    password = fdata.get('password', '')
    if not user.check_password(password):
        return abort(401)  # password failed

    login_user(user)  # remember=fdata.get('remember_me', False))
    l_to = app.config.get('LOGIN_TO', {}).copy()
    return urlencode(list(l_to.items()))


@mod.route('/logged', methods=['POST, GET'])
def logged():
    if not current_user.is_authenticated:
        abort(401)

    return ''  # 200 OK


@mod.route('/logout')
def logout():
    logout_user()
    return ''  # 200 OK


@mod.route('/pyroes/')
@mod.route('/pyroes/list')
@login_required
def plist():
    return jsonify(pyroes_management.get_pyroes(current_user.id))


app.register_blueprint(mod)
