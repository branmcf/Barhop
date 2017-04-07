# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0021_auto_20170328_0013'),
    ]

    operations = [
        migrations.AddField(
            model_name='griddetails',
            name='location',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
