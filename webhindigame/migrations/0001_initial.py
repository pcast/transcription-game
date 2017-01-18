# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=50)),
                ('picture', models.CharField(max_length=50)),
                ('transcript', models.CharField(max_length=50)),
                ('time', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(unique=True, max_length=50)),
                ('score', models.IntegerField()),
                ('pvp', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Transcript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', models.CharField(max_length=50)),
                ('transcript', models.CharField(max_length=50)),
                ('score', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', models.CharField(unique=True, max_length=50)),
                ('word', models.CharField(max_length=50)),
                ('transcript', models.CharField(max_length=50)),
                ('solved', models.BooleanField()),
            ],
        ),
    ]
