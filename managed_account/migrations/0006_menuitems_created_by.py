# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0005_trigger_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitems',
            name='created_by',
            field=models.ForeignKey(related_name='menu_item_created', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
