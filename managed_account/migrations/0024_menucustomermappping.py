# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0023_auto_20170411_0421'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuCustomerMappping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('menu_data', picklefield.fields.PickledObjectField(editable=False)),
                ('customer', models.ForeignKey(related_name='customer_menu_map', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('dealer', models.ForeignKey(related_name='dealer_menu_map', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('trigger', models.ForeignKey(related_name='tigger_menu_map', blank=True, to='managed_account.Trigger', null=True)),
            ],
        ),
    ]
