# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-26 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0005_auto_20160705_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalindicator',
            name='notes',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='notes',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
