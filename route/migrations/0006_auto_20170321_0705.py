# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0012_auto_20170321_0705'),
        ('route', '0005_conversation_step_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversation',
            name='step_status',
        ),
        migrations.AddField(
            model_name='conversation',
            name='process_stage',
            field=models.PositiveIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='trigger',
            field=models.ForeignKey(related_name='trigger', default=1, to='managed_account.Trigger'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='from_client',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='from_dealer',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='ConversationStepStatus',
        ),
    ]
