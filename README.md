# BatchM
#### 平台简介：
1. 该平台目前准备开发的功能是saltstack-web管理（包含WEB-vnc的功能），docker-web管理，服务器信息录入，变更工单申请，外挂一个ELK的连接。
2. 目前已开发完成的功能docker-web管理，服务器信息录入，变更工单申请，saltstack-web管理（包含WEB-vnc的功能）。
3. 该平台基于python3.5开发而来，django版本为1.10，平台依赖于第三方模块如pycurl,paramiko,docker,salt-api等模块.
4. 客户端采集信息的包目前是python2.6,python2.7版本,依赖于python的psutil模块，也依赖于lsb_release系统命令，同时需要saltstack-minion.在客户端执行的时候，首先会执行install_rpm.py这个文件
主要的功能是先进行命令或者模块的安装。且执行安装的系统命令都会在执行安装动作的时候打印出来，安装命令放在first_install 这个文件里面。

客户端执行的命令如下:  
```
[root@lvsmaster191 ~]# python SansaClient_py2/bin/NedStark.py

        CDSS(collect_data_by_saltstack)           通过saltstack来收集服务器信息后展现且汇报到服务器端
        run_forever    进入后台运行，deamon模式
        report_sys_status     汇报服务器状态信息

[root@lvsmaster191 ~]# python SansaClient_py2/bin/NedStark.py CDSS
```
 请注意：我们在执行的时候，一定要是在这个客户端包的最外面执行，不然会提示路径出错。

 那么客户端需要配置下汇报数据的服务器地址，配置文件如下:  
 ```
 [root@lvsmaster191 ~]# vim SansaClient_py2/conf/settings.py
 Params = {
    "server": "172.16.22.81",   # 这一行表示服务器地址，用引号引起来
    "port":8888,     # 这一行表示端口，必须是数字，不要用引号引起来
    'request_timeout':30,    # 表示超时时间，必须是数字，不要用引号引起来
    其他的配置保持默认，不要更改
}
```
然后我们再看看执行命令前需要执行的安装命令，命令存放在var/first_install里面：
```
wget -Onc /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-6.repo     # 下载一个repo，确保能够安装下面的包，请下载对应当前系统版本的repo
yum -y install salt-minion
yum -y install '*/lsb_release'
yum -y install python-pip python-devel && pip install psutil
```
在第一次执行倘若```python SansaClient_py2/bin/NedStark.py CDSS```的时候，首先会进行安装包，安装成功后会生成一个配置文件在var/installed,下次再次执行CDSS的时候，如果发现有 installed，那么就不在进行安装包了。
安装的时间可能比较长，请耐心等待。


在第一次汇报资产数据的时候，需要等待管理员的批准，等待批准后，第二次汇报资产数据后就会拿到资产ID的值.这个值会放在var/.asset_id,有这个ID后，每次都会汇报数据都会带上这个ID。
如果出现这样的报错：
```
Cannot find a asset object in DB by using asset id [35] and SN [VMware-42 10 36 c3 b5 7f ae 63-a4 bd ce bc 48 7e d7 8c]
```
那么就说明数据库里面删除来这条资产记录，我们这个时候就需要把当前var/.asset_id给删除,然后重新汇报资产信息既可。

5. 唯一不足的地方感觉是前端页面太丑陋了，因为当初用的模版丑陋，没有办法了，只能先这样了，因为最近跳槽全心全意做自动化开发了，刚入职有点小忙，所以这个项目目前需要暂停一段时间了

#### 平台展示图如下：  
后续补上
