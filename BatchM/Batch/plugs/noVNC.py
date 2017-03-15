# 主要是在指定主机上启动vnc,然后通过noVNC来代理VNC后在web界面上访问
from BatchM import settings
from django.core.cache import cache
from Batch.views import saltapi
from Batch.plugs import record_log
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
        :param cmd_path:     novnc的启动脚本
        '''
        self.target_ip = target_ip
        self.vnc_port = vnc_port
        self.host_ip = "%s:%s"%(self.target_ip,self.vnc_port)
        self.cmd_path = settings.novnc_cmd_path
        self.rlog = record_log.handler_log(settings.logfile_path)

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

    def StartTargetNoVnc(self,minion_name,action='start'):
        '''
        启动NOVNC,链接到指定的IP上，指定的主机为需要链接的VNC
        :return:
        '''
        self.listen_port = self.make_port()  # 返回一个NOVNC-port
        self.create_dir()
        if action=='start':
            if self.StartVnc(minion_name,func='service.start',args='vncserver'):   # 启动VNC服务
                cmd='%s --vnc %s --listen %d >%s/%s'%(self.cmd_path,self.host_ip,self.listen_port,
                                                      settings.novnc_outputcontent_path,self.host_ip)
                exec_result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # NOVNC开始代理目标IP的VNC
                grep_http_url_cmd = 'grep http %s/%s'%(settings.novnc_outputcontent_path,self.host_ip)
                novnc_http_url = subprocess.Popen(grep_http_url_cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.rlog.info("start_vnc: %s,NoVnc_url: %s,"%(self.host_ip,novnc_http_url))
                return novnc_http_url
            else:
                return False
        elif action=='stop':   # 停止VNC服务
            return self.StartVnc(minion_name, func='service.stop', args='vncserver')


    def StartVnc(self,minion_name,func,args):
        '''
        启动在指定IP的vnc，不是novnc
        :param minion_name : saltstack-minion id
        :param func: 执行哪个方法
        :param args: 执行哪个参数
        :return:
        '''
        try:
            saltapi.api_exec(target=minion_name, func=func, arg=args,arg_num=1)
        except BaseException as e:
            self.rlog.info('module_name: NoVnc ,error: %s,'%(e))
            return False

        return True



