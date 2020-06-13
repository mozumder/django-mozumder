from django.db import models

class MaterializedForeignKey(models.ForeignKey):
    def __init__(
        self, to, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(to, *args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs
        
class IntegerMaterializedField(models.IntegerField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class PositiveSmallIntegerMaterializedField(models.PositiveSmallIntegerField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class BooleanMaterializedField(models.BooleanField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class DirtyBitField(models.BooleanField):
    def __init__(self, *args, **kwargs):
        self.dirty_bit = True
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

class ActiveBitField(BooleanMaterializedField):
    def __init__(self, active_conditions=None, *args, **kwargs):
        self.active_bit = True
        self.active_conditions = active_conditions
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.active_conditions != None:
            kwargs['active_conditions'] = self.active_conditions
        return name, path, args, kwargs

class CharMaterializedField(models.CharField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class TextMaterializedField(models.TextField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class DateMaterializedField(models.DateField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class DateTimeMaterializedField(models.DateTimeField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class StartTimeField(DateTimeMaterializedField):
    def __init__(self, start_conditions=None, *args, **kwargs):
        self.start_time = True
        self.start_conditions = start_conditions
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.start_conditions != None:
            kwargs['start_conditions'] = self.start_conditions
        return name, path, args, kwargs

class StopTimeField(DateTimeMaterializedField):
    def __init__(self, stop_conditions=None, *args, **kwargs):
        self.stop_time = True
        self.stop_conditions = stop_conditions
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.stop_conditions != None:
            kwargs['stop_conditions'] = self.stop_conditions
        return name, path, args, kwargs

class URLMaterializedField(models.URLField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

class SlugMaterializedField(models.SlugField):
    def __init__(
        self, source=None, *args, **kwargs
    ):
        self.source = source
        super().__init__(*args, **kwargs)
    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.source != None:
            kwargs['source'] = self.source
        return name, path, args, kwargs

