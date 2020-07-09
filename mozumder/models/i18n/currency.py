from django.db import models

# Create your models here.
class Currency(models.Model):
    iso_4217 = models.CharField(max_length=3, unique=True)
    symbol = models.CharField(max_length=4)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return self.iso_4217

class CurrencyLang(models.Model):
    namedlang = models.ForeignKey('Currency', related_name='namedcurrency', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    lang = models.ForeignKey('Lang', related_name='langs', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'namedcurrency',
                    'lang',
                    ],
                name='currencylang_uniquetogether'
            )
        ]
