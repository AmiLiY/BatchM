# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-21 08:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0045_auto_20170220_1545'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ApproveHosts',
        ),
        migrations.AlterField(
            model_name='workorderofupdate',
            name='OrderId',
            field=models.CharField(default='20170221164341', max_length=128, primary_key=True, serialize=False, verbose_name='工单ID'),
        ),
    ]
