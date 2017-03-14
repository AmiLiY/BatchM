# 主要是在指定主机上启动vnc,然后通过noVNC来代理VNC后在web界面上访问
from BatchM import settings
from django.core.cache import cache
import subprocess
import os
import random


class handle_novnc(object):
    '''
    处理novnc的方法集合
    '''
    def __init__(self,target_ip,vnc_port):
        '''
        :param target_ip:   需要链接的 IP
        :param vnc_port:     vnc's port
        :param cmd_path:
        '''
        self.target_ip = target_ip
        self.vnc_port = vnc_port
        self.host_ip = "%s:%s"%(self.target_ip,self.vnc_port)
        self.cmd_path = settings.novnc_cmd_path

    def make_port(self):
        '''
        产生一个随机数，用来做NOVNC的端口
        :return:
        '''
        if  cache.get(self.host_ip) is None:
            listen_port = random.randint(settings.novnc_begin_port, settings.novnc_end_port)
            cache.set(self.host_ip, listen_port)  # 定义一个缓存，用来把VNC端口和VNC主机IP绑定在一块的
        listen_port = cache.get(self.host_ip)
        return listen_port

    def create_dir(self):
        '''
        创建一个目录，专门存放启动vnc脚本的输出内容的
        :return:
        '''
        if settings.novnc_outputcontent_path:
            if not os.path.exists(settings.novnc_outputcontent_path):
                os.mkdir(settings.novnc_outputcontent_path)
        else:
            os.mkdir('/tmp/NoVnc')
        return True

    def StartTargetNoVnc(self):
        '''
        启动在指定IP的novnc,指定的主机为需要链接的VNC
        :return:
        '''
        self.listen_port = self.make_port()  # 返回一个NOVNC-port
        self.create_dir()
        cmd='%s --vnc %s --listen %d >%s/%s'%(self.cmd_path,self.host_ip,self.listen_port,
                                              settings.novnc_outputcontent_path,self.host_ip)
        exec_result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def StartVnc(self):
        '''
        启动在指定IP的vnc，不是novnc
        :return:
        '''


