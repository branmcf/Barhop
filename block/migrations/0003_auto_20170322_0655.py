# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('block', '0002_auto_20170310_0803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockmodel',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
