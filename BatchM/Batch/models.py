from django.db import models
import time
from django.contrib.auth.models import User

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


class ModelOfContainer(models.Model):
    '''
    存容器配置模板信息的
    '''
    Host_ip = models.ManyToManyField(DockerOfHost,verbose_name='Docker宿主机IP')
    Container_name = models.CharField(u'容器名字', max_length=300, null=True, blank=True)
    Container_image = models.CharField(u'容器镜像', max_length=300)
    Command = models.CharField(u'运行的命令', max_length=300, null=True, blank=True)



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
    # asset = models.ForeignKey('Asset',verbose_name='资产编号')
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
        verbose_name = '系统5分钟内运行状态'
        verbose_name_plural =  '系统5分钟内运行状态'


class NewSaltstackMinionsStatus(models.Model):
    '''
    记录saltstack Minions 的状态信息,存放最新的状态记录的。
    '''
    # asset = models.ForeignKey('Asset',verbose_name='资产编号')
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




