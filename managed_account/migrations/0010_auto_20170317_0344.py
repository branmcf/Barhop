# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0009_auto_20170314_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='griddetails',
            name='grid_counter',
            field=models.PositiveIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='griddetails',
            name='grid',
            field=models.ForeignKey(related_name='grid_details', to='managed_account.Grid'),
        ),
        migrations.AlterField(
            model_name='griddetails',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
