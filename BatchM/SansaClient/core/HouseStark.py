#_*_coding:utf-8_*_
__author__ = 'Leo'

from . import info_collection
from conf import settings
from . import status_collection
import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse,sys,os,json,datetime
from . import api_token
import subprocess


class ArgvHandler(object):
    def __init__(self,argv_list):
        self.argvs = argv_list
        self.parse_argv()


    def parse_argv(self):
        if len(self.argvs) >1:
            if hasattr(self,self.argvs[1]):
                func = getattr(self,self.argvs[1])
                func()
            else:
                self.help_msg()
        else:
            self.help_msg()
    def help_msg(self):
        msg = '''
        collect_data   收集服务器信息后展现，并不汇报到服务器端（通过自己写的代码来收集信息）
        CDSS(collect_data_by_saltstack)           收集服务器信息后展现,通过saltstack来收集数据
        run_forever    进入后台运行，deamon模式
        get_asset_id   获取资产ID
        report_asset   采集资产信息后汇报，不会展现
        report_sys_status     汇报服务器状态信息
        '''
        print(msg)

    def collect_data(self):
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()
        print(asset_data)
    def run_forever(self):
        pass
 
    def report_sys_status(self):
        '''
           report system basic status to CMDB  server ,these datat include sys load average,disk max usage and so on
        '''
       	status_result = status_collection.system_load()
        self.__submit_data('report_system_status',status_result,'post')
    
    def CDSS(self):
        '''
            collect machine's info by saltstack....
        '''
        try:
            import salt.config
            import salt.loader
        except ImportError as e:
            print("\033[32m Installing saltstack-minion \n\n %s \033[30m"%e)
            result = subprocess.getstatusoutput("yum -y install saltstack-minion saltstack")
            if result[0] == 0:
                import salt.config
                import salt.loader
            else:
                exit("\033[31m I'm Sorry! saltstack installed was false!! \n\t please you install it by yourself!! \033[0m")
        minion_conf = salt.config.minion_config('/etc/salt/minion')
        salt_minion_id = minion_conf['id']
        grains = salt.loader.grains(minion_conf)
        asset_id = self.load_asset_id(grains["serialnumber"])
        grains = self.__saltstack_collect_handler(grains)
        grains['salt_minion_id'] = minion_conf['id']
        if asset_id: # means this is not first time to report asset
            grains['asset_id'] = asset_id
            post_url = "asset_salt_report"
        else:
            grains['asset_id'] = None
            post_url = "asset_report_with_no_id"
        data = {"asset_data": json.dumps(grains)}
        print(('data ===>',data))
        
        response = self.__submit_data(post_url,data,'post') # means post data to server
        if "asset_id" in response:
            self.__update_asset_id(response["asset_id"])
        self.log_record(response)
        
   
    def __saltstack_collect_handler(self,data):
        '''
           it will process these data by saltstack collect!!
        '''
        data_processed = {}
        no_need_item = ('wake_up_type','uuid','os_release','os_distribution',
                        'nic','cpu_count','ram','cpu_model','manufactory',
                        'asset_type','physical_disk_driver','sn','os_release',
                        'os_type','cpu_core_count','model','ram_size')
        # sn
        data_processed['sn'] = data['serialnumber']
        data_processed['os_release'] = "%s %s [%s]-%s" %(data['os'],data['osrelease'],data['lsb_distrib_codename'],data['kernelrelease'])
        data_processed['os_type'] = data['kernel']
        data_processed['os_distribution'] = data['os']
        nic_info = []
        i=0
        # get ipaddress each NIC
        for k,v in list(data['ip4_interfaces'].items()):
            if k != "lo":
                nic_info.append({})
                nic_info[i]['name'] = k
                if len(v) != 0:
                    nic_info[i]['ipaddress'] = v[0]
                nic_info[i]['model'] = 'unknow'
                nic_info[i]['network'] = 'unknow'
                nic_info[i]['netmask'] = 'unknow'
                nic_info[i]['bonding'] = 'unknow'
                i+=1
        # get macaddress each NIC
        for k,v in list(data['hwaddr_interfaces'].items()):
            for i in nic_info:
                if k in list(i.values()):
                    nic_info[nic_info.index(i)]['macaddress'] = v
        from plugins.linux.sysinfo import DiskPlugin,raminfo   # only linux system can use it!!
        dp = DiskPlugin()    # make it to a instance
        disk_info = dp.linux()    # get disk info by linux function!
        data_processed['physical_disk_driver']  = disk_info['physical_disk_driver']
        data_processed['nic'] = nic_info
        data_processed['cpu_count'] = data['num_cpus']
        ram_info = raminfo()
        data_processed['ram'] = ram_info['ram']
        data_processed['cpu_model'] = data['cpu_model']
        data_processed['manufactory'] = data['manufacturer']
        data_processed['cpu_core_count'] = data['num_cpus']
        data_processed['model'] = data['productname']
        data_processed['ram_size'] = data['mem_total']
        #data_processed['cpu_model'] = data['cpu_model']
        data_processed['asset_type'] = "server"
        return data_processed
        
    def __attach_token(self,url_str):
        '''generate md5 by token_id and username,and attach it on the url request'''
        user = settings.Params['auth']['user']
        token_id = settings.Params['auth']['token']

        md5_token,timestamp = api_token.get_token(user,token_id)
        url_arg_str = "user=%s&timestamp=%s&token=%s" %(user,timestamp,md5_token)
        if "?" in url_str:#already has arg
            new_url = url_str + "&" + url_arg_str
        else:
            new_url = url_str + "?" + url_arg_str
        return  new_url
        #print(url_arg_str)

    def __submit_data(self,action_type,data,method):
        '''
        action_type: means what get from setttings
        method : get or post 
        data : need to put server and this data's type must be json....
        '''
        if action_type in settings.Params['urls']:
            if type(settings.Params['port']) is int:
                url = "http://%s:%s%s" %(settings.Params['server'],settings.Params['port'],settings.Params['urls'][action_type])
            else:
                url = "http://%s%s" %(settings.Params['server'],settings.Params['urls'][action_type])

            url =  self.__attach_token(url)
            print(('Connecting [%s], it may take a minute' % url ))
            if method == "get":    #
                args = ""
                for k,v in list(data.items()):
                    args += "&%s=%s" %(k,v)
                args = args[1:]
                url_with_args = "%s?%s" %(url,args)
                try:
                    req = urllib.request.Request(url_with_args)
                    req_data = urllib.request.urlopen(req,timeout=settings.Params['request_timeout'])
                    callback = req_data.read()
                    print(("-->server response:",callback))
                    return callback
                except urllib.error.URLError as e:
                    sys.exit("\033[31;1m%s\033[0m"%e)
            elif method == "post":   # post  data of asset to the CMDB server
                #try:
                    data_encode = urllib.parse.urlencode(data)
                    req = urllib.request.Request(url=url,data=data_encode.encode())   # python3 必须把data_encode给encode下
                    print('req',type(req.data),req.data)
                    res_data = urllib.request.urlopen(req,timeout=settings.Params['request_timeout'])
                    callback = res_data.read()
                    callback = json.loads(callback.decode())
                    print(("\033[31;1m[%s]:[%s]\033[0m response:\n%s" %(method,url,callback) ))
                    return callback
                #except Exception as e:
                    #sys.exit("\033[3;1m%s\033[0m"%e)
        else:
            raise KeyError



    #def __get_asset_id_by_sn(self,sn):
    #    return  self.__submit_data("get_asset_id_by_sn",{"sn":sn},"get")
    def load_asset_id(self,sn=None):
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

    def __update_asset_id(self,new_asset_id):
        asset_id_file = settings.Params['asset_id']
        f = open(asset_id_file,"wb")
        f.write(str(new_asset_id))
        f.close()


    def report_asset(self):
        '''
            report machine's info to the server peer
        '''
        obj = info_collection.InfoCollection()
        asset_data = obj.collect() #collected server info data
        asset_id = self.load_asset_id(asset_data["sn"])
        if asset_id: #reported to server before
            asset_data["asset_id"] = asset_id
            post_url = "asset_report"
        else:#first time report to server
            '''report to another url,this will put the asset into approval waiting zone, when the asset is approved ,this request returns
            asset's ID'''

            asset_data["asset_id"] = None
            post_url = "asset_report_with_no_id"

        print(asset_data)
        #data = {"asset_data": json.dumps(asset_data)}
        asset_data = {'asset_data':asset_data}
        response = self.__submit_data(post_url,asset_data,method="post")
        if "asset_id" in response:
            self.__update_asset_id(response["asset_id"])

        self.log_record(response)

    def log_record(self,log,action_type=None):
        f = open(settings.Params["log_file"],"a")
        if log is str:
            pass
        if type(log) is dict:

            if "info" in log:
                for msg in log["info"]:
                    log_format = "%s\tINFO\t%s\n" %(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),msg)
                    #print msg
                    f.write(log_format)
            if "error" in log:
                for msg in log["error"]:
                    log_format = "%s\tERROR\t%s\n" %(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),msg)
                    f.write(log_format)
            if "warning" in log:
                for msg in log["warning"]:
                    log_format = "%s\tWARNING\t%s\n" %(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),msg)
                    f.write(log_format)

        f.close()
