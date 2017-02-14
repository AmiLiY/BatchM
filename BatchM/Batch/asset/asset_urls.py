#!/usr/bin/env python
'''

'''
import os
import sys

path = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( path )


from django.conf.urls import url,include
from django.contrib import admin
from . import asset_views as views

urlpatterns = [
    url(r'new_assets/approval/',views.new_assets_approval,name="new_assets_approvel"),   #新的资产等待批准入库
    url(r'salt_group_create/$',views.create_salt_group,name="create_salt_group"),       # 创建saltstack组
    url(r'asset_list/$',views.asset_list ,name='asset_list'),       # 显示资产列表的信息,包含所有，大表
    url(r'asset_graphic/$|asset_graphic$',views.asset_graphic,name='asset_graphic'),   # 显示资产的饼状图
    url(r'asset_list/(\d+)/$',views.asset_detail,name='asset_detail'),    #显示单一一个资产信息，详细信息
    url(r'asset_list/list/$',views.get_asset_list,name='get_asset_list'),
    url(r'asset_list/category/$',views.asset_category,name='asset_category'),
    url(r'asset_list/shell/(\d+)$',views.run_shell),
    url(r'asset_event_logs/(\d+)/$',views.asset_event_logs,name='asset_event_logs'),
    url(r'approval/$',views.new_assets_approval),
    url(r'report/asset_with_no_asset_id/',views.report_with_no_id),
    url(r'report/?',views.report_resource),
    ]