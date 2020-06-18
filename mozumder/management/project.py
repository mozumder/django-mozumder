#!/usr/bin/env python
import sys
import os
from os.path import join, getsize

import django
from django.utils.version import get_docs_version
from django.core.management.utils import get_random_secret_key

import mozumder

def create():
    secret_key = get_random_secret_key()
    django_version = django.__version__
    docs_version = get_docs_version()
    project_name = sys.argv[1]

    # Get path by deleting '/__init__.py' from pathname
    source_root = os.path.join(mozumder.__file__[:-12], 'include','project_template')
    source_root_length = len(source_root)

    target_root = os.path.join(os.getcwd(),project_name)
    access_rights = 0o755

    try:
        os.mkdir(target_root, access_rights)
    except OSError:
        print ("Creation of the directory %s failed" % target_root)
    else:
        print ("Created project directory %s " % target_root)

    for root, dirs, files in os.walk(source_root):
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
                print ("Creation of the directory %s failed" % path)
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
