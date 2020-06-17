# Generated by Django 3.0.7 on 2020-06-17 01:12

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alpha_2', models.CharField(max_length=2, unique=True)),
                ('alpha_3', models.CharField(max_length=3, unique=True)),
                ('numeric', models.CharField(max_length=3, unique=True)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Lang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variant', models.CharField(blank=True, max_length=30, null=True)),
                ('extension', models.CharField(blank=True, max_length=30, null=True)),
                ('private_use', models.CharField(blank=True, max_length=30, null=True)),
                ('active', models.BooleanField(default=False)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='langs', to='i18n.Country')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iso_639_3', models.CharField(max_length=3, unique=True)),
                ('iso_639_1', models.CharField(blank=True, max_length=2, null=True, unique=True)),
                ('iso_639_2b', models.CharField(blank=True, max_length=3, null=True, unique=True)),
                ('iso_639_2t', models.CharField(blank=True, max_length=3, null=True, unique=True)),
                ('scope', models.CharField(choices=[('I', 'Individual'), ('M', 'Macrolanguage'), ('S', 'Special')], default='I', max_length=1)),
                ('type', models.CharField(choices=[('A', 'Ancient'), ('C', 'Constructed'), ('E', 'Exctinct'), ('H', 'Historical'), ('L', 'Living'), ('S', 'Special')], default='L', max_length=1)),
            ],
            options={
                'ordering': ['iso_639_3'],
            },
        ),
        migrations.CreateModel(
            name='Locale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='i18n.Country')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='i18n.Language')),
            ],
        ),
        migrations.CreateModel(
            name='RetiredLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iso_639_3', models.CharField(max_length=3, unique=True)),
                ('ref_name', models.CharField(max_length=150)),
                ('reason', models.CharField(choices=[('C', 'Change'), ('D', 'Duplicate'), ('N', 'Nonexistent'), ('S', 'Split'), ('M', 'Merge')], default='C', max_length=1)),
                ('change_to', models.CharField(blank=True, max_length=3, null=True)),
                ('ret_remedy', models.CharField(blank=True, max_length=300, null=True)),
                ('effective_date', models.DateField(default=datetime.date.today)),
            ],
            options={
                'ordering': ['iso_639_3'],
            },
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iso_15294', models.CharField(max_length=4, unique=True)),
                ('code_number', models.CharField(max_length=3, unique=True)),
                ('unicode_alias', models.CharField(max_length=75)),
                ('unicode_version', models.CharField(max_length=4)),
                ('version_date', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='Subdivision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_subdivisions', to='i18n.Country')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subdivisions', to='i18n.Subdivision')),
            ],
        ),
        migrations.CreateModel(
            name='SubdivisionType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='SubdivisionTypeLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdivision_type_langs', to='i18n.Lang')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdivision_types', to='i18n.SubdivisionType')),
            ],
        ),
        migrations.CreateModel(
            name='SubdivisionLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdivision_langs', to='i18n.Lang')),
                ('subdivision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdivision_names', to='i18n.Subdivision')),
            ],
        ),
        migrations.AddField(
            model_name='subdivision',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdivisions', to='i18n.SubdivisionType'),
        ),
        migrations.CreateModel(
            name='ScriptLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='script_langs', to='i18n.Lang')),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='names', to='i18n.Script')),
            ],
        ),
        migrations.CreateModel(
            name='MacroLanguageMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('A', 'Active'), ('R', 'Retired')], default='A', max_length=1)),
                ('individual_language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individuallangs', to='i18n.Language')),
                ('macrolanguage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='macrolangs', to='i18n.Language')),
                ('retired_individual_language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='macrolanguages', to='i18n.RetiredLanguage')),
            ],
        ),
        migrations.CreateModel(
            name='LocaleLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locale_langs', to='i18n.Lang')),
                ('locale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='names', to='i18n.Locale')),
            ],
        ),
        migrations.AddField(
            model_name='locale',
            name='script',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locales', to='i18n.Script'),
        ),
        migrations.CreateModel(
            name='LanguageLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('print_name', models.CharField(max_length=150)),
                ('inverted_name', models.CharField(max_length=150)),
                ('ref_name', models.BooleanField(default=False)),
                ('comment', models.CharField(blank=True, max_length=150, null=True)),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='name_langs', to='i18n.Lang')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lang_codes', to='i18n.Language')),
            ],
            options={
                'ordering': ['print_name'],
            },
        ),
        migrations.CreateModel(
            name='LangLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='langs', to='i18n.Lang')),
                ('namedlang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='namedlangs', to='i18n.Lang')),
            ],
        ),
        migrations.AddField(
            model_name='lang',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='langs', to='i18n.Language'),
        ),
        migrations.AddField(
            model_name='lang',
            name='script',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='langs', to='i18n.Script'),
        ),
        migrations.CreateModel(
            name='CountryLang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=510)),
                ('official_name', models.CharField(blank=True, max_length=500, null=True)),
                ('common_name', models.CharField(blank=True, max_length=140, null=True)),
                ('UN_formal_name', models.CharField(blank=True, max_length=160, null=True)),
                ('UN_short_name', models.CharField(blank=True, max_length=150, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_names', to='i18n.Country')),
                ('lang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='country_langs', to='i18n.Lang')),
            ],
            options={
                'verbose_name': 'Country Lang',
                'verbose_name_plural': 'Countries Lang',
            },
        ),
        migrations.AddConstraint(
            model_name='subdivisiontypelang',
            constraint=models.UniqueConstraint(fields=('type', 'lang'), name='subdivisiontypelang_unique'),
        ),
        migrations.AddConstraint(
            model_name='subdivisionlang',
            constraint=models.UniqueConstraint(fields=('subdivision', 'lang'), name='subdivisionlang_unique'),
        ),
        migrations.AddConstraint(
            model_name='subdivision',
            constraint=models.UniqueConstraint(fields=('code', 'country'), name='subdivision_unique'),
        ),
        migrations.AddConstraint(
            model_name='scriptlang',
            constraint=models.UniqueConstraint(fields=('script', 'lang'), name='scriptlang_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='macrolanguagemapping',
            constraint=models.UniqueConstraint(fields=('macrolanguage', 'individual_language'), name='individualmacrolanguage_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='macrolanguagemapping',
            constraint=models.UniqueConstraint(fields=('macrolanguage', 'retired_individual_language'), name='retiredindividualmacrolanguage_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='localelang',
            constraint=models.UniqueConstraint(fields=('locale', 'lang'), name='localelang_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='locale',
            constraint=models.UniqueConstraint(fields=('language', 'script', 'country'), name='locale_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='languagelang',
            constraint=models.UniqueConstraint(fields=('language', 'lang', 'print_name'), name='languagelang_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='langlang',
            constraint=models.UniqueConstraint(fields=('namedlang', 'lang'), name='langlang_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='lang',
            constraint=models.UniqueConstraint(fields=('language', 'script', 'country', 'variant', 'extension', 'private_use'), name='lang_uniquetogether'),
        ),
        migrations.AddConstraint(
            model_name='countrylang',
            constraint=models.UniqueConstraint(fields=('country', 'lang'), name='countrylang_unique'),
        ),
    ]
