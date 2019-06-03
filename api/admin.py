from django.contrib import admin

# Register your models here.
from repository import models
admin.site.register(models.Asset)
admin.site.register(models.Server)
admin.site.register(models.NetworkDevice)
admin.site.register(models.UserInfo)
admin.site.register(models.UserGroup)
admin.site.register(models.BusinessUnit)
admin.site.register(models.IDC)
admin.site.register(models.Disk)
admin.site.register(models.Memory)
admin.site.register(models.Nic)
admin.site.register(models.AssetRecord)
admin.site.register(models.ErrorLog)
