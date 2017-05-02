
from django.db import models
from django.utils import timezone

from t_auth.models import CustomUser

class BlockModel(models.Model):
    blocker = models.ForeignKey(CustomUser, related_name='blocker')
    blocked_user = models.ForeignKey(CustomUser, related_name='blocked_user')
    date = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'block_model'