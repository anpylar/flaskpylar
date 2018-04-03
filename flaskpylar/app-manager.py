#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
# Copyright 2018 Daniel Rodriguez. All Rights Reserved.
# Use of this source code is governed by the MIT license
###############################################################################
import argparse
import fnmatch
import logging
import os
import os.path
import shutil
import subprocess
import sys
import traceback

import config_flaskpylar as confpylar


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


DEV_DIR = confpylar.FLASKPYLAR_DEV
APPS_DIR = confpylar.FLASKPYLAR_APPS
OUT_DIR = 'static'
BUNDLE_NAME = 'anpylar.js'
WORK_DIR = 'app'
WEBIGNORE = 'webignore'
APP_PKG = confpylar.FLASKPYLAR_APP_PKG


class Ignorer:
    # Define a function object which filters which things go to deployment
    def __init__(self, rootdir, devdir, keep_dev, skip_patterns):
        self.rootdir = rootdir
        self.devdir = devdir
        self.keep_dev = keep_dev
        self.skip_patterns = skip_patterns

    def __call__(self, d, listdir):
        to_ignore = []

        # Check if dev dir and skipping all contents is needed
        if not self.keep_dev:
            for l in listdir:
                ld = os.path.join(d, l)
                if os.path.samefile(self.devdir, ld):
                    logging.info('Skipping devdir: %s', ld)
                    to_ignore.append(l)  # append l from listdir
                    break

        # Check patterns
        for p in self.skip_patterns:
            to_ignore.extend(fnmatch.filter(listdir, p))

        # unique names in the list
        to_ignore = list(set(to_ignore))
        rel_d = os.path.relpath(d, self.rootdir)
        logging.info('Directory: %s -> ignoring %s', rel_d, to_ignore)
        return to_ignore


def run(pargs=None):
    args, parser = parse_args(pargs)
    logconfig(args.quiet, args.verbose)  # configure logging

    # Work out directories
    if args.workdir:
        workdir = args.workdir
        logging.info('Taking specified workdir in arguments')
    else:
        wd1 = os.path.normpath(os.path.join(sys.path[0], WORK_DIR))
        logging.info('Trying workdir: %s', wd1)
        if os.path.exists(wd1):
            workdir = wd1
        else:
            logging.error('Workdir autodetection failed')
            sys.exit(1)

    rootdir = os.path.join(workdir, '..')

    logging.info('rootdir: %s', rootdir)
    logging.info('workdir: %s', workdir)

    # relative will be usually shorter (better for command line arguments)
    relworkdir = os.path.relpath(workdir)
    if len(relworkdir) < len(workdir):
        workdir = relworkdir
        rootdir = os.path.relpath(rootdir)
        logging.info('Using relative workdir: %s', relworkdir)
        logging.info('Using relative rootdir: %s', rootdir)

    tmpldir = os.path.join(workdir, 'templates')
    logging.info('templates dir: %s', tmpldir)

    staticdir = os.path.join(workdir, 'static')
    logging.info('static dir: %s', staticdir)

    devdir = os.path.join(workdir, args.devdir)
    logging.info('devdir: %s', devdir)

    appsdir = os.path.join(devdir, args.appsdir)
    logging.info('appsdir: %s', appsdir)

    # Outdir is relative to workdir
    outdir = os.path.normpath(os.path.join(workdir, args.outdir))
    logging.info('outdir: %s', outdir)

    if not os.path.exists(outdir):
        logging.info('Output dir does not exist, creating')
        try:
            os.mkdir(outdir)
        except OSError as e:
            logging.error('Failed: %s', str(e))
            sys.exit(1)

    appsoutdir = os.path.join(outdir, args.appsdir)
    logging.info('appsoutdir: %s', appsoutdir)

    if os.path.exists(appsoutdir):
        logging.info('Output dir for apps does exist')
        if args.clean_output:
            logging.info('Clean-up of output dir for apps: %s', appsoutdir)
            try:
                shutil.rmtree(appsoutdir)
            except OSError as e:
                logging.error('Failed: %s', str(e))
                sys.exit(1)

            ajs_name = os.path.join(outdir, args.bundle_name)
            logging.info('Removing bundle from out dir: %s', ajs_name)
            os.remove(ajs_name)

    if not os.path.exists(appsoutdir):
        logging.info('Output dir for apps does not exist, creating')
        try:
            os.mkdir(appsoutdir)
        except OSError as e:
            logging.error('Failed: %s', str(e))
            sys.exit(1)

    pkg_list = []  # needed for bundle initialization/creationg below
    if not args.init:
        if args.no_paketize:
            logging.info('Skipping paketization')
        else:
            paket_cmd_base = ['anpylar-paketize', '--auto-vfs']
            if not os.path.exists(appsdir):
                logging.error('appsdir %s does not exist. No pakets', appsdir)
                d, dnames, fnames = '', [], []
            else:
                d, dnames, fnames = next(os.walk(appsdir))

            # base template destination
            tmpldst = os.path.join(tmpldir, APPS_DIR)
            staticdst = os.path.join(staticdir, APPS_DIR)

            for dname in dnames:
                fdname = os.path.join(appsdir, dname)
                logging.info('Paketizing: %s', fdname)
                apptarget = os.path.join(fdname, APP_PKG)
                logging.info('Checking if app or package repo: %s', apptarget)
                if os.path.exists(apptarget):
                    logging.info('Apps has "app" ... paketizing subapp')
                    paket_cmd = paket_cmd_base + (
                        ['--vfspath', APP_PKG, os.path.join(fdname, APP_PKG)])
                else:
                    logging.info('Apps has no "app" ... paketizing complete')
                    paket_cmd = paket_cmd_base + [fdname]

                filename = os.path.basename(fdname) + '.auto_vfs.js'
                outfile = os.path.join(appsoutdir, filename)
                pkg_list += ['--auto-vfs', outfile]
                logging.info('output file for paket is: %s', outfile)
                paket_cmd.append(outfile)

                logging.info('Executing command "%s"', ' '.join(paket_cmd))
                ret = subprocess.call(paket_cmd)
                if ret:
                    logging.error('Command failed with code: %d', ret)
                    sys.exit(1)

                # Manage static files
                logging.info('Managing static files for: %s', fdname)
                staticapp = os.path.join(fdname, 'static')
                if not os.path.exists(staticapp):
                    logging.info('No static files found for: %s', dname)
                    continue

                statictarget = os.path.join(staticdst, dname)
                if os.path.exists(statictarget):
                    logging.info('Deleting static target for %s at %s',
                                 dname, statictarget)
                    try:
                        shutil.rmtree(statictarget)
                    except:
                        logging.error('Error removing dir')
                        logging.error(traceback.format_exc())
                        sys.exit(1)
                try:
                    logging.info('copytree %s -> %s', staticapp, statictarget)
                    shutil.copytree(staticapp, statictarget)
                except:
                    logging.error('Error during template copying')
                    logging.error(traceback.format_exc())
                    sys.exit(1)

                # Template section
                logging.info('Looking for templates for: %s', fdname)

                # Now put the templates in place
                tmplapp = os.path.join(fdname, 'templates')
                if not os.path.exists(tmplapp):
                    logging.info('No templates found for: %s', dname)
                    continue

                tmpltarget = os.path.join(tmpldst, dname)
                if os.path.exists(tmpltarget):
                    logging.info('Deleting template target for %s at %s',
                                 dname, tmpltarget)
                    try:
                        shutil.rmtree(tmpltarget)
                    except:
                        logging.error('Error removing dir')
                        logging.error(traceback.format_exc())
                        sys.exit(1)
                try:
                    logging.info('copytree %s -> %s', tmplapp, tmpltarget)
                    shutil.copytree(tmplapp, tmpltarget)
                except:
                    logging.error('Error during template copying')
                    logging.error(traceback.format_exc())
                    sys.exit(1)

    else:
        logging.info('Initializing. Skipping package paketization')
        logging.info('Initializing dev dir. Optimize: False, Debug: True')
        args.no_optimize = True
        args.no_debug = False

        logging.info('Making dev directory: %s', devdir)
        try:
            os.mkdir(devdir)
        except OSError as e:
            logging.error('Failed: %s', str(e))
            sys.exit(1)

        logging.info('Making dev apps directory: %s', appsdir)
        try:
            os.mkdir(appsdir)
        except OSError as e:
            logging.error('Failed: %s', str(e))
            sys.exit(1)

        logging.info('Setting outdir for bundle to devdir')
        outdir = devdir

    if not args.init and args.no_bundle:
        logging.info('Skipping generation of anpylar bundle')
    else:
        logging.info('Preparing command for bundle generation')
        # Do the bundle now
        bundle_cmd = ['anpylar-bundle', '--skip-packages']
        if args.webpack:
            if args.web_debug:
                bundle_cmd.append('--debug')

        elif not args.no_debug:
            bundle_cmd.append('--debug')

        if not args.no_optimize:
            bundle_cmd.append('--optimize')

        bundle_cmd += pkg_list
        ajs_name = os.path.join(outdir, args.bundle_name)
        bundle_cmd.append(ajs_name)

        logging.info('Creating bundle with command: %s', ' '.join(bundle_cmd))
        ret = subprocess.call(bundle_cmd)
        if ret:
            logging.error('Command failed with code: %d', ret)
            sys.exit(1)

    if args.init:
        sys.exit(0)  # nothing else to do

    # Webpacking if requested
    if args.webpack:
        logging.info('Webpacking')
        webdir = os.path.join(rootdir, args.webpack)
        if os.path.exists(webdir):
            logging.info('Webpack dir %s exists. Removing', webdir)
            try:
                shutil.rmtree(webdir)
            except OSError as e:
                logging.error('Failed: %s', str(e))
                sys.exit(1)

        # Note: copytree creates the output directory itself

        # read patterns from file if possible
        if args.web_ignore:
            if not os.path.exists(args.web_ignore):
                logging.error('Webignore not found: %s', args.web_ignore)
                sys.exit(1)

            webignore = args.web_ignore
        else:
            webignore = os.path.join(rootdir, WEBIGNORE)
            if os.path.exists(webignore):
                logging.info('Using standard webignore at: %s', webignore)
            else:
                webignore = None

        if webignore:
            logging.info('Reading skip patterns from: %s', webignore)
            try:
                with open(webignore, 'r') as f:
                    skip_patterns = [l.rstrip() for l in f]
            except OSError as e:
                logging.error('Failed: %s', str(e))
                sys.exit(1)
        else:
            logging.info('No skip patterns read from any file')
            skip_patterns = []

        # Create an Ignorer to skip some files
        ignorer = Ignorer(rootdir, devdir, args.keep_dev, skip_patterns)
        # Proceed to actual tree copying
        try:
            shutil.copytree(rootdir, webdir, ignore=ignorer)
        except:
            logging.error('Error during webpack copying')
            logging.error(traceback.format_exc())
            sys.exit(1)


def parse_args(pargs=None, name=None):
    if not name:
        name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    parser = argparse.ArgumentParser(
        prog=name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=('Flaskpylar paketizer')
    )

    pgroup = parser.add_argument_group(title='Initialization options')
    pgroup.add_argument('--init', action='store_true',
                        help='Create dev dir and deploy bundle')

    pgroup = parser.add_argument_group(title='WebPacking options')
    pgroup.add_argument('--webpack', action='store', nargs='?',
                        default=None, const='__webpack__',
                        help=('Create a deployment which packs everything'
                              ' except the contents of the development'
                              ' directory. If no argument is specified'
                              ' things are deployed to "__webpack__"'))

    pgroup.add_argument('--keep-dev', action='store_true',
                        help=('Keep dev directory contents in webpack'))

    pgroup.add_argument('--web-ignore', action='store',
                        help=('Read patterns (unix-shell style) to ignore '
                              ' from the specified file'
                              '. If not specified, then a file named {}'
                              ' will be used if available'.format(WEBIGNORE)))

    pgroup.add_argument('--web-debug', action='store_true',
                        help=('The default for webpacking is to generate a'
                              ' bundle with no debugging. Use this option to'
                              ' enable it. Has precedence over the --no-debug'
                              ' flag'))

    pgroup = parser.add_argument_group(title='Directory/File Options')
    pgroup.add_argument('--workdir', action='store',
                        help='Override auto working directory detection')

    pgroup.add_argument('--devdir', action='store', default=DEV_DIR,
                        help='Development directory where to find sources')

    pgroup.add_argument('--appsdir', action='store', default=APPS_DIR,
                        help='Apps directory under dev/output dir')

    pgroup.add_argument('--outdir', action='store', default=OUT_DIR,
                        help='Base output directory under workdir')

    pgroup.add_argument('--clean-output', action='store_true',
                        help='Remove apps dir under output before starting')

    pgroup = parser.add_argument_group(title='Bundle Generation')
    pgroup.add_argument('--bundle-name', action='store', default=BUNDLE_NAME,
                        help='File Name for anpylar.js output')

    pgroup.add_argument('--no-debug', action='store_true',
                        help='Generate a no debug version of anpylar')

    pgroup.add_argument('--no-optimize', action='store_true',
                        help='Skip anpylar optimization against used packages')

    pgroup.add_argument('--no-bundle', action='store_true',
                        help='Skip generation of anpylar bundle')

    pgroup.add_argument('--no-paketize', action='store_true',
                        help='Skip paketization of apps')

    pgroup = parser.add_mutually_exclusive_group()
    pgroup.add_argument('--quiet', '-q', action='store_true',
                        help='Remove output (errors will be reported)')

    pgroup.add_argument('--verbose', '-v', action='store_true',
                        help='Increase verbosity level')

    args = parser.parse_args(pargs)
    return args, parser


if __name__ == '__main__':
    run()
