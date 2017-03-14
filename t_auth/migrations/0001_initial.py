# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={b'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator(b'^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', b'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('email', models.EmailField(max_length=254, unique=True, null=True, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('mobile', models.CharField(blank=True, max_length=15, null=True, verbose_name='Mobile', validators=[django.core.validators.RegexValidator(regex=b'^\\+[1-9][0-9]{10,15}$', message=b'The required format is +XXXXXXXXXXX with Country code eg +13362688901. The number is 11 to 15 characters long.')])),
                ('is_ref_user', models.BooleanField(default=False)),
                ('is_dealer', models.BooleanField(default=False)),
                ('profile_image', models.CharField(default=b'default_avatar.png', max_length=50, blank=True)),
            ],
            options={
                'db_table': 'User',
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DealerEmployeMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('created_by', models.ForeignKey(related_name='user_created_by', to=settings.AUTH_USER_MODEL)),
                ('dealer', models.ForeignKey(related_name='dealer_mapping', to=settings.AUTH_USER_MODEL)),
                ('employe', models.ForeignKey(related_name='employee_mapping', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RefNewUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dealer_mobile', models.CharField(max_length=15)),
                ('mobile', models.CharField(max_length=15)),
                ('trigger', models.CharField(max_length=30)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('dealer', models.ForeignKey(related_name='user_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'new_user',
            },
        ),
    ]
