# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0002_auto_20170310_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='trigger',
            name='employe',
            field=models.ForeignKey(related_name='trigger_employee', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
