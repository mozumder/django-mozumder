from django.db import models
from datetime import date

# Create your models here.

class Country(models.Model):
    """
    A region designator is a code that represents a country.
    Use the ISO 3166-1 standard, a two-letter, capitalized code
    """
    alpha_2 = models.CharField(max_length=2,unique=True)
    alpha_3 = models.CharField(max_length=3,unique=True)
    numeric = models.CharField(max_length=3,unique=True)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.alpha_2

class CountryLang(models.Model):
    country = models.ForeignKey('Country', related_name='country_names', on_delete=models.CASCADE)
    name = models.CharField(max_length=510)
    official_name = models.CharField(max_length=500, null=True, blank=True)
    common_name = models.CharField(max_length=140, null=True, blank=True)
    UN_formal_name = models.CharField(max_length=160, null=True, blank=True)
    UN_short_name = models.CharField(max_length=150, null=True, blank=True)
    lang = models.ForeignKey('Lang', related_name='country_langs', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Country Lang'
        verbose_name_plural = 'Countries Lang'
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'country',
                    'lang',
                    ],
                name='countrylang_unique'
            )
        ]

    def __str__(self):
        return self.name

class SubdivisionType(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.id)

class SubdivisionTypeLang(models.Model):
    type = models.ForeignKey('SubdivisionType', related_name='subdivision_types', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=True, blank=True)
    lang = models.ForeignKey('Lang', related_name='subdivision_type_langs', on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'type',
                    'lang',
                    ],
                name='subdivisiontypelang_unique'
            )
        ]

    def __str__(self):
        return self.name

class Subdivision(models.Model):
    """
    Use the ISO 3166-2 standard, a two-letter, capitalized code
    """
    code = models.CharField(max_length=3)
    country = models.ForeignKey('Country', related_name='country_subdivisions', on_delete=models.CASCADE)
    parent = models.ForeignKey('Subdivision', related_name='subdivisions', on_delete=models.SET_NULL, null=True, blank=True)
    type = models.ForeignKey('SubdivisionType', related_name='subdivisions', on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'code',
                    'country',
                    ],
                name='subdivision_unique'
            )
        ]

    def __str__(self):
        return self.country.alpha_2 + '-' + self.code


class SubdivisionLang(models.Model):
    subdivision = models.ForeignKey('Subdivision', related_name='subdivision_names', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=True, blank=True)
    lang = models.ForeignKey('Lang', related_name='subdivision_langs', on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'subdivision',
                    'lang',
                    ],
                name='subdivisionlang_unique'
            )
        ]

    def __str__(self):
        return self.name


