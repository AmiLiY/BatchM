# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 11:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0013_auto_20161225_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='username',
            field=models.CharField(max_length=30, verbose_name='用户名'),
        ),
        migrations.AlterField(
            model_name='workorderofupdate',
            name='OrderId',
            field=models.CharField(default='20161225191530', max_length=128, primary_key=True, serialize=False, verbose_name='工单ID'),
        ),
    ]
