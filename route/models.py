__author__ = 'nibesh'

from django.db import models
from django.utils import timezone

from t_auth.models import CustomUser
from trophy.models import TrophyModel
from managed_account.models import Trigger
from django.utils.translation import ugettext_lazy as _

# class ConversationSteps(models.Model):
#     step_id = models.PositiveIntegerField(default=0, blank=True, null=True)
#     step = models.CharField(max_length=100,blank=True, null=True)
#     step_description = models.TextField(max_length=300)

class Conversation(models.Model):
    dealer = models.ForeignKey(CustomUser, related_name='sender')
    trophy = models.ForeignKey(TrophyModel)
    customer = models.ForeignKey(CustomUser, related_name='receiver')
    trigger = models.ForeignKey(Trigger, related_name='trigger')
    process_stage = models.PositiveIntegerField(default=0, blank=True, null=True)
    closed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    has_new_message = models.BooleanField(default=True)

    class Meta:
        db_table = 'conversation'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation)
    message = models.CharField(max_length=160)
    date = models.DateTimeField(auto_now=True)
    direction = models.BooleanField(default=False)
    from_client = models.BooleanField(default=False)
    from_dealer = models.BooleanField(default=False)

    class Meta:
        db_table = 'message'