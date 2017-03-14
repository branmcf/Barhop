# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('closed', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('has_new_message', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'conversation',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=160)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('direction', models.BooleanField(default=False)),
                ('conversation', models.ForeignKey(to='route.Conversation')),
            ],
            options={
                'db_table': 'message',
            },
        ),
    ]
