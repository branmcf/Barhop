# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0020_auto_20170327_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitems',
            name='item_price',
            field=models.FloatField(default=0, null=True, blank=True),
        ),
    ]
