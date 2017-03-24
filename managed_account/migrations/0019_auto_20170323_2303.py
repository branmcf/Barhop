# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0018_auto_20170323_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='order_code',
            field=models.CharField(max_length=250, unique=True, null=True, blank=True),
        ),
    ]
