__author__ = 'nibesh'

from django.db import models
from django.utils import timezone
# from t_auth.models import CustomUser


class TrophyModel(models.Model):
    dealer = models.ForeignKey('t_auth.CustomUser')
    twilio_mobile = models.CharField(max_length=15, blank=True, null=True)
    trophy = models.CharField(max_length=30, blank=True, null=True)
    message = models.CharField(max_length=160, blank=True, null=True)
    default_order_response = models.CharField(max_length=160, blank=True, null=True)
    enabled = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'trophy'
        verbose_name = 'Trophy'
        verbose_name_plural = 'Trophies'


class Trigger(models.Model):    
    dealer = models.ForeignKey('t_auth.CustomUser', related_name='delear_triggers')
    trigger_name = models.CharField(max_length=250)    
    active = models.BooleanField(default=True)    

    def __str__(self):        
        return self.trigger_name

    class Meta:
        db_table = 'trigger'
        verbose_name = 'Trigger'
        verbose_name_plural = 'Triggers'
