# vim: set fileencoding=utf8 :
from .models import ShirtPreference, ShirtOption
from django.contrib import admin

class ShirtPreferenceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'choice1', 'choice2')

class ShirtOptionAdmin(admin.ModelAdmin):
    list_display = ('choice',)

admin.site.register(ShirtPreference, ShirtPreferenceAdmin)
admin.site.register(ShirtOption, ShirtOptionAdmin)
