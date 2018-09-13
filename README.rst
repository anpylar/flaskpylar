*Flaskpylar*
############

.. image:: https://img.shields.io/github/release/anpylar/anpylar.svg
   :alt: Release
   :scale: 100%
   :target: https://github.com/anpylar/anpylar/releases/

.. image:: https://img.shields.io/github/license/anpylar/anpylar.svg
   :alt: License MIT
   :scale: 100%
   :target: https://github.com/anpylar/anpylar/blob/master/LICENSE


A sample skeleton showing the combination of *AnPyLar* and *Flask*. With the
goal to show how a real full-stack Python application can be made.

The application does nothing really useful, but it shows how a login can be
handled both on the client and on the server using Python and how logged users
have access to a component which can only fetch info if logged in.

No database is used to keep users, as there is only one test user. This
simplifies running and playing around with this skeleton.

Things are kept tidy using ``pipenv`` which will install

  - ``anpylar`` (as a development package only)
  - ``flask`` which is the core for the server side app
  - ``flask-login`` is used to control user management
  - ``uwsgi`` in case you'd like to run the app directly with it

To get things ready do::

  cd flaskpylar
  pipenv install --dev  # to include development packages

Login Details
*************

The sample application has only one valid user with the following credentials

  - Username: ``test``
  - Password: ``test``

Layout and development
**********************

Main directory
**************
::

  flaskpylar
  ...
  ├── app-manager.py
  ├── config_flaskpylar.py
  ├── config.py
  ├── Pipfile
  ├── Pipfile.lock
  ├── run.py
  ├── uwsgi.conf
  ├── uwsgi-run.py
  └── webignore

Holds the management scripts, requirement files and general and ``flaskpylar``
specific configuration


Server Side
***********
::

  flaskpylar
  ├── app
  ... ...
  │   ├── static
  │   ├── templates
  │   │   ├── index.html
  │   │   └── layout.html
  │   ├── __init__.py
  │   ├── api.py
  │   ├── app_loader.py
  │   ├── pyroes_management.py
  │   └── user_management.py
  ...

Things start out with a usual ``flask`` layout: things are under the directory
``app``. In this sample the server-side components are in

  - ``app/__init__.py`` - Kickstarts the custom ``Flask`` object

  - ``app/pyroes_management.py`` - dict holding *Pyroes* in place of a real
    database

  - ``app/user_management.py`` - Classes and management for ``flask-login``

  - ``app/api.py`` - The API the client side components will use

  - ``app/app_loader.py``  **THE KEY**

    It generates a Flask *Blueprint* for each client side component. This is
    made here in a generic way and would probably needs specific *Blueprints*
    for specific needs of real world applications.

The core code in ``app/__init__.py`` is::

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


There are only 2 client side pages and each gets a Blueprint with
``app_loader.load_app``. The *Blueprint* already understands the layout of the
client side applications on the disk (the templates account for the differences
if needed by checking the value of ``app.config['TESTING']``.

Client Side
***********

The chosen pattern on the server side was to create a *Blueprint* per component
on the client side. The pattern here is:

  - Each component is a complete *AnPyLar* module (or mini-application)

It fits the multi-page paradigm of working with ``Flask``. The usual pattern
for an *AnPyLar* only application is ``SPA`` (*Single Page Application*) in
which a single *AnPyLar* module controls the entire routing and lifecycle of
components (it may of course foster sub-modules)

Everything is under the ``dev`` directory::

  flaskpylar
  ├── app
  │   ├── dev
  │   │   ├── apps
  │   │   │   ├── libs
  │   │   │   │   ├── api
  │   │   │   │   │   └── __init__.py
  │   │   │   │   ├── hello
  │   │   │   │   │   └── __init__.py
  │   │   │   │   └── __init__.py
  │   │   │   ├── pyroes
  │   │   │   │   ├── app
  │   │   │   │   │   ├── __init__.py
  │   │   │   │   │   ├── app_component.py
  │   │   │   │   │   └── app_module.py
  │   │   │   │   ├── static
  │   │   │   │   │   └── sample.jpg
  │   │   │   │   └── templates
  │   │   │   │       └── index.html
  │   │   │   └── users
  │   │   │       ├── app
  │   │   │       │   ├── __init__.py
  │   │   │       │   ├── app_component.css
  │   │   │       │   ├── app_component.html
  │   │   │       │   ├── app_component.py
  │   │   │       │   └── app_module.py
  │   │   │       └── static
  ... ... ...

As shown, each mini-application can have its own set of ``static`` files and
``templates`` if needed be (the sample shows how the ``pyroes`` mini-app uses
this facility)

Managing
********

The sample comes with a script called ``app-manager.py`` which can be used to
manage the packaging and web-packaging of the application. It uses the commands
of the ``anpylar-cli`` command family to do so (hence the need to have
``anpylar`` installed as a development package). See below the complete usage
help.

Although the ``app-manager`` has several command line switches (see below for a
complete reference), there are three (3) common use cases

Initializing
============
::

   pipenv run ./app-manager --init

Creates the ``dev`` directory where client side apps go and creates an initial
``anpylar.js`` bundle (non-optimized and with debug info enabled) inside.

This is meant to kick-start development and things will be run and tested
usually with the command (see below for a longer explanation)::

  pipenv run ./run.py --debug

Packing
=======
::

   pipenv run ./app-manager

Takes the client side components inside the ``dev`` directory, packages them
and moves them to the ``static`` and ``templates`` directory of the server side
application, in order for them to be delivered as if they were on the server.

This is meant for a close-to-production test of things and is usually meant to
be run with the command (see below for a longer explanation)::

  pipenv run ./run.py --no-testing

Webpacking
==========
::

  pipenv run ./app-manager --webpack

This takes the already packed application and generates a bundle (optimized and
with no debug info) that can be taken for deployment to a server (with for
example a combination of ``nginx`` and ``uwsgi``) The default directory for the
bundle is ``__webpack__`` but can be given as ``__webpack__ DIRNAME``

When *webpacking* the application manager pays attention to the patterns in the
file ``webignore`` (usual shell wildcard patterns) to ignore any specified
pattern for inclusion in the *webpack*

Running
*******

During development run as::

  pipenv run ./run.py --debug
  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
  * Restarting with stat
  * Debugger is active!
  * Debugger PIN: 144-058-227

This logs messages to the console and has *Werkzeug* also running in debug
mode. Python files (and associated *html/css* files, should there be) for
client side mini-applications will be fetched directly from the development
directory.

The application can be packed (do not confuse with *webpacking*) to test how
things would work on the production server. The usual sequence of commands will
be::

  pipenv run ./app-manager.py
  pipenv run ./run.py --not-testing  # you may also add --debug if wished

When the application is *webpacked*, things are expected to be taken to a
production server, where you may run them with, for example, ``uwsgi``. The
provided configuration file can be matched to usual, for example, ``nginx``
configurations.

Usage
*****

run.py
======
::

  $ ./run.py --help
  usage: run.py [-h] [--debug] [--no-testing] [--logging] [--flush]

  flaskyplar demo

  optional arguments:
    -h, --help    show this help message and exit
    --debug       run in debug mode (default: False)
    --no-testing  disable testing mode (default: False)
    --logging     log everything possible from wsgi (default: False)

Where:

  - ``--debug`` (should actually be ``--development``) runs with debugging
    output enabled and directly from the sources

  - ``--no-testing`` runs the app from individual packaged files and expects
    static files /templates for client side components to be in the right
    directories (see ``app-manager`` above)

  - ``--logging`` -  does log the WSGI requests/responses

app-manager.py
==============
::

  $ ./app-manager.py --help
  usage: app-manager [-h] [--init] [--webpack [WEBPACK]] [--keep-dev]
                     [--web-ignore WEB_IGNORE] [--workdir WORKDIR]
                     [--devdir DEVDIR] [--appsdir APPSDIR] [--outdir OUTDIR]
                     [--clean-output] [--bundle-name BUNDLE_NAME] [--no-debug]
                     [--no-optimize] [--no-bundle] [--no-paketize]
                     [--quiet | --verbose]

  Flaskpylar paketizer

  optional arguments:
    -h, --help            show this help message and exit
    --quiet, -q           Remove output (errors will be reported) (default:
                          False)
    --verbose, -v         Increase verbosity level (default: False)

  Initialization options:
    --init                Create dev dir and deploy bundle (default: False)

  WebPacking options:
    --webpack [WEBPACK]   Create a deployment which packs everything except the
                          contents of the development directory. If no argument
                          is specified things are deployed to "__webpack__"
                          (default: None)
    --keep-dev            Keep dev directory contents in webpack (default:
                          False)
    --web-ignore WEB_IGNORE
                          Read patterns (unix-shell style) to ignore from the
                          specified file. If not specified, then a file named
                          webignore will be used if available (default: None)
    --web-debug           The default for webpacking is to generate a bundle
                          with no debugging. Use this option to enable it. Has
                          precedence over the --no-debug flag (default: False)

  Directory/File Options:
    --workdir WORKDIR     Override auto working directory detection (default:
                          None)
    --devdir DEVDIR       Development directory where to find sources (default:
                          dev)
    --appsdir APPSDIR     Apps directory under dev/output dir (default: apps)
    --outdir OUTDIR       Base output directory under workdir (default: static)
    --clean-output        Remove apps dir under output before starting (default:
                          False)

  Bundle Generation:
    --bundle-name BUNDLE_NAME
                          File Name for anpylar.js output (default: anpylar.js)
    --no-debug            Generate no debug version of anpylar (default: False)
    --no-optimize         Generate no debug version of anpylar (default: False)
    --no-bundle           Skip generation of anpylar bundle (default: False)
    --no-paketize         Skip paketization of apps (default: False)
