###############################################################################
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from flask_login import LoginManager, UserMixin
from passlib.apps import custom_app_context as pwd_context


from . import app

login_manager = LoginManager(app)  # available as app.login_manager


@login_manager.user_loader
def load_user(uid):
    return User.get_by_id(uid)


class User(UserMixin):
    _USERS = {
        'test': ('0', pwd_context.encrypt('test')),  # name: (uid, pwd)
    }

    # Convert to: uid: (name, hash)
    _USERS_ID = {idpwd[0]: (name, idpwd[1]) for name, idpwd in _USERS.items()}

    def __init__(self, uid, username, passhash):
        self.id = uid  # mixin expects 'id'
        self.username = username
        self.passhash = passhash

    def check_password(self, password):
        return pwd_context.verify(password, self.passhash)

    @staticmethod
    def get_by_id(uid):
        try:
            username, passhash = User._USERS_ID[uid]
        except KeyError:
            return None  # Failed to find user by uid

        return User(uid, username, passhash)

    @staticmethod
    def get_by_name(username):
        try:
            uid, passhash = User._USERS[username]
        except KeyError:
            return None  # Failed to find user by name

        return User(uid, username, passhash)
