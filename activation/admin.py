# vim: set fileencoding=utf8 :
from activation.models import *
from django.contrib import admin

class ActivationAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProfileActivation, ActivationAdmin)
