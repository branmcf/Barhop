__author__ = 'nibesh'

from django.db import models
from django.utils import timezone

from t_auth.models import CustomUser
from trophy.models import TrophyModel


class Conversation(models.Model):
    dealer = models.ForeignKey(CustomUser, related_name='sender')
    trophy = models.ForeignKey(TrophyModel)
    customer = models.ForeignKey(CustomUser, related_name='receiver')

    closed = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    has_new_message = models.BooleanField(default=True)

    class Meta:
        db_table = 'conversation'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation)
    message = models.CharField(max_length=160)
    date = models.DateTimeField(default=timezone.now)
    direction = models.BooleanField(default=False)

    class Meta:
        db_table = 'message'
