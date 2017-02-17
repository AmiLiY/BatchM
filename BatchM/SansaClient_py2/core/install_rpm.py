#!/usr/bin/env
# conding:utf8
# this script will install some dependent rpm packages first ,
import os
import commands
import sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_command():
    '''
    getting need to execute commands from file first_install in directory var
    :return:
    '''
    if not os.path.exists("%s/var/installed"%base_dir):
        f = open('%s/var/first_install'%base_dir,'r')
        tmp_list=[]
        how_many=len(f.readlines())   # how many command need to execute
        f.seek(0)
        for line in f.readlines():
            print(line)
            result = commands.getstatusoutput(line.strip())
            if result[0] != 0:   # 0 means the  command execute correctly,because the function getstatusoutput return 0 is means True.
                exit("\033[31m I'm Sorry! some dependent rpm packages installed was false!! "
                     "\n\t please install it by yourself!! "
                     "\n\t installing commands are in SansaClient_py2/var/first_install ,"
                     "\n\t so that you can install them by yourself\033[0m")
            else:
                tmp_list.append(line)    # if the command execute correctly,then put result into tmp_list
        if tmp_list.count(0) == how_many:   # if length of tmp_list equal how_many ,then we can say packages was installed successfully!
            os.mknod('%s/var/installed'%base_dir)





