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
from Batch.plugs import  record_log
from django.core import mail
from multiprocessing import Pool,TimeoutError
from urllib import error
import json
import pycurl
import urllib
import time,datetime
from io import  BytesIO

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
    print('action', action, 'object_type', object_type, 'hosts',hosts_list,'containers_id',containers_id)

    if action and containers_id:   # 如果没有提供任何执行动作与容器ID,那么就不执行.
        if action == "exec_cmd":   # 对选定的容器执行命令
            cmd = request.POST.get('cmd')
            print('cmd',cmd)
            for ID,host in  containers_id.items():
                docker_manage2 = docker_control.docker_operation2(host,version=settings.DockerVersion)
                result = pool.apply_async(docker_manage2.exec_cmd, (ID,cmd),)
                print(result)
                info_result[ID] = result.get()


        else:   # 如果不是对容器执行命令，那么就是对容器启动，停止，删除等操作
            for ID,host in containers_id.items():
                print(ID,host)
                host,port = host.split(':')
                result = pool.apply_async( docker_manage.control_containers, (host,port,action,object_type,ID),)
                info_result[ID] = result.get()
        pool.close()
        pool.join()
        print('DockerManager-info_result',info_result)
        for k,v in info_result.items():   # 遍历执行结果（对容器操作的执行结果）
            if action == "exec_cmd":
                if v[0] == False:  # 表示执行命令返回有错
                    err_dict[k] = "%s:%s" % (v[1], v[2])
                else:
                    success_dict[k] = v

            elif action == 'top':  # 对容器的操作动作是top的时候，如果容器没有运行，
                # 那么就会直接报错（HTTP 500错误），容器ID写错，那么就是HTTP 404错误，whatever error，返回来的事元组，下标0为False,

                if type(v) is tuple and v[0] == False:
                    err_dict[k] = "%s:%s" %(v[1],v[2])
                else:
                    success_dict[k] = v
            else:  # 如果对容器的操作动作不是top,and not exec_cmd ，那么返回来的值是HTTP状态码，判断状态码来分别放到不同到列表中
                if str(v[0]).startswith('20') or str(v[0]).startswith('30'):
                    success_dict[k] = v
                else:
                    err_dict[k] = v

    elif action and hosts_list:   # 对镜像进行操作
        for k,ID  in hosts_list.items():
            host,port= k.split(':')
            print(host, ID)
            if ID is not None and len(ID) > 1:  # 如果一个宿主机上多个镜像，那么做删除操作的时候需要遍历下镜像ID列表，因为前端提交的就是一个列表
                info_result['%s:%s' % (host, port)] = []
                for i in ID:
                    result = pool.apply_async(docker_manage.control_containers, (host, port, action, object_type, i), )
                    print('in for id',result)
                    info_result['%s:%s' % (host, port)].append(result.get())
            else:
                result = pool.apply_async( docker_manage.control_containers, (host,port,action,object_type,ID),)
                result = result.get(timeout=30)
                info_result['%s:%s' % (host, port)] = result

            if action == 'select':
                info_result['%s:%s'%(host,port)] = '' if len(result) == 0 else result
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
                    for image in v:   # 遍历镜像列表
                        if len(image.get('Labels')) == 0 :   # 因为Labels是字典到数据格式，如果没有数据那么就设置为None，方便前端展示如果Labels为空的时候
                            image['Labels'] = None
                        success_dict[k] = v

            else:    # 删除镜像和添加镜像到功能，因为要关心镜像ID和宿主机的IP，所以必须载记录镜像ID和宿主机的IP
                print(len(v))
                if len(v) > 1:  #大于1表示在对同一个宿主机的多个镜像做操作，len(v)就是统计要操作的镜像的数量
                    err_dict[k] = []    # 设置这个宿主机的值为列表
                    success_dict[k] = []
                    for per_tuple in v:  # 遍历每一个value里面元素，元素就是元组
                        if str(per_tuple[0]).startswith('4') or str(per_tuple[0]).startswith('5'):  # HTTP状态码是4/5开头的
                            err_dict[k].append(per_tuple[2])
                        elif str(per_tuple[0]).startswith('2') or str(per_tuple[0]).startswith('3'):  # HTTP状态码是2/3开头的
                            success_dict[k].append(per_tuple[2])
                else:
                    if str(v[0]).startswith('4') or str(v[0]).startswith('5'):      # HTTP状态码是4/5开头的
                        err_dict[k] = v[2]
                    elif str(v[0]).startswith('2') or str(v[0]).startswith('3'):    # HTTP状态码是2/3开头的
                        success_dict[k] = v[2]

        if action == 'select':  # 如果是刷新容器镜像信息，那么就走下面到代码,入库存信息
            mod_obj = models.DockerOfImages.objects.all().delete()  # 清空数据库信息。
            for k,v in success_dict.items():
                for image in v:
                    store_body = {
                       "Image_id":image.get('Id'),"Parent_id":image.get('ParentId'),
                        "Repo_tags":image.get('RepoTags'),"Repo_digests":'' if len(image.get('RepoDigests')) == 0 else image.get('RepoDigests'),
                        "Created":time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(image.get('Created'))),"Image_size":image.get('Size'),
                        "Virtual_size":image.get('VirtualSize'),"Labels":'' if image.get('Labels') is None else image.get('Labels'),
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
    :param request:   用户的请求头，从view视图里面传入
    :return:
    '''
    error_dict = {}
    success_dict = {}
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
    # 端口映射的话，要求输入的是字典模式，前台传入过来的是字符串模式，后台需要把字符串类型的字典改为真正的字典模式。
    request_dict2['ports'] = eval(request_dict2.get('ports')) if request_dict2.get('ports') else request_dict2.get('ports')
    request_dict2['detach'] = True    # 创建容器使用的是run方法，detach=True，那么才会返回container_obj，否则什么也不会返回
    request_dict2['volumes'] = eval(request_dict2.get('volumes')) if request_dict2.get('volumes') else request_dict2.get('volumes')
    print('request_dict2',request_dict2)
    if action == "save_model":
        pass
    elif action == "create_container":    # 创建容器的代码
        dc = docker_control.docker_operation2(host_port,version)
        container_instance = dc.create(**request_dict2)

        if type(container_instance) is tuple:
            if container_instance[0] is False:
                error_dict[container_instance[1]] = container_instance[2].decode()
                return error_dict
        return container_instance.id




class run_salt_api(object):
    '''
    调用saltapi来调用salt完成相关操作
    '''

    def __init__(self,username,passwd,auth_method='pam',ip="127.0.0.1",port=8080):
        self.ip = ip
        self.port = port
        self.username = username
        self.passwd = passwd
        self.auth_method = auth_method
        self.logger = record_log.handler_log('root', settings.logfile_path)
        self.token = self.api_login()


    def api_login(self):
        '''
        登陆用户，获取token
        '''
        url = "http://%s:%d/login" %(self.ip,self.port)
        ch = pycurl.Curl()
        info = BytesIO()
        ch.setopt(ch.URL,url)
        ch.setopt(ch.WRITEFUNCTION,info.write)
        ch.setopt(ch.POST,True)
        # add auth info to http header
        ch.setopt(ch.HTTPHEADER,['Accept: application/json'])
        ch.setopt(ch.POSTFIELDS,'username=%s&password=%s&eauth=%s'%(self.username,self.passwd,self.auth_method))
        ch.setopt(ch.HEADER,True)
        ch.perform()
        # get token from salt-api  response
        html = info.getvalue().decode()
        return_data = html.split('\n')[-1]
        import json
        token = json.loads(return_data)
        token = token['return'][0]['token']
        info.close()
        ch.close()
        self.logger.info('already got this token')
        return token

    def api_exec(self,target,func,arg='',expr_form=None,arg_num=0):
        '''
        调用saltapi执行相关的saltstack函数去执行
        pparam target: 要对哪个minion执行
        :param func:   执行哪个方法
        :param arg:     执行这个方法的参数
        :param arg_num:  参数的数量
        :return:
        '''
        import time

        url = "http://%s:%d" %(self.ip,self.port)
        ch = pycurl.Curl()    # ch == channel
        info = BytesIO()
        ch.setopt(ch.URL,url)
        ch.setopt(ch.WRITEFUNCTION,info.write)
        ch.setopt(ch.POST,True)

        ch.setopt(ch.HTTPHEADER,['Accept: application/x-yaml','X-Auth-Token: %s'%self.token])
        if arg_num == 0:
            if expr_form:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;expr_form=%s&amp;fun=%s'
                           %(target,expr_form,func))

            else:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;fun=%s'%(target,func))
        elif arg_num == 1:
            if expr_form:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;expr_form=%s&amp;fun=%s&amp;arg=%s'
                %(target,expr_form,func,arg))
            else:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;fun=%s&amp;arg=%s'%(target,func,arg))

        ch.setopt(ch.HEADER,False)
        ch.perform()
        html = info.getvalue().decode()
        info.close()
        ch.close()
        self.logger.info('already executed this command : [%s %s] ,targets: [%s] ,expr_form:[%s]'%(func,arg,target,expr_form))
        return html


class Create_SaltGroup(object):
    '''
    生成saltstack 的group的配置文件，在/etc/salt/master.d/下面生成。
    '''
    def __init__(self,**group_info):
        self.group_info = group_info   # self.group_info must be dict format
        self.group_file = settings.SaltGroupConfigFile
        nodegroups = os.popen("grep nodegroups: %s >/dev/null;echo $?"%self.group_file).read().split('\n')[0]
        if int(nodegroups):
            os.system("echo 'nodegroups:' >>%s"%self.group_file)


    def add_groups(self,create_group_id_list):
        '''
        添加组和组成员信息的
        ;:param:create_group_id_list 组ID列表，用来过滤哪些是已经在salt配置文件里面增加来到。
        :return:
        '''
        # 通过数据库里面到y一个字段来判断是否已经在配置文件里面生成来。
        for i in models.SaltGroup.objects.filter(id__in=create_group_id_list):
                if  i.whether_create:
                    self.group_info.pop(i.group_name)

        with open(self.group_file,'a') as f:
            for i,k in self.group_info.items():
                # 判断之前是否有同样到组名
                result_code = os.popen("grep ^'    %s:' %s >/dev/null ;echo $?"%(i,self.group_file)).read().split('\n')[0]
                if  int(result_code):
                    f.seek(0,2)
                    f.write("    %s: "%(i))
                    for v in k:
                        f.seek(0,2)
                        if k.index(v) == 0:  # if the v is first value in the list ,it should add L@ befor itself
                            f.write("L@%s,"%(v))
                        elif k.index(v) == len(k)-1: # if the v is last one in the list,it should add ' end of line
                            f.write("%s\n"%v)
                        else:
                            f.write("%s,"%(v))
        return True

    def del_groups(self):
        '''
        删除组和组成员信息的
        :return:
        '''
        import datetime
        new_file_name = self.group_file+datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        onef=open(new_file_name,'a+')
        with open(self.group_file,'a+') as f:
            for line in f:
                for group_name in self.group_info:
                    if not line.strip().startswith(group_name):
                        onef.write(line)
        onef.close()
        os.system("\mv %s  %s"%(new_file_name,self.group_file))

        return True



    def changge_groups(self):
        '''
        改变组和组成员信息的
        :return:
        '''
        pass




