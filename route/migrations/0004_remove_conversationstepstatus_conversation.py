# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0003_conversationstepstatus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversationstepstatus',
            name='conversation',
        ),
    ]
