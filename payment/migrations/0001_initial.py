# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ManagedAccountStripeCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('publishable_key', models.CharField(max_length=500, null=True, blank=True)),
                ('livemode', models.BooleanField()),
                ('access_token', models.CharField(max_length=500, null=True, blank=True)),
                ('scope', models.CharField(max_length=200, null=True, blank=True)),
                ('refresh_token', models.CharField(max_length=500, null=True, blank=True)),
                ('account_user_id', models.CharField(max_length=300, null=True, blank=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'ManagedAccountStripeCredentials',
                'verbose_name_plural': 'ManagedAccountStripeCredentials',
            },
        ),
        migrations.CreateModel(
            name='PaymentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('charge_id', models.CharField(max_length=40, null=True, blank=True)),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('total_amount', models.FloatField(help_text=b'Amount in cents')),
                ('order_amount', models.FloatField(help_text=b'Atual item amount')),
                ('sales_tax', models.IntegerField(default=0, help_text=b'Amounts in cents')),
                ('tip', models.IntegerField(default=0, help_text=b'Tip in Cents')),
                ('detail', models.TextField(max_length=200)),
                ('stripeToken', models.CharField(max_length=30, null=True, blank=True)),
                ('stripeTokenType', models.CharField(max_length=15, null=True, blank=True)),
                ('stripeEmail', models.EmailField(max_length=254, null=True, blank=True)),
                ('bill_number', models.CharField(max_length=200, null=True, blank=True)),
                ('processed', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'payment',
                'verbose_name': 'Customer Payment',
                'verbose_name_plural': 'Customer Payments',
            },
        ),
        migrations.CreateModel(
            name='RevenueModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_amount', models.IntegerField(help_text=b'Amount in Cents')),
                ('charge_amount', models.IntegerField(help_text=b'Amount in Cents')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'revenue',
                'verbose_name': 'Revenue',
                'verbose_name_plural': 'Revenue',
            },
        ),
        migrations.CreateModel(
            name='StripeData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('secret_key', models.CharField(max_length=200)),
                ('client_id', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Stripe Credentials',
                'verbose_name_plural': 'Stripe Credentials',
            },
        ),
    ]
