#!/usr/bin/env python
import sys
import os
import subprocess
import site
from shutil import copyfile
import argparse
from urllib.parse import urlparse
#from virtualenv import cli_run
import venv

import django
from django.utils.version import get_docs_version
from django.core.management.utils import get_random_secret_key

import mozumder

def create():
    parser = argparse.ArgumentParser(
        description='Create a new Mozumder project.')
    subparsers = parser.add_subparsers(help='Create new project, or create UWSGI vassals file', dest='subparser_name')
    parser_startproject = subparsers.add_parser('startproject', help='Create a new Mozumder project')
    parser_uwsgi = subparsers.add_parser('createuwsgi', help='Create a UWSGI Vassal .ini file')
    parser_h2o = subparsers.add_parser('createh2o', help='Create h2o config file')

    parser.add_argument(
        'project_name',
        action='store',
        help='Name of project. Project directory will be created with this name.')

    parser_startproject.set_defaults(func=startproject)
    parser_uwsgi.set_defaults(func=createuwsgi)
    parser_h2o.set_defaults(func=createh2o)

    parser_startproject.add_argument(
        '--db_url',
        action='store',
        help='Database connection URL in the format: postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]')
    parser_startproject.add_argument(
        '--db_name',
        action='store',
        default='project_name',
        help='When not using a database URL, name of database to connect to')
    parser_startproject.add_argument(
        '--db_host',
        action='store',
        help='When not using a database URL, hostname or IP address of database server')
    parser_startproject.add_argument(
        '--db_port',
        action='store',
        help='When not using a database URL, port number of database server')
    parser_startproject.add_argument(
        '--db_user_name',
        action='store',
        help='When not using a database URL, username to connect to the database')
    parser_startproject.add_argument(
        '--db_user_password',
        action='store',
        help='When not using a database URL, password of user connecting to the database')
    parser_startproject.add_argument(
        '--allowed_hosts',
        nargs='*',
        action='store',
        default=['127.0.0.1'],
        help='Comma separated lists of hosts that are allowed to accept connections for the site. Default to: 127.0.0.1')
    parser_startproject.add_argument(
        '--log_dir',
        action='store',
        default='log',
        help='Django log directory. Default to: log')
    parser_startproject.add_argument(
        '--static_dir',
        action='store',
        default='static',
        help='Static files directory. Default to: static')
    parser_startproject.add_argument(
        '--media_dir',
        action='store',
        default='media',
        help='Django log directory. Default to: media')
    parser_startproject.add_argument(
        '--static_url',
        action='store',
        default='static',
        help='Static files URL path. Default to: static')
    parser_startproject.add_argument(
        '--media_url',
        action='store',
        default='media',
        help='Media files URL path. Default to: media')
    parser_startproject.add_argument(
        '--admin_url',
        action='store',
        default='admin',
        help='Admin URL path. Default to: admin')
    parser_startproject.add_argument(
        '--virtualenv_dir',
        action='store',
        default='venv',
        help='Python virtualenv directory. Default to: venv')
    parser_startproject.add_argument(
        '--develop_path',
        action='store',
        default='venv',
        help='Use django-mozumder in developer mode by providing path to source tree.')
    parser_startproject.add_argument(
        '--site_name',
        action='store',
        default='Mozumder Website',
        help='Full Name of site. Default: "Mozumder Website"')
    parser_startproject.add_argument(
        '--site_short_name',
        action='store',
        default='Mozumder',
        help='Short Name of site. Default: Mozumder')
    parser_startproject.add_argument(
        '--site_description',
        action='store',
        default='A new website',
        help='Site description. Default: "A new website"')
    parser_startproject.add_argument(
        '--site_lang',
        action='store',
        default='en-US',
        help='Site default language. Default: en-US')
    parser_startproject.add_argument(
        '--site_theme_color',
        action='store',
        default='black',
        help='Site theme color. Default: black')
    parser_startproject.add_argument(
        '--site_background_color',
        action='store',
        default='pink',
        help='Site theme color. Default: pink')
    parser_startproject.add_argument(
        '--hostname',
        action='store',
        help='Full Host name for HTTP server. Example: www.example.com')
    parser_startproject.add_argument(
        '--domainname',
        action='store',
        help='Top-level domain name for this server. This will be permanently redirected to the server hostname. Example: example.com')
    parser_startproject.add_argument(
        '--redirects',
        action='store',
        help='List of additional domains that will be temporarily redirected to this HTTP host. Example: host1.example.com host2.example.com')
    parser_startproject.add_argument(
        '--letsencrypt_dir',
        action='store',
        default='/usr/local/etc/letsencrypt/live',
        help='Letsencrypt live key directory. Default to: /usr/local/etc/letsencrypt/live')
    parser_startproject.add_argument(
        '--h2o_log_dir',
        action='store',
        default='/var/log/h2o',
        help='H2O log directory. Default to: /var/log/uwsgi')
    parser_startproject.add_argument(
        '--uwsgi_http_sockets',
        nargs='*',
        action='store',
        default=['127.0.0.1:8010'],
        help='Comma separated list of additional UWSGI HTTP sockets. Connect to these for debugging purposes without going through the main HTTP reverse proxy web server. Make sure these are only accessible in your debug environment. Default to: 127.0.0.1:8010')
    parser_startproject.add_argument(
        '--uwsgi_processes',
        action='store',
        default=1,
        type=int,
        help='Number of UWSGI processes to run. Default 1.')
    parser_startproject.add_argument(
        '--uwsgi_threads',
        action='store',
        default=8,
        type=int,
        help='Number of threads per UWSGI process to run. Default 8.')
    parser_startproject.add_argument(
        '--uwsgi_run_dir',
        action='store',
        default='/var/run/uwsgi',
        help='UWSGI run directory for temporary run files. Default to: /var/run/uwsgi')
    parser_startproject.add_argument(
        '--uwsgi_log_dir',
        action='store',
        default='/var/log/uwsgi',
        help='UWSGI log directory. Default to: /var/log/uwsgi')
    parser_startproject.add_argument(
        '--create_db',
        action='store_true',
        help='Create Postgres user and database')
    parser_startproject.add_argument(
        '--db_admin_url',
        action='store',
        default='postgresql://postgres@127.0.0.1',
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
    parser_startproject.add_argument(
        '--create_h2o',
        action='store_true',
        default=False,
        help='Create h2o config file.')
    parser_startproject.add_argument(
        '--create_venv',
        action='store_true',
        default=False,
        help='Create Python Virtualenv.')


    parser_uwsgi.add_argument(
        '--db_url',
        action='store',
        help='Database connection URL in the format: postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]')
    parser_uwsgi.add_argument(
        '--db_name',
        action='store',
        default='project_name',
        help='When not using a database URL, name of database to connect to')
    parser_uwsgi.add_argument(
        '--db_host',
        action='store',
        help='When not using a database URL, hostname or IP address of database server')
    parser_uwsgi.add_argument(
        '--db_port',
        action='store',
        help='When not using a database URL, port number of database server')
    parser_uwsgi.add_argument(
        '--db_user_name',
        action='store',
        help='When not using a database URL, username to connect to the database')
    parser_uwsgi.add_argument(
        '--db_user_password',
        action='store',
        help='When not using a database URL, password of user connecting to the database')
    parser_uwsgi.add_argument(
        '--allowed_hosts',
        nargs='*',
        action='store',
        default=['127.0.0.1'],
        help='Comma separated lists of hosts that are allowed to accept connections for the site. Default to: 127.0.0.1')
    parser_uwsgi.add_argument(
        '--log_dir',
        action='store',
        default='log',
        help='Django log directory. Default to: log')
    parser_uwsgi.add_argument(
        '--static_dir',
        action='store',
        default='static',
        help='Static files directory. Default to: static')
    parser_uwsgi.add_argument(
        '--media_dir',
        action='store',
        default='media',
        help='Django log directory. Default to: media')
    parser_uwsgi.add_argument(
        '--static_url',
        action='store',
        default='static',
        help='Static files URL path. Default to: static')
    parser_uwsgi.add_argument(
        '--media_url',
        action='store',
        default='media',
        help='Media files URL path. Default to: media')
    parser_uwsgi.add_argument(
        '--admin_url',
        action='store',
        default='admin',
        help='Admin URL path. Default to: admin')
    parser_uwsgi.add_argument(
        '--virtualenv_dir',
        action='store',
        default='venv',
        help='Python virtualenv directory. Default to: venv')
    parser_uwsgi.add_argument(
        '--develop_path',
        action='store',
        default='venv',
        help='Use django-mozumder in developer mode by providing path to source tree.')
    parser_uwsgi.add_argument(
        '--site_name',
        action='store',
        default='Mozumder Website',
        help='Full Name of site. Default: "Mozumder Website"')
    parser_uwsgi.add_argument(
        '--site_short_name',
        action='store',
        default='Mozumder',
        help='Short Name of site. Default: Mozumder')
    parser_uwsgi.add_argument(
        '--site_description',
        action='store',
        default='A new website',
        help='Site description. Default: "A new website"')
    parser_uwsgi.add_argument(
        '--site_lang',
        action='store',
        default='en-US',
        help='Site default language. Default: en-US')
    parser_uwsgi.add_argument(
        '--site_theme_color',
        action='store',
        default='black',
        help='Site theme color. Default: black')
    parser_uwsgi.add_argument(
        '--site_background_color',
        action='store',
        default='pink',
        help='Site theme color. Default: pink')
    parser_uwsgi.add_argument(
        '--hostname',
        action='store',
        help='Full Host name for HTTP server. Example: www.example.com')
    parser_uwsgi.add_argument(
        '--domainname',
        action='store',
        help='Top-level domain name for this server. This will be permanently redirected to the server hostname. Example: example.com')
    parser_uwsgi.add_argument(
        '--redirects',
        action='store',
        help='List of additional domains that will be temporarily redirected to this HTTP host. Example: host1.example.com host2.example.com')
    parser_uwsgi.add_argument(
        '--letsencrypt_dir',
        action='store',
        default='/usr/local/etc/letsencrypt/live',
        help='Letsencrypt live key directory. Default to: /usr/local/etc/letsencrypt/live')
    parser_uwsgi.add_argument(
        '--h2o_log_dir',
        action='store',
        default='/var/log/h2o',
        help='H2O log directory. Default to: /var/log/uwsgi')
    parser_uwsgi.add_argument(
        '--uwsgi_run_dir',
        action='store',
        default='/var/run/uwsgi',
        help='UWSGI run directory for temporary run files. Default to: /var/run/uwsgi')
    parser_uwsgi.add_argument(
        '--uwsgi_log_dir',
        action='store',
        default='/var/log/uwsgi',
        help='UWSGI log directory. Default to: /var/log/uwsgi')
    parser_uwsgi.add_argument(
        '--uwsgi_http_sockets',
        nargs='*',
        action='store',
        default=['127.0.0.1:8010'],
        help='Comma separated list of additional UWSGI HTTP sockets. Connect to these for debugging purposes without going through the main HTTP reverse proxy web server. Make sure these are only accessible in your debug environment. Default to: 127.0.0.1:8010')
    parser_uwsgi.add_argument(
        '--uwsgi_processes',
        action='store',
        default=1,
        type=int,
        help='Number of UWSGI processes to run. Default 1.')
    parser_uwsgi.add_argument(
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
    static_url = args.static_url
    media_url = args.media_url
    admin_url = args.admin_url
    log_dir = args.log_dir
    log_file = os.path.join(log_dir, f'{project_name}.log')
    error_log_file = os.path.join(log_dir, f'{project_name}.error.log')
    access_log_file = os.path.join(log_dir, f'{project_name}.access.log')
    cache_log_file = os.path.join(log_dir, f'{project_name}.cache.log')
    db_log_file = os.path.join(log_dir, f'{project_name}.db.log')

    # Get path by deleting '/__init__.py' from pathname
    source_root = os.path.join(mozumder.__file__[:-12], 'include','project_template')
    source_root_length = len(source_root)

    target_root = os.path.join(os.getcwd(),project_name)
    access_rights = 0o755
    log_path = os.path.join(target_root,log_dir)
    static_path = os.path.join(target_root,static_dir)
    media_path = os.path.join(target_root,media_dir)
    
    venv_name = args.virtualenv_dir + f'.{project_name}'
    venv_path = os.path.join(target_root,venv_name)
    venv_bin = os.path.join(venv_path, 'bin')
    python_bin = os.path.join(venv_path, 'bin', 'python')
    develop_path = args.develop_path.replace(' ', '\ ')

    uwsgi_run_dir = args.uwsgi_run_dir
    uwsgi_log_dir = args.uwsgi_log_dir
    
    site_name = args.site_name
    site_short_name = args.site_short_name
    site_description = args.site_description
    site_lang = args.site_lang
    site_theme_color = args.site_theme_color
    site_background_color = args.site_background_color

    return project_name, db_host, db_port, db_name, db_username, db_password, \
        allowed_hosts, static_dir, media_dir, static_url, media_url, \
        admin_url, log_dir, log_file, error_log_file, access_log_file, \
        cache_log_file, db_log_file, secret_key, django_version, docs_version, \
        source_root, source_root_length, target_root, access_rights, log_path, \
        static_path, media_path, venv_name, venv_path, venv_bin, \
        python_bin, develop_path, uwsgi_run_dir, uwsgi_log_dir, site_name, \
        site_short_name, site_description, site_lang, site_theme_color, \
        site_background_color

def startproject(args):

    project_name, db_host, db_port, db_name, db_username, db_password, \
        allowed_hosts, static_dir, media_dir, static_url, media_url, \
        admin_url, log_dir, log_file, error_log_file, access_log_file, \
        cache_log_file, db_log_file, secret_key, django_version, docs_version, \
        source_root, source_root_length, target_root, access_rights, log_path, \
        static_path, media_path, venv_name, venv_path, venv_bin, \
        python_bin, develop_path, uwsgi_run_dir, uwsgi_log_dir, site_name, \
        site_short_name, site_description, site_lang, site_theme_color, \
        site_background_color = process_args(args)

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
        os.chdir(target_root)

    try:
        os.mkdir(log_path, access_rights)
    except OSError:
        print (f"Creation of log directory {log_path} failed")
    else:
        print (f"Created project directory {log_path}")

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
        sub_dir = root[source_root_length+1:].replace('project_name',project_name)
        target_path = os.path.join(target_root, sub_dir)
        for name in dirs:
            if name == 'project_name':
                name = project_name
            path = os.path.join(target_path, name)
            try:
                os.mkdir(path,mode=0o755)
            except OSError:
                print (f"Creation of the directory {path} failed")
            else:
                print (f"Created directory {path}")
        for name in files:
            source_filename = os.path.join(root, name)
            if name[-4:] == '-tpl':
                f = open(source_filename, "r")
                fstring_from_file = 'f"""'+f.read()+'"""'
                f.close()
                # Evaluate F-String
                compiled_fstring = compile(fstring_from_file, source_filename, 'eval')
                formatted_output = eval(compiled_fstring)
                name = name[:-4]
                target_filename = os.path.join(target_path, name)
                # Write evaluated F-String
                f = open(target_filename, "w")
                f.write(formatted_output)
                f.close()
                status = os.stat(source_filename).st_mode & 0o777
                os.chmod(target_filename,status)
            else:
                target_filename = os.path.join(target_path, name)
                copyfile(source_filename, target_filename)

    if args.create_venv == True:
        
        # Create new Python virtual environment with venv
        venv_builder = venv.EnvBuilder(with_pip=True)
        try:
            venv_builder.create(venv_path)
        except OSError:
            print (f"Creation of Python Virtualenv {venv_name} failed")
        else:
            print (f"Created Python virtualenv {venv_name}")

        # Activate new virtual environment in this script
        # prepend bin to PATH (this file is inside the bin directory)
        os.environ["PATH"] = os.pathsep.join([venv_bin] + os.environ.get("PATH", "").split(os.pathsep))
        os.environ["VIRTUAL_ENV"] = venv_path  # virtual env is right above bin directory

        # add the virtual environments libraries to the host python import mechanism
        prev_length = len(sys.path)
        for lib in f"{venv_path}/lib/python3.8/site-packages".split(os.pathsep):
            path = os.path.realpath(os.path.join(venv_bin, lib))
            site.addsitedir(path.decode("utf-8") if "" else path)
        sys.path[:] = sys.path[prev_length:] + sys.path[0:prev_length]

        sys.real_prefix = sys.prefix
        sys.prefix = venv_path

        # Install Python requirements with pip
        subprocess.check_call([python_bin, "-m", "pip", "install", "-r", "requirements.txt"])

        # Install django-mozumder into environment in develop mode if needed
        if develop_path:
            print('Installing django-mozumder into development path')
            os.system(f'source {venv_bin}/activate;cd {develop_path};{python_bin} {develop_path}/setup.py develop')
       
#        import pip._internal.main
#        pip._internal.main.main(['install', '--isolated', '-r', 'requirements.txt'])

    if args.create_uwsgi == True:
        createuwsgi(args,use_secret_key=secret_key)

    if args.create_h2o == True:
        createh2o(args)
        
    if args.create_db == True:
        psql_base_command = f'PGPASSWORD={db_admin_password} psql -X --echo-all '
        psql_command = f"CREATE ROLE {db_username} WITH LOGIN PASSWORD '{db_password}';"
        command = f'{psql_base_command} -U {db_admin_username} -c "{psql_command}"'
        os.system(command)
        createdb_command = f'PGPASSWORD={db_admin_password} createdb --echo -U {db_admin_username} -O {db_username} {db_name}'
        os.system(createdb_command)
        psql_command = f"CREATE EXTENSION pgcrypto;"
        command = f'{psql_base_command} -U {db_admin_username} {db_name} -c "{psql_command}"'
        os.system(command)
        print('Migrating')
        subprocess.run(['manage.py', 'migrate'])

    print('Collecting Static Files')
    subprocess.run(['manage.py', 'collectstatic', '--noinput'])

def createuwsgi(args, use_secret_key=None):

    project_name, db_host, db_port, db_name, db_username, db_password, \
        allowed_hosts, static_dir, media_dir, static_url, media_url, \
        admin_url, log_dir, log_file, error_log_file, access_log_file, \
        cache_log_file, db_log_file, secret_key, django_version, docs_version, \
        source_root, source_root_length, target_root, access_rights, log_path, \
        static_path, media_path, venv_name, venv_path, venv_bin, \
        python_bin, develop_path, uwsgi_run_dir, uwsgi_log_dir, site_name, \
        site_short_name, site_description, site_lang, site_theme_color, \
        site_background_color = process_args(args)
    
    venv = os.path.join(venv_path,project_name)

    if use_secret_key:
        secret_key = use_secret_key
    processes = args.uwsgi_processes
    threads = args.uwsgi_threads
    
    http_socket = ''
    for http_socket_host in args.uwsgi_http_sockets:
        http_socket += 'http-socket     = ' + http_socket_host + '\n'

    target_filename = os.path.join(target_root, 'uwsgi.ini')
    f = open(target_filename, 'w')
    f.write(
f"""[uwsgi]
home            = {venv_path}
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

def createh2o(args):

    project_name, db_host, db_port, db_name, db_username, db_password, \
        allowed_hosts, static_dir, media_dir, static_url, media_url, \
        admin_url, log_dir, log_file, error_log_file, access_log_file, \
        cache_log_file, db_log_file, secret_key, django_version, docs_version, \
        source_root, source_root_length, target_root, access_rights, log_path, \
        static_path, media_path, venv_name, venv_path, venv_bin, \
        python_bin, develop_path, uwsgi_run_dir, uwsgi_log_dir, site_name, \
        site_short_name, site_description, site_lang, site_theme_color, \
        site_background_color = process_args(args)
        

    domainname = args.domainname
    hostname = args.hostname
    redirects = args.redirects
    letsencrypt_dir = args.letsencrypt_dir
    h2o_log_dir = args.h2o_log_dir
    h2o_access_log = os.path.join(h2o_log_dir,project_name + '.log')
    well_known_dir = os.path.join(target_root,'.well-known')
    uwsgi_fcgi_socket = os.path.join(uwsgi_run_dir,project_name + '.fastcgi.sock')

    robots_txt_file = os.path.join(static_path,'robots.txt')
    manifest_json_file = os.path.join(static_path,'manifest.json')
    browserconfig_xml_file = os.path.join(static_path,'browserconfig.xml')
    icon_path = os.path.join(static_path,'icon')
    favicon_ico_file = os.path.join(icon_path,'icon-16.png')
    android_icon_192x192_png_file = os.path.join(icon_path,'icon-192.png')
    apple_icon_180x180_png_file = os.path.join(icon_path,'icon-180.png')
    favicon_16x16_png_file = os.path.join(icon_path,'icon-16.png')
    favicon_32x32_png_file = os.path.join(icon_path,'icon-32.png')
    favicon_96x96_png_file = os.path.join(icon_path,'icon-96.png')

    if domainname == None:
        raise Exception('Need a domain name when creating H2O config file. Please set --domainname')
    if hostname == None:
        raise Exception('Need a host name when creating H2O config file. Please set --hostname')

    first_temp_redirect = ''
    additional_temp_redirects = ''
    domain_redirect = ''
    if redirects:
        first = True
        for redirect in redirects:
            if first:
                first = False
                # first item
                first_temp_redirect = f""""{redirect}:80": &temp_redirect
  <<: *default_redirect
  paths: &temp_paths
    "/":
      redirect:
        status: 302
        url:    "https://{hostname}/\""""
            else:
                # other items
                additional_temp_redirects += f'"{redirect}:80": *temp_redirect\n'
    if domainname != None:
        domain_redirect = f'"{domainname}:80": *default_redirect'

    cipher = """minimum-version: TLSv1.2
cipher-suite: ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256
cipher-preference: server"""
    certificate_file = os.path.join(letsencrypt_dir, domainname, "fullchain.pem")
    key_file = os.path.join(letsencrypt_dir, domainname, "privkey.pem")

    first_temp_ssl_redirect = ''
    additional_temp_ssl_redirects = ''
    domain_ssl_redirect = ''
    if redirects:
        first = True
        for redirect in redirects:
            if first:
                first = False
                # first item
                first_temp_ssl_redirect = f""""{redirect}:443": &temp_ssl_redirect
  <<: *ssl_redirect
  paths: &temp_paths
    "/":
      redirect:
        status: 302
        url:    "https://{hostname}/\""""
            else:
                # other items
                additional_temp_ssl_redirects += f'"{redirect}:443": *temp_redirect\n'
    if domainname != None:
        domain_ssl_redirect = f'"{domainname}:80": *default_redirect'

    target_filename = os.path.join(target_root, 'h2o.conf')
    f = open(target_filename, "w")
    f.write(f"""{hostname}:80": &default_redirect
  listen:
    port: 80
  paths: &default_paths
    "/":
      redirect:
        status: 301
        url:    "https://{hostname}/"
    "/.well-known": &well_known
      file.dir: {well_known_dir}
{first_temp_redirect}
{additional_temp_redirects}
{domain_redirect}

"{domainname}:443": &ssl_redirect
  <<: *default_redirect
  listen: &default_ssl
    port: 443
    ssl:
      {cipher}
      certificate-file: {certificate_file}
      key-file:         {key_file}
{first_temp_ssl_redirect}
{additional_temp_ssl_redirects}
"{hostname}:443":
  access-log:
    path: {h2o_access_log}
    format: "%{{%Y-%m-%d %H:%M:%S}}t.%{{msec_frac}}t %h:%{{remote}}p %H %{{Referer}}i %m %U%q %s %bb %{{duration}}xs (%{{connect-time}}xs, %{{request-total-time}}xs, %{{process-time}}xs, %{{response-time}}xs) \"%{{user-agent}}i\""
  listen: *default_ssl
  paths:
    <<: *default_paths
    "/": &{project_name}_socket
      fastcgi.connect:
        port: {uwsgi_fcgi_socket}
        type: unix
    "/{static_url}":
      file.dir: {static_path}
      expires: 30 day
      file.send-compressed: ON
    "/{media_url}":
      file.dir: {media_path}
      expires: 30 day
    "/{admin_url}": *{project_name}_socket
    /robots.txt: &default_file
      file.file: {robots_txt_file}
      file.send-compressed: ON
      expires: 30 day
    /manifest.json:
      <<: *default_file
      file.file: {manifest_json_file}
    /browserconfig.xml:
      <<: *default_file
      file.file: {browserconfig_xml_file}
    /favicon.ico:
      <<: *default_file
      file.file: {favicon_ico_file}
    /android-icon-192x192.png:
      <<: *default_file
      file.file: {android_icon_192x192_png_file}
    /apple-icon-180x180.png:
      <<: *default_file
      file.file: {apple_icon_180x180_png_file}
    /favicon-16x16.png:
      <<: *default_file
      file.file: {favicon_16x16_png_file}
    /favicon-32x32.png:
      <<: *default_file
      file.file: {favicon_32x32_png_file}
    /favicon-96x96.png:
      <<: *default_file
      file.file: {favicon_96x96_png_file}
""")
    f.close()
