# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0015_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='conversation',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='order_code',
        ),
    ]
