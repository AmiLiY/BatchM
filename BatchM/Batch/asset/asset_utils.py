'''
主要处理token认证
'''

import time,hashlib,json
from Batch import models
from django.shortcuts import render,HttpResponse
from BatchM import settings


def json_date_handler(obj):
    if hasattr(obj,'isformat'):
        return obj.strftime("%Y-%m-%d")

def json_datetime_handler(obj):
    if hasattr(obj,'isoformat'):
        return obj.strftime("%Y-%m-%d %H:%M:%S")

def gen_token(username,timestamp,token):
    token_format = "%s\n%s\n%s" %(username,timestamp,token)
    obj = hashlib.md5()
    obj.update(token_format)
    return obj.hexdigest()[10:17]

def token_required(func):
    def wrapper(*args,**kwargs):
        response = {"error":[]}

        get_args = args[0].GET
        username = get_args.get("user")
        token_md5_from_client = get_args.get('token')
        timestamp = get_args.get('timestamp')
        if not username or not timestamp or not token_md5_from_client:
            response['errors'].append({"auth_failed":"This api requires token authentication!"})
            return HttpResponse(json.dumps(response))

        try:
            user_obj = models.UserProfile.objects.get(email=username)
            token_md5_from_server = gen_token(username,timestamp,user_obj.token)
            if token_md5_from_client != token_md5_from_server:
                response['errors'].append({"auth_failed":"Invalid username or token_id"})
            else:
                if abs(time.time()) - int(timestamp) > settings.TOKEN_TIMEOUT: # default timeout 120
                    response['error'].append({'auth_failed':"the token is expired"})
                else:
                    pass

                print("\033[41;1m;%s ---client:%s\033[0m" %(time.time(),timestamp), time.time() - int(timestamp))

        except Exception as e:
            response['error'].append({"auth_failed":"Invalid username or token_id"})
        if response['error']:
            return HttpResponse(json.dumps(response))
        else:
            return  func(*args,**kwargs)
    return wrapper



