# vim: set fileencoding=utf8 :
from django.contrib import admin
from .models import Confirmation

class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'study', 'experience', 'resits', 'priorities',
            'firstaid', 'rusfriends', 'comment')

admin.site.register(Confirmation, ConfirmationAdmin)
