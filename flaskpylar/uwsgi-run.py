#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
import argparse
import logging
import os.path
import subprocess
import sys
import traceback


def logconfig(quiet, verbose):
    if quiet:
        verbose_level = logging.ERROR
    else:
        verbose_level = logging.INFO - verbose * 10  # -> DEBUG

    logging.basicConfig(
        # format="%(levelname)s: %(message)s",
        format="%(message)s",
        level=verbose_level
    )


UWSGI_CONF = 'uwsgi.conf'


def run(pargs=None):
    args, parser = parse_args(pargs)
    logconfig(args.quiet, args.verbose)  # configure logging

    rootdir = sys.path[0]  # keep a reference
    try:
        os.chdir(rootdir)
    except OSError:
        logging.error('Failed to chdir to: %s', rootdir)
        traceback.print_exc()
        sys.exit(1)

    if not os.path.exists(UWSGI_CONF):
        logging.error('%s not located, cannot run')
        sys.exit(1)

    run_cmd = ['pipenv', 'run',  'uwsgi', '--ini', 'uwsgi.conf']
    logging.info('Running command: %s', ' '.join(run_cmd))
    try:
        retcode = subprocess.call(run_cmd)
        if retcode:
            logging.error('Execution failed with retcode: %d', retcode)
            sys.exit(retcode)
    except KeyboardInterrupt:
        logging.info('Stopped with Ctrl-C or SIGINT')
        sys.exit(0)
    except Exception as e:
        logging.error('Another Exception stopped the process')
        traceback.print_exc()
        sys.exit(1)


def parse_args(pargs=None, name=None):
    if not name:
        name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    parser = argparse.ArgumentParser(
        prog=name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=('Flaskpylar uwsgi runner')
    )

    pgroup = parser.add_mutually_exclusive_group()
    pgroup.add_argument('--quiet', '-q', action='store_true',
                        help='Remove output (errors will be reported)')

    pgroup.add_argument('--verbose', '-v', action='store_true',
                        help='Increase verbosity level')

    args = parser.parse_args(pargs)
    return args, parser


if __name__ == '__main__':
    run()
