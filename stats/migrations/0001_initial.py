# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOnTask',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('tries', models.IntegerField(default=0)),
                ('state', models.CharField(default='n', max_length=1, choices=[('n', 'None'), ('c', 'Correct'), ('r', 'Revealed')])),
                ('skipped', models.BooleanField(default=False)),
                ('seed', models.IntegerField(default=0)),
                ('last', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(related_name='uots', to='courses.Task')),
                ('user', models.ForeignKey(related_name='uots', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WrongAnswer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(default='', max_length=1000)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('uot', models.ForeignKey(related_name='wrong_answers', to='stats.UserOnTask')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
