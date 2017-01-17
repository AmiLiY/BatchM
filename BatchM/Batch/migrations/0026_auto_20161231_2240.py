# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 14:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0025_auto_20161231_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dockercontainers',
            name='Real_host_ip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.DockerOfHost', verbose_name='容器宿主机IP'),
        ),
        migrations.AlterField(
            model_name='workorderofupdate',
            name='OrderId',
            field=models.CharField(default='20161231224017', max_length=128, primary_key=True, serialize=False, verbose_name='工单ID'),
        ),
    ]
