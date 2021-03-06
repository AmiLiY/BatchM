# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-24 08:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0007_auto_20161224_1624'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkOrderOfUpdate',
            fields=[
                ('OrderId', models.CharField(default='20161224163246', max_length=128, primary_key=True, serialize=False, verbose_name='工单ID')),
                ('username', models.CharField(max_length=255, verbose_name='申请人')),
                ('target_host', models.CharField(max_length=255, verbose_name='目标主机IP/域名')),
                ('whether_update_code', models.BooleanField(verbose_name='是否更新代码')),
                ('code_source', models.CharField(max_length=500, verbose_name='源码来源')),
                ('whether_change_configfile', models.BooleanField(default=False, verbose_name='是否修改配置文件')),
                ('configfile_path', models.CharField(max_length=255, verbose_name='配置文件路径')),
                ('edit_configfile', models.CharField(blank=True, max_length=10240, null=True, verbose_name='修改配置文件到内容')),
                ('whether_change_database', models.BooleanField(default=False, verbose_name='是否修改数据库')),
                ('sql_command', models.CharField(blank=True, max_length=10240, null=True, verbose_name='sql语句')),
                ('whether_change_crond', models.BooleanField(default=False, verbose_name='是否修改定时任务')),
                ('crond_task', models.CharField(blank=True, max_length=10240, null=True, verbose_name='定时任务')),
                ('system_env_change', models.CharField(blank=True, max_length=10240, null=True, verbose_name='系统环境变更')),
                ('update_of_reason', models.CharField(blank=True, max_length=10240, null=True, verbose_name='更新原因')),
                ('email_issend', models.BooleanField(verbose_name='提醒邮件是否已经发送')),
                ('tags', models.CharField(blank=True, max_length=1020, null=True)),
                ('update_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('flow_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.TypeOfApp', verbose_name='归属应用')),
                ('flow_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.TypeOfProject', verbose_name='归属项目')),
                ('order_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.WorkOrderOfType', verbose_name='工单操作类型')),
            ],
            options={
                'verbose_name_plural': '代码更新工单记录',
                'verbose_name': '代码更新工单记录',
            },
        ),
        migrations.RemoveField(
            model_name='workorderofcodeupdate',
            name='flow_app',
        ),
        migrations.RemoveField(
            model_name='workorderofcodeupdate',
            name='flow_project',
        ),
        migrations.RemoveField(
            model_name='workorderofcodeupdate',
            name='order_type',
        ),
        migrations.RemoveField(
            model_name='workorderofconfigfile',
            name='flow_app',
        ),
        migrations.RemoveField(
            model_name='workorderofdatabasechange',
            name='order_type',
        ),
        migrations.DeleteModel(
            name='WorkOrderOfCodeUpdate',
        ),
        migrations.DeleteModel(
            name='WorkOrderOfConfigfile',
        ),
        migrations.DeleteModel(
            name='WorkOrderOfDatabaseChange',
        ),
    ]
