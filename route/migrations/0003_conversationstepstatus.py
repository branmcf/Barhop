# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0002_auto_20170310_0803'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversationStepStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('step_id', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('step', models.CharField(max_length=100, null=True, blank=True)),
                ('step_description', models.TextField(max_length=300)),
                ('conversation', models.ForeignKey(to='route.Conversation')),
            ],
        ),
    ]
