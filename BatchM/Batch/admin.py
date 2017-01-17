from django.contrib import admin

# Register your models here.
from Batch import models
from Batch.customize_auth_model import MyUser
from Batch.customize_auth_admin import UserAdmin



class app(admin.ModelAdmin):
    list_display = ['app_name','update_time']

class project(admin.ModelAdmin):
    list_display = ['name_of_project','update_time']

class WorkOrderOfCode(admin.ModelAdmin):
    list_display = ['OrderId','username','flow_project','flow_app','target_host','code_source','configfile_path',\
                    'configfile_content','sql_command','crond_task','system_env_change','update_of_reason','email_issend',\
                    'tags','update_time']
    search_fields = ['target_host','OrderId']




##   these infos are for saltstack under this annotation

class saltstack_minions(admin.ModelAdmin):
    list_display = ['ip','hostname','tags']
    search_fields = ['ip','hostname']

class saltstack_group(admin.ModelAdmin):
    list_display = ['group_name','whether_create','tags']
    #  def  salt_minion_id(self,obj):
    #     '''
    #     这个方法就是用来对salt_minion_id这个字段做处理，把我们需要展示的前端内容截取出来。需要注意的是，方法名必须要和在list_display里面的一致，这样才可以调用。
    #     '''
    #     print(obj.host_target.salt_minion_id)
    #     return obj.host_target.salt_minion_id
    # salt_minion_id.short_description = "Minion's ID "     # 对salt_minion_id这个做个简短的title。
    # search_fields = ['ip','hostname']


class saltstack_minionsStatus(admin.ModelAdmin):
    list_display = ['ipaddress','hostname','zombie_process','mem_use_precent','up_time','load_average_fiveMin_ago',\
                    'cpu_ioWait','login_users','disk_max_usage','update_time','poweron_time',]
    search_fields = ['ipaddress','hostname']


class new_saltstack_minions_status(admin.ModelAdmin):
    list_display = ['ipaddress','hostname','zombie_process','mem_use_precent','up_time','load_average_fiveMin_ago',\
                    'cpu_ioWait','login_users','disk_max_usage','update_time','poweron_time',]
    search_fields = ['ipaddress','hostname']



class dockercontainers(admin.ModelAdmin):
    list_display = ['Real_host_ip','Container_id','Container_name','Container_image','Container_Image_id','Command','Created','Status',\
                    'Port','SizeRw','SizeRootFs','Host_config','Network_settings','Mounts','Record_time']
    search_fields = ['Container_id','Container_name','Container_image','Status']

class docker_host(admin.ModelAdmin):
    list_display = ['host_ip']
    search_fields = ['host_ip']

class docker_images(admin.ModelAdmin):
    list_display = ['Host_ip','Image_id','Repo_tags','Created','Image_size','Virtual_size','Labels']
    search_fields = ['host_ip','Image_id','Repo_tags']

    def Host_ip(self,obj):
        '''
        因为host_ip是多对多关系，所有这里需要单独这对个字段做操作
        :param obj:
        :return:
        '''
        print(obj.host_ip.Host_ip)
        return obj.host_ip.Host_ip
    Host_ip.short_description = '宿主机IP'

admin.site.register(models.TypeOfApp,app)
admin.site.register(models.TypeOfProject,project)
admin.site.register(models.WorkOrderOfUpdate,WorkOrderOfCode)

##   these info are for saltstack under this annotation

admin.site.register(models.SaltstackMinions,saltstack_minions)
admin.site.register(models.SaltstackGroup,saltstack_group)
admin.site.register(models.SaltstackMinionsStatus,saltstack_minionsStatus)
admin.site.register(models.NewSaltstackMinionsStatus,new_saltstack_minions_status)
admin.site.register(MyUser, UserAdmin)

## these info are for docker under this annotation

admin.site.register(models.DockerContainers,dockercontainers)
admin.site.register(models.DockerOfHost,docker_host)
admin.site.register(models.DockerOfImages,docker_images)