# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0012_auto_20170321_0705'),
        ('t_auth', '0002_auto_20170310_0803'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='refnewuser',
            name='trigger',
        ),
        migrations.AddField(
            model_name='refnewuser',
            name='current_trigger',
            field=models.ForeignKey(blank=True, to='managed_account.Trigger', null=True),
        ),
    ]
