# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-07 21:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0019_auto_20160406_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='time_posted',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]