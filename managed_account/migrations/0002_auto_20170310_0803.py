# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trigger',
            name='dealer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='customer',
            field=models.ForeignKey(related_name='purchase_order_customer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='dealer',
            field=models.ForeignKey(related_name='purchase_order_dealer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='menu',
            field=models.ForeignKey(default=True, blank=True, to='managed_account.MenuItems'),
        ),
        migrations.AddField(
            model_name='menuitems',
            name='dealer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='griddetails',
            name='grid',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='griddetails',
            name='order',
            field=models.ForeignKey(to='managed_account.PurchaseOrder'),
        ),
        migrations.AddField(
            model_name='grid',
            name='dealer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='grid',
            name='trigger',
            field=models.ForeignKey(to='managed_account.Trigger'),
        ),
    ]
