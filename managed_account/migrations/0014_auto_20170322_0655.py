# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0013_auto_20170322_0526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='griddetails',
            name='created',
            field=models.DateTimeField(auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='created',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
