# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('title', models.CharField(max_length=30, unique=True)),
                ('slug', models.SlugField(max_length=35, unique=True, blank=True)),
                ('code', models.CharField(max_length=10, blank=True)),
                ('description', models.TextField(help_text="See <a href='/staff/help/formatting'>here</a> for formatting help")),
                ('ending', models.TextField(blank=True)),
                ('published', models.BooleanField(default=False)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['code'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('title', models.CharField(max_length=30)),
                ('slug', models.SlugField(max_length=35, blank=True)),
                ('introduction', models.TextField(help_text="See <a href='/staff/help/formatting'>here</a> for formatting help")),
                ('closing', models.TextField(blank=True)),
                ('published', models.BooleanField(default=False)),
                ('answers_published', models.BooleanField(default=False)),
                ('course', models.ForeignKey(related_name='lessons', to='courses.Course')),
            ],
            options={
                'ordering': ['course', 'order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('title', models.CharField(max_length=30)),
                ('slug', models.SlugField(max_length=35, blank=True)),
                ('introduction', models.TextField(help_text="See <a href='/staff/help/formatting'>here</a> for formatting help")),
                ('closing', models.TextField(blank=True)),
                ('lesson', models.ForeignKey(related_name='sections', to='courses.Lesson')),
            ],
            options={
                'ordering': ['lesson', 'order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('description', models.TextField(help_text="See <a href='/staff/help/formatting'>here</a> for formatting help")),
                ('after_text', models.TextField(blank=True)),
                ('wrong_text', models.TextField(blank=True)),
                ('skip_text', models.TextField(blank=True)),
                ('commentary', models.TextField(blank=True)),
                ('language', models.CharField(default='r', max_length=10, choices=[('dummy', 'Dummy Interface'), ('r', 'R')])),
                ('random_id', models.CharField(max_length=10, blank=True)),
                ('hidden_pre_code', models.TextField(blank=True)),
                ('visible_pre_code', models.TextField(blank=True)),
                ('model_answer', models.TextField()),
                ('validate_answer', models.TextField(blank=True)),
                ('post_code', models.TextField(blank=True)),
                ('uses_random', models.BooleanField(default=False)),
                ('uses_image', models.BooleanField(default=False)),
                ('automark', models.BooleanField(default=True)),
                ('takes_prior', models.BooleanField(default=False)),
                ('section', models.ForeignKey(related_name='tasks', to='courses.Section')),
            ],
            options={
                'ordering': ['section', 'order'],
            },
            bases=(models.Model,),
        ),
    ]
