# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0001_initial'),
        ('managed_account', '0002_auto_20170310_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='revenuemodel',
            name='dealer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='customer',
            field=models.ForeignKey(related_name='customer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='dealer',
            field=models.ForeignKey(related_name='dealer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='paymentmodel',
            name='order',
            field=models.ForeignKey(related_name='order', to='managed_account.PurchaseOrder'),
        ),
        migrations.AddField(
            model_name='managedaccountstripecredentials',
            name='dealer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
