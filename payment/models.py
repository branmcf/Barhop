from django.db import models
from django.utils import timezone

from t_auth.models import CustomUser
from trophy.models import TrophyModel
from managed_account.models import PurchaseOrder

class StripeData(models.Model):
    secret_key = models.CharField(max_length=200, null=False, blank=False)
    client_id = models.CharField(max_length=200, null=False, blank=False)
 
    class Meta:
        verbose_name = 'Stripe Credentials'
        verbose_name_plural = 'Stripe Credentials'


class ManagedAccountStripeCredentials(models.Model):
    dealer = models.ForeignKey(CustomUser)
    account_id = models.CharField(max_length=300, null=True, blank=True)
    managed = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s" % (self.dealer)

    class Meta:
        verbose_name = 'ManagedAccountStripeCredentials'
        verbose_name_plural = 'ManagedAccountStripeCredentials'


class BankAccount(models.Model):
    dealer = models.OneToOneField(CustomUser)
    country = models.CharField(max_length=40, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    routing_number = models.CharField(max_length=40, null=True, blank=True)
    account_number = models.CharField(max_length=40, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    account_holder_type = models.CharField(max_length=15, null=True, blank=True)
    stripeToken = models.CharField(max_length=40, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)



class PaymentModel(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name='order')
    dealer = models.ForeignKey(CustomUser, related_name='dealer')
    customer = models.ForeignKey(CustomUser, related_name='customer')
    charge_id = models.CharField(max_length=40, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now=True)
    total_amount = models.FloatField(help_text='Amount in cents')
    order_amount = models.FloatField(help_text='Atual item amount')
    sales_tax = models.IntegerField(help_text='Amounts in cents', default=0)
    tip = models.IntegerField(help_text='Tip in Cents', default=0)
    detail = models.TextField(max_length=200)
    stripeToken = models.CharField(max_length=30, blank=True, null=True)
    stripeTokenType = models.CharField(max_length=15, blank=True, null=True)
    stripeEmail = models.EmailField(blank=True, null=True)
    bill_number = models.CharField(max_length=200, null=True, blank=True)
    processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Customer Payment'
        verbose_name_plural = 'Customer Payments'
        db_table = 'payment'

class RevenueModel(models.Model):
    dealer = models.ForeignKey(CustomUser)
    transaction_amount = models.IntegerField(help_text='Amount in Cents')
    charge_amount = models.IntegerField(help_text='Amount in Cents')
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Revenue'
        verbose_name_plural = 'Revenue'
        db_table = 'revenue'
