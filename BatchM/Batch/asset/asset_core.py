#!/usr/bin/env python
#__author__: Leo
'''
大量的功能，包含Asset类和run_salt_api的类。
'''
import os
import sys
import pycurl
path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(path)

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import  IntegrityError
from Batch import models
from Batch.plugs import record_log
from django.utils import timezone
import json
from io import BytesIO
from BatchM import settings
import paramiko
import collections



# 代码错误列表
# 1XX表示数据库客户提交的数据有问题，比如收集的信息不全，
# 101 表示资产数据在等待管理审核的时候再次提交资产数据.
# 2xx 表示管理员操作时间，比如管理员在审核提交的数据
error_code = {101: "you had post these data already ,don't post data again,please waiting  administrator for approving ",
              102: "Cannot find a asset object in DB by using asset id [%s] and SN [%s]",
              103: "The field [%s] is mandatory and not provided in your reporting data",
              104:"Cannot find any matches in source data by using key field val [%s],component data is missing in reporting data!",
              201:"this is a new asset , so you need IT admin's approval to creat the new asset id..",
              }

outdated_devices = ['fd0']   # floppy disk and so on ,these outdated devices were storaged in this list...

class Asset(object):
    '''
    处理资产信息的所有方法集合
    '''

    def __init__(self, request):
        '''
        实例化的时候做一些初始化操作，
        :param request:
        :return:
        '''
        self.request = request
        # must contains 'sn','asset_id' and 'asset_type'
        self.mandatory_fields = ['sn', 'asset_id', 'asset_type']
        self.field_sets = {
            'asset': ['manufactory'],
            'server': ['model', 'cpu_count', 'cpu_core_count', 'cpu_model', 'raid_type',
                       'os_type', 'os_distribution', 'os_release'],
            'networkdevice': []
        }
        self.response = {
            'error': [],
            'info': [],
            'warning': []
        }

    def response_msg(self, msg_type, key, msg):
        '''
        把错误信息归档，放到指定的消息类型中
        :param msg_type:   消息类型为error,info,warning
        :param key:
        :param msg:
        :return:
        '''

        if msg_type in self.response:
            self.response[msg_type].append({key: msg})
        else:
            raise ValueError

    def mandatory_check(self, data, only_check_sn=False):
        '''
        强制入库检测,
        1 首先判断是否提供了sn号，资产编号，资产类型，没有提供，在response里面添加该报错信息，
        2 是否对sn号进行检测，通过only_check_sn来确定是否需要执行,如果需要的话，要把Asset表里面的内容根据asset_id和sn号提取出来。
        :param data:
        :param only_check_sn:
        :return:
        '''
        for field in self.mandatory_fields:
            if not field in data:
                self.response_msg('error', 'MandatoryCheckFailed',
                                  error_code[103] % field)
        else:
            if self.response['error']: return False
        try:
            if not only_check_sn:  # means true
                self.asset_obj = models.Asset.objects.get(id=int(data['asset_id']), sn=data['sn'])
            else:
                self.asset_obj = models.Asset.objects.get(sn=data['sn'])
            return True
        except ObjectDoesNotExist as e:
            print(e)
            self.response_msg('error', 'AssetDataInvalid', error_code[102] %(data['asset_id'], data['sn']))
            # 添加批准确认标志
            self.waitting_approval = True
            return False

    def get_asset_id_by_sn(self):
        '''
        When the client first time reports it's data to Server,it doesn't know it's asset id yet,
        so it will come to the server asks for the asset it first,then report the data again
        :return:
        '''

        data = self.request.POST.get('asset_data')
        response = {}
        print('asset_data',data)
        if data:
            try:
                data = json.loads(data)
                # if the asset is already exist in DB,just return it's asset id to client
                if self.mandatory_check(data, only_check_sn=True):
                    response = {'asset_id': self.asset_obj.id}
                else:
                    if hasattr(self, 'waitting_approval'):
                        response = {'needs_aproval': error_code[201]}
                        self.clean_data = data
                        ret = self.save_new_asset_to_approval_zone()
                        if ret is not True:
                            response = {'needs_aproval':error_code[ret]}

                    else:
                        response = self.response
            except ValueError as e:
                print('here',e)
                self.response_msg("error", 'AssetDataInvalid', str(e))
                response = self.response
        else:
            self.response_msg('error', 'AssetDataInvalid', 'the reported asset data is not valid or provied')
            response = self.response
        return response

    def save_new_asset_to_approval_zone(self):
        '''
        When find out it is a new asset, will save the data into approval zone to waiting for IT admin's approvals
        :return:
        '''
        asset_sn = self.clean_data.get('sn')
        try:
            asset_already_in_approval_zone = models.NewAssetApprovalZone.objects.get_or_create(sn=asset_sn,
                                                                                       data=json.dumps(
                                                                                           self.clean_data),
                                                                                       manufactory=self.clean_data.get(
                                                                                           'manufactory'),
                                                                                       model=self.clean_data.get(
                                                                                           'model'),
                                                                                       asset_type=self.clean_data.get(
                                                                                           'asset_type'),
                                                                                       ram_size=self.clean_data.get(
                                                                                           'ram_size'),
                                                                                       cpu_model=self.clean_data.get(
                                                                                           'cpu_model'),
                                                                                       cpu_count=self.clean_data.get(
                                                                                           'cpu_count'),
                                                                                       cpu_core_count=self.clean_data.get(
                                                                                           'cpu_core_count'),
                                                                                       os_distribution=self.clean_data.get(
                                                                                           'os_distribution'),
                                                                                       os_release=self.clean_data.get(
                                                                                           'os_release'),
                                                                                       os_type=self.clean_data.get(
                                                                                           'os_type'),
                                                                                       salt_minion_id = self.clean_data.get(
                                                                                           'salt_minion_id'
                                                                                       )
                                                                                           )

            return True
        except IntegrityError:
            return 101     # error code里面的101

    def data_is_valid(self):
        '''
        检测数据是否有效，把获取到的数据jslon.load下，判断response消息字典里面有没有消息，没有才会return true
        :return:
        '''
        data = self.request.POST.get('asset_data')
        if data:
            try:
                data = json.loads(data)
                self.mandatory_check(data)
                self.clean_data = data

                if not self.response['error']:
                    print("-----dataisvalid!!")
                    return True
                elif self.waitting_approval:
                    self.save_new_asset_to_approval_zone()
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', 'The reported data is not valid or provied')
        else:
            self.response_msg('error', 'AssetDataInvalid', 'The reported asset data is not valid or provided')

    def __is_new_asset(self):
        '''
        判断这个数据是不是新的资产
        :return:
        '''
        # if have this(asset_type) attribute,this is a new asset!
        if not hasattr(self.asset_obj, self.clean_data['asset_type']):
            return True
        else:
            return False

    def data_inject(self):
        '''
        save data into DB,the data_is_valid() must returns True before call this function
        :return:
        '''

        if self.__is_new_asset():
            print("\033[32m --- new asset , going to create --- \033[0m")
            self.create_asset()
        # asset already exist,just update it!
        else:
            print('\003[33 ---asset already exist, going to update --\033[0m')
            self.update_asset()

    def data_is_valid_without_id(self):
        '''
        when there's no asset id in reporting data, goes through this function first
        :return:
        '''
        data = self.request.POST.get('asset_data')
        if data:
            try:
                data = json.loads(data)
                # push asset id into reporting data before doing the mandatory check
                asset_obj = models.Asset.objects.get_or_create(sn=data.get('sn'), name=data.get('sn'))
                data['asset_id'] = asset_obj[0].id
                # 强制数据检测
                self.mandatory_check(data, only_check_sn=True)
                self.clean_data = data
                if not self.response['error']:
                    return True
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))
        else:
            self.response_msg('error', 'AssetDataInvalid', 'The reported asset data is not valid or provided')

    def update_asset(self):
        '''
        更新数据的方法
        :return:
        '''
        func = getattr(self, '_update_%s' % self.clean_data['asset_type'])
        create_obj = func()

    def _update_server(self):
        '''
        更新服务器信息的方法
        :return:
        '''
        nic = self.__update_asset_component(data_source=self.clean_data['nic'],
                                            fk='nic_set',
                                            update_fields=['name', 'sn', 'model', 'macaddress', 'ipaddress', 'netmask',
                                                           'bonding'],
                                            identify_field='macaddress'
                                            )
        disk = self.__update_asset_component(data_source=self.clean_data['physical_disk_driver'],
                                             fk='disk_set',
                                             update_fields=['slot', 'sn', 'model', 'manufactory', 'capacity',
                                                            'iface_type'],
                                             identify_field='slot'
                                             )
        ram = self.__update_asset_component(data_source=self.clean_data['ram'],
                                            fk='ram_set',
                                            update_fields=['slot', 'sn', 'model', 'capacity'],
                                            identify_field='slot'
                                            )
        cpu = self.__update_cpu_component()
        manufactory = self.__update_manufactory_component()

        server = self.__update_server_component()


    def __update_manufactory_component(self):
        self.__create_or_update_manufactory(ignore_errs=True)

    def reformat_components(self, identify_field, data_set):
        '''
        This function is used as workround for some components's data structor is big dict ,yet
        the standard structor is list,e.g:
        :param identify_field:
        :param data_set:
        :return:
        '''
        for k, data in data_set.items():
            data[identify_field] = k

    def __verify_field(self, data_set, field_key, data_type, required=True,ignore_list=False):
        '''
        对 传入的数据做类型检测。
        :param data_set:  传入的数据
        :param field_key: 要对哪个字段进行判断
        :param data_type:  这个字段要属于哪个类型
        :param required:  标志位
        :return:
        '''
        field_val = data_set.get(field_key)
        if field_val:
            try:
                # 判断数据类型
                if type(field_val) is not list:
                    data_set[field_key] = data_type(field_val)
                    print('data_set',data_set)
                # 主要对没有做raid的磁盘做检测，并且有个标志位检测，如果是忽略列表为真，那么就跳过这个检测
                elif type(field_val) is list and not ignore_list:
                    for data in field_val:
                        data_set[field_key][data_set[field_key].index(data)] = data_type(data)
            except ValueError as e:
                self.response_msg('error', 'InvalidField',
                                  "the field [%s]'s data type is invalid , the correct data type should be [%s] " % (
                                  field_key, data_type))
        elif required == True:
            self.response_msg('error', 'LackOfField',
                              "the field [%s] has no value provided in your reporting data [%s]" % (
                              field_key, data_set))

    def _create_server(self):
        '''
        开始创建server类型的资产记录，下面都是调用相对应的cpu，磁盘内存存入的方法
        :return:
        '''
        self.__create_server_info()
        self.__create_or_update_manufactory()
        self.__create_cpu_component()
        self.__create_nic_component()
        self.__create_ram_component()
        self.__create_disk_component()

    def __create_server_info(self, ignore_errs=False):
        '''
        创建server的基本信息，包含资产ID，系统信息等
        :param ignore_errs: 标志位
        :return:
        '''
        try:
            self.__verify_field(self.clean_data, 'model', str)
            # no processing when theres no error happend
            if not len(self.response['error']) or ignore_errs == True:
                data_set = {
                    'asset_id': self.asset_obj.id,
                    'raid_type': self.clean_data.get('raid_type'),
                    'model': self.clean_data.get('model'),
                    'os_type': self.clean_data.get('os_type'),
                    'os_distribution': self.clean_data.get('os_distribution'),
                    'os_release': self.clean_data.get('os_release'),
                    'salt_minion_id':self.clean_data.get('salt_minion_id'),
                }
                obj = models.Server(**data_set)
                obj.save()

        except Exception as e:
            self.response_msg('error', 'ObjectCreateException', 'Object [server] %s' % str(e))

    def __create_or_update_manufactory(self, ignore_errs=False):
        '''
        更新或者创建工厂信息，如果有之前的记录，，那么就
        :param ignore_errs:
        :return:
        '''
        try:
            self.__verify_field(self.clean_data, 'manufactory', str)
            manufactory = self.clean_data.get('manufactory')
            if not len(self.response['error']) or ignore_errs == True:
                obj_exist = models.Manufactory.objects.filter(manufactory=manufactory)
                if obj_exist:
                    obj = obj_exist[0]
                # create a new record
                else:
                    obj = models.Manufactory(manufactory=manufactory)
                    obj.save()
                self.asset_obj.manufactory = obj
                print(' xxxxx begin create record xxxx')
                self.asset_obj.save()
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [manufactory] %s' % str(e))

    def __create_cpu_component(self, ignore_errs=False):
        '''
        创建CPU信息的记录，
        :param ignore_errs:
        :return:
        '''
        try:
            # self.__verify_field(self.clean_data,'model',str)
            self.__verify_field(self.clean_data, 'cpu_count', int)
            self.__verify_field(self.clean_data, 'cpu_core_count', int)
            # 如果没有错误或者说忽略错误的话，那么就往下走
            if not len(self.response['error']) or ignore_errs == True:
                data_set = {
                    'asset_id': self.asset_obj.id,
                    'cpu_model': self.clean_data.get('cpu_model'),
                    'cpu_count': self.clean_data.get('cpu_count'),
                    'cpu_core_count': self.clean_data.get('cpu_core_count'),
                }
                obj = models.CPU(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> has added new [cpu] component with data [%s]" % (self.asset_obj, data_set)
                self.response_msg('info', 'NewComponetAdded', log_msg)
                return obj

        except Exception as e:
           self.response_msg('error','ObjectCreateException','Object [cpu] %s' %str(e))

    def __create_disk_component(self):
        '''
        创建磁盘信息记录，
        :return:
        '''
        disk_info = self.clean_data.get('physical_disk_driver')
        print('disk_info',disk_info)
        if disk_info:
            try:
                for disk_item in disk_info:
                    print('disk_item',disk_item)

                    self.__verify_field(disk_item, 'slot', str)
                    print(disk_item.get('slot'))
                    if disk_item.get('slot') in outdated_devices:   # storaging outdated devices
                        data_set = { 'slot':disk_item.get('slot')}
                        obj = models.Disk(**data_set)
                        obj.save()
                        break

                    self.__verify_field(disk_item, 'slot', str)
                    self.__verify_field(disk_item, 'capacity', float)
                    if len(disk_item) > 2:
                        self.__verify_field(disk_item, 'iface_type', str)
                        self.__verify_field(disk_item, 'model', str)
                    # 如果没有错误那么就处理，有错误就不处理
                    print('self.response', self.response)
                    if not len(self.response['error']):
                        if len(disk_item) > 2:
                            data_set = {
                                'asset_id': self.asset_obj.id,
                                'sn': disk_item.get('sm'),
                                'slot': disk_item.get('slot'),
                                'capacity': disk_item.get('capacity'),
                                'model': disk_item.get('model'),
                                'iface_type': disk_item.get('iface_type'),
                                'manufactory': disk_item.get('manufactory'),
                            }
                        else:
                            data_set = {
                                'capacity': disk_item.get('capacity'),
                                'asset_id': self.asset_obj.id,
                                'slot': disk_item.get('slot'),
                            }
                    obj = models.Disk(**data_set)
                    obj.save()
            except Exception as e:
                self.response_msg('error','ObjectCreationException','Object [disk] %s' %str(e))
        else:
            self.response_msg('error', 'LackOfData', 'Disk info is not provide in your reporting data')

    def __create_nic_component(self):
        '''
        创建网卡信息记录
        :return:
        '''
        nic_info = self.clean_data.get('nic')
        print('nic_info',nic_info)
        if nic_info:
            for nic_item in nic_info:
                try:
                    self.__verify_field(nic_item, 'macaddress', str)
                    if not len(self.response['error']):
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'name': nic_item.get('name'),
                            'sn': nic_item.get('sn'),
                            'macaddress': nic_item.get('macaddress'),
                            'ipaddress': nic_item.get('ipaddress'),
                            'bonding': nic_item.get('bonding'),
                            'model': nic_item.get('model'),
                            'netmask': nic_item.get('netmask'),
                        }
                        obj = models.NIC(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error', 'ObjectCreateException', 'object [nic] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'Nic info is not provide in you reporting data')

    def __create_ram_component(self):
        '''
        创建内存信息记录。
        :return:
        '''
        ram_info = self.clean_data.get('ram')
        print('ram_info',ram_info)
        if ram_info:
            for ram_item in ram_info:
                try:
                    print('ram_item',ram_item)
                    self.__verify_field(ram_item, 'capacity', int)
                    print('self.response',self.response)
                    if not len(self.response['error']):
                        print('ram_info in not len',ram_info)
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'slot': ram_item.get('slot'),
                            'sn': ram_item.get('sn'),
                            'capacity': ram_item.get('capacity'),
                            'model': ram_item.get('model'),
                        }
                        obj = models.RAM(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg('error', 'ObjectCreateException', 'Object [ram] %s' % str(e))

    def __update_server_component(self):
        # def __update_server(self):
        '''
        更新服务器信息的
        :return:
        '''
        # 定义需要更新的哪些字段
        update_fields = ['model', 'raid_type', 'os_type', 'os_distribution', 'os_release']
        # 判断是否是属于server（也就是是否是主机）
        if hasattr(self.asset_obj, 'server'):
            self.__compare_component(model_obj=self.asset_obj.server,
                                     fields_from_db=update_fields,
                                     data_source=self.clean_data)
        else:
            self.__create_server_info(ignore_errs=True)

    def __update_manufatory_component(self):
        '''
        更新部件厂商信息，其实调用的就是创建厂商信息的方法
        :return:
        '''
        self.__create_or_update_manufactory(ignore_errs=True)

    def __update_cpu_component(self):
        '''
        更新CPU的信息，
        :return:
        '''
        # 定义需要更新的字段，
        update_fields = ['cpu_model', 'cpu_count', 'cpu_core_count']
        if hasattr(self.asset_obj, 'cpu'):

            self.__compare_component(model_obj=self.asset_obj.cpu,
                                     fields_from_db=update_fields,
                                     data_source=self.clean_data,
                                     )
        else:
            self.__create_cpu_component(ignore_errs=True)

    def __update_asset_component(self, data_source, fk, update_fields, identify_field=None):
        '''
        更新资产资源
        :param data_source: this component from reporting data
        :param fk: use it to find the connection between main asset obj and echo asset component
        :param update_fields: these fields will be updated
        :param identify_field:
        :return:
        '''
        # print(data_source,update_fields,identify_field)
        try:
            component_obj = getattr(self.asset_obj, fk)
            # this component is reverse many to many relation with Asset model
            if hasattr(component_obj, 'select_related'):
                objects_from_db = component_obj.select_related()
                for obj in objects_from_db:
                    key_field_data = getattr(obj, identify_field)
                    # use this key_field_data to find the relative data source from reporting data
                    if type(data_source) is list:
                        for source_data_item in data_source:
                            key_field_data_from_source_data = source_data_item.get(identify_field)
                            if key_field_data_from_source_data:
                                # #find the matched source data for this component,then should compare each field in
                                # this component to see if there's any changes since last update
                                if key_field_data == key_field_data_from_source_data:
                                    self.__compare_componet(model_obj=obj, fields_from_db=update_fields,
                                                            data_source=source_data_item)
                                    # #must break as last ,then if the loop is finished , logic will goes for ..
                                    # else part,then you will know that no source data is matched for by using this
                                    # key_field_data, that means , this item is lacked from source data, it makes sense
                                    # when the hardware info got changed. e.g: one of the RAM is broken, sb takes it away,
                                    # then this data will not be reported in reporting data
                                    # 如果循环没有退出，你就知道没有source data匹配到通过这个key_filed_data，换句话说，
                                    # 如果这个缺少source data，那么就说明这个硬件信息被更改了，
                                    break
                            else:  # key field data from source data cannot be none
                                self.response_msg('warning', 'AssetUpdateWarning',
                                                  "Asset component [%s]'s key field [%s] is not provided in reporting data " % (
                                                  fk, identify_field))

                        else:  # couldn't find any matches, the asset component must be broken or changed manually
                            self.response_msg("error", "AssetUpdateWarning",error_code[104]% (key_field_data))

                    else:
                        print('\033[31;1mMust be sth wrong,logic should goes to here at all.\033[0m')
                # compare all the components from DB with the data source from reporting data
                self.__filter_add_or_deleted_components(model_obj_name=component_obj.model._meta.object_name,
                                                        data_from_db=objects_from_db, data_source=data_source,
                                                        identify_field=identify_field)
            else:  # this component is reverse fk relation with Asset model
                pass
        except ValueError as e:
            print('\033[41;1m%s\033[0m' % str(e))

    def __compare_componet(self, model_obj, fields_from_db, data_source):
        for field in fields_from_db:
            val_from_db = getattr(model_obj, field)
            val_from_data_source = data_source.get(field)
            if val_from_data_source:
                # if type(val_from_db) is unicode:val_from_data_source = unicode(val_from_data_source)#no unicode in py3
                # if type(val_from_db) in (int,long):val_from_data_source = int(val_from_data_source) #no long in py3
                if type(val_from_db) in (int,):
                    val_from_data_source = int(val_from_data_source)
                elif type(val_from_db) is float:
                    val_from_data_source = float(val_from_data_source)
                if val_from_db == val_from_data_source:  # this field haven't changed since last update
                    pass
                    # print '\033[32;1m val_from_db[%s]  == val_from_data_source[%s]\033[0m' %(val_from_db,val_from_data_source)
                else:

                    db_field = model_obj._meta.get_field(field)
                    db_field.save_form_data(model_obj, val_from_data_source)
                    model_obj.update_date = timezone.now()
                    model_obj.save()
                    log_msg = "Asset[%s] --> component[%s] --> field[%s] has changed from [%s] to [%s]" % (
                    self.asset_obj, model_obj, field, val_from_db, val_from_data_source)
                    self.response_msg('info', 'FieldChanged', log_msg)
                    log_handler(self.asset_obj, 'FieldChanged', self.request.user, log_msg, model_obj)
            else:
                self.response_msg('warning', 'AssetUpdateWarning',
                                  "Asset component [%s]'s field [%s] is not provided in reporting data " % (
                                  model_obj, field))

        model_obj.save()

    def __filter_add_or_deleted_components(self, model_obj_name, data_from_db, data_source, identify_field):
        '''
        :param model_obj_name:
        :param data_from_db:
        :param data_source:
        :param identify_field:
        :return:
        '''
        data_source_key_list = []
        for data in data_source:
            if type(data) is str and type(data_source) is dict:
                data_source_key_list.append(data_source[data])
            else:
                data_source_key_list.append(data.get(identify_field))

        print('-->identify field [%s] from source  :', data_source_key_list)
        print('-->identify[%s] from data db:', [getattr(obj, identify_field) for obj in data_from_db])
#        if type(data_source_key_list) is not list:
        data_source_key_list = set(data_source_key_list)
        data_identify_val_from_db = set([getattr(obj, identify_field) for obj in data_from_db])
        # delete record in db
        data_only_in_db = data_identify_val_from_db - data_source_key_list
        # add into db
        data_only_in_data_source = data_source_key_list - data_identify_val_from_db
        if data_only_in_db:
            self.__delete_components(all_components=data_from_db, delete_list=data_only_in_db,
                                 identify_field=identify_field)
        if data_only_in_data_source:
            self.__add_components(model_obj_name=model_obj_name,
                                  all_components=data_source,
                                  add_list=data_only_in_data_source,
                                  identify_field=identify_field)

    def __add_components(self, model_obj_name, all_components, add_list, identify_field):
        '''
        添加要创建的资产数据表
        :param model_obj_name:
        :param all_components:
        :param add_list:
        :param identify_field:
        :return:
        '''
        print("all_components",all_components)
        print('add_list',add_list)
        print('identify_field',identify_field)
        model_class = getattr(models, model_obj_name)
        will_be_create_list = []
        for data in all_components:
            if data[identify_field] in add_list:
                will_be_create_list.append(data)
        try:
            for component in will_be_create_list:
                data_set = {}
                for field in model_class.auto_create_fields:
                    data_set[field] = component.get(field)
                data_set['asset_id'] = self.asset_obj.id
                data_set_tmp = data_set.copy()
                for data_set_items in data_set_tmp.keys():
                    if data_set[data_set_items] is  None:
                        data_set.pop(data_set_items)
                obj = model_class(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> component[%s] has justed added a new item [%s]" % (
                self.asset_obj, model_obj_name, data_set)
                self.response_msg('info', 'NewComponentAdded', log_msg)
                log_handler(self.asset_obj, 'NewComponentAdded', self.request.user, log_msg, model_obj_name)
        except Exception as e:
            print("\033[31m %s \033[0m" % str(e))
            log_msg = "Asset[%s] --> component[%s] has error: %s" % (self.asset_obj, model_obj_name, str(e))
            self.response_msg('error', "AddingComponentException", log_msg)

    def __delete_components(self, all_components, delete_list, identify_field):
        '''
        删除掉指定的资产记录
        :param all_components:
        :param delete_list:
        :param identify_field:
        :return:
        '''
        deleting_obj_list = []

        for obj in all_components:
            val = getattr(obj, identify_field)
            if val in delete_list:
                deleting_obj_list.append(obj)

        for i in deleting_obj_list:
            log_msg = "Asset[%s] --> component[%s] --> is lacking from reporting source data, assume it has been removed or replaced,will also delete it from DB" % (
            self.asset_obj, i)
            self.response_msg('info', 'HardwareChanged', log_msg)
            log_handler(self.asset_obj, 'HardwareChanged', self.request.user, log_msg, i)
            i.delete()


    def __compare_component(self, model_obj, fields_from_db, data_source):
        '''

        :return:
        '''

        for field in fields_from_db:
            val_from_db = getattr(model_obj, field)
            val_from_data_source = data_source.get(field)
            if val_from_data_source:
                if type(val_from_db) in (int,):
                    val_from_data_source = int(val_from_data_source)
                elif type(val_from_db) is float:
                    val_from_data_source = float(val_from_data_source)
                # 如果下面两个相等，那么说明这个字段的数据在最后一次更新的时候有更新
                if val_from_db != val_from_data_source:
                    print('\033[34;1m val_from_db[%s]  != val_from_data_source[%s]\033[0m' \
                          % (val_from_db, val_from_data_source), type(val_from_db), type(val_from_data_source))
                    db_field = model_obj._meta.get_field(field)
                    db_field.save_form_data(model_obj, val_from_data_source)
                    model_obj.update_date = timezone.now()
                    model_obj.save()
                    log_msg = "Asset[%s] --> component[%s] --> field[%s] has changed from [%s] to [%s]" % (
                    self.asset_obj, model_obj, field, val_from_db, val_from_data_source)
                    self.response_msg('info', 'FieldChanged', log_msg)
                    log_handler(self.asset_obj, 'FieldChanged', self.request.user, log_msg, model_obj)
            else:
                self.response_msg('warning', 'AssetUpdateWarning', "Asset component [%s]'s field [%s] \
                 is not provided in reporting data " % (model_obj, field))
        model_obj.save()

    def create_asset(self):
        '''
        create asset by get asset type
        :return:
        '''
        # dir(self)
        try:
            func = getattr(self, '_create_%s' % self.clean_data['asset_type'])
            create_obj = func()
        except AttributeError:
            if self.clean_data['asset_type'] == 'server':
                self._create_server()
            elif self.clean_data['asset_type'] == 'network':
                self._create_network_device()
                # create_obj = func()
                # self.__create_server()




class run_salt_api(object):
    '''
    调用saltapi来调用salt完成相关操作
    '''

    def __init__(self,username,passwd,auth_method='pam',ip="127.0.0.1",port=8010):
        self.ip = ip
        self.port = port
        self.username = username
        self.passwd = passwd
        self.auth_method = auth_method
        self.token = self.api_login()
        self.logger = record_log('root', '%s/../log/access.log' % os.path.dirname(__file__))

    def api_login(self):
        '''
        登陆用户，获取token
        '''
        url = "http://%s:%d/login" %(self.ip,self.port)
        ch = pycurl.Curl()
        info = BytesIO()
        ch.setopt(ch.URL,url)
        ch.setopt(ch.WRITEFUNCTION,info.write)
        ch.setopt(ch.POST,True)
        # add auth info to http header
        ch.setopt(ch.HTTPHEADER,['Accept: application/json'])
        ch.setopt(ch.POSTFIELDS,'username=%s&password=%s&eauth=%s'%(self.username,self.passwd,self.auth_method))
        ch.setopt(ch.HEADER,True)
        ch.perform()
        # get token from salt-api  response
        html = info.getvalue().decode()
        return_data = html.split('\n')[-1]
        import json
        token = json.loads(return_data)
        token = token['return'][0]['token']
        info.close()
        ch.close()
        self.logger.info('already get this token')
        return token

    def api_exec(self,target,func,arg='',expr_form=None,arg_num=0):
        '''
        调用saltapi执行相关的saltstack函数去执行
        pparam target: 要对哪个minion执行
        :param func:   执行哪个方法
        :param arg:     执行这个方法的参数
        :param arg_num:  参数的数量
        :return:
        '''
        import time

        url = "http://%s:%d" %(self.ip,self.port)
        ch = pycurl.Curl()
        info = BytesIO()
        ch.setopt(ch.URL,url)
        ch.setopt(ch.WRITEFUNCTION,info.write)
        ch.setopt(ch.POST,True)

        ch.setopt(ch.HTTPHEADER,['Accept: application/x-yaml','X-Auth-Token: %s'%self.token])
        if arg_num == 0:
            if expr_form:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;expr_form=%s&amp;fun=%s'
                           %(target,expr_form,func))

            else:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;fun=%s'%(target,func))
        elif arg_num == 1:
            if expr_form:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;expr_form=%s&amp;fun=%s&amp;arg=%s'
                %(target,expr_form,func,arg))
            else:
                ch.setopt(ch.POSTFIELDS,'client=local&amp;tgt=%s&amp;fun=%s&amp;arg=%s'%(target,func,arg))

        ch.setopt(ch.HEADER,False)
        ch.perform()
        html = info.getvalue().decode()
        info.close()
        ch.close()
        self.logger.info('already execute this command : [%s %s] ,targets: [%s] ,expr_form:[%s]'%(func,arg,target,expr_form))
        return html


class Create_SaltGroup(object):
    '''
    生成saltstack 的group的配置文件，在/etc/salt/master.d/下面生成。
    '''
    def __init__(self,**group_info):
        self.group_info = group_info   # self.group_info must be dict format
        self.group_file = settings.SaltGroupConfigFile
        nodegroups = os.popen("grep nodegroups: %s >/dev/null;echo $?"%self.group_file).read().split('\n')[0]
        if int(nodegroups):
            os.system("echo 'nodegroups:' >>%s"%self.group_file)


    def add_groups(self,create_group_id_list):
        '''
        添加组和组成员信息的
        ;:param:create_group_id_list 组ID列表，用来过滤哪些是已经在salt配置文件里面增加来到。
        :return:
        '''
        # 通过数据库里面到y一个字段来判断是否已经在配置文件里面生成来。
        for i in models.SaltGroup.objects.filter(id__in=create_group_id_list):
                if  i.whether_create:
                    self.group_info.pop(i.group_name)

        with open(self.group_file,'a') as f:
            for i,k in self.group_info.items():
                # 判断之前是否有同样到组名
                result_code = os.popen("grep ^'    %s:' %s >/dev/null ;echo $?"%(i,self.group_file)).read().split('\n')[0]
                if  int(result_code):
                    f.seek(0,2)
                    f.write("    %s: "%(i))
                    for v in k:
                        f.seek(0,2)
                        if k.index(v) == 0:  # if the v is first value in the list ,it should add L@ befor itself
                            f.write("L@%s,"%(v))
                        elif k.index(v) == len(k)-1: # if the v is last one in the list,it should add ' end of line
                            f.write("%s\n"%v)
                        else:
                            f.write("%s,"%(v))
        return True

    def del_groups(self):
        '''
        删除组和组成员信息的
        :return:
        '''
        import datetime
        new_file_name = self.group_file+datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        onef=open(new_file_name,'a+')
        with open(self.group_file,'a+') as f:
            for line in f:
                for group_name in self.group_info:
                    if not line.strip().startswith(group_name):
                        onef.write(line)
        onef.close()
        os.system("\mv %s  %s"%(new_file_name,self.group_file))

        return True



    def changge_groups(self):
        '''
        改变组和组成员信息的
        :return:
        '''
        pass

class sftp_paramiko(object):
    '''
     put pkg or file to remote machine
    '''

    def __init__(self,request,auth_method,host,port=22,username='root',password=None):
        self.s = paramiko.SSHClient()
        self.s.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.s.load_system_host_keys()
        self.auth_method = auth_method
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key = paramiko.RSAKey.from_private_key_file(settings.SshKeyFile)
        #paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        #self.logger = record_log("%s %s"%(request.user.get_username(),request.user.email, '%s/../log/access.log' % os.path.dirname(__file__)))

    def put_file(self,local_file,remote_file):
        '''
        send file to remote host
        :param file:
        :return:
        '''
        try:
            if self.auth_method == 'key':
                #self.key = paramiko.RSAKey.from_private_key_file(settings.SshKeyFile)
                t = paramiko.Transport((self.host,self.port))
                t.connect(username=self.username,pkey=self.key)
                sftp = paramiko.SFTPClient.from_transport(t)
                sftp.put(local_file,remote_file)
            else:
                t = paramiko.Transport((self.host,self.port))
                t.connect(username=self.username,password=self.password)
                print(" ")
                sftp=paramiko.SFTPClient.from_transport(t)
                sftp.put(local_file,remote_file)
                print(sftp.stat(remote_file))
            t.close()
            return True
        except paramiko.ssh_exception.AuthenticationException as e:
            return "Authentication failed"

    def execute_command(self,cmd):
        '''
        执行命令在远程服务器上
        :param cmd:
        :return:
        '''
        if self.auth_method == 'password':
            self.s.connect(self.host, self.port, self.username, self.password, timeout=10)
        else:
            #self.key = paramiko.RSAKey.from_private_key_file(settings.SshKeyFile)
            self.s.connect(self.host, self.port, self.username, self.key, timeout=10)
        stdin, stdout, stderr = self.s.exec_command(cmd)
        result = stdout.read(), stderr.read()
        rt = ''
        for i in result:
            rt+=i.decode()
        self.s.close()
        return rt


    def communicate_with_shell(self,session_timeout=30,**kwargs):
        '''
        execute script by bash,  sending some word to answer the recive's response
        :param session_timeout:
        :param kwargs:
        :return:
        '''
        print('communicate_with_shell',kwargs,kwargs.keys())
        tmp_list = []
        script_name = kwargs.get('script_name')
        tmp_list =  kwargs.get('args').split(',')

        if tmp_list[0] == "n" or  tmp_list[0] == "N":  # if  n in request, so remove a mark from matchs list!
            settings.InvokeShellMatchs.pop(1)
        tmp_list.append('\n')

        print('tmp_list',tmp_list)

        t = paramiko.Transport((self.host, self.port))
        if self.auth_method == "key":
            t.connect(username=self.username,pkey=self.key)
        else:
            t.connect(username=self.username, password=self.password)
        channel = t.open_session()
        channel.settimeout(session_timeout)
        channel.get_pty()
        channel.invoke_shell()
        channel.send('%s %s\n'%(settings.ScriptDefaultInterpreter,script_name))

        recv_content = channel.recv(8888)
        for i in settings.InvokeShellMatchs:   # matching recvives and send a correct answer
            print('InvokeShellMatchs',i)
            while not recv_content.endswith(b'%b'%(i.encode())):
                recv_content = channel.recv(8888)
                print(recv_content)
            print('index',settings.InvokeShellMatchs.index(i))
            print('send word',tmp_list[settings.InvokeShellMatchs.index(i)])
            channel.send("%s\n"%(tmp_list[settings.InvokeShellMatchs.index(i)]))
        return True


def log_handler(asset_obj, event_name, user, detail, component=None):
    log_catelog = {
        1: ['FieldChanged', 'HardwareChanged'],
        2: ['NewComponentAdded']
    }
    if not user.id:
        user = models.MyUser.objects.filter(is_admin=True).last()
    event_type = None
    for k, v in log_catelog.items():
        if event_name in v:
            event_type = k
            break
    log_obj = models.EventLog(
            name=event_name,
            event_type=event_type,
            asset_id=asset_obj.id,
            component=component,
            detail=detail,
            user_id=user.id,
    )
    log_obj.save()
