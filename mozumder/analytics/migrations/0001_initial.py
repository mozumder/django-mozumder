# Generated by Django 3.0.7 on 2020-06-17 01:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accept_string', models.CharField(db_index=True, max_length=254, unique=True, verbose_name='Accept Encoding String')),
            ],
            options={
                'verbose_name': 'Accept Encoding',
            },
        ),
        migrations.CreateModel(
            name='AccessLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('lookup_time', models.FloatField(blank=True, default=0, null=True, verbose_name='DNS Lookup Time')),
                ('ssl_time', models.FloatField(blank=True, default=0, null=True, verbose_name='SSL Time')),
                ('connect_time', models.FloatField(blank=True, default=0, null=True, verbose_name='Connect Time')),
                ('response_time', models.FloatField(default=0, verbose_name='Response Time')),
                ('log_timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(verbose_name='HTTP Status Code')),
                ('protocol', models.CharField(choices=[('0', 'Unknown'), ('9', 'HTTP/1.0'), ('1', 'HTTP/1.0'), ('2', 'HTTP/1.1'), ('3', 'HTTP/2')], default='0', max_length=1)),
                ('method', models.CharField(choices=[('0', 'UNKNOWN'), ('1', 'GET'), ('2', 'HEAD'), ('3', 'POST'), ('4', 'PUT'), ('5', 'DELETE'), ('6', 'CONNECT'), ('7', 'OPTIONS'), ('8', 'TRACE'), ('9', 'PATCH')], default='1', max_length=1)),
                ('ajax', models.BooleanField(default=False, verbose_name='AJAX Request')),
                ('preview', models.BooleanField(default=False, verbose_name='Preview Request')),
                ('prefetch', models.BooleanField(default=False, verbose_name='Prefetch Request')),
                ('request_content_length', models.PositiveIntegerField(blank=True, null=True)),
                ('response_content_length', models.PositiveIntegerField(blank=True, null=True)),
                ('compress', models.CharField(choices=[('0', 'None'), ('1', 'gzip'), ('2', 'SDCH'), ('3', 'Brotli'), ('4', 'deflate')], default='0', max_length=1)),
                ('cached', models.BooleanField(default=False)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
            ],
            options={
                'verbose_name': 'Access Log',
                'verbose_name_plural': 'Accesses',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Browser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family', models.CharField(db_index=True, max_length=254)),
                ('major_version', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('minor_version', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('patch', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family', models.CharField(blank=True, db_index=True, max_length=254)),
                ('brand', models.CharField(db_index=True, max_length=254, null=True)),
                ('model', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('mobile', models.BooleanField(default=False)),
                ('pc', models.BooleanField(default=False)),
                ('tablet', models.BooleanField(default=False)),
                ('touch', models.BooleanField(default=False)),
                ('bot', models.BooleanField(default=False)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=80, unique=True, verbose_name='Domain Name')),
                ('bot', models.BooleanField(default=False)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Domain Name',
            },
        ),
        migrations.CreateModel(
            name='Encoding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('encoding_string', models.CharField(db_index=True, max_length=80, unique=True, verbose_name='Request Encoding String')),
            ],
            options={
                'verbose_name': 'Request Encoding',
            },
        ),
        migrations.CreateModel(
            name='HostName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=120, unique=True, verbose_name='Host')),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Host Name',
            },
        ),
        migrations.CreateModel(
            name='IP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.GenericIPAddressField(db_index=True, unique=True, verbose_name='IP Address')),
                ('bot', models.BooleanField(default=False)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'IP Address',
                'verbose_name_plural': 'IP Addresses',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_string', models.CharField(db_index=True, max_length=80, unique=True, verbose_name='Language String')),
            ],
            options={
                'verbose_name': 'Language Encoding',
            },
        ),
        migrations.CreateModel(
            name='MIME',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mime_type_string', models.CharField(db_index=True, max_length=80, unique=True, verbose_name='MIME Type String')),
            ],
            options={
                'verbose_name': 'MIME Type',
            },
        ),
        migrations.CreateModel(
            name='OS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family', models.CharField(db_index=True, max_length=254)),
                ('major_version', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('minor_version', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('patch', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('minor_patch', models.CharField(blank=True, db_index=True, max_length=254, null=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Operating System',
            },
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_path', models.CharField(db_index=True, max_length=254, unique=True, verbose_name='Search Path String')),
            ],
            options={
                'verbose_name': 'Search Path',
            },
        ),
        migrations.CreateModel(
            name='QueryString',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_string', models.CharField(db_index=True, max_length=254, unique=True, verbose_name='Query String')),
            ],
            options={
                'verbose_name': 'Query String',
            },
        ),
        migrations.CreateModel(
            name='SessionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=40, null=True, unique=True)),
                ('start_time', models.DateTimeField(db_index=True, default=django.utils.timezone.now, null=True)),
                ('expire_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('bot', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Session Log',
                'verbose_name_plural': 'Sessions',
            },
        ),
        migrations.CreateModel(
            name='UserAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_agent_string', models.CharField(db_index=True, max_length=254, unique=True, verbose_name='User Agent String')),
                ('bot', models.BooleanField(default=False)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('browser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='analytics.Browser', verbose_name='Browser')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='analytics.Device', verbose_name='Device')),
                ('os', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='analytics.OS', verbose_name='OS')),
            ],
            options={
                'verbose_name': 'User Agent',
            },
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=510, unique=True)),
                ('scheme', models.BooleanField(default=True)),
                ('port', models.SmallIntegerField(blank=True, null=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('authority', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.HostName')),
                ('canonical', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.URL')),
                ('path', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.Path')),
                ('query_string', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.QueryString')),
            ],
            options={
                'verbose_name': 'URL',
            },
        ),
        migrations.AddConstraint(
            model_name='os',
            constraint=models.UniqueConstraint(fields=('family', 'major_version', 'minor_version', 'patch', 'minor_patch'), name='os_unique'),
        ),
        migrations.AddField(
            model_name='ip',
            name='host',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.HostName', verbose_name='Host'),
        ),
        migrations.AddField(
            model_name='hostname',
            name='domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.Domain', verbose_name='Domain'),
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(fields=('brand', 'family', 'model'), name='device_unique'),
        ),
        migrations.AddConstraint(
            model_name='browser',
            constraint=models.UniqueConstraint(fields=('family', 'major_version', 'minor_version', 'patch'), name='browser_unique'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='accept_encoding',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.Encoding'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='accept_language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.Language'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='accept_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.Accept'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='ip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.IP', verbose_name='IP Address'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='referer_url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accesslog_referer_url', to='analytics.URL', verbose_name='Referer'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='request_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accesslog_request_content_type', to='analytics.MIME'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='request_url',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accesslog_request_url', to='analytics.URL', verbose_name='Request URL'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='response_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accesslog_response_content_type', to='analytics.MIME'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.Session'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='session_log',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.SessionLog'),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='user_agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.UserAgent'),
        ),
    ]
