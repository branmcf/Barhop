# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TrophyModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('twilio_mobile', models.CharField(max_length=15, null=True, blank=True)),
                ('trophy', models.CharField(max_length=30, null=True, blank=True)),
                ('message', models.CharField(max_length=160, null=True, blank=True)),
                ('default_order_response', models.CharField(max_length=160, null=True, blank=True)),
                ('enabled', models.BooleanField(default=False)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('dealer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'trophy',
                'verbose_name': 'Trophy',
                'verbose_name_plural': 'Trophies',
            },
        ),
    ]
