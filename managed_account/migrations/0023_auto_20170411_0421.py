# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0022_griddetails_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='menulistimages',
            name='dealer',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='griddetails',
            name='order',
            field=models.ForeignKey(related_name='order_grid_detail', blank=True, to='managed_account.PurchaseOrder', null=True),
        ),
    ]
