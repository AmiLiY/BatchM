# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-26 05:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0015_auto_20161225_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorderofupdate',
            name='OrderId',
            field=models.CharField(default='20161226132916', max_length=128, primary_key=True, serialize=False, verbose_name='工单ID'),
        ),
        migrations.AlterField(
            model_name='workorderofupdate',
            name='configfile_content',
            field=models.CharField(blank=True, max_length=10240, null=True, verbose_name='修改配置文件内容'),
        ),
    ]
