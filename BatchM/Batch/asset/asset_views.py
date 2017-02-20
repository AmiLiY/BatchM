from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import  cache
from Batch.asset import asset_core as core
from Batch.asset import asset_handler as handler
from Batch.asset import  asset_utils  as utils
from Batch import models
from django.contrib.auth.decorators import login_required
from django.core.exceptions import  ObjectDoesNotExist
from BatchM import settings
from Batch.plugs import record_log
import json
import os
import sys
import time
import collections
import datetime




# Create your views here.
@csrf_exempt
def report_resource(request):
    '''
    处理客户端自动汇报资料的方法
    :param request:
    :return:
    '''
    print(request.method)
    if request.method == 'POST':
        aas_handler = core.Asset(request)
        if aas_handler.data_is_valid():
            aas_handler.data_inject()
        return HttpResponse(json.dumps(aas_handler.response))

    return HttpResponse(json.dumps('ok'))

@csrf_exempt
def report_with_no_id(request):
    '''
    处理客户端第一次汇报数据
    :param request:
    :return:
    '''
    if request.method == 'POST':
        asset_handler = core.Asset(request)
        res = asset_handler.get_asset_id_by_sn()
        return HttpResponse(json.dumps(res))


@csrf_exempt
def saltstack_report(request):
    '''
    通过saltstack上传的数据，在此处理。
    :param request:
    :return:
    '''
    if request.method == "POST":
        print(request)
    return HttpResponse(json.dumps('ok'))




@login_required
def new_assets_approval(request):
    '''
    展示新资产第一次批准入库页面,
    如果是get请求，那么就展现需要批准的资产数量和详情，
    如果是post请求，那么久说明同意入库，入库完成后跳转到新上线待批准资产的页面
    :param request:
    :return:
    '''
    if request.method == "POST":
        request.POST = request.POST.copy()
        approved_asset_id_list = request.POST.getlist('approved_asset_list')
        print('approved_asset_list',approved_asset_id_list)
        approved_asset_list = models.NewAssetApprovalZone.objects.filter(id__in=approved_asset_id_list)
        response_dic = {}
        approved_host_list = []
        for obj in approved_asset_list:
            request.POST['asset_data'] = obj.data
            ass_handler = core.Asset(request)
            if ass_handler.data_is_valid_without_id():
                ass_handler.data_inject()
                obj.approved = True
                obj.save()
                response_dic[obj.id] = ass_handler.response
                approved_host_list.append(obj.salt_minion_id)
        # add which host was approved into Asset table..
        ApproveHosts = models.ApproveHosts.objects.create(minion_name=approved_host_list,how_many=len(approved_host_list))
        ApproveHosts.save()

        return HttpResponseRedirect('/admin/Batch/newassetapprovalzone/')

    else:
        ids = request.GET.get('ids')
        ids_list = ids.split(',')
        asset_info = models.NewAssetApprovalZone.objects.filter(id__in=ids_list)
        return render(request,'asset/whether_approval.html',{'asset_info':asset_info})


def create_salt_group(request):
    '''
    we will create or delete of group's config in saltstack master folder.(/etc/salt/master.d/)
    :param request:
    :return:
    '''
    if request.method == 'POST':
        group_info = {}
        request.POST = request.POST.copy()
        if request.POST.getlist('create_group'):
            create_group_id_list = request.POST.getlist('create_group')
            flag = 'create'
        elif request.POST.getlist('delete_group'):
            create_group_id_list = request.POST.getlist('delete_group')
            flag = 'delete'
        need_create_groups = models.SaltGroup.objects.filter(id__in=create_group_id_list)
        for number in need_create_groups:
            group_info[number.group_name]= []
            for i in number.host_target.select_related():
                group_info[number.group_name].append(i.salt_minion_id)
        operation_group = core.Create_SaltGroup(**group_info)
        if flag == 'create':
            result = operation_group.add_groups(create_group_id_list)
            if result:
                models.SaltGroup.objects.filter(id__in=create_group_id_list).update(whether_create=1)
        elif flag == 'delete':
            result = operation_group.del_groups()
            if result:
                models.SaltGroup.objects.filter(id__in=create_group_id_list).delete()

        if result:  # if the execute's action return is ture,then redirect this web page!
            return HttpResponseRedirect('/admin/asset/saltgroup/')
        else:
            return HttpResponse("<h3>There have some thing wrong with you opration</h3>")

    else:
        group_list = request.GET.get('ids')
        group_list = group_list.split(',')
        group_number = models.SaltGroup.objects.filter(id__in=group_list)
        action = request.GET.get('action')
        if action == 'add':
            title = '创建'
            action = 'create_group'
        elif action == 'delete':
            title = '删除'
            action = 'delete_group'
        return render(request,'asset/Create_salt_group.html',{'group_number':group_number,'title':title,'action':action})




#@login_required
def index_page(request):
    '''
    显示首页
    :param request:
    :return:
    '''
    return render(request,'index.html')

@csrf_exempt
def system_status(request):
    '''
    存入系统状态信息，这里有2张表，第一张表是用来存储历史数据的，第二张表是用来存储最新数据的表
    :param request:
    :return:
    '''
    if request.method == 'POST':
        print(request.POST)
        request_post = request.POST.copy()
        ipaddr = models.NIC.objects.filter(asset__id=request.POST.get('asset_id'))
        asset_id = models.Asset.objects.filter(id=request.POST.get('asset_id'))
        request_set = {}
        request_set = {
            'ipaddress':ipaddr.first().ipaddress,
            'asset':asset_id.first(),
            'load_average_fiveMin_ago':request.POST.get('load_average_fiveMin_ago'),
            'hostname':request.POST.get('hostname'),
            'disk_max_usage':request.POST.get('disk_max_usage'),
            'cpu_ioWait':request.POST.get('cpu_ioWait'),
            'zombie_process':request.POST.get('zombie_process'),
            'up_time':request.POST.get('up_time'),
            'login_users':request.POST.get('login_users'),
            'mem_use_precent':request.POST.get('mem_use_precent'),
            'poweron_time':request.POST.get('start_time'),
            'update_time':request.POST.get('update_time'),
        }
        # 开始存入专门用来放历史记录的表，
        print(request_set)
        data_save_obj = models.SaltstackMinionsStatus(**request_set)
        #　更新专门用来存放最新一条历史记录的的表
        if models.NewSaltstackMinionsStatus.objects.filter(asset=asset_id.first()):
            models.NewSaltstackMinionsStatus.objects.filter(asset=asset_id.first()).update(**request_set)
        else:
            models.NewSaltstackMinionsStatus.objects.create(**request_set)
        data_save_obj.save()
    return HttpResponse(json.dumps('put ok'))

@login_required
def assets(request):
    '''
    展示资产首页的方法
    :param request:
    :return:
    '''
    assets = handler.fetch_asset_list()
    return render(request,'asset/assets_list.html',{'assets':assets,'title':'服务器信息表'})


@login_required
def asset_list(request):
    '''
    获取资产的所有信息
    :param request:
    :return:
    '''
    assets = handler.fetch_asset_list()
    return render(request,'asset/assets_list.html',{'assets':assets['data'],'title':'服务器信息表'})

@login_required
def get_asset_list(request):
    '''
    获取资产列表的信息
    :param request:
    :return:
    '''
    asset_dic = handler.fetch_asset_list()
    print('asset_dic',asset_dic)
     # return HttpResponse(json.dumps(asset_dic,default=utils.json_datetime_handler))
    return asset_dic

@login_required
def asset_category(request):
    '''
    返回资产模块（前端web模块）
    :param request:
    :return:
    '''
    category_type = request.GET.get('category_type')
    if not category_type:category_type="server"
    if request.is_ajax():
        categories = handler.AssetCategroy(request)
        data = categories.serialize_data()
        return HttpResponse(data)
    else:
        return render(request,'asset/asset_category.html',{'catetory_type':category_type})


@csrf_exempt
@login_required()
def asset_graphic(request):
    '''
    显示资产列表的圆饼图
    :param request:
    :return:
    '''
    if request.method == 'GET':
        return render(request,'asset/assets_list.html',{'title':'服务器信息饼状图'})
    elif request.method == 'POST':   # how manay type of OS release and release's number
        graphic_type = request.POST.get('graphic_type')
        os_release_list =   all_os_release = []

        if graphic_type == 'os_release':
            all_os_release = models.Server.objects.all().values('os_release')
        elif graphic_type == "manufactory":
            all_os_release = models.Manufactory.objects.all().values('manufactory')
        elif graphic_type == 'hosts_show':
            # filter which host was approved in  this table ApproveHosts
            now_month = datetime.datetime.now().month
            already_approved = models.ApproveHosts.objects.filter(update_time__month=now_month).order_by('update_time')
            waiting_approve = models.NewAssetApprovalZone.objects.filter(date__month=now_month,approved=False).order_by('date')
            response_dict= {'already_approved':{},'waiting_approve':{}}
            for i in already_approved:
                if str(i.update_time).split()[0] in response_dict['already_approved'].keys():
                    response_dict['already_approved'][str(i.update_time).split()[0]] =  response_dict['already_approved'][str(i.update_time).split()[0]]+i.how_many     # update_time as key in this dictionary
                else:
                    response_dict['already_approved'][str(i.update_time).split()[0]] = i.how_many

            for i in waiting_approve:
                if str(i.date).split()[0] in response_dict['waiting_approve'].keys():  # if the day in the key of dict,so we need to incrase 1
                    response_dict['waiting_approve'][str(i.date).split()[0]] = response_dict['waiting_approve'][str(i.date).split()[0]]+1
                else:   # not in ,so we also incrase 1
                    response_dict['waiting_approve'][str(i.date).split()[0]] =   1

            print(response_dict)
            return HttpResponse(json.dumps(response_dict))

        for os_release in all_os_release:
            os_release_list.append(os_release[graphic_type])
        print(collections.Counter(os_release_list))
        response_data = {"os_release_number":collections.Counter(os_release_list),"total_number":len(os_release_list)}
        return HttpResponse(json.dumps(response_data))

@login_required
def asset_event_logs(request,asset_id):
    '''
    获取对资产操作的日志记录
    :param request:
    :param asset_id:
    :return:
    '''
    if request.method == "GET":
        log_list = handler.fetch_asset_event_logs(asset_id)
        return HttpResponse(json.dumps(log_list,default=utils.json_datetime_handler))

@login_required
def asset_detail(request,asset_id):
    '''
    展现某个资产的详细数据
    :param request:
    :param asset_id:
    :return:
    '''
    if request.method == "GET":
        try:
            asset_obj = models.Asset.objects.get(id=asset_id)
        except ObjectDoesNotExist as e:
            return render(request,'asset/asset_detail.html',{'error':e})
        return render(request,'asset/asset_detail.html',{"asset_obj":asset_obj})

@login_required
def host_status(request):
    '''
    从数据库获取主机状态信息，然后返回到前端
    :param request:
    :return:
    '''
    all_host_status = models.NewSaltstackMinionsStatus.objects.all().order_by('id')
    print('all_host_status',all_host_status)
    return render(request,'asset/host_status.html',{'host_status_list':all_host_status})


@login_required
def host_status_detail(request,host_id):
    '''
    展现服务器详细信息
    :param request:
    :param hoost_id: 服务器的资产id号
    :return:
    '''
    disk_usage_a_hour = []
    sys_load_a_hour = []
    cpu_io_wait_a_hour = []
    mem_usage_a_hour = []
    update_time_stamp = []
    tmp_time = []
    a_hour_data = models.SaltstackMinionsStatus.objects.filter(asset__id=host_id).order_by('-update_time')[0:12]
    for info in a_hour_data:
        disk_usage_a_hour.append(float(info.disk_max_usage))
        sys_load_a_hour.append(float(info.load_average_fiveMin_ago))
        cpu_io_wait_a_hour.append(float(info.cpu_ioWait))
        mem_usage_a_hour.append(float(info.mem_use_precent))
        tmp_time.append(info.update_time)

    # 把时间转换成unix时间，然后发给客户端
    for t in tmp_time:
        time_stamp = t
        update_time_stamp.append(time_stamp.timestamp())
    print(update_time_stamp.reverse())
    return render(request,'asset/host_status_detail.html',{'host_id':host_id,
                                                            'disk_usage_a_hour': disk_usage_a_hour,
                                                            'sys_load_a_hour': sys_load_a_hour,
                                                            'cpu_io_wait_a_hour' : cpu_io_wait_a_hour,
                                                            'update_time':update_time_stamp,
                                                            'mem_usage_a_hour': mem_usage_a_hour })



@login_required
@csrf_exempt
def get_status_data(request):
    '''
    获取服务器状态信息
    :param request:
    :return:
    '''
    if request.method == 'POST':
        print(request.POST)
        host_id = request.POST.get('host_id')
        a_hour_data = models.SaltstackMinionsStatus.objects.filter(asset__id=host_id)[0:12]
        responce_data = {'disk_usage_a_hour':[],'cpu_io_wait_a_hour':[],
                         'mem_usage_a_hour':[],'sys_load_a_hour':[]}
        for info in a_hour_data:
            responce_data['disk_usage_a_hour'].append(float(info.disk_max_usage))
            responce_data['sys_load_a_hour'].append(float(info.load_average_fiveMin_ago))
            responce_data['cpu_io_wait_a_hour'].append(float(info.cpu_ioWait))
            responce_data['mem_usage_a_hour'].append(float(info.mem_use_precent))
        print(responce_data)
        return HttpResponse(json.dumps(responce_data))
    return HttpResponse('permission denied')



'''
just for geting a token from saltapi befor execute commands from client.it can speed execute
'''
print("\033[32mLet me start to get token from saltapi,it may be take some minutes!!\nplease wait for me.....\033[0m")
# if settings.SaltApiOfHost and settings.SaltApiUsername and settings.SaltApiPasswd:
#     ip = settings.SaltApiOfHost
#     username = settings.SaltApiUsername
#     passwd = settings.SaltApiPasswd
#     saltapi = core.run_salt_api(,username=username,passwd=passwd,ip=ip)
# else:
#     assert "Your are not set saltapi's username,password,hostip in settings"

print("\033[32m ok ,i already get this token from saltapi,let's continue..\033[0m")

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


@login_required()
def show_approve_hosts(request):
    '''
    show how many hosts was approvel
    :return:
    '''
    now = datetime.datetime.now()
    models.Asset.objects.dates()
    all_approvel_host =  models.Asset.objects.filter(update_date__month=now.month)

    hosts_approvel = models.ApproveHosts.objects.all()



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






@login_required()
def distributecode(request,project_name):
    '''
    代码分发，这个方法主要是用来处理用户上传的代码包以及scp代码包到目标服务器上。成功scp代码包到目标服务器后，
    就会跳转到另一个输入命令的页面
    :param request:
    :return:
    '''
    if request.method == "POST":

        print(request.POST,request.FILES)

        code_pkg = request.FILES.get('code_pkg')
        #install_script = request.FILES.get('install_script')    this line code was dropped
        remote_ip = request.POST.get('remote_ip')
        remote_code_pkg = "%s/%s"%(settings.CodePkgPath,code_pkg)
        remote_inst_script = "%s/%s_%s.sh"%(settings.InstallScriptPath,settings.InstallScriptPrefix,project_name)
        pkg_file_path = "uploads/%s" %(code_pkg)
        #install_script_path = "uploads/%s" %(install_script)

        recv_size = 0
        with open(pkg_file_path, 'wb') as new_file:
            for chunk in code_pkg.chunks():
                new_file.write(chunk)
                recv_size += len(chunk)
                cache.set(code_pkg.name, recv_size)
        print(new_file,'has been wirte down')

        # these lines were dropped  ，this block code as handle upload file
        # with open(install_script_path,'wb') as new_script:
        #     for chunk in install_script.chunks():
        #         new_script.write(chunk)
        # print(new_script, 'has been wirte down')

        timestamp = time.time()  # timestamp as a id in cache, and send this stamp to web pages,
        auth_method = request.POST.get('auth_method')
        cache.set('%s_auth_method' % (timestamp), auth_method, 150)
        if auth_method == 'password':
            username = request.POST.get('username')
            password = request.POST.get('password')
            cache.set('%s_username' % (timestamp), username, 150)
            cache.set('%s_password' % (timestamp), password, 150)
            sput = core.sftp_paramiko(request,auth_method=auth_method,host=remote_ip,username=username,password=password)
        else:
            sput = core.sftp_paramiko(request,auth_method=auth_method, host=remote_ip)

        abs_pkg_file_path = "%s/../%s" %(os.path.dirname(__file__),pkg_file_path)
        # abs_install_script_path = "%s/../%s" %(os.path.dirname(__file__),install_script_path)  this line was dropped
        result = sput.put_file(abs_pkg_file_path,remote_code_pkg)
        #sput.put_file(abs_install_script_path,remote_inst_script)  this line was dropped

        # remote all of you upload file on localhost!!
        os.system('rm -f %s'%(abs_pkg_file_path))
        # 记录日志
        rh = record_log.handler_log(request.user.get_username(),
                                    logfile_path="%s/../log/distributecode.log" % os.path.dirname(__file__))
        rh.info("host: %s,script_name: %s,code_pkg: %s,auth_method: %s ,"
                % (remote_ip,remote_inst_script,code_pkg,auth_method))
        if result is True:
            return render(request,'asset/remote_run_cmd.html',{'script_name':remote_inst_script,'timestamp_cache':timestamp,
                                                                "code_pkg_name":remote_code_pkg,"remote_ip":remote_ip})
        else:
            return  HttpResponse("<h1>Authentication failed.</h1> please check username or password or auth method!!!")
    else:
        return render(request, 'asset/distribute_code.html',{'project_name':project_name})

@login_required()
def remote_run_cmd_by_distributecode(request):
    '''
    执行命令的，在执行替换网站代码的脚本时候，会和脚本进行交互，把用户输入的命令拿过来进行交互下。
    :param request:
    :return:
    '''
    if request.method == "POST":
        print(request.POST.get('args'))
        kwargs = {}
        kwargs['remote_ip'] = request.POST.get("remote_ip")
        kwargs['args'] = request.POST.get('args')
        kwargs['code_pkg_name'] = request.POST.get('code_pkg_name')
        kwargs['script_name'] = request.POST.get('script_name')
        whether_run = request.POST.get("whether_run")
        timestamp = request.POST.get('timestamp_cache')
        auth_method = cache.get('%s_auth_method'%(timestamp))
        if whether_run == "yes":
            if auth_method == 'password':
                username = cache.get('%s_username'%(timestamp))
                password = cache.get('%s_password' % (timestamp))
                shell = core.sftp_paramiko(request,auth_method=auth_method,host=kwargs.get('remote_ip'),
                                           username=username,password=password)
            else:
                shell = core.sftp_paramiko(request,auth_method=auth_method, host=kwargs.get('remote_ip'))
            print(kwargs)

            if settings.InvokeShellTimeout:   # whether set Invoke shell timeout
                result = shell.communicate_with_shell(**kwargs,session_timeout=settings.InvokeShellTimeout)
            else:
                result = shell.communicate_with_shell(**kwargs)

            # remove all of you upload files on remote machine!
            shell.execute_command('rm -f %s' %(kwargs.get('code_pkg_name')))
            print('--result-->',result)
            rh = record_log.handler_log(request.user.get_username(),
                                        logfile_path="%s/../log/distributecode.log" % os.path.dirname(__file__))
            rh.info("host: %s,script_name: %s,code_pkg: %s,auth_method: %s , args: %s,result: %s"
                    % (kwargs['remote_ip'],kwargs['script_name'], kwargs['code_pkg_name'],
                       auth_method ,kwargs['args'],result if result else False))
            if result:
                return HttpResponse(json.dumps("Execute this script successfully!!"))
    else:
        return render(request, 'asset/remote_run_cmd.html')

def file_upload_progress(request):
    '''
    获取已经上传文件大小的值
    :param request:
    :return:
    '''
    filename = request.GET.get('filename')
    progress = cache.get(filename)
    print('-------------->file %s uploading process %s'%(filename,progress))
    return HttpResponse(json.dumps({'recv_size':progress}))

def delete_cache_key(request):
    '''
    :param request:
    :return:
    '''
    cache_key = request.GET.get('cache_key')
    cache.delete(cache_key)
    return HttpResponse('cache_key_was_deleted',cache_key)