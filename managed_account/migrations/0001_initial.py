# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grid_row', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('grid_column', models.PositiveIntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'db_table': 'Grid',
                'verbose_name': 'Grid',
                'verbose_name_plural': 'Grids',
            },
        ),
        migrations.CreateModel(
            name='GridDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'GridDetails',
                'verbose_name': 'GridDetails',
                'verbose_name_plural': 'GridDetails',
            },
        ),
        migrations.CreateModel(
            name='MenuItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_name', models.CharField(max_length=800)),
                ('item_price', models.FloatField(null=True, blank=True)),
                ('quantity_available', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'MenuItems',
                'verbose_name': 'MenuItem',
                'verbose_name_plural': 'MenuItems',
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_code', models.CharField(unique=True, max_length=250)),
                ('order_status', models.CharField(max_length=1, verbose_name='Status', choices=[(b'PENDING', 'Pending'), (b'PAID', 'Paid'), (b'EXPIRED', 'Expired'), (b'READY', 'Ready'), (b'CLOSED', 'Closed')])),
                ('total_amount_paid', models.FloatField(null=True, blank=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires', models.DateTimeField(null=True, blank=True)),
                ('ip_address', models.FloatField(null=True, blank=True)),
                ('location', models.CharField(max_length=500, null=True, blank=True)),
            ],
            options={
                'db_table': 'PurchaseOrder',
                'verbose_name': 'PurchaseOrder',
                'verbose_name_plural': 'PurchaseOrders',
            },
        ),
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trigger_name', models.CharField(unique=True, max_length=250)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'trigger',
                'verbose_name': 'Trigger',
                'verbose_name_plural': 'Triggers',
            },
        ),
    ]
