# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0007_auto_20170314_0734'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuitems',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='menu_item',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='trigger',
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='menu',
            field=models.ForeignKey(blank=True, to='managed_account.MenuItems', null=True),
        ),
    ]
