#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import pprint
import os
import os.path
from app import app

from jinja2.environment import create_cache

if False:
    import logging
    import sys
    log = logging.getLogger('werkzeug')
    out_hdlr = logging.StreamHandler(sys.stdout)
    log.setLevel(logging.DEBUG)
    log.addHandler(out_hdlr)


class LoggingMiddleware(object):
    '''
    https://stackoverflow.com/q/25466904
    '''
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(environ, log_response)


def run():
    args = parse_args()

    app.config['TESTING'] = not args.no_testing
    if args.logging:
        app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    extra_files = []
    if args.debug:
        app.jinja_env.cache = create_cache(0)
        # app.app.config['TEMPLATES_AUTO_RELOAD'] = True
        extra_dirs = ['static', 'templates']
        extra_files = extra_dirs[:]
        for extra_dir in extra_dirs:
            for dirname, dirs, files in os.walk(extra_dir):
                for filename in files:
                    filename = os.path.join(dirname, filename)
                    if os.path.isfile(filename):
                        extra_files.append(filename)

    # run the app
    if False:
        app.logger.addHandler(out_hdlr)

    app.run(host='0.0.0.0', debug=args.debug, extra_files=extra_files)


def parse_args():
    # prepare and parse args
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='flaskyplar demo')

    parser.add_argument('--debug', required=False, action='store_true',
                        help=('run in debug mode'))

    parser.add_argument('--no-testing', required=False, action='store_true',
                        help=('disable testing mode'))

    parser.add_argument('--logging', required=False, action='store_true',
                        help=('log everything possible from wsgi'))

    return parser.parse_args()


if __name__ == '__main__':
    run()
