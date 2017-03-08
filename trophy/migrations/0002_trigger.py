# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trophy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trigger_name', models.CharField(max_length=250)),
                ('active', models.BooleanField(default=True)),
                ('dealer', models.ForeignKey(related_name='delear_triggers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'trigger',
                'verbose_name': 'Trigger',
                'verbose_name_plural': 'Triggers',
            },
        ),
    ]
