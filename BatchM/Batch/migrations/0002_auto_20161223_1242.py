# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-23 12:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Batch', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeOfApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_name', models.CharField(max_length=255, verbose_name='应用名字')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
        ),
        migrations.CreateModel(
            name='TypeOfProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_of_project', models.CharField(max_length=255)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('include_apps', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.TypeOfApp')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderOfCodeUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='申请人')),
                ('target_host', models.CharField(max_length=255, verbose_name='目标主机IP/域名')),
                ('code_source', models.CharField(max_length=500, verbose_name='源码来源')),
                ('whether_change_configfile', models.BooleanField(default=False, verbose_name='是否修改配置文件')),
                ('edit_configfile', models.CharField(blank=True, max_length=10240, null=True, verbose_name='修改配置文件到内容')),
                ('whether_change_database', models.BooleanField(default=False, verbose_name='是否修改数据库')),
                ('sql_command', models.CharField(blank=True, max_length=10240, null=True, verbose_name='sql语句')),
                ('whether_change_crond', models.BooleanField(default=False, verbose_name='是否修改定时任务')),
                ('crond_task', models.CharField(blank=True, max_length=10240, null=True, verbose_name='定时任务')),
                ('system_env_change', models.CharField(blank=True, max_length=10240, null=True)),
                ('update_of_reason', models.CharField(blank=True, max_length=10240, null=True)),
                ('email_issend', models.BooleanField()),
                ('tags', models.CharField(blank=True, max_length=1020, null=True)),
                ('update_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('flow_app', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.TypeOfApp')),
                ('flow_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.TypeOfProject')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderOfConfigfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='申请人')),
                ('target_host', models.CharField(max_length=255, verbose_name='目标主机IP/域名')),
                ('configfile_path', models.CharField(max_length=255, verbose_name='配置文件路径')),
                ('content', models.CharField(max_length=10240, verbose_name='修改内容')),
                ('email_issend', models.BooleanField()),
                ('tags', models.CharField(blank=True, max_length=1020, null=True)),
                ('update_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderOfDatabaseChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='申请人')),
                ('sql_command', models.CharField(max_length=10240, verbose_name='sql语句')),
                ('target_host', models.CharField(max_length=255, verbose_name='目标主机IP/域名')),
                ('tags', models.CharField(blank=True, max_length=10240, null=True, verbose_name='备注')),
                ('email_issend', models.BooleanField()),
                ('update_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderOfType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_of_type', models.CharField(max_length=255, verbose_name='工单类型')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
        ),
        migrations.AddField(
            model_name='workorderofdatabasechange',
            name='order_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.WorkOrderOfType'),
        ),
        migrations.AddField(
            model_name='workorderofcodeupdate',
            name='order_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Batch.WorkOrderOfType'),
        ),
    ]
