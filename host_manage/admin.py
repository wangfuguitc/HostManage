from django.contrib import admin
from host_manage import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Host)
admin.site.register(models.HostGroup)
