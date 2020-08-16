import os
import mozumder
from ...models.development import *
from .models import *
from .templates import *
from .views import *
from .urls import *
from .admin import *
from ..utilities.name_case import *
from shutil import copyfile
        
def write_app(app_obj):
        app_name = app_obj.name
        access_rights = 0o755
        source_root = os.path.join(mozumder.__file__[:-12], 'include','app_template')
        source_root_length = len(source_root)

        target_root = os.path.join(os.getcwd(),app_name)
        try:
            os.mkdir(target_root, access_rights)
        except OSError:
            print (f"Creation of app directory {target_root} failed")
        else:
            print (f"Created app directory {target_root}")

        for root, dirs, files in os.walk(source_root):
            # Process files from source templates directory and install
            # them in the new app directory
            sub_dir = root[source_root_length+1:].replace('app_name',app_name)
            target_path = os.path.join(target_root, sub_dir)
            for name in dirs:
                if name == 'app_name':
                    name = app_name
                path = os.path.join(target_path, name)
                try:
                    os.mkdir(path,mode=0o755)
                except OSError:
                    print (f"Creation of the directory {path} failed")
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

        
        # Write models.py, templates, and views.py
        context = {}
        context['app'] = app_obj

        template_dir = os.path.join(os.getcwd(),app_name,'templates',app_name)
        try:
            os.mkdir(template_dir, access_rights)
        except OSError:
            print (f"Creation of template directory {template_dir} failed")
        else:
            print (f"Created template directory {template_dir}")

        models_imports = ''
        views_imports = ''
        admin_imports = ''
        model_objs = TrackedModel.objects.filter(owner=app_obj, abstract=True)
        if model_objs:
            context['models'] = model_objs
            MetaModelsWriter().write(context)
            models_imports += f"from .meta import *\n"

        model_objs = TrackedModel.objects.filter(owner=app_obj, abstract=False)
        for model_obj in model_objs:
            context['model'] = model_obj
            context['model_code_name'] = CamelCase_to_snake_case(model_obj.name)

            # Write models.py as part of module
            ModelWriter().write(context)
            models_imports += f"from .{context['model_code_name']} import {model_obj.name}\n"

            # Write views.py as part of module
            ViewWriter().write(context)
            view_objs = TrackedView.objects.filter(model=model_obj)
            views_imports_list = ', '.join([str(view_obj.name) for view_obj in view_objs])
            views_imports += f"from .{context['model_code_name']} import {views_imports_list}\n"

            # Write URLs for views
            URLsWriter().update(context)
            APIURLsWriter().update(context)
            
            # Write Admin
            AdminWriter().write(context)
            admin_imports += f"from .{context['model_code_name']} import {model_obj.name}Admin\n"

            # Write Django templates
            ModelListBlock().write(context)
            ModelListPage().write(context)
            ModelDetailBlock().write(context)
            ModelDetailPage().write(context)
            UpdateModelsListBlock().write(context)
            CreateFormBlock().write(context)
            CreateFormPage().write(context)
            UpdateFormBlock().write(context)
            UpdateFormPage().write(context)
            CopyFormBlock().write(context)
            CopyFormPage().write(context)
            DeleteFormBlock().write(context)
            DeleteFormPage().write(context)

        # Write apps models
        ModelsBlock().write(context)

        # Write models/__init__.py for python module
        model_package_file = os.path.join(target_root,'models','__init__.py')
        f = open(model_package_file, "w")
        f.write(models_imports)
        f.close()

        # Write views/__init__.py for python module
        views_package_file = os.path.join(target_root,'views','__init__.py')
        f = open(views_package_file, "w")
        f.write(views_imports)
        f.close()

        # Write admin/__init__.py for python module
        admin_package_file = os.path.join(target_root,'admin','__init__.py')
        f = open(admin_package_file, "w")
        f.write(admin_imports)
        f.close()

