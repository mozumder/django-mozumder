#
# Components are based on Python descriptors.
#
# WARNING: Python descriptors reference Class properties, not Instance
# properties.
#
# An instance of a descriptor must be added to a class as a class attribute,
# not as an instance attribute. Therefore, to store different data for each
# instance, the descriptor needs to maintain a dictionary that maps instances
# to instance-specific values.
#
# A normal Python dictionary stores references to objects it uses as keys.
# Those references by themselves are enough to prevent the object from being
# garbage collected. To prevent class instances from hanging around after we
# are finished with them, we use the WeakKeyDictionary from the weakref
# standard module. Once the last strong reference to the instance passes away,
# the associated key-value pair will be discarded.

class code(object):
    def __init__(self,value=None):
        self.data = value
    def __set__(self,obj,value):
        self.data = value
    def __get__(self,obj,type=None):
        return self.data
    def __delete__(self,obj):
        del self.data
    def __iter__(self,request,context=None):
        yield self.data
    def __str__(self):
        line = ''
        for i in self.__iter__():
            line = line + i
        return line
    def next(self):
        return self.send()
    def send(self,request=None,context=None):
        return self.__iter__(request,context)

class Component(object):

    def __init__(self):
        self.html = code("")
        self.inline_head_css = code("")
        self.inline_head_js = code("")
        self.inline_bodyopen_js = code("")
        self.inline_bodyclose_js = code("")
