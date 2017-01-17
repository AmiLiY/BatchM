from django.shortcuts import HttpResponse
from Batch import models
import json


def system_status(request):
    '''
    存入系统状态信息，这里有2张表，第一张表是用来存储历史数据的，第二张表是用来存储最新数据的表
    :param request:
    :return:
    '''
    if request.method == 'POST':
        print(request.POST)
        request_post = request.POST.copy()
        #ipaddr = models.NIC.objects.filter(asset__id=request.POST.get('asset_id'))
        #asset_id = models.Asset.objects.filter(id=request.POST.get('asset_id'))

        request_set = {
            #'ipaddress':ipaddr.first().ipaddress,
            #'asset':asset_id.first(),
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
        data_save_obj = models.SystemStatus(**request_set)
        #　更新专门用来存放最新一条历史记录的的表
        #if models.NewSystemStatus.objects.filter(asset=asset_id.first()):
        #    models.NewSystemStatus.objects.filter(asset=asset_id.first()).update(**request_set)
        #else:
        #    models.NewSystemStatus.objects.create(**request_set)
        data_save_obj.save()
    return HttpResponse(json.dumps('put ok'))