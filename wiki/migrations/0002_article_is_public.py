# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-04-09 08:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
    ]
