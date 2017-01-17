
'''

'''

from django import template

from django.utils.html import format_html
register = template.Library()   # 注册到tempate库里面


@register.filter
def docker_short_id(container_id):
    '''
    缩减容器ID的，使前端页面显示不会很长
    :param container_id: 容器ID
    :return:
    '''
    return container_id[0:13]

@register.filter   # filter只能对一个参数传入有效,调用到时候这样用  {{ xx.line  | ljf_power}}
def ljf_lower(val):
    return val.lower()


@register.simple_tag()     # simple_tag能够对传入多个参数有效
def guess_page(current_page,loop_num):
    '''

    :param current_page:  当前页
    :param loop_num:     页数范围
    :return:
    '''

    offset = abs(current_page - loop_num)
    if offset < 3:
        if current_page == loop_num :
            page_element = '''
            <li class="active"><a href="?page=%s">%s<span class="sr-only">(current)</span></a></li>
            '''%(loop_num,loop_num)
        else:
            page_element = '''
            <li><a href="?page=%s">%s<span class="sr-only">(current)</span></a></li>
            '''%(loop_num,loop_num)
        return format_html(page_element)
    else:
        return ''


