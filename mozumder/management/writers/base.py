import os
from dotmap import DotMap

class Writer:
    """Need to set self.extension and get_source when subclassing
    """
    sub_directory = ''
    filename = ''
    extension = ''
    
    def __init__(self, sub_directory=None, filename=None, extension=None):
        if sub_directory is not None:
            self.sub_directory = sub_directory
        if filename is not None:
            self.filename = filename
        if extension is not None:
            self.extension = extension
    def get_filename(self, context):
        # Subclass as needed. This function defines the file name.
        return f"{self.filename}{self.extension}"
    def get_filepath(self, context):
        # Subclass as needed. This function defines the file path.
        return os.path.join(os.getcwd(),context['app'].name,self.sub_directory)
    def get_file(self, context):
        # Subclass as needed. This function defines the full file.
        return os.path.join(self.get_filepath(context),self.get_filename(context))

    def write(self, context):
        file = self.get_file(context)
        print(f'Writing file: {file}')
        f = open(file, "w")
        f.write(self.generate(DotMap(context)))
        f.close()
