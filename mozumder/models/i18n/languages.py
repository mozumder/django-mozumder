from django.db import models
from datetime import date

# Create your models here.

LANGUAGE_SCOPE_CHOICES = (
('I', 'Individual'),
('M', 'Macrolanguage'),
('S', 'Special'),
)
LANGUAGE_TYPE_CHOICES = (
('A', 'Ancient'),
('C', 'Constructed'),
('E', 'Exctinct'),
('H', 'Historical'),
('L', 'Living'),
('S', 'Special'),
)

class Language(models.Model):
    """
    A language designator is a code that represents a language.
    Use the two-letter ISO 639-1 standard (preferred) or the three-letter ISO 639-2 standard.
    If an ISO 639-1 code is not available for a particular language, use the ISO 639-2 code instead.
    For example, there is no ISO 639-1 code for the Hawaiian language, so use the ISO 639-2 code.
    """
    iso_639_3 = models.CharField(max_length=3, unique=True)
    iso_639_1 = models.CharField(max_length=2, unique=True, null=True, blank=True)
    iso_639_2b = models.CharField(max_length=3, unique=True, null=True, blank=True)
    iso_639_2t = models.CharField(max_length=3, unique=True, null=True, blank=True)
    scope = models.CharField(choices=LANGUAGE_SCOPE_CHOICES, default='I', max_length=1)
    type = models.CharField(choices=LANGUAGE_TYPE_CHOICES, default='L', max_length=1)

    def __str__(self):
        if self.iso_639_1:
            return self.iso_639_1
        elif self.iso_639_2b:
            return self.iso_639_2b
        elif self.iso_639_2t:
            return self.iso_639_2t
        else:
            return self.iso_639_3

    class Meta:
        ordering = ['iso_639_3']

class LanguageLang(models.Model):
    language = models.ForeignKey('Language', related_name='lang_codes', on_delete=models.CASCADE)
    print_name = models.CharField(max_length=150)
    inverted_name = models.CharField(max_length=150)
    ref_name = models.BooleanField(default=False)
    comment = models.CharField(max_length=150, null=True, blank=True)
    lang = models.ForeignKey('Lang', related_name='name_langs', on_delete=models.CASCADE)

    def __str__(self):
        return self.print_name

    class Meta:
        ordering = ['print_name']
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'language',
                    'lang',
                    'print_name'
                    ],
                name='languagelang_uniquetogether'
            )
        ]

MACROLANGUAGE_STATUS_CHOICES = (
('A', 'Active'),
('R', 'Retired'),
)

class MacroLanguageMapping(models.Model):
    # The identifier for a macrolanguage
    macrolanguage = models.ForeignKey('Language', related_name='macrolangs', on_delete=models.CASCADE)
    # The identifier for an individual language that is a member of the macrolanguage
    individual_language = models.ForeignKey('Language', related_name='individuallangs', on_delete=models.CASCADE, null=True, blank=True)
    retired_individual_language = models.ForeignKey('RetiredLanguage', related_name='macrolanguages', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(choices=MACROLANGUAGE_STATUS_CHOICES, default='A', max_length=1)

    def __str__(self):
        return self.macrolanguage.__str__() + "_" + self.individual_language.__str__()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = [
                    'macrolanguage',
                    'individual_language',
                    ],
                name='individualmacrolanguage_uniquetogether'
            ),
            models.UniqueConstraint(
                fields = [
                    'macrolanguage',
                    'retired_individual_language',
                    ],
                name='retiredindividualmacrolanguage_uniquetogether'
            ),
        ]


RETIREMENT_REASON_CHOICES = (
('C', 'Change'),
('D', 'Duplicate'),
('N', 'Nonexistent'),
('S', 'Split'),
('M', 'Merge'),
)

class RetiredLanguage(models.Model):
    iso_639_3 = models.CharField(max_length=3, unique=True)
    ref_name = models.CharField(max_length=150)
    reason = models.CharField(choices=RETIREMENT_REASON_CHOICES, default='C', max_length=1)
    # In the cases of C, D, and M, the identifier
    # to which all instances of this Id should be changed
    change_to = models.CharField(max_length=3, null=True, blank=True)
    # change_to = models.ForeignKey('Language', related_name='retirement_changes', on_delete=models.CASCADE, null=True, blank=True)
    # The instructions for updating an instance
    # of the retired (split) identifier
    ret_remedy = models.CharField(max_length=300, null=True, blank=True)
    effective_date = models.DateField(default=date.today)

    def __str__(self):
        return self.iso_639_3

    class Meta:
        ordering = ['iso_639_3']
