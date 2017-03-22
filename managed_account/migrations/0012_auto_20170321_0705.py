# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0011_auto_20170320_0318'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderMenuMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('total_item_amount', models.FloatField(null=True, blank=True)),
                ('menu_item', models.ForeignKey(blank=True, to='managed_account.MenuItems', null=True)),
            ],
            options={
                'db_table': 'OrderMenuMapping',
                'verbose_name': 'OrderMenuMapping',
                'verbose_name_plural': 'OrderMenuMappings',
            },
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='menu_item',
        ),
        migrations.AlterField(
            model_name='trigger',
            name='dealer',
            field=models.ForeignKey(related_name='trigger_dealer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordermenumapping',
            name='order',
            field=models.ForeignKey(related_name='order_menu_datar', blank=True, to='managed_account.PurchaseOrder', null=True),
        ),
    ]
