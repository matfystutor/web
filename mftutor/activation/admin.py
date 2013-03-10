# vim: set fileencoding=utf8 :
from .models import *
from django.contrib import admin

class ActivationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'email', 'first_name', 'last_name', 'activation_key', 'activation_request_time')
    search_fields = ['email', 'first_name', 'last_name', 'activation_key']

admin.site.register(ProfileActivation, ActivationAdmin)
