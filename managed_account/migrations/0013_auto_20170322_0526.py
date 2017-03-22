# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0012_purchaseorder_conversation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='conversation',
            field=models.ForeignKey(related_name='order_conversation', to='route.Conversation'),
        ),
    ]
