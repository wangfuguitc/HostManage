from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    role_type_choices = (
        (1, 'admin'),
        (2, 'user'),
    )
    username = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    role = models.IntegerField(choices=role_type_choices, default=1)
    host = models.ManyToManyField('Host', blank=True)
    host_group = models.ManyToManyField('HostGroup', blank=True)

    def __str__(self):
        return self.name


class Host(models.Model):
    state_type_choices = (
        (1, '在线'),
        (2, '下线')
    )
    kind_choices = (
        (1, '服务器'),
        (2, '防火墙'),
        (3, '路由器'),
        (4, '交换机')
    )
    host_name = models.CharField(max_length=32, unique=True)
    state = models.IntegerField(choices=state_type_choices, default=1)
    kind = models.IntegerField(choices=kind_choices, default=1)
    group_id = models.ForeignKey('HostGroup', on_delete=models.SET_NULL, null=True)
    ip = models.GenericIPAddressField(unique=True)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)

    def __str__(self):
        return self.host_name


class HostGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name
