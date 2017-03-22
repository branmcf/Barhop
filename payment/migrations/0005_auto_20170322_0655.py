# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20170320_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='managedaccountstripecredentials',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='paymentmodel',
            name='payment_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='revenuemodel',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
