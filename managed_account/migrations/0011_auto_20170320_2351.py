# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0010_auto_20170317_0344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grid',
            name='trigger',
            field=models.ForeignKey(related_name='grid_trgger', blank=True, to='managed_account.Trigger', null=True),
        ),
    ]
