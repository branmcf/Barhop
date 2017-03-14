__author__ = 'nibesh'

from django.db import models
from django.utils import timezone
from t_auth.models import CustomUser


class ManagedAccount(models.Model):
    dealer = models.ForeignKey(CustomUser)
    account_id = models.CharField(max_length=25, blank=False, null=False, unique=True)
    secret_key = models.CharField(max_length=40, blank=False, null=False, unique=True)
    public_key = models.CharField(max_length=40, blank=False, null=False, unique=True)
    managed = models.BooleanField(default=True)

    date = models.DateTimeField(default=timezone.now)


class BankAccount(models.Model):
    dealer = models.ForeignKey(CustomUser)
    country = models.CharField(max_length=40)
    currency = models.CharField(max_length=10)
    routing_number = models.CharField(max_length=40)
    account_number = models.CharField(max_length=40)
    name = models.CharField(max_length=100)
    account_holder_type = models.CharField(max_length=15)
    stripeToken = models.CharField(max_length=40)
    date = models.DateTimeField(default=timezone.now)

class Trigger(models.Model):
    dealer = models.ForeignKey(CustomUser)
    trigger_name = models.CharField(max_length=250, unique=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, related_name='trigger_created_by')

    def __str__(self):
        return self.trigger_name

    class Meta:
        db_table = 'trigger'
        verbose_name = 'Trigger'
        verbose_name_plural = 'Triggers'