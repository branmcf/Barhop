# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('managed_account', '0003_trigger_employe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trigger',
            name='employe',
        ),
        migrations.AddField(
            model_name='grid',
            name='created_by',
            field=models.ForeignKey(related_name='created_employee', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='grid',
            name='dealer',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='grid',
            name='trigger',
            field=models.ForeignKey(blank=True, to='managed_account.Trigger', null=True),
        ),
        migrations.AlterField(
            model_name='griddetails',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='griddetails',
            name='grid',
            field=models.ForeignKey(to='managed_account.Grid'),
        ),
        migrations.AlterField(
            model_name='griddetails',
            name='order',
            field=models.ForeignKey(blank=True, to='managed_account.PurchaseOrder', null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='customer',
            field=models.ForeignKey(related_name='purchase_order_customer', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='dealer',
            field=models.ForeignKey(related_name='purchase_order_dealer', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='menu',
            field=models.ForeignKey(blank=True, to='managed_account.MenuItems', null=True),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='order_status',
            field=models.CharField(max_length=10, verbose_name='Status', choices=[(b'PENDING', 'Pending'), (b'PAID', 'Paid'), (b'EXPIRED', 'Expired'), (b'READY', 'Ready'), (b'CLOSED', 'Closed')]),
        ),
    ]
