# 主要是在指定主机上启动vnc,然后通过noVNC来代理VNC后在web界面上访问
import  subprocess


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


    def StartNoVnc(self):
        '''
        启动在本机的novnc,指定的主机为需要链接的VNC
        :return:
        '''
        pass

    def StartTargetVnc(self):
        '''
        启动指定IP的vnc,
        :return:
        '''
        pass
