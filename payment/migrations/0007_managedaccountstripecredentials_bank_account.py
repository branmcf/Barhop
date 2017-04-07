# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_auto_20170323_0549'),
    ]

    operations = [
        migrations.AddField(
            model_name='managedaccountstripecredentials',
            name='bank_account',
            field=models.ForeignKey(blank=True, to='payment.BankAccount', null=True),
        ),
    ]
