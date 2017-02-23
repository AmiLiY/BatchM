from django.db import models
import time
from django.contrib.auth.models import User

from Batch.customize_auth_model import MyUser

# Create your models here.   \
# 最新创建到数据库表都在最前面


class DockerOfHost(models.Model):
    '''
    用来记录docker宿主机信息到
    '''

    host_ip = models.CharField(u'Docker宿主机IP',max_length=250,unique=True)

    def __str__(self):
        return self.host_ip

    class Meta:
        verbose_name = "Docker宿主机IP"
        verbose_name_plural = "Docker宿主机IP"


# class ModelOfContainer(models.Model):
#     '''
#     存容器配置模板信息的
#     '''
#     Host_ip = models.ManyToManyField(DockerOfHost,verbose_name='Docker宿主机IP')
#     Container_name = models.CharField(u'容器名字', max_length=300, null=True, blank=True)
#     Container_image = models.CharField(u'容器镜像', max_length=300)
#     Command = models.CharField(u'运行的命令', max_length=300, null=True, blank=True)



class DockerOfImages(models.Model):
    '''
    用来记录docker宿主机上镜像到
    '''
    Host_ip = models.ManyToManyField(DockerOfHost,verbose_name='Docker宿主机IP')
    Image_id = models.CharField(u'镜像ID',max_length=300,)
    Parent_id = models.CharField(u'父级镜像ID',max_length=300,default=None)
    Repo_tags = models.CharField(u'仓库备注',max_length=300,default=None)
    Repo_digests = models.CharField(u'仓库摘要',max_length=300,default=None)
    Created = models.CharField(u'创建时间', max_length=200,default=None)
    Image_size = models.CharField(u'镜像实际大小',max_length=300,default=None)
    Virtual_size = models.CharField(u'镜像虚拟大小',max_length=300)
    Labels = models.CharField(u'标签',max_length=300,default=None)
    update_time = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return "ID:%s,Tags:%s"%(self.Image_id,self.Repo_tags)

    class Meta:
        verbose_name = 'Docker镜像'
        verbose_name_plural = 'Docker镜像'



class DockerContainers(models.Model):
    '''
    用来记录docker容器信息的
    '''
    Real_host_ip = models.ForeignKey(DockerOfHost,verbose_name='Docker宿主机IP')
    Container_id = models.CharField(u'容器ID',max_length=400,primary_key=True,unique=True)
    Container_name = models.CharField(u'容器名字',max_length=300,null=True,blank=True)
    Container_image = models.CharField(u'容器镜像',max_length=300)
    Container_Image_id = models.CharField(u'镜像ID',max_length=500,null=True,blank=True)
    Command = models.CharField(u'运行的命令',max_length=300,null=True,blank=True)
    Created = models.CharField(u'创建时间',max_length=200)
    Status = models.CharField(u'运行状态',max_length=100,null=True,blank=True)
    Port = models.CharField(u'容器端口',max_length=1000,null=True,blank=True)
    SizeRw = models.IntegerField(null=True,blank=True)
    SizeRootFs = models.IntegerField(null=True,blank=True)
    Host_config = models.CharField(u'主机配置',max_length=1024,null=True,blank=True)
    Network_settings = models.CharField(u'网络配置',max_length=3000,null=True,blank=True)
    Mounts = models.CharField(u'挂载目录',max_length=1024,null=True,blank=True)
    Record_time = models.DateTimeField(u'数据更新时间',auto_now=True)

    def __str__(self):
        return "%s:%s"%(self.Real_host_ip,self.Container_id)

    class Meta:
        verbose_name = "Docker容器信息"
        verbose_name_plural = "Docker容器信息"


class TypeOfApp(models.Model):
    '''
    记录app信息到
    '''
    app_name = models.CharField(u'应用名字',max_length=255)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    def __str__(self):
        return self.app_name

    class Meta:
        verbose_name = '应用类型'
        verbose_name_plural =  '应用类型'



class TypeOfProject(models.Model):
    '''
    记录项目到表
    '''
    name_of_project = models.CharField(u'项目名字',max_length=255)
    include_apps = models.ManyToManyField(TypeOfApp)
    update_time = models.DateTimeField(u'更新时间',auto_now=True)

    def __str__(self):
        return self.name_of_project

    class Meta:
        verbose_name = "项目列表"
        verbose_name_plural = "项目列表"

class WorkOrderOfUpdate(models.Model):
    '''
    记录代码更新到信息
    '''
    OrderId = models.CharField(u'工单ID',max_length=128,primary_key=True,default=time.strftime("%Y%m%d%H%M%S", time.localtime()))
    username = models.CharField(u'申请人',max_length=255)
    flow_project = models.ForeignKey(TypeOfProject,verbose_name=u'归属项目')
    flow_app = models.ForeignKey(TypeOfApp,verbose_name=u'归属应用')
    target_host = models.CharField(u'目标主机IP/域名',max_length=255)
    code_source = models.CharField(u'源码来源',max_length=500,blank=True,null=True)
    configfile_path = models.CharField(u'配置文件路径', max_length=255,blank=True,null=True)
    configfile_content = models.CharField(u'修改配置文件内容',max_length=10240,null=True,blank=True)
    sql_command = models.CharField(u'sql语句',max_length=10240,null=True,blank=True)
    crond_task = models.CharField(u'定时任务',max_length=10240,null=True,blank=True)
    system_env_change = models.CharField(u'系统环境变更',null=True,blank=True,max_length=10240)
    update_of_reason = models.CharField(u'更新原因',null=True,blank=True,max_length=10240)
    email_issend = models.BooleanField(u'提醒邮件是否已经发送')
    tags = models.CharField(null=True,blank=True,max_length=1020)
    accessory_path = models.CharField(u'附件路径',null=True,blank=True,max_length=250)
    update_time = models.DateTimeField(u'创建时间',auto_now_add=True)

    def __str__(self):
        return self.OrderId

    class Meta:
        verbose_name = "更新工单记录"
        verbose_name_plural = "更新工单记录"


# class WorkOrderOfConfigfile(models.Model):
#     '''
#     记录配置文件更改到工单
#     '''
#     OrderId = models.CharField(u'工单ID',max_length=128,primary_key=True,default=time.strftime("%Y%m%d%H%M%S", time.localtime()))
#     username = models.CharField(u'申请人', max_length=255)
#     target_host = models.CharField(u'目标主机IP/域名',max_length=255)
#     flow_app = models.ForeignKey(TypeOfApp,verbose_name=u'归属应用',default="1")
#
#     content = models.CharField(u'修改内容',max_length=10240)
#     email_issend = models.BooleanField()
#     tags = models.CharField(null=True,blank=True,max_length=1020)
#     update_time = models.DateTimeField(u'创建时间',auto_now_add=True)
#
#     def __str__(self):
#         return self.OrderId
#
#     class Meta:
#         verbose_name = "配置文件更改工单记录"
#         verbose_name_plural = "配置文件更改工单记录"

class SaltstackMinions(models.Model):
    '''
    记录saltstack minion信息
    '''
    ip = models.GenericIPAddressField(u'IP')
    hostname = models.CharField(u'Minion的主机名',max_length=255)
    tags = models.CharField(max_length=2048)

    def __str__(self):
        return self.ip,self.hostname

    class Meta:
        verbose_name = "saltstack minion信息"
        verbose_name_plural = "saltstack minion信息"

class SaltstackGroup (models.Model):
    '''
    记录saltstack组信息
    '''
    group_name = models.CharField(u'组名',max_length=255)
    group_number = models.ManyToManyField(SaltstackMinions,verbose_name='组成员',null=True,blank=True)
    whether_create = models.IntegerField(u'是否创建了组在saltstack配置文件里',default=0) #0：没有创建，1：表示创建了
    tags = models.CharField(max_length=2048)


    def __str__(self):
        return self.group_name,self.group_number

    class Meta:
        verbose_name = "saltstack组信息"
        verbose_name_plural = "saltstack组信息"

class SaltstackMinionsStatus(models.Model):
    '''
    记录saltstack Minions 的状态信息,存放历史状态记录的。
    '''
    asset = models.ForeignKey('Asset',verbose_name='资产编号',default=1)
    ipaddress = models.GenericIPAddressField(u'IP')
    hostname = models.CharField(u'主机名',max_length=128)
    zombie_process =  models.IntegerField(u'僵死进程数量')
    mem_use_precent = models.FloatField(u'内存使用率',max_length=4)
    up_time = models.CharField(u'系统运行时间',max_length=128)
    load_average_fiveMin_ago = models.FloatField(u'系统五分钟以内的负载')
    cpu_ioWait = models.FloatField(u'CPU IoWait')
    login_users = models.CharField(u'登陆用户数量',max_length=128)
    disk_max_usage = models.FloatField(u'磁盘最大使用率')
    update_time = models.DateTimeField(u'数据更新时间')
    poweron_time = models.DateTimeField(u'系统开机时间',)

    def __str__(self):
        return self.hostname

    class Meta:
        verbose_name = '系统5分钟内运行状态'
        verbose_name_plural =  '系统5分钟内运行状态'


class NewSaltstackMinionsStatus(models.Model):
    '''
    记录saltstack Minions 的状态信息,存放最新的状态记录的。
    '''
    asset = models.ForeignKey('Asset',verbose_name='资产编号',default=1)
    ipaddress = models.GenericIPAddressField(u'IP')
    hostname = models.CharField(u'主机名',max_length=128)
    zombie_process =  models.IntegerField(u'僵死进程数量')
    mem_use_precent = models.FloatField(u'内存使用率',max_length=4)
    up_time = models.CharField(u'系统运行时间',max_length=128)
    load_average_fiveMin_ago = models.FloatField(u'系统五分钟以内的负载')
    cpu_ioWait = models.FloatField(u'CPU IoWait')
    login_users = models.CharField(u'登陆用户数量',max_length=128)
    disk_max_usage = models.FloatField(u'磁盘最大使用率')
    update_time = models.DateTimeField(u'数据更新时间')
    poweron_time = models.DateTimeField(u'系统开机时间',)

    def __str__(self):
        return self.ipaddress

    class Meta:
        verbose_name = '系统状态'
        verbose_name_plural =  '系统状态'


# class ApproveHosts(models.Model):
#     '''
#     how many hosts was approved
#     '''
#     minion_name = models.CharField(u'saltstack_minion_name',max_length=4096)
#     how_many = models.IntegerField()
#     update_time = models.DateTimeField(u'批准时间',auto_now=True)
#
#     def __str__(self):
#         return self.minion_name
#
#     class Meta:
#         verbose_name = '批准主机的数量'
#         verbose_name_plural = '批准主机的数量'



############ 以下就是关于资产的数据库  #####

class Asset(models.Model):
    asset_type_choices = (
        ('server', u'服务器'),
        ('switch', u'交换机'),
        ('router', u'路由器'),
        ('firewall', u'防火墙'),
        ('storage', u'存储设备'),
        ('NLB', u'NetScaler'),
        ('wireless', u'无线AP'),
        ('software', u'软件资产'),
        ('others', u'其它类'),
    )
    asset_type = models.CharField(choices=asset_type_choices,max_length=64, default='server')
    name = models.CharField(max_length=64,unique=True)
    sn = models.CharField(u'资产SN号',max_length=128, unique=True)
    manufactory = models.ForeignKey('Manufactory',verbose_name=u'制造商',null=True, blank=True)
    # 针对IMPI这样的管理IP
    management_ip = models.GenericIPAddressField(u'管理IP',blank=True,null=True)

    # 签合同时间和交易时间可能是不同的一天。
    contract = models.ForeignKey('Contract', verbose_name=u'合同',null=True, blank=True)
    # 交易时间
    trade_date = models.DateField(u'购买时间',null=True, blank=True)
    expire_date = models.DateField(u'过保修期',null=True, blank=True)
    price = models.FloatField(u'价格',null=True, blank=True)
    # 业务线，
    business_unit = models.ForeignKey('BusinessUnit', verbose_name=u'所属业务线',null=True, blank=True)
    #　给服务器打上标签。
    tags = models.ManyToManyField('Tag' ,blank=True)
    admin = models.ForeignKey(MyUser, verbose_name=u'资产管理员',null=True, blank=True)
    idc = models.ForeignKey('IDC', verbose_name=u'IDC机房',null=True, blank=True)

    memo = models.TextField(u'备注', null=True, blank=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True, auto_now=True)
    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = "资产总表"
    def __str__(self):
        return 'id:%s name:%s'  %(self.id,self.name )

class Server(models.Model):
    asset = models.OneToOneField('Asset')
    created_by_choices = (
        ('auto','Auto'),
        ('manual','Manual'),
    )
    created_by = models.CharField(choices=created_by_choices,max_length=32,default='auto') #auto: auto created,   manual:created manually
    hosted_on = models.ForeignKey('self',related_name='hosted_on_server',blank=True,null=True) #for vitural server
    model = models.CharField(u'型号',max_length=128,null=True, blank=True )
    # 若有多个CPU，型号应该都是一致的，故没做ForeignKey
    raid_type = models.CharField(u'raid类型',max_length=512, blank=True,null=True)
    os_type  = models.CharField(u'操作系统类型',max_length=64, blank=True,null=True)
    os_distribution =models.CharField(u'发型版本',max_length=64, blank=True,null=True)
    os_release  = models.CharField(u'操作系统版本',max_length=64, blank=True,null=True)
    salt_minion_id = models.CharField(u'salt minion id',max_length=254,blank=True,null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True,null=True)
    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = "服务器"
        #together = ["sn", "asset"]

    def __str__(self):
        return '%s sn:%s' %(self.asset.name,self.asset.sn)


class NetworkDevice(models.Model):
    asset = models.OneToOneField('Asset')
    vlan_ip = models.GenericIPAddressField(u'VlanIP',blank=True,null=True)
    intranet_ip = models.GenericIPAddressField(u'内网IP',blank=True,null=True)
    sn = models.CharField(u'SN号',max_length=128,unique=True)
    model = models.CharField(u'型号',max_length=128,null=True, blank=True )
    firmware = models.ForeignKey('Software',blank=True,null=True)
    port_num = models.SmallIntegerField(u'端口个数',null=True, blank=True )
    device_detail = models.TextField(u'设置详细配置',null=True, blank=True )
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True,null=True)

    class Meta:
        verbose_name = '网络设备'
        verbose_name_plural = "网络设备"

class Software(models.Model):
    os_types_choice = (
        ('linux', 'Linux'),
        ('windows', 'Windows'),
        ('network_firmware', 'Network Firmware'),
        ('software', 'Softwares'),
    )
    os_distribution_choices = (('windows','Windows'),
                               ('centos','CentOS'),
                               ('ubuntu', 'Ubuntu'))
    type = models.CharField(u'系统类型', choices=os_types_choice, max_length=64,help_text=u'eg. GNU/Linux',default=1)
    distribution = models.CharField(u'发型版本', choices=os_distribution_choices,max_length=32,default='windows')
    version = models.CharField(u'软件/系统版本', max_length=64, help_text=u'eg. CentOS release 6.5 (Final)', unique=True)
    language_choices = (('cn',u'中文'),
                        ('en',u'英文'))
    language = models.CharField(u'系统语言',choices = language_choices, default='cn',max_length=32)

    def __str__(self):
        return self.version
    class Meta:
        verbose_name = '软件/系统'
        verbose_name_plural = "软件/系统"


class CPU(models.Model):
    asset = models.OneToOneField('Asset')
    cpu_model = models.CharField(u'CPU型号', max_length=128,blank=True)
    cpu_count = models.SmallIntegerField(u'物理cpu个数')
    cpu_core_count = models.SmallIntegerField(u'cpu核数')
    memo = models.TextField(u'备注', null=True,blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True,null=True)
    class Meta:
        verbose_name = 'CPU部件'
        verbose_name_plural = "CPU部件"
    def __str__(self):
        return self.cpu_model


class RAM(models.Model):
    asset = models.ForeignKey('Asset')
    sn = models.CharField(u'SN号', max_length=128, blank=True,null=True)
    manufactory = models.CharField(u'制造商', max_length=64,blank=True,null=True)
    model =  models.CharField(u'内存型号', max_length=128)
    slot = models.CharField(u'插槽', max_length=64)
    capacity = models.IntegerField(u'内存大小(MB)')
    ram_size_in_total = models.IntegerField(u'内存总量', null=True, blank=True)
    memo = models.CharField(u'备注',max_length=128, blank=True,null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return '%s:%s:%s' % (self.asset_id,self.slot,self.capacity)
    class Meta:
        verbose_name = 'RAM'
        verbose_name_plural = "RAM"
        # 联合几个字段作为主键。
        unique_together = ("asset", "slot")
    auto_create_fields = ['sn','slot','model','capacity']


# class RamDiskSize(models.Model):
#     '''
#     存放每台服务器的内存的最大值
#     '''
#     asset = models.ForeignKey('Asset')
#     ram_size_in_total = models.CharField(u'内存总量',null=True,blank=True)
#     disk_size_in_total = models.CharField(u'磁盘总量',null=True,blank=True)
#
#     def __str__(self):
#         return self.asset_id,self.ram_size_in_total,self.disk_size_in_total
#
#     class Meta:
#         verbose_name = u'每台服务器内存与磁盘总量'
#         verbose_name_plural = u'每台服务器内存与磁盘总量'

class Disk(models.Model):
    asset = models.ForeignKey('Asset')
    sn = models.CharField(u'SN号', max_length=128, blank=True,null=True)
    slot = models.CharField(u'插槽位',max_length=64)
    manufactory = models.CharField(u'制造商', max_length=64,blank=True,null=True)
    model = models.CharField(u'磁盘型号', max_length=128,blank=True,null=True)
    capacity = models.FloatField(u'磁盘容量GB')
    disk_iface_choice = (
        ('SATA', 'SATA'),
        ('SAS', 'SAS'),
        ('SCSI', 'SCSI'),
        ('SSD', 'SSD'),
    )

    iface_type = models.CharField(u'接口类型', max_length=64,choices=disk_iface_choice,default='SAS')
    disk_size_in_total = models.IntegerField(u'磁盘总量', null=True, blank=True)
    memo = models.TextField(u'备注', blank=True,null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True,null=True)

    auto_create_fields = ['sn','slot','manufactory','model','capacity','iface_type']
    class Meta:
        unique_together = ("asset", "slot")
        verbose_name = '硬盘'
        verbose_name_plural = "硬盘"
    def __str__(self):
        return '%s:slot:%s capacity:%s' % (self.asset_id,self.slot,self.capacity)



class NIC(models.Model):
    asset = models.ForeignKey('Asset')
    name = models.CharField(u'网卡名', max_length=64, blank=True,null=True)
    sn = models.CharField(u'SN号', max_length=128, blank=True,null=True)
    model =  models.CharField(u'网卡型号', max_length=128, blank=True,null=True)
    macaddress = models.CharField(u'MAC', max_length=64,unique=True)
    ipaddress = models.GenericIPAddressField(u'IP', blank=True,null=True)
    netmask = models.CharField(max_length=64,blank=True,null=True)
    bonding = models.CharField(max_length=64,blank=True,null=True)
    memo = models.CharField(u'备注',max_length=128, blank=True,null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return '%s' % (self.ipaddress)
    class Meta:
        verbose_name = u'网卡'
        verbose_name_plural = u"网卡"
    auto_create_fields = ['name','sn','model','macaddress','ipaddress','netmask','bonding']

class RaidAdaptor(models.Model):
    asset = models.ForeignKey('Asset')
    sn = models.CharField(u'SN号', max_length=128, blank=True,null=True)
    slot = models.CharField(u'插口',max_length=64)
    model = models.CharField(u'型号', max_length=64,blank=True,null=True)
    memo = models.TextField(u'备注', blank=True,null=True)
    create_date = models.DateTimeField(blank=True, auto_now_add=True)
    update_date = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return self.name
    class Meta:
        unique_together = ("asset", "slot")


class Manufactory(models.Model):
    manufactory = models.CharField(u'厂商名称',max_length=64, unique=True)
    support_num = models.CharField(u'支持电话',max_length=30,blank=True)
    memo = models.CharField(u'备注',max_length=128,blank=True)
    def __str__(self):
        return self.manufactory
    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = "厂商"


class BusinessUnit(models.Model):
    parent_unit = models.ForeignKey('self',related_name='parent_level',blank=True,null=True)
    name = models.CharField(u'业务线',max_length=64, unique=True)
    memo = models.CharField(u'备注',max_length=64, blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '业务线'
        verbose_name_plural = "业务线"


class Contract(models.Model):
    sn = models.CharField(u'合同号', max_length=128,unique=True)
    name = models.CharField(u'合同名称', max_length=64 )
    memo = models.TextField(u'备注', blank=True,null=True)
    price = models.IntegerField(u'合同金额')
    detail = models.TextField(u'合同详细',blank=True,null=True)
    start_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True)
    license_num = models.IntegerField(u'license数量',blank=True)
    create_date = models.DateField(auto_now_add=True)
    update_date= models.DateField(auto_now=True)
    class Meta:
        verbose_name = '合同'
        verbose_name_plural = "合同"
    def __str__(self):
        return self.name

class IDC(models.Model):
    name = models.CharField(u'机房名称',max_length=64,unique=True)
    memo = models.CharField(u'备注',max_length=128,blank=True,null=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '机房'
        verbose_name_plural = "机房"


class Tag(models.Model):
    name = models.CharField('Tag name',max_length=32,unique=True )
    creater = models.ForeignKey(MyUser)
    create_date = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name

class EventLog(models.Model):
    name = models.CharField(u'事件名称', max_length=100)
    event_type_choices = (
        (1,u'硬件变更'),
        (2,u'新增配件'),
        (3,u'设备下线'),
        (4,u'设备上线'),
        (5,u'定期维护'),
        (6,u'业务上线\更新\变更'),
        (7,u'其它'),
    )
    event_type = models.SmallIntegerField(u'事件类型', choices= event_type_choices)
    asset = models.ForeignKey('Asset')
    component = models.CharField('事件子项',max_length=255, blank=True,null=True)
    detail = models.TextField(u'事件详情')
    date = models.DateTimeField(u'事件时间',auto_now_add=True)
    user = models.ForeignKey(MyUser,verbose_name=u'事件源')
    memo = models.TextField(u'备注', blank=True,null=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '事件纪录'
        verbose_name_plural = "事件纪录"


    def colored_event_type(self):
        if self.event_type == 1:
            cell_html = '<span style="background: orange;">%s</span>'
        elif self.event_type == 2 :
            cell_html = '<span style="background: yellowgreen;">%s</span>'
        else:
            cell_html = '<span >%s</span>'
        return cell_html % self.get_event_type_display()
    colored_event_type.allow_tags = True
    colored_event_type.short_description = u'事件类型'


class NewAssetApprovalZone(models.Model):
    sn = models.CharField(u'资产SN号',max_length=128, unique=True)
    asset_type_choices = (
        ('server', u'服务器'),
        ('switch', u'交换机'),
        ('router', u'路由器'),
        ('firewall', u'防火墙'),
        ('storage', u'存储设备'),
        ('NLB', u'NetScaler'),
        ('wireless', u'无线AP'),
        ('software', u'软件资产'),
        ('others', u'其它类'),
    )
    asset_type = models.CharField(choices=asset_type_choices,max_length=64,blank=True,null=True)
    manufactory = models.CharField(max_length=64,blank=True,null=True)
    model = models.CharField(max_length=128,blank=True,null=True)
    ram_size = models.IntegerField(blank=True,null=True)
    cpu_model = models.CharField(max_length=128,blank=True,null=True)
    cpu_count = models.IntegerField(blank=True,null=True)
    cpu_core_count = models.IntegerField(blank=True,null=True)
    os_distribution =  models.CharField(max_length=64,blank=True,null=True)
    os_type =  models.CharField(max_length=64,blank=True,null=True)
    os_release =  models.CharField(max_length=64,blank=True,null=True)
    data = models.TextField(u'资产数据')
    date = models.DateTimeField(u'汇报日期',auto_now_add=True)
    approved = models.BooleanField(u'已批准',default=False)
    approved_by = models.ForeignKey(MyUser,verbose_name=u'批准人',blank=True,null=True)
    approved_date = models.DateTimeField(u'批准日期',blank=True,null=True)
    salt_minion_id = models.CharField(u'saltstack_minion_id',max_length=1024,blank=True,null=True)

    def __str__(self):
        return self.sn
    class Meta:
        verbose_name = '新上线待批准资产'
        verbose_name_plural = "新上线待批准资产"
