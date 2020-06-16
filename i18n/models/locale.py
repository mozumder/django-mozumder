from django.db import models
from datetime import date

# Create your models here.

class Lang(models.Model):
    """
    A language ID identifies a language used in many regions, a dialect used in a specific region,
    or a script used in multiple regions.
    To specify a language used in many regions, use a language designator by itself.
    To specify a specific dialect, use a hyphen to combine a language designator
    with a region designator.
    To specify a script, combine a language designator with a script designator.
    """
    language = models.ForeignKey('Language', related_name='langs', on_delete=models.CASCADE)
    script = models.ForeignKey('Script', related_name='langs', on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey('Country', related_name='langs', on_delete=models.CASCADE, null=True, blank=True)
    variant = models.CharField(max_length=30, null=True, blank=True)
    extension = models.CharField(max_length=30, null=True, blank=True)
    private_use = models.CharField(max_length=30, null=True, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        if self.script:
            return self.language.__str__() + "-" + self.script.__str__()
        elif self.country:
            return self.language.__str__() + "-" + self.country.__str__()
        else:
            return self.language.__str__()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'language',
                    'script',
                    'country',
                    'variant',
                    'extension',
                    'private_use',
                    ],
                name='lang_uniquetogether'
            )
        ]


class LangLang(models.Model):
    namedlang = models.ForeignKey('Lang', related_name='namedlangs', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    lang = models.ForeignKey('Lang', related_name='langs', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'namedlang',
                    'lang',
                    ],
                name='langlang_uniquetogether'
            )
        ]

class Locale(models.Model):
    """
    ISO 15897

    A locale ID identifies a specific region and its cultural conventions —
    such as the formatting of dates, times, and numbers.
    To specify a locale, use an underscore character to combine a language ID
    with a region designator
    """
    language = models.ForeignKey('Language', related_name='locales', on_delete=models.CASCADE)
    script = models.ForeignKey('Script', related_name='locales', on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey('Country', related_name='locales', on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.script:
            if self.country:
                return self.language.__str__() + "-" + self.script.__str__() + "_" + self.country.__str__()
            else:
                return self.language.__str__() + "_" + self.script.__str__()
        else:
            if self.country:
                return self.language.__str__() + "_" + self.country.__str__()
            else:
                return self.language.__str__()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'language',
                    'script',
                    'country',
                    ],
                name='locale_uniquetogether'
            )
        ]

class LocaleLang(models.Model):
    locale = models.ForeignKey('Locale', related_name='names', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    lang = models.ForeignKey('Lang', related_name='locale_langs', on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'locale',
                    'lang',
                    ],
                name='localelang_uniquetogether'
            )
        ]

    def __str__(self):
        return self.name

