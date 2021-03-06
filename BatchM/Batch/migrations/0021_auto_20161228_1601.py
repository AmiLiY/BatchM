# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 08:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0020_auto_20161228_1548'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dockercontainers',
            options={'verbose_name': 'Docker容器信息', 'verbose_name_plural': 'Docker容器信息'},
        ),
        migrations.AddField(
            model_name='dockercontainers',
            name='Record_time',
            field=models.DateField(auto_now=True, verbose_name='数据更新时间'),
        ),
        migrations.AlterField(
            model_name='dockercontainers',
            name='Created',
            field=models.CharField(max_length=200, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='dockercontainers',
            name='Host_config',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='主机配置'),
        ),
        migrations.AlterField(
            model_name='dockercontainers',
            name='Mounts',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='挂载目录'),
        ),
        migrations.AlterField(
            model_name='dockercontainers',
            name='Network_settings',
            field=models.CharField(blank=True, max_length=3000, null=True, verbose_name='网络配置'),
        ),
        migrations.AlterField(
            model_name='dockercontainers',
            name='SizeRootFs',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dockercontainers',
            name='SizeRw',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dockercontainers',
            name='Status',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='运行状态'),
        ),
        migrations.AlterField(
            model_name='workorderofupdate',
            name='OrderId',
            field=models.CharField(default='20161228160134', max_length=128, primary_key=True, serialize=False, verbose_name='工单ID'),
        ),
    ]
