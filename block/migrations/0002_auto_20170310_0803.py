# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('block', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blockmodel',
            name='blocked_user',
            field=models.ForeignKey(related_name='blocked_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blockmodel',
            name='blocker',
            field=models.ForeignKey(related_name='blocker', to=settings.AUTH_USER_MODEL),
        ),
    ]
