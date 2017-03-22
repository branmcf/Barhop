# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0002_auto_20170310_0803'),
        ('managed_account', '0011_auto_20170320_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='conversation',
            field=models.ForeignKey(default=1, to='route.Conversation'),
            preserve_default=False,
        ),
    ]
