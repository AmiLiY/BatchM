from django.shortcuts import render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from Batch.plugs import record_log
from Batch import  formself,core,models
from BatchM import  settings
from datetime import timedelta,timezone,datetime
from Batch import formself
import json
import time
import datetime


import sys,os
# Create your views here.


tzutc_8 = timezone(timedelta(hours=8))   # 当前时间往后+8小时在通过strftime格式化输出到时候


@login_required
def dashboard_index(request):
    '''
    x显示首页方法
    :param request
    :return:
    '''

    return render(request,'index.html')

def server_host_status(request):
    '''
    获取运行此系统的服务器cpu和内存的使用方法，供首页展示
    :param request:
    :return:
    '''
    if sys.platform != "win32":   # if the platform is not windowns,then these code will be execute.just get cpu and mem \
        # useage from localhost
        Usages = os.popen('sh %s/plugs/get_cpu.sh' %os.path.dirname(__file__) ).read()
        Usage = {}
        Usage['cpu_usage'],Usage['mem_usage'] = Usages.split('\n')[0].split('.')[0],Usages.split('\n')[1].split('.')[0]
    else:
        Usage = {'cpu_usage': '35', 'mem_usage': '68'}
    # 获取IP的
    if "HTTP_X_FORWARDED_FOR" in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return HttpResponse(json.dumps(Usage))


@login_required
def saltstack_index(request):
    '''
    展现出saltstack主机数量，group数量，以及待认证的服务器。
    :param request:
    :return:
    '''
    return render(request,'saltstack/saltstack.html')

def saltstack_minions_show(request):
    '''

    :param request:
    :return:
    '''
    if request.method == 'GET':
        limit = request.GET.get('limit')  # how many items per page
        offset = request.GET.get('offset')  # how many items in total in the DB
        search = request.GET.get('search')
        sort_column = request.GET.get('sort')  # which column need to sort
        order = request.GET.get('order')  # ascending or descending
        if search:  # 判断是否有搜索字
            all_saltminions = models.Server.objects.filter( Q(os_type__contains=search)
                | Q(business_unit__name__contains=search)| Q(idc__name__contains=search) |
                Q(os_release__contains=search)| Q(salt_minion_id__contains=search)|
                                                            Q(asset_id=search))
        else:
            all_saltminions = models.Server.objects.all()

        if all_saltminions:
            all_saltminions_count=all_saltminions.count()    # 统计多少条数据
        else:
            return HttpResponse(json.dumps("Not Found anything what you want"))

        if not offset:
            offset = 0
        if not limit:
            limit = 20    # 默认是每页20行的内容，与前端默认行数一致
        pageinator = Paginator(all_saltminions, limit)   # 开始做分页
        print('all_saltminions',all_saltminions)
        page = int(int(offset) / int(limit) + 1)
        response_data = {'total':all_saltminions_count,'rows':[]}   # 必须带有rows和total这2个key，total表示总页数，rows表示每行的内容
        for minion in pageinator.page(page):
            response_data['rows'].append({
                "asset_id": minion.asset_id,
                "model":minion.model,
                "os_type":minion.os_type,
                "os_release":minion.os_release,
                "salt_minion_id":minion.salt_minion_id,
                "update_date":minion.update_date
            })
        return HttpResponse(json.dumps(response_data))


@login_required()
def apply_update_search(request):
    '''
    显示搜索工单页面
    :param request:
    :return:
    '''
    if request.method == 'GET':
        records = models.WorkOrderOfUpdate.objects.filter(username=request.user.get_username()).order_by('OrderId').reverse()  #把当前登录用户申请到工单按照工单ID排序返回给前端。
        pageinator = Paginator(records,30)    #30表示每一页到内容
        page = request.GET.get('page')
        try:
            contacts = pageinator.page(page)
        except PageNotAnInteger:      # 如果输入到不是一个数字，发送第一页
            contacts = pageinator.page(1)
        except EmptyPage:   # 如果获取到超过来页数范围，那么就返回最后一页。
            contacts = pageinator.page(pageinator.num_pages)
        return render(request,'apply_update.html',{'btitle':'搜索操作记录','contacts':contacts})


    elif request.method == "POST":     # 搜索工单
        order_id = request.POST.get('order_id')
        searuch_result = models.WorkOrderOfUpdate.objects.get(username=request.user.get_username(),OrderId=order_id)
        update_time = searuch_result.update_time.astimezone(tzutc_8)    # 纠正时区
        flow_project_name = searuch_result.flow_project.name_of_project
        flow_app_name = searuch_result.flow_app.app_name
        response_body = {'OrderId':searuch_result.OrderId,'username':searuch_result.username,\
                        'flow_project':flow_project_name,'flow_app':flow_app_name,\
                         'target_host':searuch_result.target_host,'code_source':searuch_result.code_source,\
                         'configfile_path':searuch_result.configfile_path,
                         'update_of_reason':searuch_result.update_of_reason,\
                         'email_issend':searuch_result.email_issend,'update_time':update_time.strftime("%Y-%m-%d %H:%M:%S")}
        return HttpResponse(json.dumps(response_body))



@login_required()
def apply_update_apply(request):
    '''
    显示申请更新到页面
    :param request:
    :return:
    '''
    if request.method == 'GET':
        apps = models.TypeOfApp.objects.all()
        projects = models.TypeOfProject.objects.all()
        return render(request,'apply_update.html',{'btitle':'申请更新','apps':apps,'projects':projects})

    elif request.method == "POST":

        file_obj = request.FILES.get('file')
        upload_file = None
        if file_obj:   # 处理附件上传到方法
            print('file--obj', file_obj)
            #user_home_dir = "upload/%s" % (request.user.userprofile.id)
            accessory_dir = settings.accessory_dir
            if not os.path.isdir(accessory_dir):
                os.mkdir(accessory_dir)
            upload_file = "%s/%s" % (accessory_dir, file_obj.name)
            with open(upload_file, 'wb') as new_file:
                for chunk in file_obj.chunks():
                    new_file.write(chunk)

        project_name = request.POST.get('flow_project')
        flow_project = models.TypeOfProject.objects.get(name_of_project=project_name)
        app_name=request.POST.get('flow_app')
        flow_app = models.TypeOfApp.objects.get(app_name=app_name)
        order_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        #print('usernane',request.user.username)      #打印用户到名字
        #print('email',request.user.email)        # 打印用户的邮箱地址
        request_set = {
            'OrderId':order_id,
            'username': request.user.email,
            'flow_project':flow_project,
            'flow_app':flow_app,
            'target_host':request.POST.get('target_host'),
            'code_source':request.POST.get('code_source'),
            'configfile_path':request.POST.get('configfile_path'),
            'configfile_content':request.POST.get('configfile_content'),
            'sql_command':request.POST.get('sql_command'),
            'crond_task':request.POST.get('crondtab_task'),
            'system_env_change':request.POST.get('change_sys_env'),
            'update_of_reason':request.POST.get('Upreason'),
            'accessory_path': upload_file
        }
        email_issend = core.selfmail(request_set)      #  调用发送邮件的功能，发送到指定到地址
        request_set['email_issend']= email_issend
        #request_set['email_issend']= True
        data_obj = models.WorkOrderOfUpdate(**request_set)
        data_obj.save()

        return  HttpResponseRedirect('/BatchM/apply_update.html/search/%s'%order_id)


@login_required
def apply_detail(request,order_id):
    '''
    显示一个工单详情
    :param request:
    :param order_id:  工单ID
    :return:
    '''
    print(order_id)
    order_detail = models.WorkOrderOfUpdate.objects.get(OrderId=order_id)
    form = formself.ApplyUpdateForm(instance=order_detail)
    return render(request,'update_order_detail.html',{'selfforms':form})


@login_required
def docker_containers_show(request):
    '''
    显示docker容器表单，带有搜索功能，还有管理容器的链接
    :param request:
    :return:
    '''
    if request.method == "GET":
        ci = request.GET.get('container_info')
        if ci:  # 如果时获取到container_info，说明说是容器搜索
            infos = models.DockerContainers.objects.filter(Q(Container_name__contains=ci)|Q(Container_id__startswith=ci))
            response_body = {}
            for info in infos:
                update_time = info.Record_time.astimezone(tzutc_8)
                response_body [info.Container_id ]= {
                   "Real_host_ip":info.Real_host_ip.host_ip,"Container_id":info.Container_id,
                    "Container_name":info.Container_name,"Container_image":info.Container_image,
                    "Command":info.Command,"Created":info.Created,"Status":info.Status,
                    "Record_time":update_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            return HttpResponse(json.dumps(response_body))

        else:
            all_data = models.DockerContainers.objects.all()
            hosts = models.DockerOfHost.objects.all()
            images = models.DockerOfImages.objects.all()
            return render(request,'DockerM.html',{"docker_containers":all_data,"hosts":hosts,
                                                  'big_title':"Docker 容器管理",'images':images},)

    elif request.method == "POST":           # 处理ajax异步刷新容器信息
        models.DockerContainers.objects.all().delete()
        result = core.DockersInfo()     # 获取容器运行信息
        print('result',result)
        disconnect_hosts = [] #定义一个列表，用来添加链接失败的主机
        for k, v in result.items():
            if  type(v) != bool:    # 如果不是布尔值，
                if len(v) > 0 :              # 如果等于0，表示这个宿主机没有创建容器，否则创建了容器
                    if v[0] is not False:        # 判断docker宿主机是否能够链接上，如为false表示链接不上
                        for value in v:

                            store_body = {
                                "Real_host_ip": k,
                                "Container_id": value.get('Id'),
                                "Container_name": value.get('Names'),
                                "Container_image": value.get('Image'),
                                "Container_Image_id": value.get('ImageID'),
                                "Command": value.get('Command'),
                                "Created": time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(value.get('Created'))),
                                "Status": value.get("Status") if value.get("Status") else "Not Running",  # 状态为空表示没有运行这个容器
                                "Port": value.get("Ports"),
                                "SizeRw": value.get('SizeRw'),
                                "SizeRootFs": value.get("SizeRootFs"),
                                "Host_config": value.get("Host_config"),
                                "Network_settings": value.get("Network_settings"),
                                "Mounts": value.get("Mounts"),
                                # "Record_time": datetime.datetime.now()
                            }
                            #data_obj = models.DockerContainers.objects.get_or_create(**store_body)
                            data_obj = models.DockerContainers(**store_body)
                            data_obj.save()

                    else:
                        disconnect_hosts.append("%s:%s" % (v[1], v[2]))
                else:
                    '''
                    表示这个宿主机没有创建容器
                    '''
                    models.DockerContainers.objects.filter(Real_host_ip__host_ip__exact=k).delete()   # 删除链接不上宿主机到容器记录
            else:
                '''
                docker宿主机链接失败
                如果Real_host_ip不在dockerhost这张表上，那么就在DockerContainers删除对应到信息，确保前端展示无误
                '''
                disconnect_hosts.append(k.host_ip)
                models.DockerContainers.objects.filter(Real_host_ip__host_ip__exact=k).delete()

        response_body={}
        if request.POST.get('type') == 'containers':    # 根据请求类型来返回不同到响应包
            now_status = models.DockerContainers.objects.all()
            for info in now_status:
                #print(info.Record_time,dir(info.Record_time))
                #update_time = info.Record_time.astimezone(tzutc_8)
                response_body [info.Container_id ]= {
                   "Real_host_ip":info.Real_host_ip.host_ip,"Container_id":info.Container_id,
                    "Container_name":info.Container_name,"Container_image":info.Container_image,
                    "Command":info.Command,"Created":info.Created,"Status":info.Status,
                    "Record_time":info.Record_time.strftime("%Y-%m-%d %H:%M:%S"),
                    #"Record_time":update_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
        elif request.POST.get('type') == "images":
            pass   # 把获取回来到结果做成字典 返回给前端页。
        if  len(disconnect_hosts) > 0:
            response_body['disconnect_hosts'] = disconnect_hosts
        return HttpResponse(json.dumps(response_body))


@login_required
def docker_images_show(request):
    '''
    展现出docker宿主机上的镜像
    :param request:
    :return:
    '''
    if request.method == "GET":
        disconnect_hosts = []  # 定义一个列表，用来添加链接失败的主机
        if request.GET.get('container_info'):     # container_info是用户输入的搜索关键字
            image_id_name = request.GET.get('container_info')
            docker_images = models.DockerOfImages.objects.filter(Q(Image_id__contains=image_id_name)
                                                                 |Q(Repo_tags__contains=image_id_name))  #搜索对应的镜像'
            response_body = {}
            for image in docker_images:
                update_time = image.update_time.astimezone(tzutc_8)
                hostip=image.Host_ip.select_related().first().host_ip
                response_body[hostip] = {    # 反向关联,以主机IP为key
                    'host_ip':hostip,
                    'image_id':image.Image_id,'Parent_id':image.Parent_id,
                    'Repo_tags':image.Repo_tags,'Repo_digests':image.Repo_digests,
                    'Created':image.Created,'Image_size':image.Image_size,
                    'Virtual_size':image.Virtual_size,'Labels':image.Labels,
                    'update_time':update_time.strftime("%Y-%m-%d %H:%M:%S")
                }
            return HttpResponse(json.dumps(response_body))
        else:
            docker_images = models.DockerOfImages.objects.all()
            return render(request,'DockerM.html',{'big_title':'Docker镜像查看','docker_images':docker_images})
    elif request.method == "POST":
        images_result = core.DockerManager(request)
        if images_result is False:
            return HttpResponse(json.dumps('unavailable params'))



def docker_manager(request):
    '''
    view下控制容器启动，停止等状态的，镜像到刷新和删除镜像的，主要调用core里面的方法来完成
    :param request:
    :return:
    '''
    if request.method == "POST":
        result = core.DockerManager(request)   # 所有处理动作放到core里面去处理，view只关心结果。
        if result is False:
            return HttpResponse(json.dumps('unavailable params'))
        else:
            ret_list = {}
            ret_list['success'] = []
            ret_list['error'] = []
            sucess_list,err_list = result
            print('result',result)
            ret_list['success'].append(sucess_list)
            if request.POST.get('type') == 'images' and request.POST.get('action') != 'select' :
                # 因为是对镜像到操作，所有需要把镜像ID和宿主机的IP返回到前端。
                ret_list['error'].append(err_list)
            else:
                for err in err_list.keys():
                    ret_list['error'].append(err)
            print('ret_list',ret_list)
            return HttpResponse(json.dumps(ret_list))

    elif request.method == "GET":
        print('request.GET', request.GET)
        if request.GET.get('create_info'):
            result = core.CreateContainer(request.GET.get('create_info'))
            print('dir container instance',result)
            return HttpResponse(json.dumps(result))
        else:
            all_images = models.DockerOfImages.objects.all()
            return render(request,'DockerM.html',{'docker_images':all_images})


def docker_container_detail_show(request,container_id):
    '''
    显示每一个容器到详细信息，预留人工修改容器信息到功能
    :param request:
    :param container_id:
    :return:
    '''

    if request.method == "GET":
        print('container_id',container_id)
        container_detail = models.DockerContainers.objects.get(Container_id=container_id)
        container_form = formself.Docker_Containers(instance=container_detail)
        return render(request,'Docker_detail.html',{'selfforms':container_form,})


def docker_host_detail_show(request,hostip):
    '''
    显示每一个宿主机到跑了多少个容器信息
    :param request:
    :param hostip: 宿主机IP
    :return:
    '''
    if request.method == "GET":
        print('hostip',hostip)
        host_detail = models.DockerContainers.objects.get(Real_host_ip=hostip)
        return HttpResponse(200)



'''
just for geting a token from saltapi befor execute commands from client.it can speed execute
'''
print("\033[32mLet me Begin to get a token from saltapi,it maybe take some minutes!!\nplease wait for me.....\033[0m")
if settings.SaltApiOfHost and settings.SaltApiUsername and settings.SaltApiPasswd:
    ip = settings.SaltApiOfHost
    username = settings.SaltApiUsername
    passwd = settings.SaltApiPasswd
    port = settings.SaltApiPort
    saltapi = core.run_salt_api(username=username,passwd=passwd,ip=ip,port=port)
else:
    assert "Your are not set saltapi's username,password,hostip in settings"

print("\033[32m ok ,i already got this token from saltapi,let's continue..\033[0m")

@login_required()
def run_shell(request,host_id):
    '''
    调用salt client api 来执行来自于前端汇报过来的saltstack命令，只是单台服务器的执行
    :param request:
    ;:param host_id: 服务器资产id
    :return:
    '''
    # if the requestion's method is post ,it's means client need to execute some cmds on this host_id

    if request.method == "POST":
        print(request.POST)
        host_id = request.POST.get('host_id').strip()
        minion_name = request.POST.get('minion_name').strip()
        func = request.POST.get('func').strip()
        args = request.POST.get('args').strip()

        rh = record_log.handler_log(request.user.get_username(),
                                    logfile_path="%s/../log/saltstack_access.log" % os.path.dirname(__file__))
        rh.info("mimion: %s ,func: %s,args: %s" % (minion_name, func, args if args else None))
        if args:  #judge wether have args on post request.if have args , must send to salt api with need to execute function
            result = saltapi.api_exec(target=minion_name,func=func,arg=args,arg_num=1)
        else:
            result = saltapi.api_exec(target=minion_name,func=func)

        return HttpResponse(json.dumps(result))
    # if not post,client wants to get web page from here....
    else:
        host_info = models.Server.objects.filter(asset__id=host_id)
        try:
            salt_minion_id = host_info[0].salt_minion_id
        except IndexError:
            return HttpResponse("<h1>404</h1>,Not Found the minion's anything on the databases,\
                            May be these infos are outdated or losed!! please communicate with \
                            the website administrator! ")
        return render(request,'asset/run_cmd.html',{'salt_minion_id':salt_minion_id,'host_id':host_id})



@csrf_exempt
@login_required()
def groupshell(request,host_id):
    '''
    execute saltstack group's command!
    :param request:
    :param host_id:  saltstack组ID
    :return:
    '''

    if int(host_id) != 000: #展示saltstack主机组首页到url结尾就是000结尾，如果不是000结尾到那就说明需要进入saltstack主机组到其他页面
        if request.method == "POST":
            print(request.POST)
            group_name = request.POST.get('group_name')
            func = request.POST.get('func')
            args = request.POST.get('args')
            rh = record_log.handler_log(request.user.get_username(),
                                        logfile_path="%s/../log/saltstack_access.log" % os.path.dirname(__file__))
            rh.info("mimion: %s ,func: %s,args: %s" % (group_name, func, args if args else None))

            if args:  #judge wether have args on post request.if have args , must send to salt api with need to execute function
                result = saltapi.api_exec(target=group_name,expr_form='nodegroup',func=func,arg=args,arg_num=1)
            else:
                result = saltapi.api_exec(target=group_name,expr_form="nodegroup",func=func)
            print(result)
            return HttpResponse(json.dumps(result))
        else:
            try:
                group_number = models.SaltGroup.objects.filter(id=host_id)
                group = group_number[0]
                return render(request,'asset/saltstack_group_detail.html',{'group_number':group_number,'group':group})
            except IndexError:
                return HttpResponse("<h1>404</h1>,Not Found the Group's anything on the databases,\
                                        May be these infos are outdated or losed!! please communicate with \
                                        the website administrator! ")

    salt_group = models.SaltGroup.objects.all()
    return render(request,'asset/saltstack_group.html',{"salt_group":salt_group,})




