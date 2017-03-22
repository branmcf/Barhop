# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0002_auto_20170310_0803'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=40, null=True, blank=True)),
                ('currency', models.CharField(max_length=10, null=True, blank=True)),
                ('routing_number', models.CharField(max_length=40, null=True, blank=True)),
                ('account_number', models.CharField(max_length=40, null=True, blank=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('account_holder_type', models.CharField(max_length=15, null=True, blank=True)),
                ('stripeToken', models.CharField(max_length=40, null=True, blank=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('dealer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
