from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.Customer)
admin.site.register(models.Question)
admin.site.register(models.Project)
admin.site.register(models.Journalism)
