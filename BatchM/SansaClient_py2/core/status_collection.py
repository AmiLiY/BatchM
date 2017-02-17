#!/usr/bin/env python
'''
 this py_file use to collect system status each side,such as cpu_id , free , disk_max_useage.....
'''
import commands
import os
import json
from conf import settings
import datetime
import psutil


__status_info = {}



def load_asset_id():
        asset_id_file = settings.Params['asset_id']
        has_asset_id = False
        if os.path.isfile(asset_id_file):
            asset_id = open(asset_id_file).read().strip()
            if asset_id.isdigit():
                return  asset_id
            else:
                has_asset_id =  False
        else:
            has_asset_id =  False


def system_load():
    '''
    collect system status, how many user login the system ,how long is the system up ....
    :return:
    '''
    system_info_list=commands.getoutput("uptime").split(',')
    print(system_info_list)
    __status_info['up_time'] = system_info_list[0].split('up')[1]
    __status_info['login_users'] = system_info_list[2].strip()
    __status_info['load_average_fiveMin_ago'] = float(system_info_list[3].split(':')[1].strip())
    __status_info['hostname'] = commands.getoutput('hostname')
    # get these info by model psutil 
    __status_info['cpu_ioWait'] = psutil.cpu_times_percent().iowait
    __status_info['start_time'] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    mem = psutil.virtual_memory()
    __status_info['mem_use_precent'] = mem.used/float(mem.total)

    disk_max_usage_list = []
    for partition in psutil.disk_partitions():
        disk_max_usage_list.append(psutil.disk_usage(partition.mountpoint).percent)
    __status_info['disk_max_usage'] = float(max(disk_max_usage_list))
    cur_time=datetime.datetime.now()
    __status_info['update_time'] = cur_time.strftime('%Y-%m-%d %H:%M:%S.%u')
    __status_info['zombie_process'] = int(commands.getoutput("ps -ef |grep defunct |grep -v defunct|wc -l"))
    
    __status_info['asset_id'] = load_asset_id()
    print(__status_info)
    return __status_info

