'''
include self defined functions,
'''

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from BatchM import settings
from Batch.plugs import docker_control
from Batch import formself,models
from django.core import mail
from multiprocessing import Pool,TimeoutError
import json
import urllib
from urllib import error
import time,datetime

import os
import re


class SettingsBackend(object):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name, and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """

    def authenticate(self, username=None, password=None):
        login_valid = (settings.ADMIN_LOGIN == username)
        pwd_valid = check_password(password, settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; the password
                # from settings.py will.
                user = User(username=username, password='get from settings.py')
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def selfmail(request_set):
    '''
    发送邮件到到运维同事
    '''

    sender = settings.sender_host
    recipients = settings.recipients
    title = '您有新到工单需要处理,工单号是：%s' %(request_set['OrderId'])

    if request_set['accessory_path'] is not None:
        request_set['accessory_path'] = "http://%s:%s/%s"%(settings.HOST,settings.APACHE_PORT,request_set['accessory_path'].split('upload')[1])
    msg_body = '''
            工单链接：http://%s/BatchM/apply_update.html/search/%s
            附件地址(None为没有附件)：%s
            申请人: %s
            归属项目：%s
            归属应用: %s
            目标服务器： %s
            更新原因： %s
            详情请看工单链接，麻烦尽快处理，谢谢。
            '''%(settings.HOST,request_set['OrderId'],request_set['accessory_path'],request_set['username'],request_set['flow_project'],request_set['flow_app'],
            request_set['target_host'],request_set['update_of_reason'])

    try:
        send_mail(title, msg_body,sender,(recipients,))
    except ConnectionRefusedError as e:
        print(e)
        return False
    return True



def DockersInfo(action='select',id=None):
    '''
    获取容器信息的，依赖于plugs下面到docker_control，对应到前端按钮事刷新容器信息。
    action: 执行到动作，比如select查询信息,restart重启容器等
    container_id: 容器ID
    docker_rhost: 必须是models objects,比如 docker_rhost = models.DockerOfHost.objects.all()
    :return:
    '''

    docker_rhost = models.DockerOfHost.objects.all()
    info_result = {}
    docker_manage = docker_control.docker_operation()
    pool = Pool(settings.pools)
    object_type = 'containers'
    for info in docker_rhost:
        host, port = info.host_ip.split(':')
        result = pool.apply_async( docker_manage.control_containers, (host,port,action,object_type,id),)
        info_result[info] = result.get()
    pool.close()
    pool.join()
    print('DockersInfo-info_result',info_result)
    return  info_result

def DockerManager(request):
    '''
    对容器进行管理的，比如启动容器，暂停容器，销毁容器，显示容器内进程的
    同时也对镜像操作，如搜寻所有镜像信息，删除镜像,添加镜像等
    :param:request  get request from caller
    :return: success_list : 动作执行成功的荣里放在这里,, err_list 是动作执行失败到放在这里。
    '''
    success_dict = {}
    err_dict = {}
    info_result = {}            # 定义操做结果列表
    action = request.POST.get('action')   # 执行什么样到操作，是删除，还是搜索，还是添加
    object_type=request.POST.get('type')    # 操作对象，是容器还是镜像
    pool = Pool(settings.pools)             # 设定进程池
    docker_manage = docker_control.docker_operation()
    containers_id = ''  # 定义初始值，避免下面到代码抛出异常
    hosts_list = ''
    if object_type == "containers":   # 操作对象为容器
        containers_id = json.loads(request.POST.get('container_id_array'))
    elif object_type == "images":  # 操作对象为镜像文件
        hosts_list = request.POST.get('hosts')
        if hosts_list == "all":
            hosts_list = {}
            hosts  = models.DockerOfHost.objects.all()
            for host in hosts:
                hosts_list[host.host_ip] = None
        else:
            hosts_list = json.loads(hosts_list)
    print('action', action, 'object_type', object_type, 'hosts',hosts_list)

    if action and containers_id:   # 如果没有提供任何执行动作与容器ID,那么就不执行.
        for ID,host in containers_id.items():
            print(ID,host)
            host,port = host.split(':')
            result = pool.apply_async( docker_manage.control_containers, (host,port,action,object_type,ID),)
            info_result[ID] = result.get()
        pool.close()
        pool.join()
        print('DockerManager-info_result',info_result)
        for k,v in info_result.items():
            if action != 'top':     # 如果对容器的操作动作不是top，那么返回来的值是HTTP状态码，判断状态码来分别放到不同到列表中
                if str(v[0]).startswith('20') or str(v[0]).startswith('30'):
                    success_dict[k] = v
                else:
                    err_dict[k] = v
            elif action == 'top':  # 对容器的操作动作是top的时候，如果容器没有运行，
                # 那么就会直接报错（HTTP 500错误），容器ID写错，那么就是HTTP 404错误，whatever error，返回来的事元组，下标0为False,

                if type(v) is tuple and v[0] == False:
                    err_dict[k] = "%s:%s" %(v[1],v[2])
                else:
                    success_dict[k] = v

    elif action and hosts_list:   # 对镜像进行操作
        for k,ID  in hosts_list.items():
            host,port= k.split(':')
            result = pool.apply_async( docker_manage.control_containers, (host,port,action,object_type,ID),)
            if action == 'select':
                print(type(result),'result',result.get(timeout=30))
                info_result['%s:%s'%(host,port)] = '' if len(result.get(timeout=30)) == 0 else result.get(timeout=30)[0]
            else:
                info_result['%s:%s' % (host, port)] = result.get(timeout=30)
        pool.close()
        pool.join()
        print('info_result',info_result)
        for k,v in info_result.items():
            if action == 'select':    # 刷新镜像的动作，因为不需要关心详细到镜像ID信息，所以直接把宿主机IP添加即可
                if v == False :
                    err_dict[k] = v
                elif len(v) == 0:    # 长度等于0表示没有获取到镜像信息/容器信息在指定的宿主机上
                    break
                else:
                    if info_result[k].get('Labels'):   # 因为Labels是字典到数据格式，如果没有数据那么就为空，方便前端展示如果Labels为空到时候
                            info_result[k]['Labels'] = ''
                    success_dict[k] = v
            else:    # 删除镜像和添加镜像到功能，因为要关心镜像ID和宿主机的IP，所以必须载记录镜像ID和宿主机的IP
                if str(v[0]).startswith('4') or str(v[0]).startswith('5'):
                    err_dict[k] = v[2]
                elif str(v[0]).startswith('2') or str(v[0]).startswith('3'):
                    success_dict[k] = v[2]

        if action == 'select':  # 如果是刷新容器镜像信息，那么就走下面到代码,入库存信息
            mod_obj = models.DockerOfImages.objects.all().delete()  # 清空数据库信息。
            for k,v in success_dict.items():
                store_body = {
                   "Image_id":v.get('Id'),"Parent_id":v.get('ParentId'),
                    "Repo_tags":v.get('RepoTags'),"Repo_digests":'' if len(v.get('RepoDigests')) == 0 else v.get('RepoDigests'),
                    "Created":time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(v.get('Created'))),"Image_size":v.get('Size'),
                    "Virtual_size":v.get('VirtualSize'),"Labels":'' if len(v.get('Labels')) == 0 else v.get('Labels'),
                }
                mod_obj = models.DockerOfImages(**store_body)
                mod_obj.save()
                mod_obj.Host_ip.add(models.DockerOfHost.objects.get(host_ip=k))  #k等于主机

    else:
        return False

    return success_dict,err_dict

def CreateContainer(request):
    '''
    创建容器的方法
    :param request:   用户的请求头
    :return:
    '''

    version = settings.DockerVersion
    request_dict = json.loads(request)
    request_dict2 = {}
    print('request',request)
    host_port,image = request_dict.get('host_image').split()  # 获取宿主机IP与镜像名字
    action = request_dict.get('action')
    image_name = image.split("'")[1].split(':')[0]
    for k,v in request_dict.items():
        if v :   # 对提交上来的数据进行清洗，value为空的就去除掉。
            request_dict2[k] = v    # 添加到新到新的字典中
    del request_dict2['host_image'], request_dict2['action']
    request_dict2['image'] = image_name
    request_dict2['dns'] = request_dict2.get('dns').split(',')  # docker模块里面表明了dns必须是个列表
    request_dict2['ports'] = eval(request_dict2.get('ports')) if request_dict2.get('ports') else request_dict2.get('ports')
    #request_dict2['volumes'] = eval(request_dict2.get('volumes')) if request_dict2.get('volumes') else request_dict2.get('ports')
    print('request_dict2',request_dict2)
    if action == "save_model":
        pass
    elif action == "create_container":
        dc = docker_control.docker_operation2(host_port,version)
        container_instance = dc.create(**request_dict2)
        print('container_instance',container_instance)
        print("request_dict2.get('detach')",request_dict2.get('detach'),type(request_dict2.get('detach')))

        if container_instance is tuple:
            if container_instance[0] is False:
                return container_instance[1:2]
        else:
            if request_dict2.get('detach') == 'True':  # 是否启动容器在创建以后
                container_instance.start()
            return container_instance




