# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0016_auto_20170323_0008'),
        ('route', '0008_remove_conversation_trigger'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='trigger',
            field=models.ForeignKey(related_name='trigger', default=1, to='managed_account.Trigger'),
            preserve_default=False,
        ),
    ]
