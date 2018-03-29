#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from django import template
from django.utils.safestring import mark_safe


register = template.Library()


# 分页显示主机
@register.simple_tag
def page_ele(page, current_page, group):
    # 判断是否通过主机组过滤主机
    if group:
        if page == current_page:
            return mark_safe('''<li class="active"><a href="/hosts?page=%s&group=%s">%s</a></li>''' % (page, group, page))
        elif abs(page-current_page) <= 2:
            return mark_safe('''<li><a href="/hosts?page=%s&group=%s">%s</a></li>''' % (page, group, page))
    else:
        if page == current_page:
            return mark_safe('''<li class="active"><a href="/hosts?page=%s">%s</a></li>''' % (page, page))
        elif abs(page-current_page) <= 2:
            return mark_safe('''<li><a href="/hosts?page=%s">%s</a></li>''' % (page, page))
    return ''


# 判断用户是否有管理某主机的权限
@register.simple_tag
def host_ele(user_host, host_id, host_name):
    for host in user_host.all():
        if host_id == host.id:
            return mark_safe('''<option value="%s" selected="selected">%s</option>''' % (host_id, host_name))
    return mark_safe('''<option value="%s">%s</option>''' % (host_id, host_name))


# 判断用户是否有管理某主机组的权限
@register.simple_tag
def host_group_ele(user_host_group, host_group_id, host_group_name):
    for host_group in user_host_group.all():
        if host_group_id == host_group.id:
            return mark_safe('''<option value="%s" selected="selected">%s''' % (host_group_id, host_group_name))
    return mark_safe('''<option value="%s">%s''' % (host_group_id, host_group_name))
