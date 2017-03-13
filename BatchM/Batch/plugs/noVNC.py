# 主要是在指定主机上启动vnc,然后通过noVNC来代理VNC后在web界面上访问
from BatchM import settings
import  subprocess

__port_dict = {}   # 定义一个字典，用来把VNC端口和VNC主机IP绑定在一块的

class handle_novnc(object):
    '''
    处理novnc的方法集合
    '''
    def __init__(self,target_ip,vnc_port):
        '''
        :param target_ip:   需要链接的 IP
        :param vnc_port:     vnc's port
        '''
        self.target_ip = target_ip
        self.vnc_port = vnc_port
        self.host_ip = "%s:%s"%(self.target_ip,self.vnc_port)
        self.cmd_path = settings.novnc_cmd_path

    def StartTargetNoVnc(self):
        '''
        启动在指定IP的novnc,指定的主机为需要链接的VNC
        :return:
        '''


        exec_result = subprocess.getstatusoutput('%s --vnc %s --listen %d'%(self.cmd_path,self.host_ip,self.listen_port))

    def StartVnc(self):
        '''
        启动在指定IP的vnc，不是novnc
        :return:
        '''


