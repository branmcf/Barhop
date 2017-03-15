# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0008_auto_20170314_2300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchaseorder',
            old_name='menu',
            new_name='menu_item',
        ),
        migrations.AddField(
            model_name='menuitems',
            name='created_by',
            field=models.ForeignKey(related_name='menu_created_by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='trigger',
            field=models.ForeignKey(blank=True, to='managed_account.Trigger', null=True),
        ),
    ]
