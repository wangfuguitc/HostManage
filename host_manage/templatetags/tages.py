#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def page_ele(page, current_page):
    if page == current_page:
        return mark_safe('''<li class="active"><a href="/hosts?page=%s">%s</a></li>''' % (page, page))
    elif abs(page-current_page) <= 2:
        return mark_safe('''<li><a href="/hosts?page=%s">%s</a></li>''' % (page, page))
    return ''
