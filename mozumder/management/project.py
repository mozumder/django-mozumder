#!/usr/bin/env python
import sys
import os
from os.path import join, getsize
import argparse

import django
from django.utils.version import get_docs_version
from django.core.management.utils import get_random_secret_key

import mozumder

def create():
    parser = argparse.ArgumentParser(
        description='Create a new Mozumder project.')
    parser.add_argument(
        'project_name',
        action='store',
        help='Name of project. Project directory will be created with this name.')
    parser.add_argument(
        '--db_name',
        action='store',
        default='project_name',
        help='Database Name.')
    parser.add_argument(
        '--db_host',
        action='store',
        default='127.0.0.1',
        help='Database Hostname.')
    parser.add_argument(
        '--db_port',
        action='store',
        default=None,
        help='Database Port.')
    parser.add_argument(
        '--db_admin_user',
        action='store',
        default='postgres',
        help='Database Admin User Name.')
    parser.add_argument(
        '--db_admin_pw',
        action='store',
        default=None,
        help='Database Admin User Password.')
    parser.add_argument(
        '--db_user',
        action='store',
        help='Database User Name.')
    parser.add_argument(
        '--db_user_pw',
        action='store',
        help='Database User Password.')
    parser.add_argument(
        '--uwsgi',
        action='store_true',
        default=False,
        help='Create UWSGI vassal .ini file.')
    parser.add_argument(
        '--uwsgi_rundir',
        action='store',
        default='/var/run/uwsgi',
        help='UWSGI run directory for temporary run files.')
    parser.add_argument(
        '--uwsgi_logdir',
        action='store',
        default='/var/log/uwsgi',
        help='UWSGI log directory.')
    parser.add_argument(
        '--uwsgi_additional_http_sockets',
        nargs='*',
        action='store',
        default=['127.0.0.1:8010'],
        help='Additional HTTP sockets for UWSGI. Connect to these for debugging purposes without going through the main HTTP reverse proxy web server. Make sure these are only accessible in your debug environment.')
    args = parser.parse_args()

    # Set some template variables from command line
    project_name = args.project_name
    db_name = args.db_name
    if db_name == 'project_name':
        db_name = project_name
    db_host = args.db_host
    db_port = args.db_port
    if db_port == None:
        db_port = ''
    db_admin_user = args.db_admin_user
    db_admin_pw = args.db_admin_pw
    db_user = args.db_user
    db_user_pw = args.db_user_pw

    # Set some internally generated template variables
    secret_key = get_random_secret_key()
    django_version = django.__version__
    docs_version = get_docs_version()

    # Get path by deleting '/__init__.py' from pathname
    source_root = os.path.join(mozumder.__file__[:-12], 'include','project_template')
    source_root_length = len(source_root)

    target_root = os.path.join(os.getcwd(),project_name)
    venvs_dir = os.path.join(target_root,'venv')
    venv_dir = os.path.join(venvs_dir,project_name)
    access_rights = 0o755

    try:
        os.mkdir(target_root, access_rights)
    except OSError:
        print (f"Creation of project directory {target_root} failed")
    else:
        print (f"Created project directory {target_root}")

    for root, dirs, files in os.walk(source_root):
        # Process files from source templates directory and install
        # them in the new project directory
        sub_dir = root[source_root_length+1:]
        if sub_dir == 'project_name':
            sub_dir = project_name
        target_path = os.path.join(target_root, sub_dir)
        for name in dirs:
            if name == 'project_name':
                name = project_name
            path = os.path.join(target_path, name)
            try:
                os.mkdir(path,mode=0o755)
            except OSError:
                print (f"Creation of the directory {path} failed")
        for name in files:
            source_filename = os.path.join(root, name)
            f = open(source_filename, "r")
            fstring_from_file = 'f"""'+f.read()+'"""'
            f.close()
            
            # Evaluate F-String
            compiled_fstring = compile(fstring_from_file, source_filename, 'eval')
            formatted_output = eval(compiled_fstring)
            
            # Write evaluated F-String
            target_filename = os.path.join(target_path, name)
            f = open(target_filename, "w")
            f.write(formatted_output)
            f.close()
    if args.uwsgi == True:
        uwsgi_rundir = args.uwsgi_rundir
        uwsgi_logdir = args.uwsgi_logdir
        http_socket = ''
        for http_socket_host in args.uwsgi_additional_http_sockets:
            http_socket += http_socket_host + '\n'

        target_filename = os.path.join(target_root, 'uwsgi.ini')
        f = open(target_filename, "w")
        f.write(
f"""[uwsgi]
home            = {venv_dir}
chdir           = {target_root}
app             = {project_name}
base            = %v
module          = %(app).wsgi:application
socket          = {uwsgi_rundir}/%(app).uwsgi.sock
fastcgi-socket  = {uwsgi_rundir}/%(app).fastcgi.sock
wsgi-file       = %(base)/%(app)/wsgi.py

env             = DJANGO_SETTINGS_MODULE={project_name}.settings
env             = DJANGO_SECRET_KEY='{secret_key}'
env             = DJANGO_DEBUG=False
env             = POSTGRES_DB={db_name}
env             = POSTGRES_HOST={db_host}
env             = POSTGRES_PORT={db_port}
env             = POSTGRES_USER={db_user}
env             = POSTGRES_PW={db_user_pw}
env             = PYTHONPYCACHEPREFIX=~/.pycache
processes       = 1
threads         = 8
import          = analytics.apps
{http_socket}
#mule            = analytics/management/utilities/log_mule.py
#mule            = mozumder/management/utilities/cache_mule.py
farm            = logger:1
farm            = cache:2
#import          = analytics.apps
#import          = mozumder.apps
stats           = {uwsgi_rundir}/%(app).stats.sock
logger          = file:{uwsgi_logdir}/%(app).log
req-logger      = file:{uwsgi_logdir}/%(app).access
log-format      = %(ftime) %(pid):%(core):%(switches) %(addr) %(user) %(proto) %(referer) %(method) %(uri) %(status) %(rsize)b %(micros)us (%(vars)v, %(pktsize)b) (%(headers)h, %(hsize)b) "%(uagent)"
log-date        = %%Y-%%m-%%d %%H:%%M:%%S
logformat-strftime

[uwsgi]
chmod-socket    = 660
master          = true
die-on-term     = true
no-orphans      = true
vacuum          = true
auto-procname   = true
threaded-logger = true
enable-threads  = true
no-threads-wait = true
procname-prefix = %(app).
""")
        f.close()
