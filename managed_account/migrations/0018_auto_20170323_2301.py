# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0009_conversation_trigger'),
        ('managed_account', '0017_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='conversation',
            field=models.ForeignKey(related_name='order_conversation', blank=True, to='route.Conversation', null=True),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='order_code',
            field=models.CharField(default=1, unique=True, max_length=250),
            preserve_default=False,
        ),
    ]
