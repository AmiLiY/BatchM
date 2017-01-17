# -*- coding: utf-8 -*-
import urllib.request
from urllib import error
import json
import http.client

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

class docker():
    '''
    操作docker容器的
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
                    status = json.loads(urllib.request.urlopen("http://%s:%s/%s/json?all=1"%(host,port,object_type)).read().decode())
                    print('status on select',status)
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



