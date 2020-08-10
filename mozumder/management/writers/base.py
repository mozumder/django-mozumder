import os
from dotmap import DotMap

# The following are the operations that are built by default for
# every model:
#
# Read One Item
# Read All
# Read Filter/Exclude
# Read Stubs List
# Search Items
# Sort Items
# Reorder Items
# Add One Item
# Insert One Item
# Add Multiple Items
# Duplicate Item
# Update Item
# Update All
# Update Filter/Exclude
# Validate Item
# Delete Item
# Delete All
# Delete Filter/Exclude
# Search Through Field
# Add Item to Field
# Add Multiple Items to Field
# Increment Field
# Decrement Field
# Validate Field
# Duplicate Items to Field
# Delete Item from Field
# Delete All Items from Field
# Delete Multiple Items from Field
# Operation on View
#
# Enable operations you need by uncommenting out the operation in
# the urls.py file

class Writer:
    """Need to set self.extension and get_source when subclassing
    """
    sub_directory = ''
    extension = ''
    
    def __init__(self, sub_directory=None,extension=None):
        if sub_directory is not None:
            self.sub_directory = sub_directory
        if extension is not None:
            self.extension = extension
    def get_filename(self, context):
        # Subclass this as needed. This function defines the file name.
        return f"{context['model_code_name']}{self.extension}"
    def get_filepath(self, context):
        # Subclass this as needed. This function defines the file path.
        return os.path.join(os.getcwd(),context['app'].name,self.sub_directory)
    def get_file(self, context):
        # Subclass this as needed. This function generates the full file.
        return os.path.join(self.get_filepath(context),self.get_filename(context))

    def write(self, context):
        file = self.get_file(context)
        print(f'Writing file: {file}')
        f = open(file, "w")
        f.write(self.generate(DotMap(context)))
        f.close()
