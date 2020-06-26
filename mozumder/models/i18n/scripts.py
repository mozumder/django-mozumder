from django.db import models
from datetime import date

# Create your models here.

class Script(models.Model):
    """
    For the script designator, use the ISO 15924 standard, four letters with the first letter
    uppercase and the last three lowercase.
    """
    iso_15294 = models.CharField(max_length=4,unique=True)
    code_number = models.CharField(max_length=3,unique=True)
    unicode_alias = models.CharField(max_length=75)
    unicode_version = models.CharField(max_length=4)
    version_date = models.DateField(default=date.today)

    def __str__(self):
        return self.iso_15294

class ScriptLang(models.Model):
    script = models.ForeignKey('Script', related_name='names', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    lang = models.ForeignKey('Lang', related_name='script_langs', on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'script',
                    'lang',
                    ],
                name='scriptlang_uniquetogether'
            )
        ]

    def __str__(self):
        return self.name
