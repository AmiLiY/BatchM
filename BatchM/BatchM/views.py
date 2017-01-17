'''
仅仅处理用户登录到操作以及返回首页
'''
from django.contrib.auth import authenticate
from django.shortcuts import HttpResponse,render,HttpResponseRedirect
from django.contrib import auth


# 显示首页
def index(request):
    return render(request,'index.html')

__tmp_list = []

def auth_login(request):
    '''
    处理用户登录的
    :param request:
    :return:
    '''
    if request.method == "GET":
        if request.GET.get('next'):
            __tmp_list.append(request.GET.get('next'))
            print('go_page',__tmp_list)
        return render(request,'login.html')
    elif request.method == "POST":
        print(request.POST)
        email = request.POST.get('email')
        passwd = request.POST.get('password')
        print(email,passwd)
        user = auth.authenticate(email=email,password=passwd)
        print(type(user))
        if user is not None:
            auth.login(request,user)
            return HttpResponseRedirect( __tmp_list[0] or '/')
        else:
            return render(request,'login.html',{'error':'Email or Password is wrong!!  Enter it again!'})

def auth_logout(request):
    '''
    负责用户推出登陆的。
    :param request:
    :return:
    '''
    auth.logout(request)
    return HttpResponseRedirect('/')

