#_*_coding:utf8_*_
__author = "Leo"
import os
BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Params = {
    #"server": "192.168.1.10",
    #"server": "192.168.1.10",
    "server": "172.16.22.91",
    "port":8888,
    'request_timeout':30,
    "urls":{
          "asset_report_with_no_id":"/asset/report/asset_with_no_asset_id/",
          "asset_report":"/asset/report/",
          "report_system_status":"/asset/status/system/",
          "asset_salt_report":"/asset/saltstack_report/",
        },
    'asset_id': '%s/var/.asset_id' % BaseDir,
    'log_file': '%s/logs/run_log' % BaseDir,

    'auth':{
        'user':'ljf1992@163.com',
        'token': 'abc'
        },
}

