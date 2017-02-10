#_*_coding:utf-8_*_
__author__ = 'Leo'


import os
import sys
path = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( path )

def LinuxSysInfo():
    from plugins.linux import sysinfo
    #print __file__
    return  sysinfo.collect()


def WindowsSysInfo():
    from plugins.windows import sysinfo as win_sysinfo
    return win_sysinfo.collect()
