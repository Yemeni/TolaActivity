# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-13 13:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0015_auto_20170913_0428'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalindicator',
            name='level',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='indicators.Level'),
        ),
        migrations.RemoveField(
            model_name='indicator',
            name='level',
        ),
        migrations.AddField(
            model_name='indicator',
            name='level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='indicators.Level'),
        ),
    ]