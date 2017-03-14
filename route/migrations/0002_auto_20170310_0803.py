# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trophy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='customer',
            field=models.ForeignKey(related_name='receiver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversation',
            name='dealer',
            field=models.ForeignKey(related_name='sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversation',
            name='trophy',
            field=models.ForeignKey(to='trophy.TrophyModel'),
        ),
    ]
