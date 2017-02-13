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



class ServerInline(admin.TabularInline):
    model = models.Server
    exclude = ('memo',)
    readonly_fields = ['create_date','salt_minion_id']

class CPUInline(admin.TabularInline):
    model = models.CPU
    exclude = ('memo',)
    readonly_fields = ['create_date']
class NICInline(admin.TabularInline):
    model = models.NIC
    exclude = ('memo',)
    readonly_fields = ['create_date']
class RAMInline(admin.TabularInline):
    model = models.RAM
    exclude = ('memo',)
    readonly_fields = ['create_date']
class DiskInline(admin.TabularInline):
    model = models.Disk
    exclude = ('memo',)
    readonly_fields = ['create_date']

class saltstack_group(admin.TabularInline):
    model = models.SaltstackGroup




class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ('asset','ipaddress','hostname','zombie_process','mem_use_precent',\
                    'load_average_fiveMin_ago','cpu_ioWait','login_users',\
                    'disk_max_usage','up_time','poweron_time','update_time',)
    search_fields = ('asset','ipaddress')


class AssetAdmin(admin.ModelAdmin):
    list_display = ('id','asset_type','sn','name','manufactory','management_ip','idc','business_unit')
    inlines = [ServerInline,CPUInline,RAMInline,DiskInline,NICInline]
    search_fields = ['sn',]
    list_filter = ['idc','manufactory','business_unit','asset_type']

class NicAdmin(admin.ModelAdmin):
    list_display = ('name','macaddress','ipaddress','netmask','bonding')
    search_fields = ('macaddress','ipaddress')


class EventLogAdmin(admin.ModelAdmin):
    list_display = ('name','colored_event_type','asset','component','detail','date','user')
    search_fields = ('asset',)
    list_filter = ('event_type','component','date','user')

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect


class NewAssetApprovalZoneAdmin(admin.ModelAdmin):
    list_display = ('sn','asset_type','manufactory','model','cpu_model','cpu_count',
                    'cpu_core_count','ram_size','os_distribution','os_release','date',
                    'approved','approved_by','approved_date')
    actions = ['approve_selected_objects']
    def approve_selected_objects(modeladmin, request, queryset):
        '''
        :param  modeladmin: 相当于self一样，这里是指class的名字。
        :param  request:
        :param  queryset:  表示所勾选的checkbox值（ID），
        :return:
        '''
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)   #把客户在前端勾选的复选框给过滤出来。
        # ContentType 是用来对动态关联不同的表。
        ct = ContentType.objects.get_for_model(queryset.model)
        #  pk is means primary key (pk)
        print('selected',selected,'ct',ct.pk)
        return HttpResponseRedirect("/asset/new_assets/approval/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
    approve_selected_objects.short_description = "批准入库"


class Saltstack_GroupAdmin(admin.ModelAdmin):
    list_display = ['group_name',]

    actions = ['Create_This_Group','delete_this_group']
    def Create_This_Group(modeladmin,request,queryset):
        '''
        :param  modeladmin: 相当于self一样，这里是指class的名字。
        :param  request:
        :param  queryset:  表示所勾选的checkbox值（ID），
        :return:
        '''
        selectd = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        return HttpResponseRedirect("/asset/salt_group_create/?ct=%s&ids=%s&action=add" %(ct.pk,','.join(selectd)))
    Create_This_Group.short_description = '创建这些组'

    def delete_this_group(modeladmin,request,queryset):
        selectd = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        return HttpResponseRedirect("/asset/salt_group_create/?ct=%s&ids=%s&action=delete" %(ct.pk,','.join(selectd)))
    delete_this_group.short_description = '删除这些组'

class ConfigSaltGroup(admin.ModelAdmin):
    '''
    在admin界面添加组后，也会在saltstack  的master的配置文件里面添加
    '''
    list_display = ('host_target.salt_minion_id','group_name')
    actions = [' Create_this_Group']





admin.site.register(models.TypeOfApp,app)
admin.site.register(models.TypeOfProject,project)
admin.site.register(models.WorkOrderOfUpdate,WorkOrderOfCode)

##   these info are for saltstack under this annotation

admin.site.register(models.SaltstackMinions,saltstack_minions)
admin.site.register(models.SaltstackGroup,Saltstack_GroupAdmin)
admin.site.register(models.SaltstackMinionsStatus,saltstack_minionsStatus)
admin.site.register(models.NewSaltstackMinionsStatus,new_saltstack_minions_status)
admin.site.register(MyUser, UserAdmin)

## these info are for docker under this annotation

admin.site.register(models.DockerContainers,dockercontainers)
admin.site.register(models.DockerOfHost,docker_host)
admin.site.register(models.DockerOfImages,docker_images)

#admin.site.register(MyUser)
admin.site.register(models.Asset,AssetAdmin)
admin.site.register(models.Server)
admin.site.register(models.NetworkDevice)
admin.site.register(models.IDC)
admin.site.register(models.BusinessUnit)
admin.site.register(models.Contract)
admin.site.register(models.CPU)
admin.site.register(models.Disk)
admin.site.register(models.NIC,NicAdmin)
admin.site.register(models.RAM)
admin.site.register(models.Manufactory)
admin.site.register(models.Tag)
admin.site.register(models.Software)
admin.site.register(models.EventLog,EventLogAdmin)
admin.site.register(models.NewAssetApprovalZone,NewAssetApprovalZoneAdmin)
#admin.site.register(models.SaltstackMinionsStatus,SystemStatusAdmin)
#admin.site.register(models.SaltstackGroup,Saltstack_GroupAdmin),