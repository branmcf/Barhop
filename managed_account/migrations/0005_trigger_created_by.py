# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0004_auto_20170313_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='trigger',
            name='created_by',
            field=models.ForeignKey(related_name='trigger_created_by', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
