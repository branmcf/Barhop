# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0006_menuitems_created_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorder',
            old_name='menu',
            new_name='menu_item',
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='trigger',
            field=models.ForeignKey(blank=True, to='managed_account.Trigger', null=True),
        ),
    ]
