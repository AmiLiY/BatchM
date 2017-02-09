# -*- coding: utf-8 -*-
import urllib.request
from urllib import error
import json
import http.client
import docker


class switch(object):
     def __init__(self, value):
         self.value = value
         self.fall = False

     def __iter__(self):
         """Return the match method once, then stop"""
         yield self.match
         raise StopIteration

     def match(self, *args):
         """Indicate whether or not to enter a case suite"""
         if self.fall or not args:
             return True
         elif self.value in args: # changed for v1.5, see below
             self.fall = True
             return True
         else:
           return False

class docker_operation():
    '''
    操作docker容器的class，自己写的方法来操作，通过RESTFUL url 来操作。包含的方法有容器查询，启动容器，停止容器，删除容器等信息
    '''
    def __init__(self):
        pass

    def control_containers(self,host,port,cmd="select",object_type='containers',ID="none"):
        '''
        因为http的方法不一样，所以这里就为每一个操作动作写了一个方法，
        :param host:  docker宿主机
        :param port:   宿主机链接端口
        :param containerID:    容器ID或者镜像ID
        :param cmd:   执行到动作 ,select(查询),start(启动容器),stop(停止容器),restart(重启容器),delete(删除容器或者镜像)
        :param object_type:    操作对象时容器还是镜像 ,type = containers,type = images
        :return:
        '''
        headers = {"Content-Type":"application/json"}
        conn = http.client.HTTPConnection(host,port=port)
        for case in switch(cmd):
            if case('select'):
                '''
                获取容器信息的，所有到容器,
                return结果： 如果有某台主机链接不上，那么在返回到集合里面第一个元素就是False，依照这个来判端是否链接 正确
                '''
                try:
                    if object_type == "containers":      # 获取对象是容器的话，那么就要把all设置为1，
                        isall = 1
                    elif object_type == 'images':    # 获取对象是容器的话，那么就要把all设置为0，避免获取到无用的镜像信息
                        isall = 0
                    status = json.loads(urllib.request.urlopen("http://%s:%s/%s/json?all=%d"%(host,port,object_type,isall)).read().decode())
                    print('status',status)
                except urllib.error.URLError:
                    return False,host,port
                finally:
                    conn.close()
                return status


            if case('start'):
                '''
                启动容器
                '''
                try:
                    print('start'.center(30,'-'))
                    url = "/%s/%s/start" %(object_type,ID)
                    conn.request('POST', url, '', headers)
                    response = conn.getresponse()
                except urllib.error.URLError:
                    return False,host,port,ID
                finally:
                    conn.close()

                return response.status,response.reason,ID


            if case('stop'):
                '''
                停止容器
                '''
                try:
                    print('stop'.center(30,'-'))
                    url = "/%s/%s/stop"  %(object_type,ID)
                    conn.request('POST', url, '', headers)
                    response = conn.getresponse()
                except urllib.error.URLError:
                    return False,host,port,ID,
                finally:
                    conn.close()
                # print('response.status,response.reason',response.status,response.reason)
                return response.status,response.reason,ID

            if case('restart'):
                '''
                重启容器
                '''
                try:
                    url = "/%s/%s/restart" %(object_type,ID)
                    conn.request('POST', url, '', headers)
                    response = conn.getresponse()
                except urllib.error.URLError:
                    return False,host,port,ID
                finally:
                    conn.close()
                return response.status,response.reason,ID

            if case('delete'):
                '''
                删除容器
                '''
                try:
                    url = "/%s/%s" %(object_type,ID)
                    conn.request('DELETE', url, '', headers)
                    response = conn.getresponse()
                except urllib.error.URLError:
                    return False,host,port,ID
                finally:
                    conn.close()
                print(response.reason)
                return response.status,response.reason,ID
            if case('top'):
                '''
                获取容器内部运行的进程
                如果容器没有运行，那么就会直接报错（HTTP 500错误），容器ID写错，那么就是HTTP 404错误
                '''
                try:
                    print('top'.center(20,'*'))
                    print(json.loads(urllib.request.urlopen("http://%s:%s/%s/%s/top?ps_args=aux"%(host,port,object_type,ID)).read().decode()))
                    top_result = json.loads(urllib.request.urlopen("http://%s:%s/%s/%s/top?ps_args=aux"%(host,port,object_type,ID)).read().decode())
                    print('topping',top_result)
                except urllib.error.URLError:
                    return False,host,port,ID
                finally:
                    conn.close()

                return top_result

            if case():
                return False



class docker_operation2(object):
    '''
    利用docker模块来创建容器,在容器中执行命令的方法
    '''
    def __init__(self,host_port,version):
        #def __init__(self,**kwargs):
        # c = docker.DockerClient(base_url='http://172.16.160.192:4343',version='auto')
        # hehe = c.containers.create(**kwargs)
        # print(hehe)
        self.host_port = host_port
        self.version = version
        self.cdocker = docker.DockerClient(base_url='http://%s'%(self.host_port),version=version)

    def create(self,**kwargs):
        '''
        创建容器的方法
        :param kwargs:
        :return:
        '''
        try:
            result = self.cdocker.containers.run(**kwargs,tty=True)
        except (docker.errors.ImageNotFound,docker.errors.APIError) as e:
            return False,self.host_port,e.explanation
        return result

    def exec_cmd(self,Container_id,Command):
        '''
        在容器中执行命令的方法
        :param Container_id: 容器ID或者名字
        :param Command:    要在容器中执行的command
        :return:  返回执行结果,如果报错那么就返回 False,容器ID和报错信息
        '''
        c = docker.DockerClient(base_url='http://%s' % (self.host_port), version=self.version)
        try:
            exec_instance = c.containers.get(Container_id)
            exec_result = exec_instance.exec_run(cmd=Command)
            print('exec_result.decode',exec_result.decode())
        except (docker.errors.NotFound, docker.errors.APIError) as e:
            print(e)
            return False,Container_id, e.explanation

        return exec_result.decode()



def hehe(**kwargs):
    try:
        c = docker.DockerClient(base_url='http://172.16.160.192:4343',version='auto')
        result = c.containers.run(**kwargs,tty=True)
    except (docker.errors.ImageNotFound, docker.errors.APIError) as e:
        return e
    return result


def exec(name,command):
    try:
        c = docker.DockerClient(base_url='http://172.16.160.192:4343',version='auto')
        result = c.containers.get(name)
        exec_result = result.exec_run(cmd=command)
    except (docker.errors.NotFound,docker.errors.APIError) as e:
        print(e)
        return name,e.explanation

    return exec_result.decode()


# a=docker_operation2('172.16.160.192:4343',version='auto')
# result = a.exec_cmd('7149cae9338e','df -hT')
# print(result)



#a=exec('7149cae9338e','df -hT')
#print(a)
# a={'hostname': 't8', 'dns': ['8.8.8.8', '1.1.1.1', ''], 'mem_limit ': '64M', 'image': 'httpd',
#     'cpu_group': 60000, 'cpu_shares ': 600,
#    'name': 't6', 'cpu_period': 1000000, 'command': '/bin/bash', 'detach': 'False'}
# c=hehe(**a)
# print(dir(c))
# print(c.response,c.explanation)
# a=c.explanation.decode()
# print(a)


# {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
#  '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}

# a={'image': 'httpd_sshd', 'detach':True,'cpu_period': 1000000, 'cpu_group': 50000, 'command': '/bin/bash',
#   'cpu_shares ': 600, 'mem_limit ': '32M', 'name': 't13', 'dns': ['114.114.114.114', '8.8.8.8', ''],
#    'ports':{'22/tcp':('0.0.0.0',1125)},'volumes':{'/mnt/':{'bind':'/temp','mode':'rw'}}}
# # a={'image': 'httpd', 'command': '/bin/bash','name': 't16',
# #    'volumes':{'/mnt':{'bind':'/home/mfs/','mode':'rw'},}}
# c=hehe(**a)
# print(type(c),dir(c))
# c.start()

