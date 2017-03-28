# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0019_auto_20170323_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitems',
            name='item_name',
            field=models.CharField(max_length=800, null=True, blank=True),
        ),
    ]
