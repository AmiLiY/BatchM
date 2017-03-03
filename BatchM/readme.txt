1. 该平台基于python3.5开发而来，django版本为1.10.
2. 平台依赖于第三方模块如pycurl,paramiko,docker,salt-api等模块.
3. 客户端采集信息的包目前是python2.6,python2.7版本,依赖于python的psutil模块，也依赖于lsb_release系统命令，同时需要saltstack-minion.在客户端执行的时候，首先会执行install_rpm.py这个文件
主要的功能是先进行命令或者模块的安装。且执行安装的系统命令都会在执行安装动作的时候打印出来，安装命令放在first_install 这个文件里面。

客户端执行的命令如下:
[root@lvsmaster191 ~]# python SansaClient_py2/bin/NedStark.py

        CDSS(collect_data_by_saltstack)           通过saltstack来收集服务器信息后展现且汇报到服务器端
        run_forever    进入后台运行，deamon模式
        report_sys_status     汇报服务器状态信息

[root@lvsmaster191 ~]# python SansaClient_py2/bin/NedStark.py CDSS

 请注意：我们在执行的时候，一定要是在这个客户端包的最外面执行，不然会提示路径出错。
 
 那么客户端需要配置下汇报数据的服务器地址，配置文件如下:
 [root@lvsmaster191 ~]# vim SansaClient_py2/conf/settings.py
 Params = {
    "server": "172.16.22.81",   # 这一行表示服务器地址，用引号引起来
    "port":8888,     # 这一行表示端口，必须是数字，不要用引号引起来
    'request_timeout':30,    # 表示超时时间，必须是数字，不要用引号引起来
    其他的配置保持默认，不要更改
}


