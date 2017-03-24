# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20170322_0655'),
    ]

    operations = [
        migrations.RenameField(
            model_name='managedaccountstripecredentials',
            old_name='account_user_id',
            new_name='account_id',
        ),
        migrations.RemoveField(
            model_name='managedaccountstripecredentials',
            name='access_token',
        ),
        migrations.RemoveField(
            model_name='managedaccountstripecredentials',
            name='livemode',
        ),
        migrations.RemoveField(
            model_name='managedaccountstripecredentials',
            name='publishable_key',
        ),
        migrations.RemoveField(
            model_name='managedaccountstripecredentials',
            name='refresh_token',
        ),
        migrations.RemoveField(
            model_name='managedaccountstripecredentials',
            name='scope',
        ),
        migrations.AddField(
            model_name='managedaccountstripecredentials',
            name='managed',
            field=models.BooleanField(default=True),
        ),
    ]
