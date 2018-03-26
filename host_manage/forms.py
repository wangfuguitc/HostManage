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
    group_id = fields.ChoiceField(widget=widgets.Select(attrs={'class': 'form-control', 'id': False,
                                                               'style': 'width:60%;display:inline'}))
    ip = fields.GenericIPAddressField(widget=widgets.Input(attrs={'class': 'form-control', 'id': False,
                                                                  'style': 'width:60%;display:inline'}))
    username = fields.CharField(widget=widgets.Input(attrs={'class': 'form-control', 'id': False,
                                                            'style': 'width:60%;display:inline'}))
    password = fields.CharField(widget=widgets.PasswordInput(attrs={'class': 'form-control', 'id': False,
                                                                    'style': 'width:60%;display:inline'}))

    # 判断主机名是否重复
    def clean_host_name(self):
        obj_host_name = models.Host.objects.filter(host_name=self.cleaned_data['host_name'])
        if not obj_host_name:
            return self.cleaned_data['host_name']
        else:
            if 'id' in self.cleaned_data.keys():
                if obj_host_name.filter(id=self.cleaned_data['id']):
                    return self.cleaned_data['host_name']
            raise ValidationError('主机名已存在')

    # 判断ip是否重复
    def clean_ip(self):
        obj_ip = models.Host.objects.filter(ip=self.cleaned_data['ip'])
        if not obj_ip:
            return self.cleaned_data['ip']
        else:
            if 'id' in self.cleaned_data.keys():
                if obj_ip.filter(id=self.cleaned_data['id']):
                    return self.cleaned_data['ip']
            raise ValidationError('ip已存在')

    # 不重启服务的情况下获取到最新的主机组列表
    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['group_id'].choices = models.HostGroup.objects.values_list('id', 'name')


class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})
    password = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})


class HostGroupForm(forms.Form):
    id = fields.IntegerField(required=False)
    name = forms.CharField(
        max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位'})

    # 判断主机组名是否重复
    def clean_name(self):
        obj_name = models.HostGroup.objects.filter(name=self.cleaned_data['name'])
        if not obj_name:
            return self.cleaned_data['name']
        else:
            if 'id' in self.cleaned_data.keys():
                if obj_name.filter(id=self.cleaned_data['id']):
                    return self.cleaned_data['name']
            raise ValidationError('组名已存在')


class UserForm(forms.Form):
    id = fields.IntegerField(required=False)
    username = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})
    password = forms.CharField(
        min_length=5, max_length=32,
        error_messages={'required': '不能为空', 'max_length': '不能大于32位', 'min_length': '不能小于5位'})
    name = forms.CharField()
    role = fields.ChoiceField(choices=[(1, 'admin'), (2, 'user'), ])
    host = fields.MultipleChoiceField(required=False)
    host_group = fields.MultipleChoiceField(required=False)

    # 判断用户名是否重复
    def clean_username(self):
        obj_username = models.User.objects.filter(username=self.cleaned_data['username'])
        if not obj_username:
            return self.cleaned_data['username']
        else:
            if 'id' in self.cleaned_data.keys():
                if obj_username.filter(id=self.cleaned_data['id']):
                    return self.cleaned_data['username']
            raise ValidationError('用户名已存在')

    # 防止修改用户名
    def clean(self):
        if 'id' in self.cleaned_data.keys():
            if models.User.objects.filter(id=self.cleaned_data['id']).filter(username=self.cleaned_data['username']):
                return self.cleaned_data
            else:
                ValidationError('用户名不能修改')

    # 不重启服务的情况下获取到最新的主机和主机组列表
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['host'].choices = models.Host.objects.values_list('id', 'host_name')
        self.fields['host_group'].choices = models.HostGroup.objects.values_list('id', 'name')
