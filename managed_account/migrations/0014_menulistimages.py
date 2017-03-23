# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managed_account', '0013_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuListImages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.FileField(upload_to=b'MenuImages/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('trigger', models.ForeignKey(blank=True, to='managed_account.Trigger', null=True)),
            ],
        ),
    ]
