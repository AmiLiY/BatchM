1. 该平台基于python3.5开发而来，django版本为1.10.
2. 平台依赖于第三方模块如pycurl,paramiko,docker,salt-api等模块.
3. 客户端采集信息的包目前是python2.6,python2.7版本,依赖于python的psutil模块，也依赖于lsb_release系统命令，同时需要saltstack-minion.在客户端执行的时候，首先会执行install_rpm.py这个文件
主要的功能是先进行命令或者模块的安装。且执行安装的系统命令都会在执行安装动作的时候打印出来，安装命令放在first_install 这个文件里面。


