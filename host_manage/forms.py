from django import forms
from django.forms import fields
from host_manage import models
from django.forms import widgets
from django.core.exceptions import ValidationError


class HostForm(forms.Form):
    host_name = fields.CharField(widget=widgets.Input(attrs={'class': 'form-control'}))
    state = fields.ChoiceField(choices=[(1, '在线'), (2, '下线'), ],
                               widget=widgets.Select(attrs={'class': 'form-control'}))
    kind = fields.ChoiceField(choices=[(1, '服务器'), (2, '防火墙'), (3, '路由器'), (4, '交换机'), ],
                              widget=widgets.Select(attrs={'class': 'form-control'}))
    group_id = fields.ChoiceField(choices=models.HostGroup.objects.values_list('id', 'name'),
                                  widget=widgets.Select(attrs={'class': 'form-control'}))
    ip = fields.GenericIPAddressField(widget=widgets.Input(attrs={'class': 'form-control'}))
    username = fields.CharField(widget=widgets.Input(attrs={'class': 'form-control'}))
    password = fields.CharField(widget=widgets.PasswordInput(attrs={'class': 'form-control'}))

    def clean_host_name(self):
        count = models.Host.objects.filter(host_name=self.cleaned_data['host_name']).count()
        if not count:
            return self.cleaned_data['host_name']
        else:
            raise ValidationError('主机名已存在')

    def clean_ip(self):
        count = models.Host.objects.filter(ip=self.cleaned_data['ip']).count()
        if not count:
            return self.cleaned_data['ip']
        else:
            raise ValidationError('ip已存在')
