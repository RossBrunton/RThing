# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExtraData',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('last_script_time', models.DateTimeField(auto_now_add=True)),
                ('last_script_code', models.TextField(default='', max_length=1000, blank=True)),
                ('last_script_output', models.TextField(default='', max_length=1000, blank=True)),
                ('last_script_error', models.BooleanField(default=False)),
                ('password_forced', models.BooleanField(default=True)),
                ('last_task', models.ForeignKey(default=None, to='courses.Task', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('user', models.OneToOneField(related_name='extra', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
