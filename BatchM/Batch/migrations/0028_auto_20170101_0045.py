# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-31 16:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0027_auto_20170101_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dockercontainers',
            name='Real_host_ip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.DockerOfHost'),
        ),
        migrations.AlterField(
            model_name='workorderofupdate',
            name='OrderId',
            field=models.CharField(default='20170101004521', max_length=128, primary_key=True, serialize=False, verbose_name='工单ID'),
        ),
    ]
