#!/usr/bin/env python
import sys
import os
from os.path import join, getsize
import argparse
from urllib.parse import urlparse

import django
from django.utils.version import get_docs_version
from django.core.management.utils import get_random_secret_key

import mozumder

def create():
    parser = argparse.ArgumentParser(
        description='Create a new Mozumder project.')
    subparsers = parser.add_subparsers(help='Create new project, or create UWSGI vassals file', dest='subparser_name')
    parser.add_argument(
        'project_name',
        action='store',
        help='Name of project. Project directory will be created with this name.')
    parser.add_argument(
        '--db_url',
        action='store',
        help='Database connection URL in the format: postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]')
    parser.add_argument(
        '--db_name',
        action='store',
        default='project_name',
        help='When not using a database URL, name of database to connect to')
    parser.add_argument(
        '--db_host',
        action='store',
        help='When not using a database URL, hostname or IP address of database server')
    parser.add_argument(
        '--db_port',
        action='store',
        help='When not using a database URL, port number of database server')
    parser.add_argument(
        '--db_user_name',
        action='store',
        help='When not using a database URL, username to connect to the database')
    parser.add_argument(
        '--db_user_password',
        action='store',
        help='When not using a database URL, password of user connecting to the database')
    parser.add_argument(
        '--allowed_hosts',
        nargs='*',
        action='store',
        default=['127.0.0.1'],
        help='Comma separated lists of hosts that are allowed to accept connections for the site. Default to: 127.0.0.1')
    parser.add_argument(
        '--log_dir',
        action='store',
        default='log',
        help='Django log directory. Default to: log')
    parser.add_argument(
        '--static_dir',
        action='store',
        default='static',
        help='Static files directory. Default to: static')
    parser.add_argument(
        '--media_dir',
        action='store',
        default='media',
        help='Django log directory. Default to: media')
    parser.add_argument(
        '--virtualenv_dir',
        action='store',
        default='venv',
        help='Python virtualenv directory. Default to: venv')

    parser_startproject = subparsers.add_parser('startproject', help='Create a new Mozumder project')
    parser_uwsgi = subparsers.add_parser('createuwsgi', help='Create a UWSGI Vassal .ini file')

    parser_startproject.set_defaults(func=startproject)

    parser_startproject.add_argument(
        '--db_admin_url',
        action='store',
        default='postgresql://postgres@localhost',
        help='Postgresql Admin database connection URL. This will be used to log in and create the new project database and user. Only uses username and password information. Database connection URL in the format: postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]')
    parser_startproject.add_argument(
        '--db_admin_name',
        action='store',
        help='When not using an database admin URL, admin username to connect to the database')
    parser_startproject.add_argument(
        '--db_admin_password',
        action='store',
        help='When not using an database admin URL, password of admin connecting to the database')
    parser_startproject.add_argument(
        '--create_uwsgi',
        action='store_true',
        default=False,
        help='Create a UWSGI vassals file.')

    parser_uwsgi.set_defaults(func=createuwsgi)

    parser.add_argument(
        '--uwsgi_run_dir',
        action='store',
        default='/var/run/uwsgi',
        help='UWSGI run directory for temporary run files. Default to: /var/run/uwsgi')
    parser.add_argument(
        '--uwsgi_log_dir',
        action='store',
        default='/var/log/uwsgi',
        help='UWSGI log directory. Default to: /var/log/uwsgi')
    parser.add_argument(
        '--uwsgi_http_sockets',
        nargs='*',
        action='store',
        default=['127.0.0.1:8010'],
        help='Comma separated list of additional UWSGI HTTP sockets. Connect to these for debugging purposes without going through the main HTTP reverse proxy web server. Make sure these are only accessible in your debug environment. Default to: 127.0.0.1:8010')
    parser.add_argument(
        '--uwsgi_processes',
        action='store',
        default=1,
        type=int,
        help='Number of UWSGI processes to run. Default 1.')
    parser.add_argument(
        '--uwsgi_threads',
        action='store',
        default=8,
        type=int,
        help='Number of threads per UWSGI process to run. Default 8.')
    args = parser.parse_args()

    args.func(args)

def process_args(args):
    
    # Set some template variables from command line
    project_name = args.project_name
    db_url = args.db_url

    if db_url == None:
        db_host = args.db_host
        db_port = args.db_port if args.db_port else ''
        db_name = args.db_name
        db_username = args.db_user_name
        db_password = args.db_user_password
    else:
        o = urlparse(db_url)
        db_host = o.hostname
        db_port = o.port if o.port else ''
        db_name = o.path[1:]
        db_username = o.username
        db_password = o.password
    allowed_hosts = ",".join(args.allowed_hosts)

    # Set some internally generated template variables
    secret_key = get_random_secret_key()
    django_version = django.__version__
    docs_version = get_docs_version()

    static_dir = args.static_dir
    media_dir = args.media_dir
    log_dir = args.log_dir
    log_file = os.path.join(log_dir, f'{project_name}.log')
    error_log_file = os.path.join(log_dir, f'{project_name}.error.log')
    access_log_file = os.path.join(log_dir, f'{project_name}.access.log')
    cache_log_file = os.path.join(log_dir, f'{project_name}.cache.log')
    db_log_file = os.path.join(log_dir, f'{project_name}.db.log')
    venv_dir = args.virtualenv_dir

    # Get path by deleting '/__init__.py' from pathname
    source_root = os.path.join(mozumder.__file__[:-12], 'include','project_template')
    source_root_length = len(source_root)

    target_root = os.path.join(os.getcwd(),project_name)
    access_rights = 0o755
    log_path = os.path.join(target_root,log_dir)
    venv_path = os.path.join(target_root,venv_dir)
    static_path = os.path.join(target_root,static_dir)

    return project_name, db_host, db_port, db_name, db_username, \
        db_password, allowed_hosts, static_dir, media_dir, \
        log_dir, log_file, error_log_file, access_log_file, \
        cache_log_file, db_log_file, venv_dir, secret_key, \
        django_version, docs_version, source_root, \
        source_root_length, target_root, access_rights, log_path, \
        venv_path, static_path

def startproject(args):

    project_name, db_host, db_port, db_name, db_username, \
        db_password, allowed_hosts, static_dir, media_dir, \
        log_dir, log_file, error_log_file, access_log_file, \
        cache_log_file, db_log_file, venv_dir, secret_key, \
        django_version, docs_version, source_root, \
        source_root_length, target_root, access_rights, log_path, \
        venv_path, static_path = \
        process_args(args)

    db_admin_url = args.db_admin_url
    if db_admin_url == None:
        db_admin_username = args.db_admin_name
        db_admin_password = args.db_admin_password
    else:
        o = urlparse(db_admin_url)
        db_admin_username = o.username
        db_admin_password = o.password

    try:
        os.mkdir(target_root, access_rights)
    except OSError:
        print (f"Creation of project directory {target_root} failed")
    else:
        print (f"Created project directory {target_root}")

    try:
        os.mkdir(log_path, access_rights)
    except OSError:
        print (f"Creation of log directory {log_path} failed")
    else:
        print (f"Created project directory {log_path}")

    try:
        os.mkdir(venv_path, access_rights)
    except OSError:
        print (f"Creation of Python Virtualenv directory {venv_path} failed")
    else:
        print (f"Created Python virtualenv directory {venv_path}")

    try:
        os.mkdir(static_path, access_rights)
    except OSError:
        print (f"Creation of static files directory {static_path} failed")
    else:
        print (f"Created static files directory {static_path}")

    media_path = os.path.join(target_root,media_dir)
    try:
        os.mkdir(media_path, access_rights)
    except OSError:
        print (f"Creation of media files directory {media_path} failed")
    else:
        print (f"Created media files directory {media_path}")


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
            status = os.stat(source_filename).st_mode & 0o777
            if name[-4:] == '-tpl':
                fstring_from_file = 'f"""'+f.read()+'"""'
                # Evaluate F-String
                compiled_fstring = compile(fstring_from_file, source_filename, 'eval')
                formatted_output = eval(compiled_fstring)
                name = name[:-4]
            else:
                fstring_from_file = f.read()
                formatted_output = fstring_from_file
            f.close()
            
            # Write evaluated F-String
            target_filename = os.path.join(target_path, name)
            f = open(target_filename, "w")
            f.write(formatted_output)
            f.close()
            os.chmod(target_filename,status)

    if args.create_uwsgi == True:
        createuwsgi(args,use_secret_key=secret_key)
        
def createuwsgi(args, use_secret_key=None):

    project_name, db_host, db_port, db_name, db_username, \
        db_password, allowed_hosts, static_dir, media_dir, \
        log_dir, log_file, error_log_file, access_log_file, \
        cache_log_file, db_log_file, venv_dir, secret_key, \
        django_version, docs_version, source_root, \
        source_root_length, target_root, access_rights, log_path, \
        venv_path, static_path = \
        process_args(args)
    
    venv = os.path.join(venv_path,project_name)

    if use_secret_key:
        secret_key = use_secret_key
    processes = args.uwsgi_processes
    threads = args.uwsgi_threads
    
    uwsgi_run_dir = args.uwsgi_run_dir
    uwsgi_log_dir = args.uwsgi_log_dir
    http_socket = ''
    for http_socket_host in args.uwsgi_http_sockets:
        http_socket += 'http-socket     = ' + http_socket_host + '\n'

    target_filename = os.path.join(target_root, 'uwsgi.ini')
    f = open(target_filename, "w")
    f.write(
f"""[uwsgi]
home            = {venv}
chdir           = {target_root}
app             = {project_name}
base            = %v
module          = %(app).wsgi:application
socket          = {uwsgi_run_dir}/%(app).uwsgi.sock
fastcgi-socket  = {uwsgi_run_dir}/%(app).fastcgi.sock
wsgi-file       = %(base)/%(app)/wsgi.py

env             = DJANGO_SETTINGS_MODULE={project_name}.settings
env             = DJANGO_SECRET_KEY='{secret_key}'
env             = DJANGO_DEBUG=False
{ 'env             = DB_HOST=' + db_host if db_host else '' }
{ 'env             = DB_PORT=' + db_port if db_port else '' }
{ 'env             = DB_NAME=' + db_name if db_name else '' }
{ 'env             = DB_USERNAME=' + db_username if db_username else '' }
{ "env             = DB_PASSWORD='" + db_password + "'" if db_password else '' }
env             = PYTHONPYCACHEPREFIX=~/.pycache
env             = ALLOWED_HOSTS={ allowed_hosts }
env             = LOG_DIR={ log_dir }
env             = STATIC_DIR={ static_dir }
env             = MEDIA_DIR={ media_dir }
processes       = {processes}
threads         = {threads}
import          = analytics.apps
{http_socket}
#mule            = analytics/management/utilities/log_mule.py
#mule            = mozumder/management/utilities/cache_mule.py
farm            = logger:1
farm            = cache:2
#import          = analytics.apps
#import          = mozumder.apps
stats           = {uwsgi_run_dir}/%(app).stats.sock
logger          = file:{uwsgi_log_dir}/%(app).log
req-logger      = file:{uwsgi_log_dir}/%(app).access
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
