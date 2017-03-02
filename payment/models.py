__author__ = 'nibesh'

from django.db import models
from django.utils import timezone

from t_auth.models import CustomUser
from trophy.models import TrophyModel


class PaymentModel(models.Model):
    dealer = models.ForeignKey(CustomUser, related_name='dealer')
    customer = models.ForeignKey(CustomUser, related_name='customer')
    trophy = models.ForeignKey(TrophyModel)
    date = models.DateTimeField(default=timezone.now)
    amount = models.IntegerField(help_text='Amount in cents')
    sales_tax = models.IntegerField(help_text='Amounts in cents', default=0)
    tip = models.IntegerField(help_text='Tip in Cents', default=0)
    detail = models.TextField(max_length=200)
    stripeToken = models.CharField(max_length=30, blank=True, null=True)
    stripeTokenType = models.CharField(max_length=15, blank=True, null=True)
    stripeEmail = models.EmailField(blank=True, null=True)
    charge_id = models.CharField(max_length=40, blank=True, null=True)
    processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Customer Payment'
        verbose_name_plural = 'Customer Payments'
        db_table = 'payment'

class TwilioPurchaseModel(models.Model):
    buyer = models.ForeignKey(CustomUser, related_name='buyer')
    date = models.DateTimeField(default=timezone.now)
    amount = models.IntegerField(help_text='Amount in cents')
    detail = models.TextField(max_length=200)
    stripeToken = models.CharField(max_length=30, blank=True, null=True)
    stripeTokenType = models.CharField(max_length=15, blank=True, null=True)
    stripeEmail = models.EmailField(blank=True, null=True)
    charge_id = models.CharField(max_length=40, blank=True, null=True)
    processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'twilio_payment'


class RevenueModel(models.Model):
    dealer = models.ForeignKey(CustomUser)
    transaction_amount = models.IntegerField(help_text='Amount in Cents')
    charge_amount = models.IntegerField(help_text='Amount in Cents')
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Revenue'
        verbose_name_plural = 'Revenue'
        db_table = 'revenue'
