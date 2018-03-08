from django import forms
from django.forms import fields
from host_manage import models
from django.forms import widgets
from django.core.exceptions import ValidationError


class HostForm(forms.Form):
    id = fields.IntegerField(required=False)
    host_name = fields.CharField(widget=widgets.Input(attrs={'class': 'form-control', 'id': False,
                                                             'style': 'width:60%;display:inline'}))
    state = fields.ChoiceField(choices=[(1, '在线'), (2, '下线'), ],
                               widget=widgets.Select(attrs={'class': 'form-control', 'id': False,
                                                            'style': 'width:60%;display:inline'}))
    kind = fields.ChoiceField(choices=[(1, '服务器'), (2, '防火墙'), (3, '路由器'), (4, '交换机'), ],
                              widget=widgets.Select(attrs={'class': 'form-control', 'id': False,
                                                           'style': 'width:60%;display:inline'}))
    group_id = fields.ChoiceField(choices=models.HostGroup.objects.values_list('id', 'name'),
                                  widget=widgets.Select(attrs={'class': 'form-control', 'id': False,
                                                               'style': 'width:60%;display:inline'}))
    ip = fields.GenericIPAddressField(widget=widgets.Input(attrs={'class': 'form-control', 'id': False,
                                                                  'style': 'width:60%;display:inline'}))
    username = fields.CharField(widget=widgets.Input(attrs={'class': 'form-control', 'id': False,
                                                            'style': 'width:60%;display:inline'}))
    password = fields.CharField(widget=widgets.PasswordInput(attrs={'class': 'form-control', 'id': False,
                                                                    'style': 'width:60%;display:inline'}))

    def clean_host_name(self):
        obg_host_name = models.Host.objects.filter(host_name=self.cleaned_data['host_name'])
        if not obg_host_name:
            return self.cleaned_data['host_name']
        else:
            if 'id' in self.cleaned_data.keys():
                if obg_host_name.filter(id=self.cleaned_data['id']):
                    return self.cleaned_data['host_name']
            raise ValidationError('主机名已存在')

    def clean_ip(self):
        obj_ip = models.Host.objects.filter(ip=self.cleaned_data['ip'])
        if not obj_ip:
            return self.cleaned_data['ip']
        else:
            if 'id' in self.cleaned_data.keys():
                if obj_ip.filter(id=self.cleaned_data['id']):
                    return self.cleaned_data['ip']
            raise ValidationError('ip已存在')


class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})
    password = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})

