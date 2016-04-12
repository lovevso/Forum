# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-08 09:24
from __future__ import unicode_literals

import blog.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0024_auto_20160408_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='thumb',
            field=models.ImageField(blank=True, upload_to=blog.models.get_unique_path),
        ),
        migrations.AlterField(
            model_name='thread',
            name='thumb',
            field=models.ImageField(blank=True, upload_to=blog.models.get_unique_path),
        ),
    ]