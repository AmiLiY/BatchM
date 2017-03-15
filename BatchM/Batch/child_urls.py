#!/usr/bin/env python
'''

'''
import os
import sys

path = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( path )


from django.conf.urls import url,include
from django.contrib import admin
from Batch import views
from Batch.asset import asset_views

urlpatterns = [
    url(r'index.html$|^$',views.dashboard_index),
    url(r'GetServerHostStatus$',views.server_host_status,name="get_server_host_status"),#获取运行次系统的服务状态信息
    url(r"^saltstack.html$",views.saltstack_index),
    url(r'^salt_single_host',views.saltstack_index,name='salt_single_host'),  # 对指定的salt-minion执行操作
    url(r'^saltstack_minions_show',views.saltstack_minions_show,name='saltstack_minions_show'),  # 针对单个salt-minion执行命令
    url(r"apply_update.html$",views.apply_update_apply),
    url(r"apply_update.html/search/(\d+)$",views.apply_detail),
    url(r"apply_update.html/search",views.apply_update_search,name='post_order_id'),  # 定义搜索工单到URL
    url(r"apply_update.html/apply",views.apply_update_apply,name='post_apply_data'), # 提交申请更新到数据到这里
    url(r'GetServerHostStatus$', views.server_host_status, name="get_server_host_status"),  # 获取运行次系统的服务状态信息
    url(r'DockerM.html$',views.docker_containers_show,name='all_containers_info'),   # 显示容器信息的
    url(r'DockerM/docker_manage',views.docker_manager ,name='docker_containers_manage'), # 控制容器起停等
    url(r'DockerM.html/images_show',views.docker_images_show,name='all_images_info'),   # 显示所有镜像，查找镜像，更新镜像等信息
    url(r'DockerM/(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:(\d+))',views.docker_container_detail_show,),    # 显示容器/宿主机/镜像详细信息

    # url(r'saltstack.html$',views.)
]

