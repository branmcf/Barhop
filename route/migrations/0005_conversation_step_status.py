# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0004_remove_conversationstepstatus_conversation'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='step_status',
            field=models.ForeignKey(related_name='step_status', default='', to='route.ConversationStepStatus'),
            preserve_default=False,
        ),
    ]
